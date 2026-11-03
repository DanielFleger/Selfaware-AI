# -*- coding: utf-8 -*-
"""B-142: Fasst einen Lauf F oder K zusammen: Gesamtproben aus den Aufzeichnungen, Beleg je Einzelpunkt, Funde und Abbruch aus dem Protokoll.

Aufruf: python -m selfaware.tools.analysis.auge_ergebnis data/research/auge_plan/laeufe/lauf_f_<stempel>
        python -m selfaware.tools.analysis.auge_ergebnis data/research/auge_plan/laeufe/lauf_k_<stempel> --lauf K --lauf-f data/research/auge_plan/laeufe/lauf_f_<stempel> --prozesse 8
Was der Lauf wirklich gesehen hat, steht im Bericht <basis>_Ergebnis.md, die Belege in <basis>.ergebnis.json und <basis>.punkte.json. Fertige Proben von Lauf K liegen in <basis>.proben.
"""
import argparse
import concurrent.futures
import json
import os
import pickle
import re
import time

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis import auge_punkte


def protokoll_lesen(basis):
    pfad = basis + ".protokoll.jsonl"
    if not os.path.exists(pfad):
        return []
    with open(pfad, encoding="utf-8") as f:
        return [json.loads(z) for z in f if z.strip()]


def auswerten(basis, gueltig=None):
    """Rueckgabe: Pfad des Berichts. Fehlt eine Aufzeichnung, heisst die Probe "nicht gesehen", der Bericht entsteht trotzdem."""
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    karte = Feldkarte.laden(feldliste=FELDLISTE)
    haupt = aw.Aufzeichnung(basis + ".auge") if os.path.exists(basis + ".auge") else None
    jahr = aw.Aufzeichnung(basis + "_jahr40.auge") if os.path.exists(basis + "_jahr40.auge") else None
    prot = protokoll_lesen(basis)
    aus = []

    if haupt or jahr:
        gesehen = []
        for auf in filter(None, (haupt, jahr)):
            e = aw.a1_aenderungsmelder(auf, karte)
            aus.append(e)
            gesehen += e.daten["gesehen"]
        aus.append(aw.a2_nie_gesehen(karte, gesehen))
    if haupt:
        aus += [aw.a3_takttreue(haupt), aw.a4_lesedauer(haupt)]
        if jahr:
            aus.append(aw.a9_befehle(haupt))  # die eigenen Befehle laufen im Hauptteil, im Jahr auf Tempo 40 kommt keiner
    fein = jahr or haupt
    if jahr:
        aus += [aw.a3_takttreue(jahr), aw.a4_lesedauer(jahr)]
    treppe = next((z["daten"] for z in prot if z.get("abschnitt") == "treppe" and "daten" in z), None)
    if treppe:
        aus.append(aw.a4_tempotreppe(treppe.get("zeilen") or []))
    if fein:
        aus += [aw.a7_zufall(fein), aw.a8_buchfuehrung(fein, karte), aw.a9_befehle(fein), aw.a10_lebenslauf(fein, aw.echte_listen(karte), aw.echte_grenzen(karte)),
                aw.a12_fluechtig(fein, aw.echte_merker(karte))]
    if haupt:
        aus.append(aw.a13_spielart({"F": haupt}))

    punkte = None
    from selfaware import workspace

    checkliste = os.path.join(workspace.DATA, "auge_plan", "Checkliste_Auge.md")
    aufz = [a for a in (haupt, jahr) if a]
    if aufz and os.path.exists(checkliste):
        punkte = auge_punkte.auswerten(checkliste, aufz, karte)
        auge_punkte.schreiben(punkte, basis + ".punkte.json")

    with open(basis + ".ergebnis.json", "w", encoding="utf-8") as f:
        json.dump({"gueltig": gueltig, "proben": [e.__dict__ for e in aus]}, f, ensure_ascii=False, indent=0, default=str)

    funde = [z for z in prot if z.get("wirkung") and not z.get("ok")]
    abbruch = next((z["grund"] for z in prot if z.get("schritt") == "abbruch"), None)
    z = ["# Ergebnis Lauf F", "", f"Basis: `{os.path.basename(basis)}`", ""]
    if abbruch:
        z += [f"**Abgebrochen:** {abbruch}", ""]
    elif gueltig and gueltig.get("gueltig"):
        z += ["**Der Lauf ist gültig:** Er konnte die Frage beantworten. Widerlegte Punkte sind Funde, kein Scheitern.", ""]
    elif gueltig is not None:
        z += [f"**Der Lauf ist nicht gültig:** {json.dumps({k: v for k, v in gueltig.items() if k != 'funde'}, ensure_ascii=False, default=str)}", ""]
    z += ["## Gesamtproben", "", aw.bericht(aus)]
    z += ["## Abschnitte", "", "| Abschnitt | Takte | Sekunden | Takte je Sekunde |", "|---|---|---|---|"]
    for e in prot:
        if "takt_bis" in e:
            z.append(f"| {e['abschnitt']} | {e['takt_bis'] - e['takt_von']} | {e['sekunden']} | {e['takte_je_s']} |")
    z += ["", "## Schaltungen ohne Wirkung", ""]
    z += [f"- {x['wirkung']}: {json.dumps({k: v for k, v in x.items() if k not in ('wirkung', 'ok')}, ensure_ascii=False, default=str)}" for x in funde] or ["keine"]
    if punkte:
        z += ["", "## Einzelpunkte", "", auge_punkte.bericht(punkte)]
    pfad = basis + "_Ergebnis.md"
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("\n".join(z) + "\n")
    return pfad


