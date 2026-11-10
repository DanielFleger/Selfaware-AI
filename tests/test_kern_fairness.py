"""B-182 (10.11.2026): Der Rust-Kern fuehrt nie fremde Einheiten, und sein Auftragsbuch endet mit der Partie. Kern 24 setzte nach Partiewechseln
alte Auftraege an Einheiten ab, die die alten Nummern trugen, auch an gegnerische (Reihen 13 bis 16). Ohne Spiel."""

import pathlib

from selfaware.tools.checks import kern_fremde_befehle as KF

KERN = (pathlib.Path(__file__).resolve().parents[1] / "crates/samurai-kern/src/lib.rs").read_text(
    encoding="utf-8"
)


def test_kern_verweigert_fremde_einheiten_und_leert_das_buch_bei_neuer_partie():
    absetzen = KERN.index("match haende::absetzen(a, &einheiten, platz)")
    sperre = KERN.rindex("if platz != ich {", 0, absetzen)
    assert absetzen - sperre < 1200 and "ERG_FREMD" in KERN[sperre:absetzen]
    epoche = KERN.index("Ereignis::Epoche { von, nach } => {")
    assert (
        "z.buch.take()" in KERN[epoche : epoche + 2500]
        and "quittieren(i, haende::ERG_VERFALLEN)" in KERN[epoche : epoche + 2500]
    )


def test_pruefung_findet_befehle_an_fremde_spieler_je_partie():
    zeilen = [
        "haende tick 10: Gruppe 3, 1 von 1 Einheiten von Spieler 1, Auftrag Auftrag { art: 17, a: 5, b: 6 }, Vorrang 4 - abgesetzt",
        "epoche 2 tick 5 von 40000 (Sprung -39995)",
        "haende tick 20: Gruppe 4, 1 von 1 Einheiten von Spieler 2, Auftrag Auftrag { art: 4, a: 9, b: 0 }, Vorrang 3 - abgesetzt",
        "haende tick 21: VERWEIGERT - 1 Einheiten von Spieler 2, wir sind Spieler 1 (nie fremde Einheiten fuehren), Auftrag x verworfen",
    ]
    liste = KF.partien(zeilen)
    assert [dict(je) for _, je, _ in liste] == [{1: 1}, {2: 1}]
    assert [v for _, _, v in liste] == [0, 1]
