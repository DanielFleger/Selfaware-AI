# -*- coding: utf-8 -*-
"""Wertungsmesser je Einheit und Partie (Daniel 16.11.2026 17:39 "einheiten bekommen einen wertigkeitsmesser - Gut ist wenn sie auf ein
ziel gehen es angreifen und zerstoeren bzw. ziele suchen und einheiten/bevoelkerung killen (jeweils punkte) und abzug beim stehenbleiben,
beim unnoetig laufwege machen, beim nicht wahrnehmen von chancen ... bonuspunkte fuer gutes reasoning und malus fuer schlechtes oder kein
nachdenken ... besonders belohnt werden kombinationen"; 17:54 "wichtig ist dass die analyse wirklich pro einheit pro spiel ist und es eine
klare aufstellung ist fuer punkte wo man am ende pro einheit genau sieht welche punkte sie wofuer bekommen hat und man dann sortieren kann
welche einheiten am effektivsten war"). Plan: Documents/DD-Berichte/SAI/SAI_2026-11-16_plan-wertungsmesser.html (Daniel: "alles passt").

Liest NUR das Lageprotokoll einer Partie (lage_*.jsonl.gz: je Lenker-Runde Einheiten, Gebaeude und das Logbuch "intents"). Zaehlt je
Einheit und Messgroesse eine MENGE (z. B. 2,5 Gebaeude-Anteile Schaden, 7 x 100 Takte Stehen) und je Ereignis eine Zeile mit Takt und Text.
Punkte = Menge x Gewicht des Reglers - das rechnet die Seite (tools/analysis/wertung_seite.py), damit ein Regler sofort wirkt.

Zuordnung (wer war es?) - gemessen am Protokoll, ungenau wo mehrere zugleich wirken:
  - Das Logbuch der Zeile k gehoert zur Runde davor (lageprotokoll.intents_lesen): es sagt, was jede Einheit zwischen Zeile k-1 und k tat.
  - Gebaeude: Angreifer ist, wer es laut Logbuch zum Ziel hat (B<nr>) oder dessen Zielgebaeude es ist, und dabei kaempft (Zustand 106/107,
    tools/experiments/schlag_messen.py) oder hoechstens NAH Felder an seiner Grundflaeche steht. Brennt es, gilt fuer den weiteren Schaden,
    wer es angezuendet hat. Mehrere Angreifer teilen sich die Menge.
  - Einheiten: Angreifer ist, wer sie im Feld Zieleinheit oder Nahziel hat oder laut Logbuch (U<nr>) und dabei in Reichweite steht.
  - Faellt der feindliche Lord, faellt die ganze Burg: was danach verschwindet, zaehlt nicht.
Nicht gemessen (noch nicht in den Messgroessen): ob eine Erwartung im Logbuch eintraf, Hin-und-Zurueck-Laeufe als eigene Groesse."""

import gzip
import json
import math
import os
import re

from selfaware import workspace

KAMPF = (106, 107)  # Zustand: Nahkampf gegen Einheit / gegen Gebaeude (gemessen, schlag_messen.py)
LORD = 55
NAH = 2  # Felder bis zur Grundflaeche, ab denen eine Einheit als "am Gebaeude" gilt (Startwert, nicht gemessen)
UMKREIS = 15  # Felder: "in der Naehe" fuer Zusammenspiel und Vorstoss (Startwert, nicht gemessen)
CHANCE_R = 15  # Felder: eine ungedeckte Chance in dieser Naehe gilt als verpasst, solange die Einheit steht (Startwert)
CHANCE_FERN, CHANCE_NAH = (
    20,
    10,
)  # ungedeckt: kein feindlicher Schuetze so nah, kein Nahkaempfer so nah (wie raids.GEFAHR_*)
FERN_REICH = 44  # Felder: ab hier trifft ein eigener Schuetze sein Einheitenziel nicht mehr (Bogen, sicht.REICHWEITE)
KEHRT_MIN = 4  # Felder je Strecke, ab denen hin und zurueck als Kehrtwende zaehlt (Startwert, nicht gemessen)
VERSION = 2  # aendert sich mit der Rechnung - die Seite rechnet ihren Zwischenspeicher dann neu

