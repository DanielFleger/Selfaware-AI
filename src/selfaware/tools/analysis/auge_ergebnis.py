# -*- coding: utf-8 -*-
"""B-142: Fasst einen Lauf F oder K zusammen: Gesamtproben aus den Aufzeichnungen, Beleg je Einzelpunkt, Funde und Abbruch aus dem Protokoll.

Aufruf: python -m selfaware.tools.analysis.auge_ergebnis data/research/auge_plan/laeufe/lauf_f_<stempel>
        python -m selfaware.tools.analysis.auge_ergebnis data/research/auge_plan/laeufe/lauf_k_<stempel> --lauf K --lauf-f data/research/auge_plan/laeufe/lauf_f_<stempel>
Was der Lauf wirklich gesehen hat, steht im Bericht <basis>_Ergebnis.md, die Belege in <basis>.ergebnis.json und <basis>.punkte.json.
"""
import argparse
import json
import os

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


def auswerten_k(basis, lauf_f=None):
    """Lauf K: haupt (Friedenszeit), t1 (2.000 Takte, jeder Takt), danach (Kampf), t2 und t3 (zweimal geladen, jeder Takt), t4 und t5 (a6_festgelegt.py). Rueckgabe: Pfad des Berichts."""
    from selfaware import workspace
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    karte = Feldkarte.laden(feldliste=FELDLISTE)
    auf = {k: aw.Aufzeichnung(basis + e) for k, e in (("haupt", ".auge"), ("t1", "_t1.auge"), ("danach", "_danach.auge"), ("t2", "_t2.auge"), ("t3", "_t3.auge"), ("t4", "_t4.auge"), ("t5", "_t5.auge")) if os.path.exists(basis + e)}
    prot = protokoll_lesen(basis)
    gueltig = next((z for z in prot if z.get("schritt") == "schluss"), None)
    aus, gesehen = [], []

    def probe(e, zu=None):
        e.nr = f"{e.nr} {zu}" if zu else e.nr
        aus.append(e)
        return e

    for k, a in auf.items():
        gesehen += probe(aw.a1_aenderungsmelder(a, karte), k).daten["gesehen"]
    probe(aw.a2_nie_gesehen(karte, gesehen), "nur Lauf K")
    for k, a in auf.items():
        probe(aw.a3_takttreue(a), k)
    t = next((z["daten"]["t"] for z in prot if z.get("abschnitt") == "sichern" and "daten" in z), None)
    takte = next((z["daten"]["t1"]["bis"] - z["daten"]["t1"]["von"] for z in prot if z.get("abschnitt") == "sichern" and "daten" in z), 0)
    if t is not None and {"t1", "t2", "t3"} <= set(auf):
        probe(aw.a5_laden_gleich_sichern(auf["t1"], t, auf["t2"], t, karte), "gespeichert gegen geladen")
        probe(aw.a5_laden_gleich_sichern(auf["t2"], t, auf["t3"], t, karte), "zweimal geladen")
        probe(aw.spielstand_gleich(auf["t1"], t + 1, auf["t2"], t, takte - 1, karte), "ohne Laden gegen geladen, ein Takt versetzt")
        probe(aw.spielstand_gleich(auf["t2"], t, auf["t3"], t, takte, karte), "zweimal geladen")
        if {"t4", "t5"} <= set(auf):
            probe(aw.spielstand_gleich(auf["t4"], t, auf["t5"], t, takte, karte), "zweimal geladen, Zaehler gleich gesetzt")
    fein = auf.get("t1") or auf.get("haupt")
    if fein:
        probe(aw.a7_zufall(fein), "t1")
    for k in ("haupt", "danach"):
        if k in auf:
            probe(aw.a9_befehle(auf[k]), k)
    for k in ("t1", "danach"):
        if k in auf:
            probe(aw.a10_lebenslauf(auf[k], aw.echte_listen(karte), aw.echte_grenzen(karte)), k)
    if "haupt" in auf:
        probe(aw.a11_pruefsummen(auf["haupt"], karte))
        vergleich = {"K": auf["haupt"]}
        if lauf_f and os.path.exists(lauf_f + ".auge"):
            vergleich["F"] = aw.Aufzeichnung(lauf_f + ".auge")
        probe(aw.a13_spielart(vergleich))
    if fein:
        probe(aw.a12_fluechtig(fein, aw.echte_merker(karte)), "t1")

    checkliste = os.path.join(workspace.DATA, "auge_plan", "Checkliste_Auge.md")
    aufz = [auf[k] for k in ("haupt", "t1", "danach") if k in auf]
    punkte = auge_punkte.auswerten(checkliste, aufz, karte, lauf="K")
    auge_punkte.schreiben(punkte, basis + ".punkte.json")
    spielart = auge_punkte.auswerten(checkliste, aufz, karte, lauf="F")
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
    a = p.parse_args(argv)
    print(auswerten_k(a.basis, a.lauf_f) if a.lauf == "K" else auswerten(a.basis))


if __name__ == "__main__":
    main()
