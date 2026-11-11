"""B-182 Sperrtest (Plan_Wegfuehrung.md, Schritt 3; Daniel 11.11. 19:47 auf die Frage "Als Naechstes den Sperrtest bauen?": "Ja, Sperrtest").

Jede Stelle im Live-Code, die selbst einen Lauf-, Angriffs- oder Zickzack-Befehl baut, ist entweder
  - ERLAUBT: im Code direkt darueber mit "# Wegfuehrung frei: <Grund>" markiert, Grund aus GRUENDE (Plan: Flucht, Halten, Graben,
    Abwehr am eigenen Lord), oder
  - ALT: noch nicht ueber die Wegfuehrung, hier je Datei, Funktion und Art gezaehlt. Die Liste darf nur kuerzer werden, bis sie leer ist.
Nicht gezaehlt: die Wegfuehrung selbst, die Kanaele (Befehl an das Spiel, Kernweg, Kern-Stecker) und tools/ (Pruefskripte, Versuche,
Auswertungen - dort spielt keine KI). Ohne Spiel.
"""

import ast
import collections
import pathlib
import re

WURZEL = pathlib.Path(__file__).resolve().parents[1] / "src" / "selfaware"
ARTEN = ("lauf", "ziel", "gebaeude", "graben", "vorrang")
GRUENDE = ("Flucht", "Halten", "Graben", "Abwehr am eigenen Lord")
MARKE = re.compile(r"#\s*Wegfuehrung frei:\s*(.+)$")
AUSGENOMMEN = {
    "micro/wegfuehrung.py": "die Wegfuehrung selbst",
    "execution/kernweg.py": "Kanal zum Kern: uebersetzt Befehle, waehlt kein Ziel",
    "game/kern_port.py": "Kanal zum Kern: Absicht wird Auftrag",
    "game/ucp/befehl.py": "Kanal zum Spiel",
}
# Funktionen, die den Befehl aus ihrem Aufruf bauen: gezaehlt wird jeder Aufruf mit seiner Art, nicht die Funktion
VERTEILER = {"micro/tasks/vorstoss.py": "Vorstoss._sende"}

ALT = {
    # Assassinen: eigene Wege ueber den toten Winkel, Stapel, Angriff auf den Lord (Plan Schritt 2: "danach ... Assassinen")
    ("micro/tasks/assassinen.py", "Angriffstrupp.schritt", "ziel"): 1,
    ("micro/tasks/assassinen.py", "Angriffstrupp.schritt", "gebaeude"): 1,
    ("micro/tasks/assassinen.py", "Einzeln.schritt", "ziel"): 4,
    ("micro/tasks/assassinen.py", "Einzeln.schritt", "gebaeude"): 1,
    ("micro/tasks/assassinen.py", "Einzeln.schritt", "lauf"): 2,
    # Feldzug: Sammelpunkt, Wegpunkte, Angriff auf den feindlichen Lord
    ("micro/tasks/feldzug.py", "Feldzug.schritt", "ziel"): 3,
    ("micro/tasks/feldzug.py", "Feldzug.schritt", "lauf"): 2,
    # alter Weg ohne Wegfuehrung: im Spiel setzt der Raid-Einsatz sie immer, den alten Weg nutzen nur noch alte Tests und Pruefskripte
    ("micro/tasks/nahkampf.py", "NahkampfRaid.schritt", "lauf"): 1,
    ("micro/tasks/nahkampf.py", "NahkampfRaid.schritt", "gebaeude"): 1,
    ("micro/tasks/nahkampf.py", "NahkampfRaid.schritt", "ziel"): 1,
    ("micro/tasks/raids.py", "Brandtrupp._angreifen", "gebaeude"): 1,
    ("micro/tasks/raids.py", "Brandtrupp._im_ausweichen", "zickzack"): 1,
    ("micro/tasks/raids.py", "Reiterjagd.schritt", "ziel"): 1,
    ("micro/tasks/vorstoss.py", "Vorstoss.schritt", "sende:schuss"): 1,
    # Deckung der Schleuderer (A_SLINGER 72) im Raid-Einsatz - noch nicht umgezogen
    ("micro/tasks/raids.py", "Deckung.schritt", "ziel"): 1,
    ("micro/tasks/raids.py", "Deckung.schritt", "lauf"): 1,
    # Vorstoss: Vorruecken - alter Weg ohne Wegfuehrung (im Spiel fuehrt sie es seit 11.11. 22:05); Zickzack des Kerns
    # (Plan: das Ausweichen ruft spaeter die Wegfuehrung selbst)
    ("micro/tasks/vorstoss.py", "Vorstoss.schritt", "sende:vor"): 1,
    ("micro/tasks/vorstoss.py", "Vorstoss._im_ausweichen", "zickzack"): 1,
    # Waechter: Stapel an einem Punkt, Angriff auf den Eindringling - alter Weg ohne Wegfuehrung; im Spiel gibt der Lenker sie
    # dem Waechter seit 11.11. 21:55 (Daniel 21:48: "Ja, freigeben")
    ("micro/tasks/waechter.py", "Waechter.schritt", "lauf"): 1,
    ("micro/tasks/waechter.py", "Waechter.schritt", "ziel"): 1,
    # Lenker: Streitkolben-Angriff auf den feindlichen Lord (ANGRIFF_AB)
    ("runtime/live/erstes_spiel.py", "phase2", "ziel"): 1,
}
HOECHSTENS = 28  # Summe von ALT am 11.11.2026 19:50 - nur senken (Plan: "darf nur sinken, bis sie 0 ist")

