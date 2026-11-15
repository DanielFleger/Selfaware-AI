"""B-182 link 2 terrain survey (tools/experiments/gelaende_erheben.py), the summary without the game."""

from selfaware.tools.experiments import gelaende_erheben as E


def test_the_summary_counts_bits_steps_and_finds_test_lines(tmp_path):
    marsh = 0x20000000
    row_a = ["ff:0:1:0:8:0"] * 10                                   # 10 plain fields, flat
    row_b = ["ff:0:1:%x:8:0" % marsh] * 9 + ["0:5:0:30:8:41"]        # 9 fields with the bit, then a blocked field
    row_c = ["ff:0:1:0:%d:0" % h for h in (8, 8, 9, 10, 12, 14, 16, 18, 20, 22)]   # a slope
    p = tmp_path / "wegkarte.txt"
    p.write_text("tick 5 x0=200 y0=200 x1=209 y1=202\n" + "\n".join(" ".join(r) for r in (row_a, row_b, row_c)) + "\n",
                 encoding="utf-8")
    s = E.summarize(*E.read_dump(str(p)))
    assert s["walkable"] == 29 and s["bits"] == {"0x20000000": 9}
    assert s["speed_classes"] == {"none": 20, "0x20000000": 9}
    assert s["height_steps"][0] == 9 + 8 + 1 and s["height_steps"][2] == 6
    lines = s["test_lines"]
    assert lines["0x20000000"]["flat"] == [(9, 200, 201, 8, 8)]
    assert lines["none"]["steepest"][0][:3] == (10, 200, 202)
    p.write_text("tick 5 x0=100 y0=50 x1=109 y1=52\n" + "\n".join(" ".join(r) for r in (row_a, row_b, row_c)) + "\n",
                 encoding="utf-8")
    assert E.summarize(*E.read_dump(str(p)))["walkable"] == 0       # row 50 holds x 149-250: these fields are not on the map


def test_only_fields_of_the_map_diamond_count():
    """Measured 00:35 (translationMatrix of a 400 map): row 0 holds x 199-200, rows 199/200 x 0-399, row 399 x 199-200, 80,400
    fields; the walk line at (375, 19) lay outside - no unit walked there."""
    import json
    import os
    assert E.in_diamond(199, 0) and E.in_diamond(200, 0) and not E.in_diamond(198, 0) and not E.in_diamond(201, 0)
    assert E.in_diamond(0, 199) and E.in_diamond(399, 200) and E.in_diamond(199, 399) and not E.in_diamond(375, 19)
    assert sum(E.in_diamond(x, y) for x in range(400) for y in range(400)) == 80400
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "research", "kartenraute_400.json")
    if os.path.exists(p):
        for y, x_min, _first, _add in json.load(open(p))["rows"]:
            assert E.in_diamond(x_min, y) and not E.in_diamond(x_min - 1, y)
