"""B-145: die Auswertung der Beschusswache zaehlt jede Art richtig (offline)."""

from selfaware.tools.experiments.kern_beschuss_auswerten import auswerten

ZEILEN = [
    "beschuss tick 100: STEHT NUR - Einheit 86 (Typ 73, Zustand 1, Zielart 0, Nahziel 0) bei (212,156) "
    "steht seit 3867 Takten und verliert Leben (11300) [Fenster 100 / still 100]",
    "beschuss tick 120: KAEMPFT - Einheit 85 (Typ 70, Zustand 106, Zielart 3, Nahziel 681) bei (158,192) "
    "steht seit 400 Takten und verliert Leben (14895) [Fenster 100 / still 100]",
    "beschuss tick 130: Einheit 85 - Ende",
    "waechter tick 500 version 15",
]


def test_arten_werden_getrennt_gezaehlt():
    f = auswerten(ZEILEN)
    assert f["STEHT NUR"] == [(100, 86, 73, 3867)]
    assert f["KAEMPFT"] == [(120, 85, 70, 400)]
    assert "HAT ZIEL" not in f