ERLAUBT = {
    ("micro/tasks/assassinen.py", "Einzeln.schritt", "lauf+vorrang", "Flucht"): 1,
    ("micro/tasks/raids.py", "Reiterjagd.schritt", "lauf", "Flucht"): 1,
    ("micro/tasks/vorstoss.py", "Vorstoss.schritt", "sende:weichen", "Flucht"): 1,
    ("micro/tasks/vorstoss.py", "Vorstoss.schritt", "sende:abziehen", "Flucht"): 1,
    ("micro/tasks/waechter.py", "Waechter.schritt", "lauf", "Abwehr am eigenen Lord"): 2,
    ("micro/tasks/waechter.py", "Waechter.schritt", "lauf", "Flucht"): 1,
    ("runtime/live/erstes_spiel.py", "schicke_graeber", "graben", "Graben"): 1,
    ("runtime/live/erstes_spiel.py", "phase2", "ziel", "Abwehr am eigenen Lord"): 1,
}


def stellen(quelle, rel):
    """[(Funktion, Art, Zeile)] jeder Befehlsstelle in einer Quelle. Befehl = {"angriff": {...}} mit "einheiten" oder
    {"angriff": dict(einheiten=...)}, ein Zickzack ueber self.kern.ausweichen, und die Aufrufe eines Verteilers mit ihrer Art."""
    verteiler = VERTEILER.get(rel)
    aus, pfad = [], []

    class Sammler(ast.NodeVisitor):
        def _rein(self, node):
            pfad.append(node.name)
            self.generic_visit(node)
            pfad.pop()

        visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _rein

        def visit_Dict(self, node):
            name = ".".join(pfad) or "<modul>"
            for k, v in zip(node.keys, node.values, strict=True):
                if not (isinstance(k, ast.Constant) and k.value == "angriff"):
                    continue
                if isinstance(v, ast.Dict):
                    schl = [kk.value for kk in v.keys if isinstance(kk, ast.Constant)]
                    if "einheiten" in schl:
                        aus.append((name, "+".join(sorted(a for a in schl if a in ARTEN)) or "?", node.lineno))
                elif (
                    isinstance(v, ast.Call)
                    and isinstance(v.func, ast.Name)
                    and v.func.id == "dict"
                    and any(kw.arg == "einheiten" for kw in v.keywords)
                    and name != verteiler
                ):
                    aus.append((name, "dynamisch", node.lineno))
            self.generic_visit(node)

        def visit_Call(self, node):
            name = ".".join(pfad) or "<modul>"
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr == "ausweichen" and isinstance(f.value, ast.Attribute) and f.value.attr == "kern":
                aus.append((name, "zickzack", node.lineno))
            if (
                verteiler
                and isinstance(f, ast.Attribute)
                and f.attr == verteiler.split(".")[-1]
                and node.args
                and isinstance(node.args[0], ast.Constant)
            ):
                aus.append((name, "sende:%s" % node.args[0].value, node.lineno))
            self.generic_visit(node)

    Sammler().visit(ast.parse(quelle))
    return aus


