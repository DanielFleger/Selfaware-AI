"""B-187 (Daniel 15.11.2026 13:08): "der kornspeicher sollte dort stehen wo er maximal niedrige laufwege fuer die apfelplantagen
verursacht". Frueher stand er an der Mitte der FRUEHEN Apfelgruppe (Partie 34: (104,216), Summe zu allen 10 Plantagen 211 Felder)."""

import json
import os

from selfaware.macro import farmen_mischen
from selfaware.macro import nahrungswahl as N


def test_laufweg_summe_zaehlt_jede_plantage():
    # Speicher (13,13) -> Mitte (15,15); Plantagen (0,0),(0,40),(40,0) -> Mitten (5,5),(5,45),(45,5): 10 + 30 + 30
    assert N.apfel_laufweg((13, 13), [(0, 0), (0, 40), (40, 0)]) == 70


def test_speicherplatz_nimmt_den_kleinsten_laufweg_nicht_den_naechsten(monkeypatch):
    plaetze = [(13, 13), (3, 15), (18, 18)]  # Summen 70, 80, 65; naechst (5,5) waere (13,13)
    monkeypatch.setattr(farmen_mischen, "lies_karte", lambda pfad: plaetze)
    aepfel = [(0, 0), (0, 40), (40, 0)]
    assert N.speicherplatz("probe", (5, 5), [], aepfel) == (18, 18)
    assert N.speicherplatz("probe", (5, 5), []) == (13, 13), (
        "ohne Plantagen wie frueher: naechst dem Punkt"
    )


def test_partie_34_karte_kuerzerer_weg_zu_allen_plantagen():
    kurz = "Lobby_sp2_bf_146_272"  # SamurAIs Startplatz in Partie 34 (Battle Brother's Strife)
    plan = json.load(open(os.path.join(N.D, "eroeffnung_plan_%s.json" % kurz), encoding="utf-8"))
    w = N.waehle(kurz, plan)
    lw = w["begruendung"]["kornspeicher_laufweg_aepfel"]
    assert (
        lw["regel"] == "kleinste Summe zu allen Plantagen"
        and lw["plantagen"] == len(w["aepfel"]) == 10
    )
    assert lw["frueher_platz"] == [104, 216] and lw["frueher"] == 211
    assert lw["summe"] == N.apfel_laufweg(w["kornspeicher"], w["aepfel"]) < lw["frueher"]
