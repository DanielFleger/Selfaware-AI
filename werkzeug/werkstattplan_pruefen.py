# -*- coding: utf-8 -*-
"""Kleine Gegenprobe fuer den Kartenausschnitt der gemeinsamen Waffenproduktion."""
import aufbau_planer as P


def karte(rahmen, lager=(90, 270)):
    x0, y0, x1, y1 = rahmen
    felder = {(x, y): (0xFF, 0, 0, 0, 0, -1)
              for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    felder[lager] = (0, 1, 0, 0, 0, P.LAGER)
    return {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "f": felder}


def pruefe():
    anker = (90, 268)
    ferner_hof = [(101, 200)]
    alter_rahmen = (55, 233, 125, 303)
    try:
        P.plane(karte(alter_rahmen), 1, 1, 1, ferner_hof)
    except RuntimeError as e:
        assert "kein Hoftor" in str(e)
    else:
        raise AssertionError("alter fehlerhafter Ausschnitt wurde nicht erkannt")

    neuer_rahmen = P.kartenrahmen(anker, ferner_hof)
    plan, _bericht = P.plane(karte(neuer_rahmen), 1, 1, 1, ferner_hof)
    assert [b[0] for b in plan.bauten] == [P.WAFFENLAGER, P.GERBEREI, P.SCHMIEDE]

    naher_hof = [(100, 250)]
    nah_plan, _bericht = P.plane(karte(P.kartenrahmen(anker, naher_hof)), 1, 1, 1, naher_hof)
    assert [b[0] for b in nah_plan.bauten] == [P.WAFFENLAGER, P.GERBEREI, P.SCHMIEDE]

    erster_plan, _bericht = P.plane(karte(neuer_rahmen), 1, 1, 1, ferner_hof)
    _art, x, y, _r, _e = erster_plan.bauten[0]
    sperre = (x, y, x + 3, y + 3)
    ersatzplan, _bericht = P.plane(karte(neuer_rahmen), 1, 1, 1, ferner_hof,
                                   ausgeschlossene_flaechen=[sperre])
    assert len(ersatzplan.bauten) == 3
    assert all(not (bx <= sperre[2] and bx + 3 >= sperre[0] and by <= sperre[3] and by + 3 >= sperre[1])
               for _art, bx, by, _r, _e in ersatzplan.bauten)

    ablehnungen = {}
    assert not P.platzablehnung_merken(ablehnungen, (90, 266), "rohstoff")
    assert not P.platzablehnung_merken(ablehnungen, (90, 266), "schutz")
    assert not P.platzablehnung_merken(ablehnungen, (90, 266), "platz")
    assert P.platzablehnung_merken(ablehnungen, (90, 266), "platz")
    print("Werkstattplan-Gegenprobe: 5/5 gruen")


if __name__ == "__main__":
    pruefe()