# Messgroessen: Schluessel -> (Name, dein Wort, Einheit der Menge, Richtung). Richtung +1 Lohn, -1 Abzug; das Startgewicht ist 1 bzw. -1
# (Plan, Punkt 2: "bis dahin stehen alle auf 1, Abzuege auf -1"). Die Einheiten sind so gewaehlt, dass Gewicht 1 vergleichbar ist:
# 1 = ein ganzes Gebaeude- oder Einheitenleben, ein Kill, 1.000 Takte, 10 Felder (erster Lauf auf Probe 7: "Absicht je 100 Takte"
# ueberstimmte alles, oben standen die, die am laengsten lebten).
MESSGROESSEN = {
    "gebaeude_schaden": (
        "Gebaeudeschaden",
        "auf ein ziel gehen es angreifen",
        "Gebaeude-Anteile (1 = ein ganzes Leben)",
        +1,
    ),
    "gebaeude_zerstoert": (
        "Gebaeude zerstoert",
        "und zerstoeren",
        "Gebaeudewert, Huette = 1 (raids.WERT / 12)",
        +1,
    ),
    "einheit_schaden": (
        "Schaden an Einheiten",
        "einheiten killen",
        "Einheiten-Anteile (1 = ein ganzes Leben)",
        +1,
    ),
    "einheit_kill": ("Soldat getoetet", "einheiten killen", "Kills", +1),
    "bevoelkerung_kill": ("Arbeiter oder Bauer getoetet", "bevoelkerung killen", "Kills", +1),
    "lord_schaden": (
        "Schaden am Lord",
        "je frueher der kill kommt desto besser",
        "je 10 % seines Lebens",
        +1,
    ),
    "lord_kill": ("Lord getoetet", "je frueher der kill kommt desto besser", "Kills", +1),
    "gemeinsam": (
        "Gemeinsam gewirkt",
        "kombinationen ... effektiv angreifen",
        "Schaden-Anteile, die mit 2+ Angreifern entstanden",
        +1,
    ),
    "vorstoss": (
        "Leben eingesetzt fuer andere",
        "vorstoesst ... leben opfert um dafuer anderen bessere siegeschancen",
        "Anteil des eigenen Lebens",
        +1,
    ),
    "mit_grund": (
        "Absicht mit Grund",
        "bonuspunkte fuer gutes reasoning",
        "Anteil der Runden (0 bis 1)",
        +1,
    ),
    "steht_ohne_wirkung": ("Steht ohne Wirkung", "abzug beim stehenbleiben", "je 1.000 Takte", -1),
    "wartet_mit_grund": ("Wartet mit Plan", "abzug beim stehenbleiben", "je 1.000 Takte", -1),
    "leben_beim_stehen": (
        "Leben verloren beim Stehen",
        "abzug beim stehenbleiben",
        "Anteil des eigenen Lebens",
        -1,
    ),
    "weg_vom_ziel": (
        "Weg vom eigenen Ziel",
        "beim unnoetig laufwege machen",
        "je 10 Felder, nur bei gleichbleibendem Ziel",
        -1,
    ),
    "kehrtwende": (
        "Kehrtwende",
        "lief ewig in eine richtung nur um dann zurueckzugehen",
        "Wenden (je 4+ Felder hin und zurueck)",
        -1,
    ),
    "chance_verpasst": (
        "Chance verpasst",
        "beim nicht wahrnehmen von chancen",
        "je 1.000 Takte",
        -1,
    ),
    "ohne_absicht": (
        "Ohne Absicht",
        "malus fuer ... kein nachdenken",
        "Anteil der Runden (0 bis 1)",
        -1,
    ),
}
# Absichten, bei denen Stehen geplant ist (Logbuch, micro/unit_log.Action)
WARTEN = {"WAIT_STAGING", "HOLD_POST", "DEFEND", "GUARD", "IDLE_PLANNED"}
FLUCHT = {"FLEE", "RETREAT"}

