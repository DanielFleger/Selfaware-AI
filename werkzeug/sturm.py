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
E0, ES = AD.E0, AD.ES
SP, FEIND = 1, 2
PD1 = 0x0115BDF8 + SP * 0x39F4
GOLD1, KEULE1, LEDER1, HOLZ1 = PD1 + 0x4D0 + 15 * 4, PD1 + 0x4D0 + 21 * 4, PD1 + 0x4D0 + 23 * 4, PD1 + 0x4D0 + 2 * 4
FEUER1 = PD1 + 136                                   # Bauern am Lagerfeuer (erstes_spiel: PD + 136)
GOLD2 = 0x0115BDF8 + FEIND * 0x39F4 + 0x4D0 + 15 * 4
STREITKOLBEN, BALLISTE, TORHAUS, KASERNE, HUETTE = 26, 77, 75, 9, 1
FERN = set(gefecht.FERN_REICH)


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
    gf = AD.gefahr_feld()
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
    art, nr, r, rand = min(kand, key=lambda k: k[2]["takte"])
    weg = r["weg"]
    i_wand = next((i for i, q in enumerate(weg) if q in set(map(tuple, r["mauern"]))), None)
    i_tor = next((i for i, q in enumerate(weg) if rand is not None and rand[q]), None)
    if i_tor is not None and (i_wand is None or i_tor < i_wand):
        return {"art": "tor", "ziel": nr, "zug": weg[i_tor - 1], "weg": weg, "takte": r["takte"], "gefahr": gf, "e": e,
                "kandidaten": [(k[0], k[1], k[2]["takte"]) for k in kand]}
    if i_wand is not None:
        return {"art": "mauer", "ziel": weg[i_wand], "zug": weg[i_wand - 1], "weg": weg, "takte": r["takte"], "gefahr": gf,
                "e": e, "kandidaten": [(k[0], k[1], k[2]["takte"]) for k in kand]}
    return {"art": "lord", "ziel": None, "zug": None, "weg": weg, "takte": r["takte"], "gefahr": gf, "e": e,
            "kandidaten": [(k[0], k[1], k[2]["takte"]) for k in kand]}


def sammelfeld(weg, zug, gf):
    """Das letzte Feld OHNE Beschuss (Gefahr 0) auf dem geplanten Weg vor dem Zugang - dort beginnt das Vorpreschen
    (Lauf 00:37: das naechste beschussfreie Feld irgendwo lag 48 Felder vom Zugang und nicht auf dem Weg - Bogen/Armbrust
    reichen 35-45 Felder, Wissensregister L82/L91). Ist der ganze Weg unter Beschuss: der Startpunkt."""
    ende = weg.index(tuple(zug)) if zug is not None and tuple(zug) in weg else len(weg) - 1
    sicher = [q for q in weg[:ende + 1] if gf[q] == 0]
    if not sicher:
        return tuple(weg[0])
    letzt = max(i for i, q in enumerate(weg[:ende + 1]) if gf[q] == 0)
    return tuple(weg[letzt])


