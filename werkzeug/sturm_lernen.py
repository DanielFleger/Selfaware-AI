# -*- coding: utf-8 -*-
"""B-167 Lernkreis fuer den Sturm (Daniel 22.10.2026 01:24: "das Wichtigste ist, dass nichts davon hart codiert ist, sondern die
KI selbst draufkommt"). Ein Aufruf = EIN Lauf:
  1. daten/sturm_lernen.jsonl lesen (je Lauf: Wahl der Stellschrauben + Ergebnis)
  2. beste bekannte Wahl = Lord tot in den wenigsten Takten (bei Gleichstand weniger eigene Tote)
  3. naechster Versuch = die beste Wahl mit GENAU EINER Schraube anders - die erste Abwandlung, die noch nie lief
     (alle schon gelaufen: die beste Wahl noch einmal, als Wiederholung zur Absicherung); die Basis selbst wird zuerst mit dem
     jetzigen Code gemessen, wenn sie nur historisch bekannt ist
  4. sturm.main(wahl) laufen lassen, Ergebnis anhaengen
Historische Laeufe (vor dem Lernkreis, mit anderem Code dazwischen) stehen mit "historisch": true drin - sie zaehlen fuer die
Startwahl, eine Abwandlung gegen sie wird trotzdem neu gemessen.
Aufruf: SHC_INSTANZ=5 python werkzeug/sturm_lernen.py            (waehlt selbst)
        SHC_INSTANZ=5 python werkzeug/sturm_lernen.py zeigen     (nur anzeigen, was er als Naechstes probieren wuerde)
"""
import json
import os
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
DATEI = os.path.join(HIER, "..", "daten", "sturm_lernen.jsonl")

# Laeufe der Nacht 21./22.10. (sturm.jsonl, Wissensregister L157) - Wahl so, wie der Code damals entschied
HISTORISCH = [
    {"zeit": "2026-10-22 00:54", "wahl": {"lord": "einzeln", "tor": "einzeln", "losgehen": "alle", "jaeger": "liste", "wegweiser": "aus"},
     "takte": 6099, "lord_tot": True, "tote": None, "rueckwaerts": None, "historisch": True},
    {"zeit": "2026-10-22 01:00", "wahl": {"lord": "gruppe", "tor": "gruppe", "losgehen": "alle", "jaeger": "liste", "wegweiser": "aus"},
     "takte": 4876, "lord_tot": False, "tote": None, "rueckwaerts": None, "historisch": True},
    {"zeit": "2026-10-22 01:03", "wahl": {"lord": "gruppe", "tor": "einzeln", "losgehen": "alle", "jaeger": "liste", "wegweiser": "aus"},
     "takte": 6111, "lord_tot": True, "tote": None, "rueckwaerts": None, "historisch": True},
    {"zeit": "2026-10-22 01:16", "wahl": {"lord": "gruppe", "tor": "einzeln", "losgehen": "bedarf", "jaeger": "liste", "wegweiser": "aus"},
     "takte": 4197, "lord_tot": False, "tote": None, "rueckwaerts": 94, "historisch": True},
    {"zeit": "2026-10-22 01:19", "wahl": {"lord": "einzeln", "tor": "einzeln", "losgehen": "alle", "jaeger": "liste", "wegweiser": "aus"},
     "takte": 5967, "lord_tot": True, "tote": None, "rueckwaerts": 66, "historisch": True},
    {"zeit": "2026-10-22 01:22", "wahl": {"lord": "kette", "tor": "einzeln", "losgehen": "alle", "jaeger": "liste", "wegweiser": "an"},
     "takte": 6980, "lord_tot": True, "tote": None, "rueckwaerts": 213, "historisch": True},
]


def lesen():
    if not os.path.exists(DATEI):
        with open(DATEI, "w", encoding="utf-8") as fh:
            for z in HISTORISCH:
                fh.write(json.dumps(z, ensure_ascii=False) + "\n")
    return [json.loads(z) for z in open(DATEI, encoding="utf-8") if z.strip()]


def schluessel(wahl):
    from sturm import STELLSCHRAUBEN
    return tuple(wahl.get(k) for k in sorted(STELLSCHRAUBEN))


def kosten(z):
    """Bewertung eines Laufs (Daniel 01:28: auch Tote und Zuruecklaufen zaehlen): Takte bis Lord tot + Tote x gemessene Takte je
    Angeworbenem in diesem Lauf (so lange dauert es, einen Toten zu ersetzen); Rueckwaerts-Meldungen nur bei Gleichstand."""
    je_rekrut = z.get("takte_je_rekrut") or 0
    return (z["takte"] + (z.get("tote") or 0) * je_rekrut, z.get("rueckwaerts") or 0)


def beste(laeufe):
    jetzt_ = [z for z in laeufe if not z.get("historisch")]
    sieg = [z for z in (jetzt_ if any(z.get("lord_tot") for z in jetzt_) else laeufe) if z.get("lord_tot")]
    if not sieg:
        return None
    return min(sieg, key=kosten)


def naechste_wahl(laeufe):
    from sturm import STANDARD, STELLSCHRAUBEN
    b = beste(laeufe)
    basis = dict(STANDARD, **(b["wahl"] if b else {}))
    # Werte, die es als Schraube nicht (mehr) gibt (historisch "liste" bei den Jaegern), durch den Standard ersetzen
    basis = {k: (v if v in STELLSCHRAUBEN.get(k, []) else STANDARD[k]) for k, v in basis.items() if k in STELLSCHRAUBEN}
    gemessen = {schluessel(z["wahl"]) for z in laeufe if not z.get("historisch")}
    if schluessel(basis) not in gemessen:
        # die Basis selbst zuerst mit dem JETZIGEN Code messen - historische Werte stammen aus anderem Code, ein Vergleich gegen sie
        # waere nicht sauber
        return basis, "Basis neu messen (bester historischer Lauf %s, %s Takte - mit anderem Code)" % (
            b["zeit"] if b else "-", b["takte"] if b else "-")
    for k in sorted(STELLSCHRAUBEN):
        for v in STELLSCHRAUBEN[k]:
            if v != basis[k]:
                w = dict(basis, **{k: v})
                if schluessel(w) not in gemessen:
                    return w, "Abwandlung %s: %s -> %s (Basis: bester Lauf %s, %s Takte)" % (
                        k, basis[k], v, b["zeit"] if b else "-", b["takte"] if b else "-")
    return basis, "alle Abwandlungen gemessen - Wiederholung der besten Wahl"


def main():
    laeufe = lesen()
    wahl, grund = naechste_wahl(laeufe)
    print("LERNEN: %d Laeufe bekannt, bester %s | naechster Versuch %s - %s" % (
        len(laeufe), (beste(laeufe) or {}).get("wahl"), wahl, grund), flush=True)
    if "zeigen" in sys.argv[1:]:
        return
    import sturm
    erg = sturm.main(wahl)
    erg.update({"zeit": time.strftime("%Y-%m-%d %H:%M"), "grund": grund})
    erg["takte_je_rekrut"] = round(erg["takte"] / float(erg["angeworben"]), 1) if erg.get("angeworben") else None
    with open(DATEI, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(erg, ensure_ascii=False, default=str) + "\n")
    b = beste(lesen())
    print("ERGEBNIS: Lord %s nach %d Takten, %s Tote, %s Rueckwaerts | bester bisher: %s Takte mit %s" % (
        "tot" if erg["lord_tot"] else "lebt", erg["takte"], erg["tote"], erg["rueckwaerts"],
        b["takte"] if b else "-", b["wahl"] if b else "-"), flush=True)


if __name__ == "__main__":
    main()
