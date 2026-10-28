# -*- coding: utf-8 -*-
"""B-274 Fairness-Pruefung (Daniel 27.10.2026 19:46): "die KI soll es unmenschlich schnell verarbeiten und steuern koennen,
nicht das Spiel veraendern, Preise einheben, Einheiten per Befehl toeten etc." - und kein verborgenes Gegnerwissen.

Durchsucht den Spielweg (Importhuelle von erstes_spiel / samurai_wache / local_launcher, wie paket_daten_pruefen.py):
1. EINGRIFFE: Befehle, die das Spiel veraendern (poke, ware, setzeEinheit, toeteAlle, gold, leereKI). Jede Fundstelle muss
   je (Modul, Funktion) in ERLAUBT stehen - sonst ROT. Der Einzelkauf (Waren/Gold per Speicher) muss fest aus sein.
2. VERBORGENES: jede Funktion, die Laufziel (laufx/laufy) oder Angriffsziel (zieleinheit/nahziel) liest, ist in LESER
   von Hand eingeordnet (gelesen 27.10. 20:05): "eigen" (eigene/verbuendete Einheiten, Protokoll) oder "feind-laufziel" /
   "feind-ziel" (sehen seit B-274 Teil 2 nur, was der Sichtfilter waechter.sichtfilter durchlaesst). Eine NEUE, nicht eingeordnete Funktion macht die Pruefung ROT.
Die Regel selbst steht in FAIRNESS.md (Repo-Wurzel).
Aufruf: python werkzeug/fairness_pruefen.py [--liste]"""
import ast
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import paket_daten_pruefen as P