REGLER_DATEI = os.path.join(workspace.DATA, "wertung", "regler.json")
VERLAUF_DATEI = os.path.join(workspace.DATA, "wertung", "regler_verlauf.jsonl")


def _typtabellen():
    """Arten aus den Modulen, die sie schon fuehren (eine Stelle je Liste, GG 161)."""
    import selfaware.baukasten.einheiten as EH
    import selfaware.micro.tasks.raids as RA
    import selfaware.micro.tasks.vorstoss as VS
    import selfaware.services.sicht as SI

    return {
        "arbeiter": set(VS.ARBEITER) | set(RA.ARBEITER),
        "fern": set(VS.FERN_FEIND),
        "nah": set(VS.NAHKAMPF),
        "tiere": set(SI.TIERE),
        "kaempfer": set(EH.ARTEN) | {LORD},
        "wert": dict(RA.WERT),
        "groesse": dict(SI.GROESSE),
    }


def typname(t):
    """Gebaeudename (Gebaeudetabelle von VillageStudio)."""
    from selfaware.telemetry.partie_vergleich import typname as tn

    return tn(t)


def einheit_name(t):
    """Spielname und Codename einer Einheitenart (baukasten/einheiten.ARTEN, micro/unit_log.NAMES) - Daniel 25.10.: keine eigenen Namen."""
    from selfaware.baukasten.einheiten import ARTEN
    from selfaware.micro.unit_log import NAMES

    a = ARTEN.get(t)
    code = NAMES.get(t)
    if a is not None:
        return "%s (%s %d)" % (a.name, code, t) if code else "%s (%d)" % (a.name, t)
    return "%s %d" % (code, t) if code else "Typ %d" % t


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _rand_abstand(p, g, groesse):
    """Felder von p bis zur Grundflaeche des Gebaeudes g (0 = darauf)."""
    b = groesse.get(g["typ"]) or 1
    dx = max(g["x"] - p[0], 0, p[0] - (g["x"] + b - 1))
    dy = max(g["y"] - p[1], 0, p[1] - (g["y"] + b - 1))
    return max(dx, dy)


def _tabelle(roh, kopfzeile):
    z = (roh or "").splitlines()
    if len(z) <= kopfzeile:
        return []
    kopf = z[kopfzeile].split()
    aus = []
    for r in z[kopfzeile + 1 :]:
        w = r.split()
        if len(w) >= len(kopf):
            aus.append({k: int(v) for k, v in zip(kopf, w, strict=False)})
    return aus


def _ziel(intent):
    """('B', nr) / ('U', nr) / ('P', (x, y)) / None aus dem Ziel einer Logbuch-Zeile."""
    t = (intent or {}).get("target") or "-"
    if t[:1] in "BU" and t[1:].isdigit():
        return t[0], int(t[1:])
    m = re.match(r"\((\d+),(\d+)\)", t)
    return ("P", (int(m.group(1)), int(m.group(2)))) if m else None


def zeilen(pfad):
    """(Takt, Einheiten {nr: dict}, Gebaeude {nr: dict}, Logbuch {nr: dict}) je Zeile des Lageprotokolls."""
    from selfaware.telemetry.lageprotokoll import intents_lesen

    with gzip.open(pfad, "rt", encoding="utf-8") as f:
        for z in f:
            r = json.loads(z)
            E = {e["nr"]: e for e in _tabelle(r.get("einheiten"), 1)}
            B = {g["nr"]: g for g in _tabelle(r.get("gebaeude"), 0)}
            _t, ints = intents_lesen(r)
            yield r["t"], E, B, ints


def spieler_aus_name(pfad):
    m = re.search(r"_sp(\d+)", os.path.basename(pfad))
    return int(m.group(1)) if m else 1


