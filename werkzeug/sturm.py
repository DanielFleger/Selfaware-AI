# -*- coding: utf-8 -*-
"""B-167 Sturm auf Franz' Lord mit unserer Armee (Daniel 22.10.2026 00:31: "in Sicherheit sammeln, dann vorpreschen",
"das Torhaus vorne rechts schlagen waere viel leichter gewesen als die vier Mauerabschnitte", "gebuendelter").

Ein Lauf: Grundstand B140 laden (beide Heere), dann je Ziel
  SAMMELN  - Streitkolben und Nahkaempfer laufen auf ein Sammelfeld ohne Beschuss (Gefahrenkarte 0), nahe am Zugang
  STURM    - alle zusammen: Mauerkachel (Angriff beim Ankommen am Zugang, logik.lua haelt die Kachel), Torhaus (Gebaeude-
             Angriff) oder Lord
  gefallen - neu planen; wer waehrend des Sturms neu dazukommt, wartet am Sammelfeld auf die naechste Welle
Planer: mechanik.durchbruch_schritte - Mauerweg gegen jedes feindliche Torhaus (Leben aus dem Lagebild / Schaden je Treffer an
Tor und Turm aus dem Code), das schnellste Ziel gewinnt (Zeit vor Gefahr).
Dazu: Nachschub (Streitkolben anwerben, sonst Keule/Leder kaufen, sonst Haus), 2 Jaeger auf Feuerballisten (Typ 77),
Fernkaempfer auf feindliche Soldaten nahe dem Lord (Pfeile auf den Lord am Bergfried wirken nicht - Wissensregister L151).
Ausloeser: keine Wirkung am Ziel bis zur Frist (Weg x 12 Takte + 2 Trefferrunden) -> Ende mit Grund. Kein zweiter Lauf.
Ergebnis: daten/sturm.jsonl.   Aufruf: SHC_INSTANZ=5 python werkzeug/sturm.py
"""
import json
import math
import os
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import numpy as np  # noqa: E402
from scipy import ndimage  # noqa: E402

import augen_durchbruch as AD  # noqa: E402
import gefecht  # noqa: E402
import mechanik  # noqa: E402
import shc  # noqa: E402
import speicher  # noqa: E402
from bauen import NACH_TYP  # noqa: E402
from laden import befehl  # noqa: E402
from waechter import lies_gebaeude, lies_lagebild  # noqa: E402

AUS = os.path.join(HIER, "..", "daten", "sturm.jsonl")
# gemessene Verlustraten je Ziel ("art:ziel" -> Tote, Takte im Sturm) - jeder Sturm schreibt nach (Daniel 01:11 "so wie du
# vorschlaegst einbauen": losgehen, wenn es reicht, statt auf den Letzten zu warten)
RATEN = os.path.join(HIER, "..", "daten", "sturm_raten.json")


def raten_laden():
    try:
        return json.load(open(RATEN, encoding="utf-8")).get("raten", {})
    except (OSError, ValueError):
        return {}