EINGRIFF = {"poke", "ware", "setzeEinheit", "toeteAlle", "gold", "leereKI"}
ERLAUBT = {
    ("erstes_spiel", "uebernehmen_start"): "eigenen Platz uebernehmen: eingebaute KI unseres Platzes aus - SamurAI spielt ihn",
    ("samurai_wache", "ki_aus"): "eigenen Platz uebernehmen (Wache)",
    ("samurai_wache", "platz_zurueckstellen"): "eigenen Platz in der Pause auf seine Platzhalter-KI zurueck (B-280, Gegenstueck zu ki_aus; kein Takt laeuft)",
    ("erstes_spiel", "ki_aus"): "nur Testgefecht 1v1 (eigener Aufbau): eingebaute KI der Gegnerplaetze aus",
    ("erstes_spiel", "angleichen"): "nur Testgefecht 1v1/2v2 (eigener Aufbau): Startwaren/-truppen angleichen",
    ("erstes_spiel", "eins_gegen_eins_start"): "nur Testgefecht 2v2 (eigener Aufbau): Liga-Startgold setzen",
    ("erstes_spiel", "bilanz_schritt"): "Einzelkauf - Schummeln; laeuft nur mit EINZELKAUF, seit B-274 fest aus (unten geprueft)",
    ("speichern", "speichere"): "Spielstand-Namen ins Textfeld schreiben (wie Tippen)",
    ("steuerkarte", "main"): "Messwerkzeug (eigener Aufruf), nicht im Lenker",
    ("shc", "gefecht"): "Werkzeug shc.py: Testgefecht aufsetzen, nicht im Lenker",
    ("shc", "sandkasten"): "Werkzeug shc.py: Sandkasten, nicht im Lenker",
    ("shc", "setze"): "Werkzeug shc.py: Sandkasten, nicht im Lenker",
}
FEIND_LAUFZIEL, FEIND_ZIEL, EIGEN = "feind-laufziel", "feind-ziel", "eigen"
LESER = {
    "assassinen._im_weg": FEIND_LAUFZIEL, "assassinen._gitter": FEIND_LAUFZIEL, "assassinen.kommt": FEIND_LAUFZIEL,
    "assassinen._nahtrupps": FEIND_LAUFZIEL, "assassinen._nahtrupp_droht": FEIND_LAUFZIEL,
    "fallenwache.kandidaten": FEIND_LAUFZIEL, "lordwache.im_anmarsch": FEIND_LAUFZIEL, "waechter.hauptheer": FEIND_LAUFZIEL,
    "waechter.schritt": FEIND_LAUFZIEL + "+ziel",
    "assassinen._bemerkt_von": FEIND_ZIEL, "erstes_spiel.phase2": FEIND_ZIEL, "feldzug._abfangen": FEIND_ZIEL,
    "raids.schritt": FEIND_ZIEL, "waechter._bewerten": FEIND_ZIEL, "zuweisung.abwehr_rang": FEIND_ZIEL,
    "assassinen._verbuendete_am_lord": EIGEN, "assassinen._lord_messen": EIGEN + " (Feinde nur im Protokoll)",
    "assassinen._route_pflegen": EIGEN, "assassinen._entdeckt_pruefen": EIGEN + " (Feind-Laufziel nur in der Meldung)",
    "assassinen.schritt": EIGEN, "erstes_spiel.platz_sauber": EIGEN, "feldzug._steht_nur": EIGEN,
    "feldzug._feuer_lenken": EIGEN, "feldzug._lohnt": EIGEN + " (Verbuendete)", "raids._alle_heerwege": EIGEN + " (Verbuendete)",
    "raids._wirkung_messen": EIGEN, "uebersicht._verbaende": EIGEN, "waechter.lies_lagebild": EIGEN + " (liest die Tabelle ein)",
    "waechter.sichtfilter": "filter (B-274: ersetzt Feind-Laufziel/Angriffsziel durch das Sichtbare)",
    # Frage-Agent 27.10. 20:02 (Ampel rot): das Gehirn auf den Speicherbildern des Auges liest gespeicherte Ziele und den
    # naechsten Schuss JEDER Einheit, auch feindlicher - erlaubt zum Erforschen der Mechanik, VERBOTEN im Spielweg
    "tagebuch.lord_runde": EIGEN + " (eigene Einheiten, die sichtbar auf den Lord schlagen)",
    "besitzbuch.steh_runde": EIGEN + " (Laufziel eigener Einheiten: Befehl angenommen?)",
    "assassinen._abgelehnt_loesen": EIGEN + " (Laufziel der eigenen Assassine: hat das Spiel den Befehl angenommen?)",
    "gehirn.prognose": "gehirn-roh", "gehirn._begegnungen": "gehirn-roh", "simulator._aufbau": "gehirn-roh",
}
# Laufziel/Angriffsziel im Lagebild (laufx, zieleinheit, nahziel) und dieselben Groessen in den Speicherbildern des Auges
# (shootTargetedUnit, attackedUnitID, sre_naechster_schuss_takte)
FELD = re.compile(r"[\"'](laufx|laufy|zieleinheit|nahziel|shootTargetedUnit|attackedUnitID|sre_naechster_schuss_takte)[\"']")
GEHIRN_MODULE = ("gehirn", "simulator")     # immer durchsucht - auch solange sie noch nicht im Spielweg sind

# B-287 (28.10.2026): auch der Rust-Kern entscheidet - jeden Takt, im Spielprozess. Kern 20 las im Reflex das gespeicherte
# Ziel feindlicher Schuetzen (+926), und diese Pruefung sah es nicht, weil sie nur Python kannte. Jetzt: jede Rust-Funktion,
# die Laufziel/Angriffsziel (Feld oder Speicherversatz) liest, ist eingeordnet - eine neue macht die Pruefung ROT.
KERN = os.path.join(os.path.dirname(HIER), "distribution", "kernel", "src")
KERN_FELD = re.compile(r"\.(laufx|laufy|zieleinheit|zieluid|nahziel|nahangreifer)\b|u \+ (836|830|926|928)\b")
KERN_FN = re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:unsafe\s+)?(?:extern\s+\"C\"\s+)?fn\s+(\w+)")
KERN_LESER = {
    "welt.rs:lesen": "auge: liest den Speicher ins Weltbild - Nutzung je Funktion unten eingeordnet",
    "welt.rs:schreiben": "protokoll: kern_lagebild.txt fuer Messwerkzeuge",
    "leitung.rs:schreiben": "durchreichen: Ring an Messwerkzeuge (Python-Leser stehen unter der Python-Pruefung, keiner im Spielweg)",
    "lib.rs:r1_ankunft": "eigen: Laufziel der EIGENEN Einheit nach dem Reflex-Befehl (Beleg, dass er ankam)",
    "lib.rs:beschuss_takt": "eigen: Nahziel EIGENER Kaempfer im Beschuss-Protokoll",
}