def main():
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
    print("ARMEE: %d Streitkolben, %d Nahkaempfer, %d Fernkaempfer | Lord %d bei %s | Kaserne %s" % (
        len(mauer), len(nah), len(fern), lnr, lord_xy, kaserne_xy), flush=True)
    kxy = {int(k): (int(x), int(y)) for x, y, k in zip(*speicher.felder())}
    kvon = {v: k for k, v in kxy.items()}

    ereignisse, spur = [], []
    phase, plan, sammel, welle = "planen", None, None, set()
    geschickt, angesetzt, jaeger, fern_ziel = set(), set(), {}, {}
    ballisten_pruefen = True                             # nur bei Anlass suchen: Anfang, Jaeger frei, neues Ziel
    versuche_ballista = {}                               # Ballista -> geschickte Jaeger (hoechstens 2 je Ballista)
    offen, erwartet, kauf_aus = None, 0, False
    haus_stellen = [(kaserne_xy[0] + dx, kaserne_xy[1] + dy) for r_ in (6, 9, 12) for dx, dy in
                    ((-r_, 0), (r_, 0), (0, -r_), (0, r_), (-r_, -r_), (r_, r_), (-r_, r_), (r_, -r_))] if kaserne_xy else []
    frist, wirk_alt, sammel_frist, t_107 = None, None, None, None
    tick0 = s32(shc.TICK)
    letzt = None
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
            ereignisse.append((t_, "LORD TOT"))
            break
        jetzt = eigene_soldaten(roh)
        # gleiche Nummer, andere Kennung = neuer Mann auf dem Platz eines Gefallenen
        lebend = {n for n in jetzt if uid_von.get(n) == kennung(roh, n)}
        for grp in (mauer, nah, fern, welle, angesetzt, geschickt):
            grp &= lebend
        for j in [j for j, b in jaeger.items() if j not in lebend or AD.einheit(roh, b)["leben"] <= 0]:
            jaeger.pop(j)
            ballisten_pruefen = True
            if j in lebend:
                mauer.add(j)                              # Ballista erledigt: zurueck zu den Streitkolben
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
                        ereignisse.append((t_, "KAUF GESCHEITERT - kein weiterer Kauf"))
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
                    if sammel is not None and jetzt[n]["typ"] not in FERN:
                        befehl({"angriff": {"einheiten": [n], "lauf": [sammel[0], sammel[1]], "trupp": 1}}, 0.3)
                        geschickt.add(n)
                erwartet = max(0, erwartet - len(neu))
                if neu:
                    ereignisse.append((t_, "ANGEWORBEN %s" % neu))

        # --- Jaeger auf Feuerballisten ---
        if ballisten_pruefen and len(jaeger) < 2 and mauer - welle - set(jaeger):
            ballisten_pruefen = False
            ballisten = [n for n in range(1, 3000) if AD.einheit(roh, n)["typ"] == BALLISTE and AD.einheit(roh, n)["leben"] > 0
                         and AD.einheit(roh, n)["besitzer"] == FEIND and AD.einheit(roh, n)["zustand"] != 0
                         and n not in jaeger.values() and versuche_ballista.get(n, 0) < 2]
            frei_ = [n for n in mauer - welle if n not in jaeger]
            while ballisten and frei_ and len(jaeger) < 2:
                b_ = ballisten.pop(0)
                bxy = (AD.einheit(roh, b_)["x"], AD.einheit(roh, b_)["y"])
                f = min(frei_, key=lambda m_: abstand((jetzt[m_]["x"], jetzt[m_]["y"]), bxy))
                frei_.remove(f)
                mauer.discard(f)
                jaeger[f] = b_
                versuche_ballista[b_] = versuche_ballista.get(b_, 0) + 1
                befehl({"angriff": {"einheiten": [f], "ziel": b_, "trupp": 1}}, 0.3)
                ereignisse.append((t_, "JAEGER %d auf Feuerballiste %d" % (f, b_)))

        # --- Fernkaempfer: feindliche Soldaten nahe dem Lord ---
        tot_ziel = [n for n, z in fern_ziel.items() if n not in fern or AD.einheit(roh, z)["leben"] <= 0]
        for n in tot_ziel:
            fern_ziel.pop(n)
        ohne = [n for n in fern if n not in fern_ziel]
        if ohne:
            feinde = [m for m in range(1, 3000) if AD.einheit(roh, m)["besitzer"] == FEIND and AD.einheit(roh, m)["leben"] > 0
                      and AD.einheit(roh, m)["zustand"] != 0 and AD.einheit(roh, m)["typ"] in shc.SOLDATEN]
            if feinde:
                z = min(feinde, key=lambda m: abstand((AD.einheit(roh, m)["x"], AD.einheit(roh, m)["y"]), lord_xy))
                befehl({"angriff": {"einheiten": sorted(ohne), "ziel": z, "trupp": 1}}, 0.3)
                for n in ohne:
                    fern_ziel[n] = z

        stuermer = (mauer | nah) - set(jaeger)
        if not stuermer and erwartet == 0 and (kaserne is None or s32(FEUER1) <= 0):
            ereignisse.append((t_, "ALLE TOT - keiner mehr anwerbbar"))
            break

        # --- Phasen ---
        if phase == "planen":
            if not stuermer:
                continue
            start = min(((jetzt[n]["x"], jetzt[n]["y"]) for n in stuermer),
                        key=lambda q: abstand(q, kaserne_xy) if kaserne_xy else 0)   # Neue kommen aus der Kaserne
            plan = plane_ziel(start, len(stuermer), mk, lord_xy)
            ballisten_pruefen = True
            if plan is None:
                ereignisse.append((t_, "KEIN WEG zum Lord von %s" % (start,)))
                break
            sammel = sammelfeld(plan["weg"], plan["zug"] if plan["zug"] else plan["weg"][-2], plan["gefahr"])
            ereignisse.append((t_, "ZIEL %s %s ueber Zugang %s, Sammelfeld %s, Weg %.0f Takte | Kandidaten %s" % (
                plan["art"], plan["ziel"], plan["zug"], sammel, plan["takte"], plan["kandidaten"])))
            geschickt, angesetzt, welle = set(), set(), set()
            befehl({"angriff": {"einheiten": sorted(stuermer), "lauf": [sammel[0], sammel[1]], "trupp": 1}}, 0.5)
            geschickt = set(stuermer)
            # echte Laufzeit je Mann zum Sammelfeld (Schrittbits) - die Luftlinie unterschaetzte (Lauf 00:39: 11 von 51 da)
            zum_sammel = mechanik.lauf_takte_zu(plan["e"]["link"], sammel, AD.sperre_feindbau(plan["e"]["bau"]))
            # Felder x Takte je Feld des Typs: Streitkolben 12 (gemessen, augen_laufen), sonst 16 - UNGEMESSEN fuer Soldaten, geliehen
            # von den Arbeitern (Wissensregister L68). Lauf 00:40: mit 12 fuer alle waren beim Sturm erst 11 von 53 da
            wege_ = [zum_sammel[jetzt[n]["x"], jetzt[n]["y"]] / mechanik.TAKTE_JE_FELD *
                     (mechanik.TAKTE_JE_FELD if jetzt[n]["typ"] == STREITKOLBEN else 16) for n in stuermer]
            erreichbar = [w for w in wege_ if np.isfinite(w)]
            sammel_frist = t_ + (max(erreichbar) if erreichbar else 0)
            if len(erreichbar) < len(wege_):
                ereignisse.append((t_, "SAMMELN: %d von %d erreichen das Sammelfeld nicht" % (len(wege_) - len(erreichbar), len(wege_))))
            phase = "sammeln"
            continue

        if phase == "sammeln":
            da = {n for n in stuermer if abstand((jetzt[n]["x"], jetzt[n]["y"]), sammel) <= 1}
            if da and (da == stuermer or t_ >= sammel_frist):
                welle = set(da)
                if plan["art"] == "mauer":
                    befehl({"angriff": {"einheiten": sorted(welle), "lauf": [plan["zug"][0], plan["zug"][1]], "trupp": 1}}, 0.5)
                elif plan["art"] == "tor":
                    befehl({"angriff": {"einheiten": sorted(welle), "gebaeude": plan["ziel"], "trupp": 1}}, 0.5)
                else:
                    befehl({"angriff": {"einheiten": sorted(welle), "ziel": lnr, "trupp": 1}}, 0.5)
                # Frist: Wegfelder des Plans vom Sammelfeld bis zum Zugang x 12 Takte + 2 Trefferrunden (nicht die Luftlinie)
                w_ = plan["weg"]
                zug = tuple(plan["zug"]) if plan["zug"] else tuple(w_[-1])
                felder_ = (w_.index(zug) - w_.index(sammel)) if zug in w_ and sammel in w_ else abstand(sammel, zug)
                frist = t_ + max(0, felder_) * mechanik.TAKTE_JE_FELD + 2 * mk["takte_je_treffer"]
                wirk_alt, t_107 = None, None
                ereignisse.append((t_, "STURM %d Mann auf %s %s (%d noch unterwegs)" % (len(welle), plan["art"], plan["ziel"],
                                                                                    len(stuermer - da))))
                phase = "sturm"
            continue

        # phase == "sturm"
        if plan["art"] == "mauer":
            k = kvon[plan["ziel"]]
            if not s32(speicher.LOGIK + 4 * k) & 0x100:
                ereignisse.append((t_, "MAUER %s GEFALLEN" % (plan["ziel"],)))
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
                ereignisse.append((t_, "TORHAUS %s GEFALLEN" % plan["ziel"]))
                phase = "planen"
                continue
            wirkung = None                                # Leben des Torhauses nur ueber das Lagebild - bei der Frist
        else:
            wirkung = lord["leben"]
        if wirkung is not None and wirk_alt is not None and wirkung < wirk_alt:
            frist = t_ + 2 * mk["takte_je_treffer"]       # Wirkung: naechste Frist 2 Trefferrunden
            t_107 = None
        wirk_alt = wirkung if wirkung is not None else wirk_alt
        # wer im Mauerangriff steht (107, Code UpdateMaceman), arbeitet - Abbruch fruehestens 2 Trefferrunden nach Beginn
        if any(jetzt[n]["lage"] == 107 for n in welle):
            t_107 = t_ if t_107 is None else t_107
            frist = max(frist, t_107 + 2 * mk["takte_je_treffer"])
        if not welle:
            ereignisse.append((t_, "WELLE GEFALLEN - neu sammeln"))
            phase = "planen"
            continue
        if t_ > frist:
            if plan["art"] == "tor":
                befehl({"lagebild": True}, 2.0, bis="LAGEBILD")
                leben = lies_gebaeude().get(plan["ziel"], {}).get("leben", 0)
                if wirk_alt is None or leben < wirk_alt:
                    wirk_alt, frist = leben, t_ + 2 * mk["takte_je_treffer"]
                    continue
            lage = {}
            for n in welle:
                lage[jetzt[n]["lage"]] = lage.get(jetzt[n]["lage"], 0) + 1
            ereignisse.append((t_, "AUSLOESER: keine Wirkung an %s %s bis Takt %d | Welle %d Mann, Zustaende %s" % (
                plan["art"], plan["ziel"], frist, len(welle), lage)))
            break
        spur.append((t_, phase, plan["art"], str(plan["ziel"]), lord["leben"], len(stuermer), len(welle)))

    befehl({"pause": True}, 0.3)
    erg = {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "takte": t_, "sekunden": round(time.time() - t_start), "ereignisse": ereignisse,
           "spur": spur[::10]}
    with open(AUS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(erg, ensure_ascii=False, default=str) + "\n")
    for e in ereignisse:
        print("  Takt %6d  %s" % e, flush=True)
    print("Takte %d" % t_, flush=True)


if __name__ == "__main__":
    main()
