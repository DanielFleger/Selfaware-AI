# -*- coding: utf-8 -*-
"""B-142: Fasst einen Lauf F zusammen: Gesamtproben aus den Aufzeichnungen, Beleg je Einzelpunkt, Funde und Abbruch aus dem Protokoll.

Aufruf: python -m selfaware.tools.analysis.auge_ergebnis data/research/auge_plan/laeufe/lauf_f_<stempel>
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


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("basis")
    a = p.parse_args(argv)
    print(auswerten(a.basis))


if __name__ == "__main__":
    main()