class _Einheit:
    def __init__(self, nr, typ, t):
        self.nr, self.typ, self.von, self.bis = nr, typ, t, t
        self.schluessel = "%d-%d-%d" % (nr, typ, t)
        self.menge = {k: 0.0 for k in MESSGROESSEN}
        self.ereignisse = []  # (Takt, Messgroesse, Menge, Text)
        self.gestorben = False
        self.leben_max = 0
        self.runden, self.runden_grund, self.runden_ohne = 0, 0, 0

    def zaehle(self, k, menge, t=None, text=None):
        self.menge[k] += menge
        if text:
            self.ereignisse.append((t, k, round(menge, 3), text))


def messen(pfad, sp=None):
    """Die Wertung einer Partie: {"partie", "spieler", "kill_takt", "letzter_takt", "einheiten": [..], "ohne_taeter": {..}}."""
    sp = spieler_aus_name(pfad) if sp is None else sp
    T = _typtabellen()
    arbeiter, fern, nah, tiere, wert, groesse = (
        T["arbeiter"],
        T["fern"],
        T["nah"],
        T["tiere"],
        T["wert"],
        T["groesse"],
    )
    kaempfer = T["kaempfer"]
    eig = {}  # nr -> _Einheit (aktuell lebend)
    alle = []
    max_leben = {}  # ("E"|"B", nr, typ/uid) -> hoechstes gesehenes Leben
    brand = {}  # Gebaeude-uid -> Einheiten-Schluessel, die es angezuendet haben
    ohne_taeter = {"gebaeude_schaden": 0.0, "gebaeude_zerstoert": 0, "einheit_schaden": 0.0}
    vor = None
    kill_takt = None
    t = None
    alle_zeilen = list(zeilen(pfad))
    for i_z, (t, E, B, ints) in enumerate(alle_zeilen):
        nach = alle_zeilen[i_z + 1] if i_z + 1 < len(alle_zeilen) else None
        # eigene Einheiten: Leben einer Einheit = solange Nummer und Art gleich bleiben
        lebend = {}
        for nr, e in E.items():
            # gewertet werden die eigenen Kaempfer (baukasten/einheiten.ARTEN und der Lord) - Arbeiter und Bauern nicht (Probe 7: 99
            # eigene Arbeiter standen sonst mit "Steht ohne Wirkung" und "Ohne Absicht" in der Liste)
            if e["besitzer"] != sp or e["leben"] <= 0 or e["typ"] not in kaempfer:
                continue
            a = eig.get(nr)
            if a is None or a.typ != e["typ"] or vor is None or nr not in vor[1]:
                a = _Einheit(nr, e["typ"], t)
                alle.append(a)
            a.bis = t
            a.leben_max = max(a.leben_max, e["leben"])
            lebend[nr] = a
        for nr, a in eig.items():
            if nr not in lebend:
                a.gestorben = True
        eig = lebend
        for e in E.values():
            if e["besitzer"] not in (0, sp):
                k = ("E", e["nr"], e["typ"])
                max_leben[k] = max(max_leben.get(k, 0), e["leben"])
        for g in B.values():
            if g["besitzer"] not in (0, sp):
                k = ("B", g["uid"])
                max_leben[k] = max(max_leben.get(k, 0), g["leben"])
        if vor is None:
            vor = (t, E, B, ints)
            continue
        t0, E0, B0, _i0 = vor
        dt = max(1, t - t0)
        nach_kill = kill_takt is not None
        if (
            kill_takt is None
            and any(e["typ"] == LORD and e["besitzer"] not in (0, sp) for e in E0.values())
            and not any(
                e["typ"] == LORD and e["besitzer"] not in (0, sp) and e["leben"] > 0
                for e in E.values()
            )
        ):
            kill_takt = t
        feind_b0 = {g["uid"]: g for g in B0.values() if g["besitzer"] not in (0, sp)}
        feind_b = {g["uid"]: g for g in B.values() if g["besitzer"] not in (0, sp)}
        feind_e0 = {
            n: e
            for n, e in E0.items()
            if e["besitzer"] not in (0, sp) and e["typ"] not in tiere and e["leben"] > 0
        }
        nr_zu_uid0 = {g["nr"]: g["uid"] for g in feind_b0.values()}

        # --- wer greift was an (zwischen Zeile k-1 und k) ---
        angriff_b = {}  # Gebaeude-uid -> [Einheit]
        angriff_e = {}  # feindliche Einheit nr -> [Einheit]
        for nr, a in eig.items():
            e = E[nr]
            p = (e["x"], e["y"])
            it = ints.get(nr)
            z = _ziel(it)
            ziele_b = set()
            if z and z[0] == "B":
                ziele_b.add(z[1])
            if e.get("zielgebaeude"):
                ziele_b.add(e["zielgebaeude"])
            for bnr in ziele_b:
                uid = nr_zu_uid0.get(bnr)
                if uid is None:
                    continue
                g = feind_b0[uid]
                if e["zustand"] in KAMPF or _rand_abstand(p, g, groesse) <= NAH:
                    angriff_b.setdefault(uid, []).append(a)
            ziele_e = {x for x in (e.get("zieleinheit"), e.get("nahziel")) if x and x > 0}
            if z and z[0] == "U":
                ziele_e.add(z[1])
            for enr in ziele_e:
                f = feind_e0.get(enr)
                if f is None:
                    continue
                d = math.hypot(f["x"] - p[0], f["y"] - p[1])
                if d <= (FERN_REICH if e["typ"] in fern else NAH + 1):
                    angriff_e.setdefault(enr, []).append(a)
        gewirkt = set()  # Einheiten-Schluessel, die in dieser Runde Schaden machten

        # --- Gebaeude: Schaden, Zerstoerung, Brand ---
        if not nach_kill:
            for uid, g0 in feind_b0.items():
                g = feind_b.get(uid)
                dl = g0["leben"] - (g["leben"] if g else 0)
                taeter = angriff_b.get(uid, [])
                if (
                    g is not None
                    and (g.get("feuer") or 0) > 0
                    and not (g0.get("feuer") or 0)
                    and taeter
                ):
                    brand[uid] = [x.schluessel for x in taeter]
                if not taeter and uid in brand:
                    taeter = [x for x in alle if x.schluessel in brand[uid]]
                if dl <= 0:
                    continue
                anteil = dl / float(max(1, max_leben.get(("B", uid), g0["leben"])))
                if kill_takt == t and g is None:
                    continue  # die Burg faellt mit dem Lord
                if not taeter:
                    ohne_taeter["gebaeude_schaden"] += anteil
                    if g is None:
                        ohne_taeter["gebaeude_zerstoert"] += 1
                    continue
                n = len(taeter)
                name = typname(g0["typ"])
                for x in taeter:
                    x.zaehle("gebaeude_schaden", anteil / n)
                    gewirkt.add(x.schluessel)
                    if n >= 2:
                        x.zaehle("gemeinsam", anteil / n)
                    if g is None:
                        x.zaehle(
                            "gebaeude_zerstoert",
                            wert.get(g0["typ"], 1) / 12.0 / n,
                            t,
                            "%s zerstoert%s"
                            % (name, (" (mit %d anderen)" % (n - 1)) if n > 1 else ""),
                        )

        # --- Einheiten: Schaden, Kills, Lord ---
        if not nach_kill:
            for enr, f0 in feind_e0.items():
                f = E.get(enr)
                if f is not None and f["typ"] != f0["typ"]:
                    continue  # Probe 7: 197 Mal wechselte ein Bauer die Art (nahm Arbeit an) - das ist kein Tod
                tot = f is None or f["leben"] <= 0
                dl = f0["leben"] - (0 if tot else f["leben"])
                taeter = angriff_e.get(enr, [])
                if dl <= 0:
                    continue
                anteil = dl / float(max(1, max_leben.get(("E", enr, f0["typ"]), f0["leben"])))
                if not taeter:
                    ohne_taeter["einheit_schaden"] += anteil
                    continue
                n = len(taeter)
                name = typname(f0["typ"])
                for x in taeter:
                    gewirkt.add(x.schluessel)
                    if n >= 2:
                        x.zaehle("gemeinsam", anteil / n)
                    if f0["typ"] == LORD:
                        x.zaehle(
                            "lord_schaden",
                            10.0 * anteil / n,
                            t,
                            "Lord: %.0f %% seines Lebens%s"
                            % (100 * anteil, " (zu %d)" % n if n > 1 else ""),
                        )
                        if tot:
                            x.zaehle(
                                "lord_kill",
                                1.0 / n,
                                t,
                                "Lord getoetet%s"
                                % (" (mit %d anderen)" % (n - 1) if n > 1 else ""),
                            )
                        continue
                    x.zaehle("einheit_schaden", anteil / n)
                    if tot:
                        k = "bevoelkerung_kill" if f0["typ"] in arbeiter else "einheit_kill"
                        x.zaehle(
                            k,
                            1.0 / n,
                            t,
                            "%s getoetet%s"
                            % (name, " (mit %d anderen)" % (n - 1) if n > 1 else ""),
                        )

        # --- ungedeckte Chancen dieser Runde (Arbeiter, Zielgebaeude) ---
        schuetzen = [(e["x"], e["y"]) for e in feind_e0.values() if e["typ"] in fern]
        nahk = [(e["x"], e["y"]) for e in feind_e0.values() if e["typ"] in nah]

        def ungedeckt(p, schuetzen=schuetzen, nahk=nahk):
            return not any(schach(p, s) <= CHANCE_FERN for s in schuetzen) and not any(
                schach(p, q) <= CHANCE_NAH for q in nahk
            )

        chancen = [(e["x"], e["y"]) for e in feind_e0.values() if e["typ"] in arbeiter]
        chancen += [(g["x"], g["y"]) for g in feind_b0.values() if g["typ"] in wert]
        chancen = [p for p in chancen if ungedeckt(p)]

        # --- je eigene Einheit: Stehen, Wege, Denken, Vorstoss ---
        beschiesst = {}
        for e in E.values():
            if e["besitzer"] not in (0, sp) and e["typ"] in fern and e.get("zieleinheit"):
                beschiesst[e["zieleinheit"]] = beschiesst.get(e["zieleinheit"], 0) + 1
        orte_gewirkt = [
            (E[x.nr]["x"], E[x.nr]["y"]) for x in eig.values() if x.schluessel in gewirkt
        ]
        for nr, a in eig.items():
            e = E[nr]
            e0 = E0.get(nr)
            if e0 is None or e0["typ"] != e["typ"] or e0["besitzer"] != sp:
                continue
            p, p0 = (e["x"], e["y"]), (e0["x"], e0["y"])
            it = ints.get(nr)
            arbeiter_art = e["typ"] in arbeiter
            if not arbeiter_art:
                a.runden += 1
                if it is None:
                    a.runden_ohne += 1
                elif (it.get("reason") or "-") != "-":
                    a.runden_grund += 1
            steht = (
                p == p0
                and e["zustand"] not in KAMPF
                and not e.get("zielart")
                and a.schluessel not in gewirkt
            )
            if steht and not arbeiter_art:
                geplant = it is not None and it.get("action") in WARTEN
                a.zaehle(
                    "wartet_mit_grund" if geplant else "steht_ohne_wirkung",
                    dt / 1000.0,
                    t,
                    "stand %d Takte%s"
                    % (
                        dt,
                        (" (" + it["action"] + " " + (it.get("reason") or "") + ")")
                        if it
                        else " ohne Absicht",
                    ),
                )
                if e["leben"] < e0["leben"]:
                    a.zaehle(
                        "leben_beim_stehen",
                        (e0["leben"] - e["leben"]) / float(max(1, a.leben_max)),
                        t,
                        "stand und verlor %d Leben%s"
                        % (
                            e0["leben"] - e["leben"],
                            ""
                            if geplant
                            else " (Absicht: %s)" % ((it or {}).get("action") or "keine"),
                        ),
                    )
                if e["typ"] not in (LORD,):
                    c = min(chancen, key=lambda q: schach(p, q), default=None)
                    if c is not None and schach(p, c) <= CHANCE_R:
                        a.zaehle(
                            "chance_verpasst",
                            dt / 1000.0,
                            t,
                            "ungedecktes Ziel bei %s, %d Felder entfernt" % (c, schach(p, c)),
                        )
            z = _ziel(it)
            # Messung 16.11.: an einem Zielwechsel passt die Bewegung so oft zur alten wie zur neuen Absicht (Probe 7: 14 zu 18, Probe 6:
            # 15 zu 15) - "weg vom Ziel" zaehlt darum nur, wenn das Ziel auch in der naechsten Runde dasselbe ist
            gleich = nach is not None and _ziel(nach[3].get(nr)) == z
            if p != p0 and z and gleich and (it or {}).get("action") not in FLUCHT:
                zp = None
                if z[0] == "P":
                    zp = z[1]
                elif z[0] == "U" and z[1] in E0:
                    zp = (E0[z[1]]["x"], E0[z[1]]["y"])
                elif z[0] == "B" and z[1] in B0:
                    g = B0[z[1]]
                    b = groesse.get(g["typ"]) or 1
                    zp = (g["x"] + b // 2, g["y"] + b // 2)
                if zp is not None:
                    mehr = schach(p, zp) - schach(p0, zp)
                    if mehr > 0:
                        a.zaehle(
                            "weg_vom_ziel",
                            mehr / 10.0,
                            t if mehr >= 5 else None,
                            "lief %d Felder von %s weg (%s)"
                            % (mehr, it.get("target"), it.get("action")),
                        )
            # Kehrtwende (Daniel 16.11.2026 00:09 "ein speertraeger liefe ewig in eine richtung nur um dann zurueckzugehen fuer ein anderes
            # gebaeude"): KEHRT_MIN+ Felder hin, in der naechsten Runde KEHRT_MIN+ Felder in die Gegenrichtung - nur aus den Orten gemessen
            if nach is not None and nr in nach[1] and nach[1][nr]["typ"] == e["typ"]:
                p1 = (nach[1][nr]["x"], nach[1][nr]["y"])
                v1, v2 = (p[0] - p0[0], p[1] - p0[1]), (p1[0] - p[0], p1[1] - p[1])
                it1 = nach[3].get(nr) or {}
                if (
                    schach(p, p0) >= KEHRT_MIN
                    and schach(p1, p) >= KEHRT_MIN
                    and v1[0] * v2[0] + v1[1] * v2[1] < 0
                    and it1.get("action") not in FLUCHT
                ):
                    a.zaehle(
                        "kehrtwende",
                        1.0,
                        nach[0],
                        "kehrte um: %d Felder nach %s, dann %d zurueck nach %s (Absicht %s %s)"
                        % (
                            schach(p, p0),
                            p,
                            schach(p1, p),
                            p1,
                            it1.get("action") or "keine",
                            it1.get("target") or "",
                        ),
                    )
            if (
                beschiesst.get(nr)
                and e["leben"] < e0["leben"]
                and any(schach(p, q) <= UMKREIS for q in orte_gewirkt if q != p)
            ):
                a.zaehle(
                    "vorstoss",
                    (e0["leben"] - e["leben"]) / float(max(1, a.leben_max)),
                    t,
                    "%d feindliche Schuetzen zielten auf sie (%d Leben), andere in der Naehe wirkten"
                    % (beschiesst[nr], e0["leben"] - e["leben"]),
                )
        vor = (t, E, B, ints)
    for a in alle:
        if a.runden:
            a.menge["mit_grund"] = a.runden_grund / float(a.runden)
            a.menge["ohne_absicht"] = a.runden_ohne / float(a.runden)
    return {
        "partie": os.path.basename(pfad).replace(".jsonl.gz", ""),
        "spieler": sp,
        "kill_takt": kill_takt,
        "letzter_takt": t,
        "version": VERSION,
        "ohne_taeter": {k: round(v, 3) for k, v in ohne_taeter.items()},
        "einheiten": [
            {
                "schluessel": a.schluessel,
                "nr": a.nr,
                "typ": a.typ,
                "name": einheit_name(a.typ),
                "runden": a.runden,
                "von": a.von,
                "bis": a.bis,
                "gestorben": a.gestorben,
                "menge": {k: round(v, 4) for k, v in a.menge.items() if v},
                "ereignisse": a.ereignisse[-200:],
            }
            for a in alle
        ],
    }


# ---- Regler ---------------------------------------------------------------------------------------------------------
def regler_standard():
    return [
        {
            "id": k,
            "messgroesse": k,
            "arten": "alle",
            "gewicht": float(r),
            "name": n,
            "wort": w,
            "archiviert": False,
            "gesetzt_von": "Startwert",
        }
        for k, (n, w, _e, r) in MESSGROESSEN.items()
    ]


def regler_lesen():
    try:
        with open(REGLER_DATEI, encoding="utf-8") as f:
            return json.load(f)["regler"]
    except (OSError, ValueError, KeyError):
        return regler_standard()


def regler_schreiben(regler, wer, grund=""):
    """Schreibt die Regler und haengt ALT und NEU an den Verlauf (Rueckweg: regler_zuruecknehmen)."""
    import datetime

    alt = regler_lesen()
    os.makedirs(os.path.dirname(REGLER_DATEI), exist_ok=True)
    with open(REGLER_DATEI, "w", encoding="utf-8") as f:
        json.dump({"regler": regler}, f, ensure_ascii=False, indent=1)
    with open(VERLAUF_DATEI, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "zeit": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "wer": wer,
                    "grund": grund,
                    "alt": alt,
                    "neu": regler,
                },
                ensure_ascii=False,
            )
            + "\n"
        )


