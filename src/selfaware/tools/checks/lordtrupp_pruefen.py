# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer den gemeinsamen Lord-Angriff mit Bedarf aus gemessenen Lagen (Daniel 05.10. 23:51: ausser
Schussweite sammeln, dann gleichzeitig; 06.10.: nicht pauschal 40 sammeln, kleinste ausreichend sichere Truppe, nicht auf
Nachzuegler warten, unbekannte Lage nur vorlaeufig). Vorher festgelegt, was gelten muss:
  1. keine gemessene Lage -> Bedarf VORLAEUFIG (Ersatzwert, so gemeldet); 19 lebende raiden; 20 sammeln schon (Schutz
     vor Verlusten beim Raiden - sonst leben nie 40 gleichzeitig, bedarf_partie_1), greifen aber nicht an
  2. gemessene Lage deckt -> Bedarf belegt (19); 18 lebende raiden, 19 sammeln ausser Schussweite, kein Lord-Befehl
  3. Neue schliessen sich der Sammlung an; solange weniger als der Bedarf angekommen ist, greift niemand an
  4. 19 angekommen, 6 noch unterwegs -> EIN Befehl mit genau den 19 gesuendesten; die 6 werden nicht abgewartet und
     gehoeren nicht zum Angriff (sie raiden wieder)
  5. angeschlagene zaehlen nicht wie volle: 19 angekommen, einer davon halb (zusammen weniger Leben als die gemessene
     Gruppe) -> kein Angriff; kommt ein 20. voller an -> Angriff mit den 19 vollen, ohne den angeschlagenen
  6. Lage nicht gedeckt (ein Bogenschuetze mehr am Lord) -> VORLAEUFIG, 25 angekommen reichen dann nicht
  7. Trainingsstand (angriff_aus) -> nie ein Lord-Befehl
  8. waehrend des Angriffs kein Gebaeude-Ziel fuer Angreifer; Abgelenkte in der naechsten Runde neu auf den Lord
  9. Messung: am Lord gezaehlt, Ablenkung nach Einheitentyp
 10. weniger als LORD_REST uebrig -> vorbei; neue Sammlung erst wieder ab dem Bedarf