def kern_leser(dateien=None):
    """{"datei:funktion": [Zeilen]} fuer jede Rust-Funktion im Kern, die Laufziel/Angriffsziel liest. dateien: {name: text}
    zum Pruefen fremder Staende (Gegenprobe); sonst distribution/kernel/src/*.rs."""
    if dateien is None:
        dateien = {f: open(os.path.join(KERN, f), encoding="utf-8").read() for f in sorted(os.listdir(KERN)) if f.endswith(".rs")}             if os.path.isdir(KERN) else {}
    aus = {}
    for name, text in dateien.items():
        fn = "<modul>"
        for i, z in enumerate(text.splitlines(), 1):
            m = KERN_FN.match(z)
            if m:
                fn = m.group(1)
            if KERN_FELD.search(z) and not z.strip().startswith("//"):
                aus.setdefault("%s:%s" % (name, fn), []).append(i)
    return aus


def _funktionen(baum):
    return [(n.lineno, n.end_lineno, n.name) for n in ast.walk(baum) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _innerste(fns, zeile):
    drin = [f for f in fns if f[0] <= zeile <= f[1]]
    return min(drin, key=lambda f: f[1] - f[0])[2] if drin else "<modul>"


def eingriffe(mods):
    """[(modul, funktion, zeile, befehl)] aller Befehle aus EINGRIFF im Spielweg."""
    aus = []
    for m in sorted(mods):
        baum = ast.parse(open(os.path.join(HIER, m + ".py"), encoding="utf-8").read())
        fns = _funktionen(baum)
        for n in ast.walk(baum):
            if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Dict):
                fn = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
                if fn in ("befehl", "sende"):
                    for k in n.args[0].keys:
                        if isinstance(k, ast.Constant) and k.value in EINGRIFF:
                            aus.append((m, _innerste(fns, n.lineno), n.lineno, k.value))
    return sorted(aus)


def leser(mods):
    """{modul.funktion: [zeilen]} aller Lesestellen von Laufziel/Angriffsziel."""
    aus = {}
    for m in sorted(mods):
        text = open(os.path.join(HIER, m + ".py"), encoding="utf-8").read()
        fns = _funktionen(ast.parse(text))
        for i, z in enumerate(text.splitlines(), 1):
            if FELD.search(z) and not z.strip().startswith("#"):
                aus.setdefault("%s.%s" % (m, _innerste(fns, i)), []).append(i)
    return aus


def einzelkauf_aus():
    """Der Einzelkauf darf nie scharf werden: in erstes_spiel kein 'EINZELKAUF = ' mit etwas anderem als False."""
    text = open(os.path.join(HIER, "erstes_spiel.py"), encoding="utf-8").read()
    return all(w.strip() == "False" for w in re.findall(r"^\s*EINZELKAUF\s*=\s*([^#\n]+)", text, re.M))


def filter_angeschlossen():
    """B-274 Teil 2: der Lenker liest feindliche Einheiten nur durch waechter.sichtfilter (FAIRNESS.md) - lies_lagebild
    ruft ihn auf, erstes_spiel.main setzt SICHT_SPIELER, und der Filter selbst besteht seine Pruefung."""
    w = open(os.path.join(HIER, "waechter.py"), encoding="utf-8").read()
    e = open(os.path.join(HIER, "erstes_spiel.py"), encoding="utf-8").read()
    if "sichtfilter(L," not in w or "W_sicht.SICHT_SPIELER = SP" not in e:
        return False
    import subprocess
    return subprocess.call([sys.executable, os.path.join(HIER, "sichtfilter_pruefen.py")], stdout=subprocess.DEVNULL) == 0


