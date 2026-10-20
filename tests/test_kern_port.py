"""B-145 (Entwurf): KernPort - bestaetigt erst die beobachtete Wirkung, lehnt bei Kern-Absage ab (offline)."""

import pytest

from selfaware.domain import Command, EntityRef, Intent, Session
from selfaware.game import kern_leitung as KL
from selfaware.game.kern_port import KernPort
from selfaware.game.ports import OutcomeStatus, ReceiptStatus


class FalscheLeitung:
    """Nachbau des gemeinsamen Speichers: Weltbilder der Reihe nach, Ring-Ergebnisse vorgegeben."""

    name = "SamurAI_Kern_1_A2"

    def __init__(self, bilder, ergebnis=1):
        self.bilder = list(bilder)
        self.auftraege = []
        self._ergebnis = ergebnis

    def lesen(self):
        return self.bilder[0] if len(self.bilder) == 1 else self.bilder.pop(0)

    def auftrag(self, art, nr, a=0, b=0):
        self.auftraege.append((art, nr, a, b))
        return len(self.auftraege) - 1

    def ergebnis(self, nummer):
        return self._ergebnis


def _bild(tick, gruppe, laufx, laufy):
    e = {
        "nr": 91,
        "leben": 28000,
        "besitzer": 1,
        "typ": 26,
        "x": 157,
        "y": 192,
        "zustand": 2,
        "laufx": laufx,
        "laufy": laufy,
        "gruppe": gruppe,
        "zielart": 0,
        "zieleinheit": 0,
        "zielgebaeude": 0,
        "nahziel": 0,
    }
    return KL.Weltbild(tick, 1, 1, 10, 0, 25, {91: e}, {})


def _intent():
    return Intent(
        "move-1",
        "test",
        Command("move", {"x": 163, "y": 192}),
        "s",
        99999,
        actors=(EntityRef("unit", 91, None),),
    )


def test_move_wird_erst_mit_sichtbarer_wirkung_bestaetigt():
    leitung = FalscheLeitung([_bild(100, 5, 157, 192), _bild(101, 5, 157, 192), _bild(102, 19, 163, 192)])
    port = KernPort(leitung)
    session = Session(5, 1, port.epoche_kennung())
    assert port.observe(session).snapshot.tick == 101
    r = port.submit(session, _intent())
    assert r.status == ReceiptStatus.DISPATCHED
    assert leitung.auftraege == [(KL.UEBERNEHMEN, 91, 0, 0), (KL.LAUF, 91, 163, 192)]
    o = port.observe(session)
    assert [(x.action_id, x.status) for x in o.outcomes] == [("move-1", OutcomeStatus.CONFIRMED)]


def test_ohne_wirkung_keine_bestaetigung_und_absage_wird_abgelehnt():
    leitung = FalscheLeitung([_bild(100, 5, 157, 192), _bild(101, 5, 157, 192), _bild(102, 5, 157, 192)])
    port = KernPort(leitung)
    session = Session(5, 1, port.epoche_kennung())
    port.observe(session)
    port.submit(session, _intent())
    assert port.observe(session).outcomes == ()
    abgesagt = KernPort(FalscheLeitung([_bild(100, 5, 157, 192)], ergebnis=-4))
    s2 = Session(5, 1, abgesagt.epoche_kennung())
    abgesagt.observe(s2)
    abgesagt.submit(s2, _intent())
    assert [x.status for x in abgesagt.observe(s2).outcomes] == [OutcomeStatus.REJECTED]


def test_fremde_epoche_wird_nicht_beobachtet():
    port = KernPort(FalscheLeitung([_bild(100, 5, 157, 192)]))
    with pytest.raises(ValueError):
        port.observe(Session(5, 1, "andere-epoche"))