ENDUNGEN_K = {"haupt": ".auge", "t1": "_t1.auge", "danach": "_danach.auge", "t2": "_t2.auge", "t3": "_t3.auge", "t4": "_t4.auge", "t5": "_t5.auge", "t6": "_t6.auge", "t7": "_t7.auge", "t8": "_t8.auge", "t9": "_t9.auge"}


def aufgaben_k(da, prot):
    """Die Proben von Lauf K in der Reihenfolge des Berichts: (Art, Zusatz, Argumente). da: die vorhandenen Aufzeichnungen.
    haupt Friedenszeit, t1 jeder Takt, danach Kampf, t2 und t3 zweimal geladen, t4 und t5 mit gleichem Zaehler, t6 bis t9 dasselbe im Kampf (a6_festgelegt.py)."""
    aus = [("A1", k, (k,)) for k in da] + [("A3", k, (k,)) for k in da]
    t = next((z["daten"]["t"] for z in prot if z.get("abschnitt") == "sichern" and "daten" in z), None)
    takte = next((z["daten"]["t1"]["bis"] - z["daten"]["t1"]["von"] for z in prot if z.get("abschnitt") == "sichern" and "daten" in z), 0)
    if t is not None and {"t1", "t2", "t3"} <= set(da):
        aus += [("A5", "gespeichert gegen geladen", ("t1", t, "t2", t)), ("A5", "zweimal geladen", ("t2", t, "t3", t)),
                ("gleich", "ohne Laden gegen geladen, ein Takt versetzt", ("t1", t + 1, "t2", t, takte - 1)), ("gleich", "zweimal geladen", ("t2", t, "t3", t, takte))]
        for a, b, zu in (("t4", "t5", "zweimal geladen, Zaehler gleich gesetzt"), ("t6", "t7", "im Kampf, Zaehler gleich gesetzt"), ("t8", "t9", "im Kampf, Zaehler und Geschosszeiger gleich gesetzt")):
            if {a, b} <= set(da):
                aus.append(("gleich", zu, (a, None, b, None, takte)))
    fein = "t1" if "t1" in da else ("haupt" if "haupt" in da else None)
    if fein:
        aus.append(("A7", "t1", (fein,)))
    aus += [("A9", k, (k,)) for k in ("haupt", "danach") if k in da]
    aus += [("A10", k, (k,)) for k in ("t1", "danach") if k in da]
    if "haupt" in da:
        aus += [("A11", "", ("haupt",)), ("A13", "", ("haupt",))]
    if fein:
        aus.append(("A12", "t1", (fein,)))
    return aus + [("Punkte", "K", ()), ("Punkte", "F", ())]


def _rechne_k(basis, lauf_f, art, zu, arg):
    from selfaware import workspace
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    karte = Feldkarte.laden(feldliste=FELDLISTE)

    def auf(k):
        return aw.Aufzeichnung(basis + ENDUNGEN_K[k])

    if art == "Punkte":
        checkliste = os.path.join(workspace.DATA, "auge_plan", "Checkliste_Auge.md")
        return auge_punkte.auswerten(checkliste, [auf(k) for k in ("haupt", "t1", "danach") if os.path.exists(basis + ENDUNGEN_K[k])], karte, lauf=zu)
    if art == "gleich":
        k1, t1, k2, t2, takte = arg
        a1, a2 = auf(k1), auf(k2)
        t1 = next(a1.rahmen()).takt if t1 is None else t1  # die Fenster aus a6_festgelegt.py beginnen beide am geladenen Takt
        t2 = next(a2.rahmen()).takt if t2 is None else t2
        e = aw.spielstand_gleich(a1, t1, a2, t2, takte, karte)
    elif art == "A1":
        e = aw.a1_aenderungsmelder(auf(arg[0]), karte)
    elif art == "A3":
        e = aw.a3_takttreue(auf(arg[0]))
    elif art == "A5":
        e = aw.a5_laden_gleich_sichern(auf(arg[0]), arg[1], auf(arg[2]), arg[3], karte)
    elif art == "A7":
        e = aw.a7_zufall(auf(arg[0]))
    elif art == "A9":
        e = aw.a9_befehle(auf(arg[0]))
    elif art == "A10":
        e = aw.a10_lebenslauf(auf(arg[0]), aw.echte_listen(karte), aw.echte_grenzen(karte))
    elif art == "A11":
        e = aw.a11_pruefsummen(auf(arg[0]), karte)
    elif art == "A12":
        e = aw.a12_fluechtig(auf(arg[0]), aw.echte_merker(karte))
    elif art == "A13":
        vergleich = {"K": auf(arg[0])}
        if lauf_f and os.path.exists(lauf_f + ".auge"):
            vergleich["F"] = aw.Aufzeichnung(lauf_f + ".auge")
        e = aw.a13_spielart(vergleich)
    else:
        raise ValueError(art)
    e.nr = f"{e.nr} {zu}" if zu else e.nr
    return e