def pruefe(mods=None):
    mods = mods or P.spielweg()
    rot = ["EINGRIFF ohne Freigabe: %s.%s Zeile %d (%s)" % e for e in eingriffe(mods) if (e[0], e[1]) not in ERLAUBT]
    if not einzelkauf_aus():
        rot.append("EINZELKAUF kann scharf werden (Waren/Gold per Speicher)")
    if not filter_angeschlossen():
        rot.append("SICHTFILTER nicht angeschlossen oder seine Pruefung rot - feindliche Laufziele/Angriffsziele ungefiltert")
    les = leser(set(mods) | {m for m in GEHIRN_MODULE if os.path.exists(os.path.join(HIER, m + ".py"))})
    # gehirn-roh ist nur ausserhalb des Spielwegs erlaubt: laedt der Lenker eines dieser Module, ist es Schummeln
    rot += ["GEHIRN-ROH im Spielweg: %s liest gespeicherte Feindziele/Schusstakte - erst auf Sichtbares umbauen (FAIRNESS.md)"
            % k for k in les if LESER.get(k) == "gehirn-roh" and k.split(".")[0] in mods]
    rot += ["NEUE Lesestelle fuer Laufziel/Angriffsziel, nicht eingeordnet: %s Zeilen %s" % (k, v) for k, v in les.items()
            if k not in LESER]
    rot += ["KERN: neue Lesestelle fuer Laufziel/Angriffsziel, nicht eingeordnet: %s Zeilen %s (FAIRNESS.md - nur Eigenes oder "
            "Protokoll)" % (k, v) for k, v in kern_leser().items() if k not in KERN_LESER]
    return rot, les


if __name__ == "__main__":
    mods = P.spielweg()
    rot, les = pruefe(mods)
    for e in eingriffe(mods):
        print("EINGRIFF %-14s %-22s Z.%-5d %-12s %s" % (e[0], e[1], e[2], e[3], ERLAUBT.get((e[0], e[1]), "NICHT FREIGEGEBEN")))
    feind = {k: v for k, v in les.items() if LESER.get(k, "").startswith("feind")}
    if "--liste" in sys.argv:
        for k, v in sorted(kern_leser().items()):
            print("KERN  %-36s %-24s Zeilen %s" % (k, KERN_LESER.get(k, "NICHT EINGEORDNET")[:24], v))
        for k, v in sorted(les.items()):
            print("LESER %-36s %-24s Zeilen %s" % (k, LESER.get(k, "NICHT EINGEORDNET"), v))
    # Gegenproben: entzogene Freigabe und entzogene Einordnung muessen anschlagen
    alt_e, alt_l = dict(ERLAUBT), dict(LESER)
    ERLAUBT.pop(("erstes_spiel", "uebernehmen_start"))
    LESER.pop("waechter.schritt")
    gegen = pruefe(mods)[0]
    ERLAUBT.update(alt_e)
    LESER.update(alt_l)
    ok_gegen = any("uebernehmen_start" in r for r in gegen) and any("waechter.schritt" in r for r in gegen)
    # Gegenprobe Kern: ein Reflex, der das gespeicherte Ziel feindlicher Schuetzen liest (wie Kern 20), muss anschlagen
    falsch = {"lib.rs": "fn anvisiert_reflex() {\n    let s = w.iter().find(|s| s.zieleinheit as i32 == nr);\n}\n"}
    ok_gegen = ok_gegen and "lib.rs:anvisiert_reflex" in kern_leser(falsch) and "lib.rs:anvisiert_reflex" not in KERN_LESER
    for r in rot:
        print("ROT:", r)
    print("Gegenprobe (Freigabe und Einordnung entzogen): %s" % ("schlaegt an" if ok_gegen else "SCHLAEGT NICHT AN"))
    print("%d Module; %d Eingriffe, alle freigegeben: %s; Einzelkauf fest aus: %s; %d Funktionen lesen Laufziel/Angriffsziel von "
          "Feinden (Laufziel %d, Angriffsziel %d) - alle nur durch den Sichtfilter: %s: %s" % (
              len(mods), len(eingriffe(mods)), not any(r.startswith("EINGRIFF") for r in rot), einzelkauf_aus(), len(feind),
              sum(1 for k in feind if "laufziel" in LESER[k]), sum(1 for k in feind if "ziel" in LESER[k].replace("laufziel", "")),
              filter_angeschlossen(), "GRUEN" if not rot and ok_gegen else "ROT"))
    sys.exit(0 if not rot and ok_gegen else 1)
