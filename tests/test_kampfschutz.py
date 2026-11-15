"""B-182 S118 (Daniel 13.11.: "Ja, abstellen"): no second attack order to a melee unit that already fights that target."""

import os

from selfaware.execution import kampfschutz as K

QUELLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "selfaware")


def _e(zustand, ziel=0, nah=0):
    return {"zustand": zustand, "zieleinheit": ziel, "nahziel": nah}


def test_a_fighting_unit_is_taken_out_and_the_rest_goes_out():
    K.stand({5: _e(106, 40), 6: _e(101, 40), 7: _e(106, 0, 40), 8: _e(106, 41), 9: _e(5, 40)})
    paket, meld = K.filtern({"befehle": [{"angriff": {"einheiten": [5, 6, 7, 8, 9], "ziel": 40}}]})
    assert paket == {
        "befehle": [{"angriff": {"einheiten": [6, 8, 9], "ziel": 40}}]
    }  # walking, other target, shooter stay
    assert len(meld) == 1 and "KAMPFSCHUTZ: 5,7 kaempfen schon gegen U40" in meld[0]


def test_nothing_left_and_other_orders_pass():
    K.stand({5: _e(106, 40)})
    assert K.filtern({"angriff": {"einheiten": [5], "ziel": 40}})[0] is None
    assert K.filtern({"befehle": [{"angriff": {"einheiten": [5], "ziel": 40}}]})[0] is None
    for c in (
        {"angriff": {"einheiten": [5], "ziel": 41}},
        {"angriff": {"einheiten": [5], "gebaeude": 40}},  # no building 40
        {"angriff": {"einheiten": [5], "lauf": [10, 10]}},
        {"halten": {"nr": [5], "x": 1, "y": 1}},
    ):
        assert K.filtern(c) == (c, [])
    liste, meld = K.liste(
        [{"angriff": {"einheiten": [5], "ziel": 40}}, {"angriff": {"einheiten": [5], "ziel": 41}}]
    )
    assert liste == [{"angriff": {"einheiten": [5], "ziel": 41}}] and len(meld) == 1


def test_the_guard_sits_on_both_order_ways_and_the_lenker_feeds_it():
    with open(os.path.join(QUELLE, "game", "ucp", "befehl.py"), encoding="utf-8") as f:
        t = f.read()
    assert (
        t.index("lordschutz.filtern(befehl)")
        < t.index("kampfschutz.filtern(befehl)")
        < t.index("for beobachter in BEOBACHTER:")
    )
    with open(os.path.join(QUELLE, "execution", "kernweg.py"), encoding="utf-8") as f:
        k = f.read()
    assert k.index("kampfschutz.liste(liste)") < k.index("self._einreihen(*u, tick)")
    with open(os.path.join(QUELLE, "runtime", "live", "erstes_spiel.py"), encoding="utf-8") as f:
        s = f.read()
    assert s.index("kampfschutz.stand(L, G)") < s.index(
        'KETTE.check(st.get("t", 0), L, G, eigen_k)'
    )
    # S142: what the guard holds back reaches the chain audit as the unit's order
    assert s.index("kanal_kette.BEOBACHTER[:] = [KETTE.from_module]") < s.index(
        "kampfschutz.ERFUELLT[:] = [KETTE.from_guard]"
    )
    import ast

    top = {
        a.asname or a.name
        for n in ast.parse(s).body
        if isinstance(n, (ast.Import, ast.ImportFrom))
        for a in n.names
    }
    assert "kampfschutz" in top  # bound at module level, the round loop can use it


def test_kernweg_does_not_put_a_resend_into_the_ring():
    from selfaware.execution import kernweg as KWG

    class Leitung:
        def __init__(self):
            self.n = 0

        def takt(self):
            return 1000

        def auftrag(self, art, nr, a=0, b=0, vorrang=0, frist=0, auftraggeber=0):
            self.n += 1
            return self.n

        def lesbar(self, ring):
            return True

        def ergebnis(self, ring):
            return 1

    le = Leitung()
    K.stand({475: _e(106, 40)})
    KWG.Kernweg(le).senden([{"angriff": {"einheiten": [475], "ziel": 40}}])
    assert le.n == 0
    K.stand({})
    KWG.Kernweg(le).senden([{"angriff": {"einheiten": [475], "ziel": 40}}])
    assert le.n >= 1  # not fighting: into the ring


def test_a_unit_hitting_that_building_is_taken_out():
    """Measured 13.11. 21:55 (S122): a second order mid-swing restarts the swing on a building (assassin +48 ticks)."""
    hut = {"x": 100, "y": 100, "typ": 1}  # hut: 4x4 from the corner
    K.stand(
        {
            5: dict(_e(107), x=99, y=101),
            6: dict(_e(107), x=110, y=101),
            7: dict(_e(101), x=99, y=101),
            8: dict(_e(107), x=105, y=103),
        },
        {200: hut},
    )
    paket, meld = K.filtern(
        {"befehle": [{"angriff": {"einheiten": [5, 6, 7, 8], "gebaeude": 200}}]}
    )
    assert paket == {
        "befehle": [{"angriff": {"einheiten": [6, 7], "gebaeude": 200}}]
    }  # far away / walking stay
    assert "KAMPFSCHUTZ: 5,8 kaempfen schon gegen B200" in meld[0]
    assert (
        K.filtern({"angriff": {"einheiten": [5], "gebaeude": 201}})[0] is not None
    )  # another building