def probe_k(basis, lauf_f, aufgabe, ordner=None):
    """Eine Probe, auch in einem eigenen Prozess. Fertige Proben liegen in ordner: Eine abgebrochene Auswertung rechnet sie nicht noch einmal."""
    art, zu, arg = aufgabe
    pfad = os.path.join(ordner, re.sub(r"[^A-Za-z0-9]+", "_", f"{art} {zu}").strip("_") + ".pkl") if ordner else None
    if pfad and os.path.exists(pfad):
        with open(pfad, "rb") as f:
            return pickle.load(f)
    start = time.time()
    e = _rechne_k(basis, lauf_f, art, zu, arg)
    if pfad:
        with open(pfad + ".neu", "wb") as f:
            pickle.dump(e, f)
        os.replace(pfad + ".neu", pfad)
    print(f"{art} {zu}: {getattr(e, 'status', 'fertig')} nach {time.time() - start:.0f} s", flush=True)
    return e


def auswerten_k(basis, lauf_f=None, prozesse=1):
    """Lauf K. prozesse: wie viele Proben gleichzeitig laufen; die Aufzeichnung des Kampfs hat 2 GB. Rueckgabe: Pfad des Berichts."""
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    karte = Feldkarte.laden(feldliste=FELDLISTE)
    prot = protokoll_lesen(basis)
    gueltig = next((z for z in prot if z.get("schritt") == "schluss"), None)
    da = [k for k, e in ENDUNGEN_K.items() if os.path.exists(basis + e)]
    aufgaben = aufgaben_k(da, prot)
    ordner = basis + ".proben"
    os.makedirs(ordner, exist_ok=True)
    if prozesse > 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=prozesse) as pool:
            fertig = list(pool.map(probe_k, *zip(*[(basis, lauf_f, a, ordner) for a in aufgaben])))
    else:
        fertig = [probe_k(basis, lauf_f, a, ordner) for a in aufgaben]
    aus, gesehen, punkte, spielart = [], [], None, None
    for a, e in zip(aufgaben, fertig):
        if a[0] == "Punkte":
            punkte, spielart = (e, spielart) if a[1] == "K" else (punkte, e)
            continue
        aus.append(e)
        if a[0] == "A1":
            gesehen += e.daten["gesehen"]
    a2 = aw.a2_nie_gesehen(karte, gesehen)
    a2.nr = f"{a2.nr} nur Lauf K"
    aus.insert(len(da), a2)
    auge_punkte.schreiben(punkte, basis + ".punkte.json")
    auge_punkte.schreiben({"punkte": [p for p in spielart["punkte"] if p["spielart"]], "zaehlung": {}}, basis + ".spielart.json")

    with open(basis + ".ergebnis.json", "w", encoding="utf-8") as f:
        json.dump({"gueltig": gueltig, "proben": [e.__dict__ for e in aus]}, f, ensure_ascii=False, indent=0, default=str)
    funde = [z for z in prot if z.get("wirkung") and not z.get("ok")]
    abbruch = next((z["grund"] for z in prot if z.get("schritt") == "abbruch"), None)
    z = ["# Ergebnis Lauf K", "", f"Basis: `{os.path.basename(basis)}`", ""]
    if abbruch:
        z += [f"**Abgebrochen:** {abbruch}", ""]
    z += ["## Gesamtproben", "", aw.bericht(aus), "## Abschnitte", "", "| Abschnitt | Takte | Sekunden | Takte je Sekunde |", "|---|---|---|---|"]
    z += [f"| {e['abschnitt']} | {e['takt_bis'] - e['takt_von']} | {e['sekunden']} | {e['takte_je_s']} |" for e in prot if "takt_bis" in e]
    z += ["", "## Schaltungen ohne Wirkung", ""]
    z += [f"- {x['wirkung']}: {json.dumps({k: v for k, v in x.items() if k not in ('wirkung', 'ok')}, ensure_ascii=False, default=str)}" for x in funde] or ["keine"]
    z += ["", "## Einzelpunkte", "", auge_punkte.bericht(punkte)]
    pfad = basis + "_Ergebnis.md"
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("\n".join(z) + "\n")
    return pfad


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("basis")
    p.add_argument("--lauf", default="F", choices=["F", "K"])
    p.add_argument("--lauf-f", help="Basis eines gueltigen Lauf F, fuer den Vergleich der Spielart")
    p.add_argument("--prozesse", type=int, default=1, help="Lauf K: Proben gleichzeitig; abgebrochene Auswertungen gehen weiter, wo sie standen")
    a = p.parse_args(argv)
    print(auswerten_k(a.basis, a.lauf_f, a.prozesse) if a.lauf == "K" else auswerten(a.basis))


if __name__ == "__main__":
    main()