def marke(zeilen, nr):
    """Grund aus "# Wegfuehrung frei: <Grund>" auf der Zeile der Stelle oder direkt darueber, sonst None."""
    for i in (nr - 1, nr - 2):
        if 0 <= i < len(zeilen):
            m = MARKE.search(zeilen[i])
            if m:
                return m.group(1).strip()
    return None


def bestand(wurzel=WURZEL):
    """(ALT-Zaehlung, ERLAUBT-Zaehlung, Fehler) ueber den Live-Code."""
    alt, erlaubt, fehler = collections.Counter(), collections.Counter(), []
    for p in sorted(wurzel.rglob("*.py")):
        rel = p.relative_to(wurzel).as_posix()
        if rel.startswith("tools/") or rel in AUSGENOMMEN:
            continue
        quelle = p.read_text(encoding="utf-8")
        zeilen = quelle.splitlines()
        for name, art, nr in stellen(quelle, rel):
            grund = marke(zeilen, nr)
            if grund is None:
                alt[(rel, name, art)] += 1
                continue
            g = next((x for x in GRUENDE if grund.startswith(x)), None)
            if g is None:
                fehler.append("%s:%d %s: Grund '%s' steht nicht im Plan (%s)" % (rel, nr, name, grund, ", ".join(GRUENDE)))
            else:
                erlaubt[(rel, name, art, g)] += 1
    return alt, erlaubt, fehler


def _unterschied(soll, ist):
    neu = {k: ist[k] - soll.get(k, 0) for k in ist if ist[k] > soll.get(k, 0)}
    weg = {k: soll[k] - ist.get(k, 0) for k in soll if soll[k] > ist.get(k, 0)}
    return neu, weg


def test_jede_befehlsstelle_ist_erlaubt_oder_steht_in_der_altliste():
    alt, _erlaubt, _fehler = bestand()
    neu, weg = _unterschied(ALT, alt)
    assert not neu, "Neue Befehlsstelle ausserhalb der Wegfuehrung - ueber micro/wegfuehrung.py fuehren oder mit Grund markieren: %s" % neu
    assert not weg, "Weniger alte Stellen als in ALT - gut: ALT und HOECHSTENS kuerzen: %s" % weg


def test_erlaubte_stellen_tragen_einen_grund_aus_dem_plan():
    _alt, erlaubt, fehler = bestand()
    assert not fehler, fehler
    neu, weg = _unterschied(ERLAUBT, erlaubt)
    assert not neu and not weg, "Erlaubte Stellen weichen von ERLAUBT ab: neu %s, weg %s" % (neu, weg)


def test_die_altliste_wird_nur_kuerzer():
    assert sum(ALT.values()) <= HOECHSTENS


def test_der_sperrtest_erkennt_was_er_zaehlen_soll():
    """Gegenprobe am Sammler selbst - sonst waere ein gruener Lauf auch ein leerer."""
    quelle = '''
class K:
    def a(self, befehl):
        befehl({"angriff": {"einheiten": [1], "lauf": [2, 3]}}, 1.0)

    def b(self, befehl):
        # Wegfuehrung frei: Flucht - Probe
        befehl({"angriff": {"einheiten": [1], "lauf": [2, 3], "vorrang": True}}, 1.0)

    def c(self):
        return {"angriff": len([])}  # Zaehler in einer Mitschrift, kein Befehl

    def d(self, n):
        self.kern.ausweichen([n], (1, 2))

    def e(self, auftrag):
        return {"angriff": dict(einheiten=[1], **auftrag)}
'''
    st = stellen(quelle, "probe.py")
    assert [(n, a) for n, a, _ in st] == [("K.a", "lauf"), ("K.b", "lauf+vorrang"), ("K.d", "zickzack"), ("K.e", "dynamisch")]
    zeilen = quelle.splitlines()
    assert [marke(zeilen, nr) for _, _, nr in st] == [None, "Flucht - Probe", None, None]
    v = 'class Vorstoss:\n    def _sende(self, art, auftrag):\n        return {"angriff": dict(einheiten=[1], **auftrag)}\n' \
        '    def schritt(self):\n        self._sende("vor", {"lauf": [1, 2]})\n'
    assert [(n, a) for n, a, _ in stellen(v, "micro/tasks/vorstoss.py")] == [("Vorstoss.schritt", "sende:vor")]