def raten_schreiben(raten, quelle):
    json.dump({"quelle": quelle, "raten": raten}, open(RATEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
E0, ES = AD.E0, AD.ES
SP, FEIND = 1, 2
PD1 = 0x0115BDF8 + SP * 0x39F4
GOLD1, KEULE1, LEDER1, HOLZ1 = PD1 + 0x4D0 + 15 * 4, PD1 + 0x4D0 + 21 * 4, PD1 + 0x4D0 + 23 * 4, PD1 + 0x4D0 + 2 * 4
FEUER1 = PD1 + 136                                   # Bauern am Lagerfeuer (erstes_spiel: PD + 136)
GOLD2 = 0x0115BDF8 + FEIND * 0x39F4 + 0x4D0 + 15 * 4
STREITKOLBEN, BALLISTE, TORHAUS, KASERNE, HUETTE = 26, 77, 75, 9, 1
AUSBILDUNG = {8, 9, 24}                               # Soeldnerposten, Kaserne, Ingenieursgilde (bauen.NACH_TYP)
FERN = set(gefecht.FERN_REICH)


# Stellschrauben (Daniel 22.10. 01:24 "das Wichtigste ist, dass nichts davon hart codiert ist, sondern die KI selbst draufkommt"):
# jede Entscheidung, die vorher eine feste Regel war, ist eine Wahl - sturm_lernen.py waehlt je Lauf und bewertet das Ergebnis
STELLSCHRAUBEN = {
    "lord": ["einzeln", "gruppe", "kette"],      # Angriff auf den Lord: Einzelbefehle / ein Gruppenbefehl / Wegkette bis vor den Lord
    "tor": ["einzeln", "gruppe"],                # Torhaus: Einzelbefehle / ein Gruppenbefehl
    "losgehen": ["alle", "bedarf"],              # erster Sturm: wenn alle da sind / sobald der Bedarf aus der Verlustrate da ist
    "jaeger": ["aus", "wirkung"],                # Jaeger: keine / nur auf Feinde, die gerade einen von uns angreifen
    "wegweiser": ["aus", "an"],                  # Sammeln/Nachschub/Sturm: direkt / Wegkette entlang des sicheren Plans
}
STANDARD = {"lord": "einzeln", "tor": "einzeln", "losgehen": "alle", "jaeger": "wirkung", "wegweiser": "an"}
ZIELEINHEIT = 926                                    # Einheit +926 (short): wen sie gerade angreift (logik.lua lagebild "zieleinheit")


def s32(a):
    return int.from_bytes(speicher.lies(a, 4), "little", signed=True)


def kennung(roh, n):
    return int.from_bytes(roh[n * ES + 0x98:n * ES + 0x9C], "little", signed=True)


def abstand(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def eigene_soldaten(roh):
    """{nr: einheit} - lebende eigene Soldaten (Kennung je Nummer separat)."""
    aus = {}
    for n in range(1, 3000):
        e = AD.einheit(roh, n)
        if e["zustand"] != 0 and e["leben"] > 0 and e["besitzer"] == SP and e["typ"] in shc.SOLDATEN:
            aus[n] = e
    return aus


def plane_ziel(start, maenner, mk, lnr_xy):
    """Schnellstes Ziel: Mauerweg oder ein Torhaus einschlagen. Rueckgabe dict art ("mauer"/"tor"/"lord"), ziel, zug, weg, takte."""
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    e = AD.ebenen()
    G = lies_gebaeude()
    sperre = AD.sperre_feindbau(e["bau"])
    gf, nah = schaden_feld(e["link"].shape[0])
    args = (e["link"], e["logik"], e["bau"], e["besitz"], e["hoehe"], e["boden"], SP, maenner, start, lnr_xy, mk)
    kand = []
    r = mechanik.durchbruch_schritte(*args, sperre=sperre, gefahr=gf)
    if r["weg"]:
        kand.append(("mauer", None, r, None))
    for nr, g_ in G.items():
        if g_["besitzer"] == FEIND and g_["typ"] == TORHAUS and g_["leben"] > 0:
            rand = ndimage.binary_dilation(e["bau"] == nr, structure=np.ones((3, 3), bool), iterations=2)
            # Einschlagen: Leben / Schaden je Treffer an Tor und Turm (Code UpdateMaceman), je Runde ein Treffer je Mann
            kosten = math.ceil(g_["leben"] / float(mk["tor_turm"]) / max(1, maenner)) * mk["takte_je_treffer"]
            rt = mechanik.durchbruch_schritte(*args, sperre=sperre & ~rand, gefahr=gf, frei=rand, frei_kosten=kosten)
            if rt["weg"] and any(rand[q] for q in rt["weg"]):
                kand.append(("tor", nr, rt, rand))
    if not kand:
        return None
    # Daniels Regel "maximale Sicherheit, dann minimaler Widerstand" auch ZWISCHEN den Kandidaten: Beschuss-Last, dann Zeit
    art, nr, r, rand = min(kand, key=lambda k: (k[2]["belastung"] or 0.0, k[2]["takte"]))
    weg = r["weg"]
    # ab dem ZWEITEN Wegfeld suchen (Lauf 00:49: der Start lag selbst auf einem Mauerfeld -> Zugang = weg[-1] = der Lord)
    i_wand = next((i for i, q in enumerate(weg) if i >= 1 and q in set(map(tuple, r["mauern"]))), None)
    i_tor = next((i for i, q in enumerate(weg) if i >= 1 and rand is not None and rand[q] and not rand[weg[0]]), None)
    gemein = {"weg": weg, "takte": r["takte"], "gefahr": gf, "nah": nah, "e": e,
              "kandidaten": [(k[0], k[1], round(k[2]["belastung"] or 0), k[2]["takte"]) for k in kand]}     # EINE Stelle fuer alle Felder (Absturz 00:46: "nah" fehlte)
    if i_tor is not None and (i_wand is None or i_tor < i_wand):
        return dict(gemein, art="tor", ziel=nr, zug=weg[i_tor - 1])
    if i_wand is not None:
        return dict(gemein, art="mauer", ziel=weg[i_wand], zug=weg[i_wand - 1])
    return dict(gemein, art="lord", ziel=None, zug=None)


# Schaden je Schuetze und Takt nach Schach-Abstand, offenes Feld (Wissensregister L73, gemessen an Assassinen, ~6.900 Runden):
# <=3: 2,10 | 4-8: 1,37 | 9-15: 0,56 | ueber 15 bis zur Reichweite: 0,06
SCHADEN_BAENDER = ((3, 2.10), (8, 1.37), (15, 0.56))
SCHADEN_WEIT = 0.06
NAH = 15                                              # ab hier faellt der Schaden auf ein Zehntel (L73) - Sammeln erlaubt


def schaden_feld(n):
    """(Schaden je Takt je Feld, Schuetzen naeher als NAH je Feld) aus dem letzten Lagebild - nur feindliche Fernkaempfer.
    (22.10. 00:42, Daniel: "er sucht das kleine Tuermchen aus und nicht die Luecke mit 1 Mauer" - mit 44 Feldern Reichweite zaehlte
    jeder Schuetze ueberall gleich, die ganze Burg war gleich gefaehrlich)"""
    L = lies_lagebild(neu_holen=False)
    d_s = np.zeros((n + 1, n + 1))
    d_n = np.zeros((n + 1, n + 1))

    def quadrat(d, x, y, r, w):
        x0, x1, y0, y1 = max(0, x - r), min(n - 1, x + r), max(0, y - r), min(n - 1, y + r)
        d[x0, y0] += w
        d[x1 + 1, y0] -= w
        d[x0, y1 + 1] -= w
        d[x1 + 1, y1 + 1] += w
    for e in L.values():
        if e.get("besitzer") == FEIND and e.get("typ") in FERN and e.get("leben", 1) > 0:
            x, y = e["x"], e["y"]
            quadrat(d_s, x, y, gefecht.FERN_REICH[e["typ"]], SCHADEN_WEIT)
            vorher = SCHADEN_WEIT
            for r, w in reversed(SCHADEN_BAENDER):
                quadrat(d_s, x, y, r, w - vorher)
                vorher = w
            quadrat(d_n, x, y, NAH, 1.0)
    return d_s.cumsum(0).cumsum(1)[:n, :n], d_n.cumsum(0).cumsum(1)[:n, :n]


def sammelfeld(weg, zug, nah):
    """Das letzte Feld auf dem geplanten Weg vor dem Zugang, an das kein Schuetze naeher als NAH Felder herankommt - dort beginnt
    das Vorpreschen (L73: dahinter ein Zehntel des Schadens; Lauf 00:42: "beschussfrei" = ausser 44 Feldern lag viel zu weit weg).
    Ist der ganze Weg naeher: der Startpunkt."""
    ende = weg.index(tuple(zug)) if zug is not None and tuple(zug) in weg else len(weg) - 1
    sicher = [i for i, q in enumerate(weg[:ende + 1]) if nah[q] == 0]
    return tuple(weg[max(sicher)]) if sicher else tuple(weg[0])


def main(wahl=None):
    """Ein Sturm mit der Wahl der Stellschrauben (fehlende Schrauben: STANDARD). Rueckgabe: Ergebnis fuer sturm_lernen.py."""
    wahl = dict(STANDARD, **(wahl or {}))
    t_start = time.time()
    print("OK:", shc.laden(shc.STANDARD_STAND), flush=True)
    befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
    L = lies_lagebild(neu_holen=False)
    lnr = next(k for k, e in L.items() if e["typ"] == 55 and e["besitzer"] == FEIND and e["leben"] > 0)
    lord_xy = (L[lnr]["x"], L[lnr]["y"])
    mk = mechanik.streitkolben()
    G = lies_gebaeude()
    kaserne = min([nr for nr, g_ in G.items() if g_["besitzer"] == SP and g_["typ"] == KASERNE] or [None])
    kaserne_xy = (G[kaserne]["x"], G[kaserne]["y"]) if kaserne is not None else None
    roh = speicher.lies(E0, 3000 * ES)
    alle = eigene_soldaten(roh)
    uid_von = {n: kennung(roh, n) for n in alle}
    mauer = {n for n, e in alle.items() if e["typ"] == STREITKOLBEN}
    fern = {n for n, e in alle.items() if e["typ"] in FERN}
    nah = set(alle) - mauer - fern
    print("WAHL:", wahl, flush=True)
    print("ARMEE: %d Streitkolben, %d Nahkaempfer, %d Fernkaempfer | Lord %d bei %s | Kaserne %s" % (
        len(mauer), len(nah), len(fern), lnr, lord_xy, kaserne_xy), flush=True)
    kxy = {int(k): (int(x), int(y)) for x, y, k in zip(*speicher.felder())}
    kvon = {v: k for k, v in kxy.items()}

    ereignisse, spur = [], []

    def melde(e_):
        """Ereignis festhalten UND sofort ausgeben (der Lauf ist so von aussen live zu verfolgen)."""
        ereignisse.append(e_)
        print("  Takt %6d  %s" % e_, flush=True)
    phase, plan, sammel, welle = "planen", None, None, set()
    # (Daniel 00:42 "die Streitkolben gehen und kommen dann wieder, dann kommen Wellen - sie sollen doch alle auf einmal"):
    # gesammelt wird EINMAL (und erst wieder, wenn die ganze Truppe gefallen ist); danach geht die Truppe von Ziel zu Ziel weiter
    gesammelt = False
    sturm_grund = None
    # Staerke-Regel (Daniel 00:46 "ja so eine Staerke-Regel"): im Sturm wird die Verlustrate gemessen (Tote der Truppe je Takt);
    # reicht die Truppe bei dieser Rate nicht bis zum Bruch des Ziels (Restarbeit aus Hoehe/Leben, Schaden je Treffer aus dem Code,
    # 96 Takte je Runde), Rueckzug zum Sammelfeld - erneut gestuermt wird erst mit noetig Mann (kleinste Zahl, die bei dieser Rate
    # das Ziel noch bricht); der Nachschub fuellt auf
    sturm_t, tote_sturm, noetig, tor_leben, tor_pruef = None, 0, None, None, None
    geschickt, angesetzt, jaeger = set(), set(), {}
    ballisten_pruefen = True                             # nur bei Anlass suchen: Anfang, Jaeger frei, neues Ziel
    steht = {}                                           # Nummer -> (Feld, seit Takt) - fuer die Nachzuegler-Regel
    wartepunkt = {}                                      # Nummer -> Feld, an dem er vor dem Sturm wartet (ohne Beschuss)
    abst_alt = {}                                        # Nummer -> Abstand zum Zugang bei der letzten Messung
    lord_an = set()                                      # Lord-Phase: wer schon den Angriff auf den Lord bekommen hat
    angestossen = {}                                     # Nummer -> wie oft ohne Bewegung neu geschickt
    versuche_ballista = {}                               # Ballista -> geschickte Jaeger (hoechstens 4 je Ballista)
    jaeger_frei = []                                     # Jaeger, deren Ziel gerade erledigt ist
    offen, erwartet, kauf_aus = None, 0, False
    haus_stellen = [(kaserne_xy[0] + dx, kaserne_xy[1] + dy) for r_ in (6, 9, 12) for dx, dy in
                    ((-r_, 0), (r_, 0), (0, -r_), (0, r_), (-r_, -r_), (r_, r_), (-r_, r_), (r_, -r_))] if kaserne_xy else []
    frist, wirk_alt, sammel_frist, t_107 = None, None, None, None
    raten = raten_laden()
    letzter_befehl = {}                                  # Nummer -> (Takt, Befehl) - fuer den Rueckwaerts-Melder

    def merke(wer, text):
        for w in wer:
            letzter_befehl[w] = (t_, text)

    def rest_treffer():
        """Treffer, die das Ziel noch braucht (Mauer: Hoehe ueber Boden / Schaden je Treffer nach Nachbarn; Torhaus: Leben / 15)."""
        if plan["art"] == "mauer":
            k_ = kvon[plan["ziel"]]
            nb = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                     if s32(speicher.LOGIK + 4 * kvon.get((plan["ziel"][0] + dx, plan["ziel"][1] + dy), k_)) & 0x10000100)
            punkte = int(speicher.lies(speicher.HOEHE + k_, 1)[0]) - int(plan["e"]["boden"][plan["ziel"]]) + 1
            return math.ceil(max(punkte, 1) / float(max(mechanik.kachel_schaden(mk["mauer"], nb), 1)))
        if plan["art"] == "tor":
            return math.ceil(max(tor_leben or 0, 1) / float(mk["tor_turm"]))
        return None

    def bedarf(rate, weg_takte):
        """Kleinste Mannzahl, die das Ziel bei dieser Verlustrate bricht (Weg zum Zugang + Hacken, ein Treffer je Mann und Runde)."""
        tr = rest_treffer()
        if tr is None or rate is None:
            return None
        dauer = lambda m_: weg_takte + math.ceil(tr / float(max(1, m_))) * mk["takte_je_treffer"]
        return next((m_ for m_ in range(1, 1000) if m_ - rate * dauer(m_) >= 1), None)

    def rate_speichern():
        """Tote und Takte dieses Sturms je Ziel nachtragen (die naechste Planung rechnet damit)."""
        if plan is None or sturm_t is None or t_ <= sturm_t:
            return
        key = "%s:%s" % (plan["art"], plan["ziel"])
        r_ = raten.setdefault(key, {"tote": 0, "takte": 0})
        r_["tote"] += tote_sturm
        r_["takte"] += t_ - sturm_t
        raten_schreiben(raten, "sturm.py, je Sturm nachgetragen (zuletzt %s)" % time.strftime("%Y-%m-%d %H:%M"))
        melde((t_, "RATE %s: %d Tote in %d Takten (gesamt %d / %d)" % (key, tote_sturm, t_ - sturm_t, r_["tote"], r_["takte"])))

    def wegpunkte(von, bis_i):
        """Wegpunkte entlang des geplanten (sicheren) Wegs ab dem Wegfeld, das von am naechsten liegt, bis Index bis_i - alle NAH
        Felder einer (Daniel 01:19 "teilweise laufen die Streitis vorne rum und werden unnoetig abgeschossen": nur mit dem Endpunkt
        nahm der Pfadsucher des Spiels den kuerzesten Weg an den Schuetzen vorbei)."""
        w_ = plan["weg"][:bis_i + 1]
        i0 = min(range(len(w_)), key=lambda i: abstand(w_[i], von))
        pkt = [tuple(q) for q in w_[i0::NAH]]
        if not pkt or pkt[-1] != tuple(w_[-1]):
            pkt.append(tuple(w_[-1]))
        return pkt

    def kette(wer, bis_i, text):
        """Jeder in wer laeuft die Wegkette bis Wegfeld bis_i; Maenner mit gleichem Einstieg als eine Kette (logik.lua wegkette:
        naechster Punkt, sobald die Mehrheit am aktuellen ist - die Gruppe bleibt gebuendelt)."""
        gruppen = {}
        for w in wer:
            if w in jetzt:
                pk = tuple(wegpunkte((jetzt[w]["x"], jetzt[w]["y"]), bis_i))
                gruppen.setdefault(pk, []).append(w)
        for pk, ws in gruppen.items():
            a_ = {"einheiten": sorted(ws), "lauf": [pk[0][0], pk[0][1]], "trupp": 1}
            if len(pk) > 1:
                a_["danach"] = [[q[0], q[1]] for q in pk[1:]]
            befehl({"angriff": a_}, 0.3)
            merke(ws, "%s ueber %d Wegpunkte" % (text, len(pk)))

    def sturm_befehl(wer):
        """Alle in wer gleichzeitig auf das Ziel des Plans; Frist = Wegfelder bis zum Zugang x 12 Takte + 2 Trefferrunden."""
        nonlocal frist, wirk_alt, t_107, phase
        # Laufen an die Mauer einzeln (trupp 1 - sonst Formation, Lauf 23:27); Torhaus und Lord als EIN Gruppenbefehl (Daniel 00:52
        # "die Streitkolben laufen zurueck": die Lua-Schlange arbeitet Einzelbefehle nacheinander ab, bis der letzte von 70 seinen
        # Befehl hat, vergehen viele Takte - wessen Ziel gerade gefallen war, lief so lange ins Lager zurueck)
        merke(wer, "Sturm %s %s" % (plan["art"], plan["ziel"]))
        if plan["art"] == "mauer" and wahl["wegweiser"] == "an" and tuple(plan["zug"]) in plan["weg"]:
            kette(wer, plan["weg"].index(tuple(plan["zug"])), "Sturm Mauer")
        elif plan["art"] == "mauer":
            befehl({"angriff": {"einheiten": sorted(wer), "lauf": [plan["zug"][0], plan["zug"][1]], "trupp": 1}}, 0.5)
        elif plan["art"] == "tor":
            # Torhaus EINZELN (Lauf 01:00: als Gruppenbefehl verteilte das Spiel sie in Formation, nach 529 Takten standen 50 von 72
            # noch in 101; im Siegerlauf 00:54 einzeln: Torhaus nach 589 Takten gefallen)
            befehl({"angriff": dict({"einheiten": sorted(wer), "gebaeude": plan["ziel"]},
                                    **({"trupp": 1} if wahl["tor"] == "einzeln" else {}))}, 0.5)
        else:
            # Lord EINZELN, die Vordersten zuerst (Lauf 01:16: als Gruppenbefehl liefen die Maenner in Formation am Lord vorbei -
            # Rueckwaerts-Melder: 22 -> 42 Felder; im ersten Sieg mit Einzelbefehlen fiel der Lord am schnellsten, 1.192 Takte)
            # (Lauf 01:19: auch einzeln liefen sie aussen herum - Rueckwaerts-Melder 66x bis 45 Felder): Wegkette entlang des Plans bis
            # vor den Lord; wer dort ankommt (<= 4 Felder, wie logik.lua wegkette), greift sofort einzeln an
            # (Lauf 01:22: die Wegkette bis vor den Lord war langsamer - Lord tot 6.980 statt 5.967, 137 Rueckwaerts-Meldungen auf der
            # Kette, 10 Mann blieben an einem Wegpunkt haengen): zurueck zum schnellsten gemessenen Weg - Einzelangriff, Vorderste zuerst
            if wahl["lord"] == "kette":
                kette(wer, len(plan["weg"]) - 2, "Weg zum Lord")
                lord_an.clear()
            elif wahl["lord"] == "gruppe":
                befehl({"angriff": {"einheiten": sorted(wer), "ziel": lnr}}, 0.5)
                lord_an.update(wer)
            else:
                reihe = sorted(wer, key=lambda n_: abstand((jetzt[n_]["x"], jetzt[n_]["y"]), lord_xy) if n_ in jetzt else 999)
                befehl({"angriff": {"einheiten": reihe, "ziel": lnr, "trupp": 1}}, 0.5)
                lord_an.update(wer)
        w_ = plan["weg"]
        zug_ = tuple(plan["zug"]) if plan["zug"] else tuple(w_[-1])
        frist = t_ + max(0, w_.index(zug_) if zug_ in w_ else len(w_)) * mechanik.TAKTE_JE_FELD + 2 * mk["takte_je_treffer"]
        wirk_alt, t_107 = None, None
        nonlocal sturm_t, tote_sturm, tor_pruef
        tor_pruef = None
        sturm_t, tote_sturm = t_, 0
        melde((t_, "STURM %d Mann auf %s %s" % (len(wer), plan["art"], plan["ziel"])))
        phase = "sturm"

    tick0 = s32(shc.TICK)
    letzt = None
    t_ = 0
    befehl({"pause": False, "tempo": 40}, 0.2)
    while True:
        tk = s32(shc.TICK)
        if tk == letzt:
            continue
        letzt = tk
        t_ = tk - tick0
        roh = speicher.lies(E0, 3000 * ES)
        lord = AD.einheit(roh, lnr)
        if lord["leben"] <= 0 or lord["typ"] != 55:
            melde((t_, "LORD TOT"))
            if phase == "sturm":
                rate_speichern()
            break
        jetzt = eigene_soldaten(roh)
        if wahl["jaeger"] == "wirkung" and t_ % mk["takte_je_treffer"] == 0:
            ballisten_pruefen = True                      # wer uns angreift, kann sich jederzeit aendern
        # gleiche Nummer, andere Kennung = neuer Mann auf dem Platz eines Gefallenen
        lebend = {n for n in jetzt if uid_von.get(n) == kennung(roh, n)}
        if phase == "sturm":
            tote_sturm += len(welle - lebend)
        for grp in (mauer, nah, fern, welle, angesetzt, geschickt):
            grp &= lebend
        def ziel_lebt(z_):
            if z_[0] == "einheit":
                return AD.einheit(roh, z_[1])["leben"] > 0 and AD.einheit(roh, z_[1])["zustand"] != 0
            g_ = G.get(z_[1])
            return g_ is not None and speicher.wegkarte()["gebaeude"][g_["x"], g_["y"]] == z_[1]
        for j in [j for j, b in jaeger.items() if j not in lebend or not ziel_lebt(b)]:
            jaeger.pop(j)
            ballisten_pruefen = True
            if j in lebend:
                jaeger_frei.append(j)                     # Ziel erledigt: naechstes Ziel aus der Liste (oder zur Truppe)
        if s32(GOLD2) > 0:                                # Daniel 21.10. 23:20: Franz wirbt sonst nach
            befehl({"player": FEIND, "gold": 0}, 0.3)

        # --- Nachschub ---
        if kaserne is not None:
            gold1, keule1, leder1, holz1, feuer1 = s32(GOLD1), s32(KEULE1), s32(LEDER1), s32(HOLZ1), s32(FEUER1)
            if offen is not None:
                art_, t_off, vorher_ = offen
                if art_ == "werbe" and gold1 < vorher_:
                    erwartet += (vorher_ - gold1) // 20     # 20 Gold je Streitkolben (Einzeltest 00:20)
                    offen = None
                elif (art_ == "kauf" and keule1 + leder1 > vorher_) or (art_ == "haus" and holz1 < vorher_):
                    offen = None
                elif t_ - t_off >= 2:                     # Befehle wirken im naechsten Takt (logik.lua befehlAbsetzen)
                    if art_ == "kauf":
                        kauf_aus = True
                        melde((t_, "KAUF GESCHEITERT - kein weiterer Kauf"))
                    offen = None
            if offen is None:
                if keule1 > 0 and leder1 > 0 and feuer1 > 0 and gold1 >= 20:
                    befehl({"werbe": {"typ": STREITKOLBEN, "gebaeude": kaserne}}, 0.3)
                    offen = ("werbe", t_, gold1)
                elif (keule1 <= 0 or leder1 <= 0) and gold1 > 0 and not kauf_aus:
                    befehl({"spielbefehl": {"nr": 38, "werte": [0, 21 if keule1 <= 0 else 23]}}, 0.3)
                    offen = ("kauf", t_, keule1 + leder1)
                elif feuer1 <= 0 and haus_stellen:
                    hx, hy = haus_stellen.pop(0)
                    befehl({"baue": {"mapper": NACH_TYP[HUETTE]["mapper"], "x": hx, "y": hy, "groesse": NACH_TYP[HUETTE]["b"],
                                     "richtung": 0}}, 0.3)
                    offen = ("haus", t_, holz1)
            if erwartet > 0:
                neu = [n for n in jetzt if uid_von.get(n) != kennung(roh, n)]
                for n in neu:
                    uid_von[n] = kennung(roh, n)
                    (mauer if jetzt[n]["typ"] == STREITKOLBEN else fern if jetzt[n]["typ"] in FERN else nah).add(n)
                    if phase == "sturm" and plan["art"] in ("mauer", "lord") and wahl["wegweiser"] == "an":
                        welle.add(n)
                        bis_ = plan["weg"].index(tuple(plan["zug"])) if plan["zug"] and tuple(plan["zug"]) in plan["weg"] else len(plan["weg"]) - 2
                        kette([n], bis_, "Nachschub")
                    elif phase == "sturm":
                        welle.add(n)
                        if plan["art"] == "mauer":
                            befehl({"angriff": {"einheiten": [n], "lauf": [plan["zug"][0], plan["zug"][1]], "trupp": 1}}, 0.3)
                        elif plan["art"] == "tor":
                            befehl({"angriff": {"einheiten": [n], "gebaeude": plan["ziel"], "trupp": 1}}, 0.3)
                        else:
                            befehl({"angriff": {"einheiten": [n], "ziel": lnr, "trupp": 1}}, 0.3)
                    elif sammel is not None and plan is not None and sammel in plan["weg"] and wahl["wegweiser"] == "an":
                        kette([n], plan["weg"].index(sammel), "Nachschub zum Sammeln")
                    elif sammel is not None:
                        befehl({"angriff": {"einheiten": [n], "lauf": [sammel[0], sammel[1]], "trupp": 1}}, 0.3)
                        geschickt.add(n)
                erwartet = max(0, erwartet - len(neu))
                if neu:
                    melde((t_, "ANGEWORBEN %s" % neu))

        # --- Jaeger auf Feuerballisten ---
        # Jaeger (Daniel 00:42 "mindestens 2 je Feuerballiste", 00:55 "die auf die Feuerballisten gehen, koennten auf dem Boden
        # stehende Fernkaempfer oder Ausbildungsgebaeude angreifen"): Zielliste nach Vorrang - 1. Feuerballisten (2 je Ballista,
        # hoechstens 4 Versuche je Ballista), 2. Fernkaempfer auf dem Boden (Feldhoehe = Bodenhoehe, also nicht auf Mauer/Turm),
        # 3. Ausbildungsgebaeude. Wird ein Ziel erledigt, nimmt der Jaeger das naechste; gibt es keins mehr, geht er zur Truppe
        if ballisten_pruefen and wahl["jaeger"] == "aus":
            ballisten_pruefen = False
        if ballisten_pruefen:
            ballisten_pruefen = False
            ziele = []
            hoehe_, boden_ = speicher.ebene(speicher.HOEHE), speicher.ebene(speicher.BODEN)
            # (Daniel 01:11 "die Jaeger gingen auf Fernkaempfer auf Mauern/Tuermen - fruchtlos"): Boden = keine Mauer, kein Gebaeude
            logik_, bau_ = speicher.ebene(speicher.LOGIK, 4), speicher.wegkarte()["gebaeude"]
            for b_n in range(1, 3000):
                e_b = AD.einheit(roh, b_n)
                if e_b["besitzer"] != FEIND or e_b["leben"] <= 0 or e_b["zustand"] == 0:
                    continue
                # nach Wirkung: nur wer gerade einen von uns angreift (Daniel 01:23 "keinen Sinn, auf eine Ballista zu gehen, die
                # literally nicht angreift")
                ziel_e = int.from_bytes(roh[b_n * ES + ZIELEINHEIT:b_n * ES + ZIELEINHEIT + 2], "little", signed=True)
                if ziel_e not in jetzt:
                    continue
                aktiv = sum(1 for z_ in jaeger.values() if z_ == ("einheit", b_n))
                if e_b["typ"] == BALLISTE:
                    ziele += [(0, ("einheit", b_n), (e_b["x"], e_b["y"]))] * max(0, min(2 - aktiv, 4 - versuche_ballista.get(b_n, 0)))
                elif e_b["typ"] in FERN and int(hoehe_[e_b["x"], e_b["y"]]) <= int(boden_[e_b["x"], e_b["y"]]) and aktiv == 0 \
                        and not (int(logik_[e_b["x"], e_b["y"]]) & 0x100) and bau_[e_b["x"], e_b["y"]] == 0:
                    ziele.append((1, ("einheit", b_n), (e_b["x"], e_b["y"])))
            # (Ausbildungsgebaeude greifen niemanden an - nach Wirkung keine Jaeger-Ziele mehr)
            ziele.sort(key=lambda z_: z_[0])
            # wer schon jagt und kein Ziel hat (frisch erledigt), bekommt zuerst eins; dann neue Jaeger bis 2 je Ballista
            ohne_ziel = [j for j in jaeger_frei if j in lebend]
            jaeger_frei = []
            frei_ = ohne_ziel + [n for n in mauer - welle if n not in jaeger and n not in ohne_ziel]
            n_jaeger_ziel = max(2, len(jaeger) + sum(1 for z_ in ziele if z_[0] == 0))   # 2 je Ballista, sonst 2
            while ziele and frei_ and (len(jaeger) < n_jaeger_ziel or ohne_ziel):
                _, z_, zxy = ziele.pop(0)
                f = min(frei_, key=lambda m_: abstand((jetzt[m_]["x"], jetzt[m_]["y"]), zxy))
                frei_.remove(f)
                if f in ohne_ziel:
                    ohne_ziel.remove(f)
                mauer.discard(f)
                welle.discard(f)
                jaeger[f] = z_
                if z_[0] == "einheit":
                    versuche_ballista[z_[1]] = versuche_ballista.get(z_[1], 0) + 1
                    befehl({"angriff": {"einheiten": [f], "ziel": z_[1], "trupp": 1}}, 0.3)
                else:
                    befehl({"angriff": {"einheiten": [f], "gebaeude": z_[1], "trupp": 1}}, 0.3)
                melde((t_, "JAEGER %d auf %s %d" % (f, "Einheit" if z_[0] == "einheit" else "Gebaeude", z_[1])))
            for j in ohne_ziel:                         # nichts mehr zu jagen: zur Truppe
                mauer.add(j)
                if phase == "sturm" and plan is not None:
                    welle.add(j)
                    if plan["art"] == "mauer":
                        befehl({"angriff": {"einheiten": [j], "lauf": [plan["zug"][0], plan["zug"][1]], "trupp": 1}}, 0.3)
                    elif plan["art"] == "tor":
                        befehl({"angriff": {"einheiten": [j], "gebaeude": plan["ziel"]}}, 0.3)
                    else:
                        befehl({"angriff": {"einheiten": [j], "ziel": lnr}}, 0.3)

        # --- Jede Einheit mit (Daniel 00:57 "wirklich jede Einheit soll mit rein, nicht nur ein paar"; Siegerlauf 00:54: 12
        # Fernkaempfer standen untaetig weit weg - der Angriff auf einen Soldaten am Lord setzte sie aus der Ferne nicht in Gang).
        # Fernkaempfer ziehen mit: beim Sammeln und im Mauer-/Torhaus-Sturm aufs Sammelfeld (von dort reichen sie gut 40 Felder,
        # L82/L91, und stehen selbst ausserhalb des Nahbereichs der Verteidiger), in der Lord-Phase zum Lord. Fuer ALLE gilt:
        # wer weiter als NAH (15) Felder vom eigenen Ziel steht und sich eine Trefferrunde (96 Takte) nicht bewegt hat, bekommt
        # den Laufbefehl neu.
        if plan is not None and sammel is not None:
            vorn_nah = sammel if phase == "sammeln" else (tuple(plan["zug"]) if plan["zug"] else lord_xy)
            vorn_fern = vorn_nah
            nachzuegler = {}
            for n in (mauer | nah | fern) - set(jaeger):
                if n not in jetzt:
                    continue
                pos = (jetzt[n]["x"], jetzt[n]["y"])
                alt_ = steht.get(n)
                if alt_ is None or alt_[0] != pos:
                    steht[n] = (pos, t_)
                    continue
                ziel_n = wartepunkt.get(n, sammel) if phase == "sammeln" else (vorn_fern if n in fern else vorn_nah)
                if t_ - alt_[1] >= mk["takte_je_treffer"] and abstand(pos, ziel_n) > NAH:
                    angestossen[n] = angestossen.get(n, 0) + 1
                    steht[n] = (pos, t_)
                    if angestossen[n] <= 2:
                        nachzuegler.setdefault(ziel_n, []).append(n)
                    elif angestossen[n] == 3:            # 2 neue Befehle ohne Bewegung: nicht weiter anstossen (Lauf 01:00: zwei Bogen
                        # bekamen 25 Befehle und standen trotzdem)
                        melde((t_, "KOMMT NICHT AN: %d (Typ %d) bei %s -> %s" % (n, jetzt[n]["typ"], pos, ziel_n)))
            for ziel_n, wer in nachzuegler.items():
                befehl({"angriff": {"einheiten": sorted(wer), "lauf": [ziel_n[0], ziel_n[1]]}}, 0.3)
                merke(wer, "Nachzuegler nach %s" % (ziel_n,))
                melde((t_, "NACHZUEGLER %d Mann (%s) -> %s" % (len(wer), sorted({jetzt[w]["typ"] for w in wer}), ziel_n)))

        # (Daniel 01:06 "es braucht alle Einheiten beim Stacken schon fuer das Zerstoeren", 01:07 "jede Einheit kann Nahkampf"):
        # die Sturm-Truppe ist jede eigene Einheit ausser den Jaegern - auch die Fernkaempfer stacken mit
        stuermer = (mauer | nah | fern) - set(jaeger)
        if not stuermer and erwartet == 0 and (kaserne is None or s32(FEUER1) <= 0):
            melde((t_, "ALLE TOT - keiner mehr anwerbbar"))
            break

        # --- Phasen ---
        if phase == "planen":
            if not stuermer:
                continue
            if gesammelt and welle:                       # weiter ab der Spitze der Truppe
                bezug = tuple(plan["zug"]) if plan and plan["zug"] else lord_xy
                start = min(((jetzt[n]["x"], jetzt[n]["y"]) for n in welle), key=lambda q: abstand(q, bezug))
            else:
                start = min(((jetzt[n]["x"], jetzt[n]["y"]) for n in stuermer),
                            key=lambda q: abstand(q, kaserne_xy) if kaserne_xy else 0)   # Neue kommen aus der Kaserne
            # (Lauf 00:49: waehrend der 1-3 s Planung lief das Spiel weiter, die Maenner ohne Befehl liefen zurueck): Spiel anhalten
            befehl({"pause": True}, 0.3)
            plan = plane_ziel(start, len(stuermer), mk, lord_xy)
            befehl({"pause": False}, 0.3)
            ballisten_pruefen = True
            if plan is None:
                melde((t_, "KEIN WEG zum Lord von %s" % (start,)))
                break
            sammel = sammelfeld(plan["weg"], plan["zug"] if plan["zug"] else plan["weg"][-2], plan["nah"])
            tor_leben = lies_gebaeude().get(plan["ziel"], {}).get("leben") if plan["art"] == "tor" else None
            melde((t_, "ZIEL %s %s ueber Zugang %s, Sammelfeld %s, Weg %.0f Takte | Kandidaten %s" % (
                plan["art"], plan["ziel"], plan["zug"], sammel, plan["takte"], plan["kandidaten"])))
            angesetzt = set()
            if gesammelt and welle:
                welle = set(stuermer)                     # alle zusammen sofort aufs naechste Ziel - kein Rueckweg
                sturm_befehl(welle)
                continue
            geschickt, welle = set(), set()
            # Schlau warten (Daniel 01:04 "die Streitkolben nicht zuruecklaufen", "es macht keinen Sinn, im Beschuss zu warten"):
            # wer hinter dem Sammelfeld steht, laeuft vor zum Sammelfeld; wer schon weiter vorn steht, laeuft NICHT zurueck - er
            # bleibt stehen, wenn ihn dort kein Schuetze naeher als NAH trifft, sonst geht er zum naechsten Feld ohne solchen Beschuss
            zum_zug = mechanik.lauf_takte_zu(plan["e"]["link"], tuple(plan["zug"]) if plan["zug"] else tuple(plan["weg"][-1]),
                                             AD.sperre_feindbau(plan["e"]["bau"]))
            sxs, sys_ = np.nonzero((plan["nah"] == 0) & np.isfinite(zum_zug))
            wartepunkt = {}
            for n in stuermer:
                pos = (jetzt[n]["x"], jetzt[n]["y"])
                if not np.isfinite(zum_zug[pos]) or zum_zug[pos] > zum_zug[sammel]:
                    wartepunkt[n] = sammel
                elif plan["nah"][pos] == 0:
                    wartepunkt[n] = pos                   # schon vorn und ohne Beschuss: stehen bleiben
                elif len(sxs):
                    i_ = int(np.argmin(np.maximum(np.abs(sxs - pos[0]), np.abs(sys_ - pos[1]))))
                    wartepunkt[n] = (int(sxs[i_]), int(sys_[i_]))
                else:
                    wartepunkt[n] = sammel
            nach_punkt = {}
            for n, wp in wartepunkt.items():
                if wp != (jetzt[n]["x"], jetzt[n]["y"]):
                    nach_punkt.setdefault(wp, []).append(n)
            for wp, wer in nach_punkt.items():
                if wp == sammel and sammel in plan["weg"] and wahl["wegweiser"] == "an":
                    kette(wer, plan["weg"].index(sammel), "Sammeln")
                else:
                    befehl({"angriff": {"einheiten": sorted(wer), "lauf": [wp[0], wp[1]], "trupp": 1}}, 0.3)
                    merke(wer, "Warten bei %s" % (wp,))
            melde((t_, "WARTEN: %d zum Sammelfeld, %d bleiben vorn stehen, %d zum naechsten Feld ohne Beschuss" % (
                sum(1 for wp in wartepunkt.values() if wp == sammel),
                sum(1 for n, wp in wartepunkt.items() if wp == (jetzt[n]["x"], jetzt[n]["y"])),
                sum(1 for n, wp in wartepunkt.items() if wp != sammel and wp != (jetzt[n]["x"], jetzt[n]["y"])))))
            geschickt = set(stuermer)
            # echte Laufzeit je Mann zum Sammelfeld (Schrittbits) - die Luftlinie unterschaetzte (Lauf 00:39: 11 von 51 da)
            zum_sammel = mechanik.lauf_takte_zu(plan["e"]["link"], sammel, AD.sperre_feindbau(plan["e"]["bau"]))
            # Felder x Takte je Feld des Typs: Streitkolben 12 (gemessen, augen_laufen), sonst 16 - UNGEMESSEN fuer Soldaten, geliehen
            # von den Arbeitern (Wissensregister L68). Lauf 00:40: mit 12 fuer alle waren beim Sturm erst 11 von 53 da
            wege_ = [(zum_sammel[jetzt[n]["x"], jetzt[n]["y"]] if wartepunkt[n] == sammel else
                      abstand((jetzt[n]["x"], jetzt[n]["y"]), wartepunkt[n]) * mechanik.TAKTE_JE_FELD) / mechanik.TAKTE_JE_FELD *
                     (mechanik.TAKTE_JE_FELD if jetzt[n]["typ"] == STREITKOLBEN else 16) for n in stuermer]
            erreichbar = [w for w in wege_ if np.isfinite(w)]
            sammel_frist = t_ + (max(erreichbar) if erreichbar else 0)
            if len(erreichbar) < len(wege_):
                melde((t_, "SAMMELN: %d von %d erreichen das Sammelfeld nicht" % (len(wege_) - len(erreichbar), len(wege_))))
            phase = "sammeln"
            continue

        if phase == "sammeln":
            da = {n for n in stuermer if abstand((jetzt[n]["x"], jetzt[n]["y"]), wartepunkt.get(n, sammel)) <= 1}
            if noetig is not None:
                # nach einem Rueckzug: erst mit noetig Mann; sind alle da und kommt kein Nachschub mehr (kein Gold fuer einen Mann,
                # keine Bauern), mit allen, die es gibt
                kein_nachschub = s32(GOLD1) < 20 or s32(FEUER1) <= 0 and not haus_stellen
                bereit = len(da) >= noetig or (da == stuermer and kein_nachschub)
            else:
                key = "%s:%s" % (plan["art"], plan["ziel"])
                r_ = raten.get(key)
                w_ = plan["weg"]
                zug_ = tuple(plan["zug"]) if plan["zug"] else tuple(w_[-1])
                weg_takte = max(0, w_.index(zug_) - w_.index(sammel)) * mechanik.TAKTE_JE_FELD if zug_ in w_ and sammel in w_ else 0
                m_noetig = bedarf(r_["tote"] / float(r_["takte"]), weg_takte) if r_ and r_["takte"] > 0 else None
                if m_noetig is not None:
                    # (Daniel 01:16 "ohne das Buendeln und Warten auf den Rest ist nicht genug Kraft dabei - das ist falsch"; Lauf 01:16:
                    # frueher Start mit 62 -> Torhaus 12 Tote in 982 Takten, gebuendelt vorher 0-2 Tote in ~580): gewartet wird auf ALLE
                    # (oder die Frist des Langsamsten); der Bedarf aus der gemessenen Rate steht nur noch in der Meldung
                    bereit = da == stuermer or t_ >= sammel_frist or (wahl["losgehen"] == "bedarf" and len(da) >= m_noetig)
                    if bereit and not sturm_grund:
                        sturm_grund = "Bedarf %d Mann (Rate %.4f Tote/Takt gemessen), %d am Wartepunkt" % (m_noetig, r_["tote"] / float(r_["takte"]), len(da))
                else:
                    bereit = bool(da) and (da == stuermer or t_ >= sammel_frist)
            if bereit:
                gesammelt, noetig = True, None
                welle = set(stuermer)                     # alle auf einmal - wer noch unterwegs ist, geht direkt mit
                sturm_befehl(welle)
                ereignisse[-1] = (t_, ereignisse[-1][1] + " (%d am Wartepunkt%s)" % (len(da), ", " + sturm_grund if sturm_grund else ""))
                sturm_grund = None
            continue

        # phase == "sturm"
        # Rueckwaerts-Melder (Daniel 01:11 "teilweise sind sie wieder zurueckgegangen" - belegen statt raten): alle 96 Takte der
        # Schach-Abstand jedes Sturm-Manns zum Zugang; ist er um 3 Felder oder mehr gewachsen, Meldung mit letztem Befehl
        if t_ % mk["takte_je_treffer"] == 0:
            zug_m = tuple(plan["zug"]) if plan["zug"] else lord_xy
            for n in welle:
                d_ = abstand((jetzt[n]["x"], jetzt[n]["y"]), zug_m)
                alt_d = abst_alt.get(n)
                if alt_d is not None and d_ >= alt_d + 3:
                    melde((t_, "RUECKWAERTS %d (Typ %d) %d -> %d Felder vom Zugang, Zustand %d, letzter Befehl %s" % (
                        n, jetzt[n]["typ"], alt_d, d_, jetzt[n]["lage"], letzter_befehl.get(n))))
                abst_alt[n] = d_
        if plan["art"] == "mauer":
            k = kvon[plan["ziel"]]
            if not s32(speicher.LOGIK + 4 * k) & 0x100:
                melde((t_, "MAUER %s GEFALLEN" % (plan["ziel"],)))
                rate_speichern()
                phase = "planen"
                continue
            wirkung = speicher.lies(speicher.HOEHE + k, 1)[0]
            ankunft = [n for n in welle if (jetzt[n]["x"], jetzt[n]["y"]) == tuple(plan["zug"]) and n not in angesetzt]
            if ankunft:
                angesetzt |= set(ankunft)
                anf_b = AD.anfrage_und_blick(plan["ziel"]) or (plan["ziel"], 0)
                befehl({"mauerziel": {"einheiten": sorted(angesetzt), "feld": k, "x": plan["ziel"][0], "y": plan["ziel"][1],
                                      "halten": True}}, 0.3)
                befehl({"angriff": {"einheiten": sorted(ankunft), "mauer": [lord_xy[0], lord_xy[1], 2, 30, anf_b[0][0], anf_b[0][1],
                                                                             anf_b[1]], "trupp": 1}}, 0.5)
        elif plan["art"] == "tor":
            fp = list(zip(*np.nonzero(plan["e"]["bau"] == plan["ziel"])))
            if not fp or speicher.wegkarte()["gebaeude"][fp[0]] != plan["ziel"]:
                melde((t_, "TORHAUS %s GEFALLEN" % plan["ziel"]))
                rate_speichern()
                phase = "planen"
                continue
            wirkung = None                                # Leben des Torhauses nur ueber das Lagebild - bei der Frist
        else:
            vor_lord = tuple(plan["weg"][-2]) if len(plan["weg"]) >= 2 else lord_xy
            ankunft_l = [n for n in welle if n not in lord_an and abstand((jetzt[n]["x"], jetzt[n]["y"]), vor_lord) <= 4]
            if ankunft_l:
                lord_an.update(ankunft_l)
                befehl({"angriff": {"einheiten": sorted(ankunft_l), "ziel": lnr, "trupp": 1}}, 0.3)
                merke(ankunft_l, "Angriff Lord")
            # Lord-Phase: Wirkung = Leben des Lords UND seiner Soldaten (Lauf 00:52: 30 Mann im Nahkampf (106) gegen die Leibwache,
            # der Lord selbst noch unberuehrt -> falscher Abbruch "keine Wirkung")
            wirkung = lord["leben"] + sum(AD.einheit(roh, m)["leben"] for m in range(1, 3000)
                                          if AD.einheit(roh, m)["besitzer"] == FEIND and AD.einheit(roh, m)["zustand"] != 0
                                          and AD.einheit(roh, m)["typ"] in shc.SOLDATEN and AD.einheit(roh, m)["leben"] > 0)
        if wirkung is not None and wirk_alt is not None and wirkung < wirk_alt:
            frist = t_ + 2 * mk["takte_je_treffer"]       # Wirkung: naechste Frist 2 Trefferrunden
            t_107 = None
        wirk_alt = wirkung if wirkung is not None else wirk_alt
        # wer im Mauerangriff steht (107, Code UpdateMaceman), arbeitet - Abbruch fruehestens 2 Trefferrunden nach Beginn
        if any(jetzt[n]["lage"] == 107 for n in welle):
            t_107 = t_ if t_107 is None else t_107
            frist = max(frist, t_107 + 2 * mk["takte_je_treffer"])
        if plan["art"] in ("mauer", "tor") and t_107 is not None and t_ - t_107 >= mk["takte_je_treffer"] and tote_sturm > 0 \
                and welle and t_ > sturm_t:
            rate = tote_sturm / float(t_ - sturm_t)                     # Tote je Takt, gemessen in diesem Sturm
            if plan["art"] == "mauer":
                k_ = kvon[plan["ziel"]]
                nb = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                         if s32(speicher.LOGIK + 4 * kvon.get((plan["ziel"][0] + dx, plan["ziel"][1] + dy), k_)) & 0x10000100)
                schaden = mechanik.kachel_schaden(mk["mauer"], nb)
                punkte = int(speicher.lies(speicher.HOEHE + k_, 1)[0]) - int(plan["e"]["boden"][plan["ziel"]]) + 1
            else:
                schaden, punkte = mk["tor_turm"], (tor_leben or 0)
            treffer = math.ceil(max(punkte, 1) / float(max(schaden, 1)))
            rest_takte = lambda m_: math.ceil(treffer / float(max(1, m_))) * mk["takte_je_treffer"]
            m = len(welle)
            if m - rate * rest_takte(m) <= 0:
                noetig = next((m_ for m_ in range(m + 1, 1000) if m_ - rate * rest_takte(m_) > 0), None)
                melde((t_, "RUECKZUG: %d Mann, %.4f Tote/Takt gemessen, Ziel braucht noch %d Treffer (%d Takte) - es braucht %s Mann" % (
                    m, rate, treffer, rest_takte(m), noetig)))
                rate_speichern()
                befehl({"angriff": {"einheiten": sorted(welle), "lauf": [sammel[0], sammel[1]], "trupp": 1}}, 0.5)
                gesammelt, welle, angesetzt = False, set(), set()
                if plan["art"] == "mauer":                # festgehaltenes Mauerziel loesen (logik.lua: ohne halten -> aus)
                    befehl({"mauerziel": {"einheiten": [], "feld": k_, "x": plan["ziel"][0], "y": plan["ziel"][1]}}, 0.3)
                phase = "sammeln"
                sammel_frist = t_
                continue
        if not welle:
            melde((t_, "TRUPPE GEFALLEN - neu sammeln"))
            gesammelt = False
            phase = "planen"
            continue
        if t_ > frist:
            if plan["art"] == "tor":
                befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
                leben = lies_gebaeude().get(plan["ziel"], {}).get("leben", 0)
                # eigener Zaehler fuer das Torhaus-Leben (Lauf 01:00: Abbruch schon an der ersten Pruefung, Ursache ungeklaert)
                if tor_pruef is None or leben < tor_pruef:
                    tor_pruef, frist, tor_leben = leben, t_ + 2 * mk["takte_je_treffer"], leben
                    continue
            lage = {}
            for n in welle:
                lage[jetzt[n]["lage"]] = lage.get(jetzt[n]["lage"], 0) + 1
            melde((t_, "AUSLOESER: keine Wirkung an %s %s bis Takt %d | Welle %d Mann, Zustaende %s | Wirkung zuletzt %s, Torhaus %s" % (
                plan["art"], plan["ziel"], frist, len(welle), lage, wirk_alt, tor_pruef)))
            break
        spur.append((t_, phase, plan["art"], str(plan["ziel"]), lord["leben"], len(stuermer), len(welle)))

    befehl({"pause": True}, 0.3)
    erg = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "takte": t_, "sekunden": round(time.time() - t_start), "ereignisse": ereignisse,
           "spur": spur[::10]}
    erg["wahl"] = wahl
    erg["lord_tot"] = any(e[1] == "LORD TOT" for e in ereignisse)
    erg["rueckwaerts"] = sum(1 for e in ereignisse if e[1].startswith("RUECKWAERTS"))
    erg["angeworben"] = sum(len(e[1].split("[")[1].split(",")) for e in ereignisse if e[1].startswith("ANGEWORBEN"))
    erg["tote"] = len(alle) + erg["angeworben"] - len(eigene_soldaten(speicher.lies(E0, 3000 * ES)))
    with open(AUS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(erg, ensure_ascii=False, default=str) + "\n")
    print("Takte %d" % t_, flush=True)
    return {"takte": t_, "lord_tot": erg["lord_tot"], "tote": erg["tote"], "rueckwaerts": erg["rueckwaerts"], "wahl": wahl}


if __name__ == "__main__":
    main()