def verlauf_lesen():
    try:
        with open(VERLAUF_DATEI, encoding="utf-8") as f:
            return [json.loads(z) for z in f if z.strip()]
    except OSError:
        return []


def regler_zuruecknehmen(wer):
    """Stellt den Stand vor der letzten Aenderung wieder her - als neue Aenderung im Verlauf (der Verlauf behaelt beides, P4.4)."""
    v = verlauf_lesen()
    if not v:
        return False
    regler_schreiben(
        v[-1]["alt"], wer, "zurueckgenommen: " + (v[-1].get("grund") or "letzte Aenderung")
    )
    return True


def punkte(einheit, regler):
    """{Regler-id: Punkte} einer Einheit aus ihrer Menge und den aktiven Reglern (dieselbe Rechnung wie die Seite)."""
    aus = {}
    for r in regler:
        if r.get("archiviert"):
            continue
        if r["arten"] != "alle" and einheit["typ"] not in r["arten"]:
            continue
        m = einheit["menge"].get(r["messgroesse"], 0)
        if m:
            aus[r["id"]] = round(m * r["gewicht"], 3)
    return aus


def main():
    import sys

    erg = messen(sys.argv[1])
    reg = regler_lesen()
    zeilen_ = sorted(
        ((sum(punkte(e, reg).values()), e) for e in erg["einheiten"]), key=lambda x: -x[0]
    )
    print(
        "Partie %s, Kill bei Takt %s, %d Einheiten"
        % (erg["partie"], erg["kill_takt"], len(erg["einheiten"]))
    )
    for s, e in zeilen_[:25]:
        print(
            "%8.1f  %-22s Nr %-4d Takt %d-%d%s  %s"
            % (
                s,
                e["name"][:22],
                e["nr"],
                e["von"],
                e["bis"],
                " tot" if e["gestorben"] else "",
                punkte(e, reg),
            )
        )


if __name__ == "__main__":
    main()