Aufruf: uv run python -m selfaware.tools.checks.lordtrupp_pruefen [HEAD | andere_assassinen.py]   (Rueckgabe 0 = gruen)
"""

from selfaware import workspace as _workspace
import importlib.util, os, subprocess, sys, types
HIER = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) > 1 and sys.argv[1] == "HEAD":       # rote Gegenprobe gegen den eingecheckten Stand
    quelle = subprocess.check_output(["git", "-C", _workspace.ROOT, "show", "HEAD:src/selfaware/micro/tasks/assassinen.py"], text=True)
    A = types.ModuleType("assassinen_alt")
    A.__file__ = _workspace.module_file("assassinen")
    exec(compile(quelle, "HEAD:src/selfaware/micro/tasks/assassinen.py", "exec"), A.__dict__)
elif len(sys.argv) > 1:
    spec = importlib.util.spec_from_file_location("assassinen", sys.argv[1])
    A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
else:
    import selfaware.micro.tasks.assassinen as A
import selfaware.services.bedrohung as B

HEIM, LORD = (141, 269), (230, 287)
ORTE = [(94, 280), HEIM]
VOLL = 12500


def einheit(typ, besitzer, x, y, leben=VOLL, **k):
    e = {"typ": typ, "besitzer": besitzer, "x": x, "y": y, "leben": leben, "zustand": 0, "zielart": 0, "zieleinheit": 0,
         "zieluid": 0, "zielgebaeude": 0, "ziel": 0, "zielx": 0, "ziely": 0, "laufx": x, "laufy": y, "auswahlvon": 0,
         "auswahlmarke": 0, "gruppe": 0, "gruppenuid": 0, "ladung": 0, "arbeitsplatz": 0, "erreichbar": 1}
    e.update(k)
    return e


def lord_befehle(bef):
    return [b for b in bef if b.get("angriff", {}).get("ziel") == 500]


def sammel_befehle(bef):
    return [b for b in bef if b.get("halten", {}).get("nr")]


def grundlage():
    L = {500: einheit(55, 2, *LORD, leben=150000), 600: einheit(22, 2, LORD[0] + 2, LORD[1]), 601: einheit(24, 2, 232, 289)}
    G = {900: {"besitzer": 2, "typ": 32, "x": 190, "y": 250, "leben": 500, "uid": 1, "erreichbar": 1}}
    return L, G


def neuer_trupp(lagen):
    t = A.Einzeln(1, pruefe_begehbar=lambda pkt: set(pkt), wegtest=lambda n, p: [True] * len(p))
    t.lagen = lagen
    return t


def assassinen(L, nummern, x=150, y=260, leben=VOLL):
    for i, n in enumerate(nummern):
        L[n] = einheit(73, 1, x + 3 * (i % 7), y + 4 * (i // 7), leben=leben)


def an_den_punkt(L, nummern, punkt):
    for n in nummern:
        L[n].update(x=punkt[0], y=punkt[1], laufx=punkt[0], laufy=punkt[1])


def main():
    ok = []
    def pruefe(nr, text, bed):
        ok.append(bool(bed)); print("%-4s %2d %s" % ("OK" if bed else "ROT", nr, text))
    L0, G = grundlage()
    gemessen = {"name": "Testlage", "mindest": 19, "gruppe_leben": 19 * VOLL, "beleg": "test",
                "fingerabdruck": B.fingerabdruck(L0, G)}
    # 1. keine gemessene Lage
    L, _ = grundlage()
    t = neuer_trupp([])
    assassinen(L, range(100, 119))
    t.aufnehmen(range(100, 119))
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    vorl = any("LORD-BEDARF" in e and "VORLAEUFIG" in e for e in erg) and t.lordtrupp.get("phase") is None
    assassinen(L, [119])
    t.aufnehmen([119])
    t.schritt(L, G, sichere_orte=ORTE)
    an_den_punkt(L, range(100, 120), t.lordtrupp.get("sammelpunkt") or HEIM)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(1, "keine Lage -> VORLAEUFIG %d gemeldet; 19 raiden, 20 sammeln, 20 am Treffpunkt greifen nicht an" % B.VORLAEUFIG,
           vorl and t.lordtrupp.get("phase") == "sammeln" and not lord_befehle(bef))
    # 2. gemessene Lage deckt: 18 raiden, 19 sammeln
    L, _ = grundlage()
    t = neuer_trupp([gemessen])
    assassinen(L, range(100, 118))
    t.aufnehmen(range(100, 118))
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    belegt_gemeldet = any("LORD-BEDARF: 19 belegt" in e for e in erg)
    kein_sammeln_18 = t.lordtrupp.get("phase") is None
    assassinen(L, [118], x=120, y=300)
    t.aufnehmen([118])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    punkt = t.lordtrupp.get("sammelpunkt")
    pruefe(2, "Lage gedeckt -> 19 belegt; 18 raiden, 19 sammeln ausser Schussweite, kein Lord-Befehl",
           belegt_gemeldet and kein_sammeln_18 and sammel_befehle(bef) and punkt is not None
           and A.schach(punkt, LORD) > A.SCHUSSWEITE and not lord_befehle(bef))
    # 3. sechs Neue kommen dazu, noch niemand angekommen
    assassinen(L, range(119, 125), x=110, y=310)
    t.aufnehmen(range(119, 125))
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(3, "25 in der Sammlung, 0 angekommen -> niemand greift an",
           set(t.lordtrupp["mitglieder"]) == set(range(100, 125)) and not lord_befehle(bef))
    # 4. 19 angekommen, 6 unterwegs -> genau die 19
    sammelort = punkt or HEIM
    an_den_punkt(L, range(100, 119), sammelort)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    lb = lord_befehle(bef)
    pruefe(4, "19 angekommen, 6 unterwegs -> EIN Befehl mit genau den 19; die 6 nicht im Angriff",
           len(lb) == 1 and lb[0]["angriff"]["einheiten"] == list(range(100, 119))
           and not set(range(119, 125)) & set(t.lordtrupp["mitglieder"]))
    angriffs_trupp, L_angriff = t, L
    # 5. angeschlagene zaehlen nicht wie volle
    L, _ = grundlage()
    t = neuer_trupp([gemessen])
    assassinen(L, range(100, 119))
    L[100]["leben"] = VOLL // 2
    t.aufnehmen(range(100, 119))
    t.schritt(L, G, sichere_orte=ORTE)
    p5 = t.lordtrupp.get("sammelpunkt") or HEIM
    an_den_punkt(L, range(100, 119), p5)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    kein_angriff = not lord_befehle(bef)
    assassinen(L, [119])
    an_den_punkt(L, [119], p5)
    t.aufnehmen([119])
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    lb = lord_befehle(bef)
    pruefe(5, "19 angekommen, einer halb -> kein Angriff; ein 20. voller -> Angriff mit den 19 vollen ohne ihn",
           kein_angriff and len(lb) == 1 and lb[0]["angriff"]["einheiten"] == list(range(101, 120)))
    # 6. Lage nicht gedeckt: ein Bogenschuetze mehr am Lord
    L, _ = grundlage()
    L[602] = einheit(22, 2, LORD[0] - 3, LORD[1] + 1)
    t = neuer_trupp([gemessen])
    assassinen(L, range(100, 125))
    t.aufnehmen(range(100, 125))
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    vorl = any("VORLAEUFIG" in e and "15:22" in e for e in erg)
    p6 = t.lordtrupp.get("sammelpunkt") or HEIM
    an_den_punkt(L, range(100, 125), p6)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(6, "ein Bogenschuetze mehr -> VORLAEUFIG (Grund 15:22); 25 angekommen greifen nicht an", vorl and not lord_befehle(bef))
    # 7. Trainingsstand
    L, _ = grundlage()
    t = neuer_trupp([gemessen])
    t.angriff_aus = True
    assassinen(L, range(100, 125))
    t.aufnehmen(range(100, 125))
    t.schritt(L, G, sichere_orte=ORTE)
    an_den_punkt(L, range(100, 125), t.lordtrupp.get("sammelpunkt") or HEIM)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(7, "Trainingsstand -> kein Lord-Befehl trotz 25 am Treffpunkt", not lord_befehle(bef))
    # 8./9. Angriff laeuft (Trupp aus Fall 4)
    t, L = angriffs_trupp, L_angriff
    alle = list(range(100, 119))
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    raid_auf_angreifer = [b for b in bef if b.get("angriff", {}).get("gebaeude") and set(b["angriff"].get("einheiten", [])) & set(alle)]
    for n in alle[:5]:
        L[n].update(x=LORD[0] + 1, y=LORD[1], zielart=4, zieleinheit=500)
    for n in alle[5:8]:
        L[n].update(zielart=4, zieleinheit=601)
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    lb = lord_befehle(bef)
    pruefe(8, "kein Gebaeude-Ziel fuer Angreifer; Abgelenkte in der naechsten Runde neu auf den Lord",
           not raid_auf_angreifer and lb and set(alle[5:8]) <= set(lb[0]["angriff"]["einheiten"]))
    a = t.angriffe[-1] if getattr(t, "angriffe", None) else {}
    pruefe(9, "Messung: am Lord %s (soll 5), abgelenkt %s (soll Typ 24: 3), Bedarf im Protokoll %s" % (
           a.get("am_lord_max"), a.get("anderes"), a.get("bedarf")),
           a.get("am_lord_max") == 5 and a.get("anderes", {}).get(24) == 3 and a.get("bedarf") == 19)
    # 10. nur 2 ueberleben -> vorbei; mit 18 lebenden keine neue Sammlung
    for n in alle[2:]:
        del L[n]
    for n in range(119, 125):
        del L[n]
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    vorbei = not t.lordtrupp["mitglieder"]
    assassinen(L, range(300, 316))
    t.aufnehmen(range(300, 316))                                   # 2 alte + 16 neue = 18
    erg, bef = t.schritt(L, G, sichere_orte=ORTE)
    pruefe(10, "unter %d uebrig -> vorbei; mit 18 lebenden keine neue Sammlung" % getattr(A.Einzeln, "LORD_REST", 3),
           vorbei and not lord_befehle(bef) and t.lordtrupp.get("phase") is None)
    print("\n%d von %d gruen" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
