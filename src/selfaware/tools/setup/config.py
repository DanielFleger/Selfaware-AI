# -*- coding: utf-8 -*-
"""Die ucp-config.yml fuer unsere Tests herrichten - mit Test und Rueckweg.

Warum es das gibt: Wer das Spiel aus der UCP3-GUI startet, bekommt eine Config
ohne unser Modul und mit 'ohne Fokus anhalten' (beides gemessen 30.09.2026,
Meilensteine M2.08 und M2.13). Hergerichtet heisst:
  - das Modul steht an drei Stellen: config-sparse.modules,
    config-sparse.load-order, config-full.load-order;
  - graphicsApiReplacer laesst das Spiel ohne Fokus weiterlaufen
    (continueOutOfFocus: render) - sonst haelt es im Hintergrund an und
    kein einziger Befehl kommt an.

Aufruf:
  uv run python -m selfaware.tools.setup.config pruefen     zeigt, ob und wo das Modul eingetragen ist
  uv run python -m selfaware.tools.setup.config eintragen   traegt fehlende Stellen ein (vorher Sicherung)

Rueckweg: vor jeder Aenderung liegt eine Sicherung neben der Config
(ucp-config.yml.sicherung-<Datum-Uhrzeit>). Zurueck = Sicherung zurueckkopieren.
Test: die Datei wird nach dem Schreiben als YAML eingelesen; geschafft heisst,
das Modul steht an allen drei Stellen. Rueckgabe 0 = geschafft, 1 = nicht.
"""
import io, os, shutil, subprocess, sys, time

import yaml


from selfaware.game.ucp.befehl import SPIEL

CONFIG = os.path.join(SPIEL, "ucp-config.yml")   # Konfiguration der gewaehlten Instanz (SHC_INSTANZ)
NAME, VERSION = "villagestudio", "0.1.0"


def stellen(daten):
    """Die drei Stellen als Ja/Nein, aus der eingelesenen YAML."""
    sp = daten.get("config-sparse") or {}
    fu = daten.get("config-full") or {}
    def in_liste(liste):
        return any((e or {}).get("extension") == NAME for e in (liste or []))
    return {
        "config-sparse.modules": NAME in (sp.get("modules") or {}),
        "config-sparse.load-order": in_liste(sp.get("load-order")),
        "config-full.load-order": in_liste(fu.get("load-order")),
    }


def lies():
    return yaml.safe_load(io.open(CONFIG, encoding="utf-8"))


def fokus_wert(daten):
    """graphicsApiReplacer: was das Spiel ohne Fokus tut ('render' = weiterlaufen, 'pause' = anhalten)."""
    try:
        return (daten["config-full"]["modules"]["graphicsApiReplacer"]["config"]["window"]
                ["continueOutOfFocus"]["contents"]["value"])
    except (KeyError, TypeError):
        return None


def gui_laeuft():
    aus = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
    return "UCP3-GUI.exe" in aus


def pruefen():
    daten = lies()
    st = stellen(daten)
    for k, v in st.items():
        print("  %-26s %s" % (k, "eingetragen" if v else "FEHLT"))
    fw = fokus_wert(daten)
    print("  %-26s %s" % ("ohne Fokus", "weiterlaufen (render)" if fw == "render"
                          else "ANHALTEN (%s) - im Hintergrund kommt kein Befehl an" % fw))
    return all(st.values()) and fw == "render"


def ende_der_liste(zeilen, kopf):
    """Index der letzten Zeile der Liste, die unter zeilen[kopf] ('  load-order:') beginnt."""
    letzte = kopf
    for i in range(kopf + 1, len(zeilen)):
        z = zeilen[i]
        if z.strip() == "":
            continue
        if len(z) - len(z.lstrip(" ")) <= 2:   # naechster Schluessel auf Ebene 0 oder 1
            break
        letzte = i
    return letzte


def eintragen():
    if gui_laeuft():
        print("Hinweis: die UCP3-GUI laeuft. Startet jemand das Spiel aus ihr, ist der Eintrag wieder weg (M2.08).")
    daten_vorher = lies()
    vorher = stellen(daten_vorher)
    fokus_ok = fokus_wert(daten_vorher) == "render"
    if all(vorher.values()) and fokus_ok:
        print("GESCHAFFT: Modul an allen drei Stellen, Spiel laeuft ohne Fokus weiter - nichts geaendert.")
        return 0

    roh = io.open(CONFIG, "rb").read()
    nl = "\r\n" if b"\r\n" in roh else "\n"
    zeilen = roh.decode("utf-8").split(nl)

    sicherung = CONFIG + ".sicherung-" + time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(CONFIG, sicherung)

    i_sp = zeilen.index("config-sparse:")
    i_fu = zeilen.index("config-full:")

    # 1) config-sparse.modules
    if not vorher["config-sparse.modules"]:
        for i in range(i_sp + 1, i_fu):
            if zeilen[i] == "  modules: {}":
                zeilen[i:i + 1] = ["  modules:", "    %s:" % NAME, "      config: {}"]
                break
            if zeilen[i] == "  modules:":
                zeilen[i + 1:i + 1] = ["    %s:" % NAME, "      config: {}"]
                break
        i_fu = zeilen.index("config-full:")

    eintrag = ["    - extension: %s" % NAME, "      version: %s" % VERSION]

    # 2) config-sparse.load-order
    if not vorher["config-sparse.load-order"]:
        kopf = next(i for i in range(i_sp + 1, i_fu) if zeilen[i] == "  load-order:")
        e = ende_der_liste(zeilen, kopf)
        zeilen[e + 1:e + 1] = eintrag
        i_fu = zeilen.index("config-full:")

    # 3) config-full.load-order
    if not vorher["config-full.load-order"]:
        kopf = next(i for i in range(i_fu + 1, len(zeilen)) if zeilen[i] == "  load-order:")
        e = ende_der_liste(zeilen, kopf)
        zeilen[e + 1:e + 1] = eintrag

    # 4) graphicsApiReplacer: ohne Fokus weiterlaufen statt anhalten
    if not fokus_ok:
        k = next(i for i, z in enumerate(zeilen) if z.strip() == "continueOutOfFocus:")
        for i in range(k + 1, k + 4):
            if zeilen[i].strip().startswith("value:"):
                zeilen[i] = zeilen[i].split("value:")[0] + "value: render"
                break

    io.open(CONFIG, "wb").write(nl.join(zeilen).encode("utf-8"))

    try:
        daten_nachher = lies()
        nachher = stellen(daten_nachher)
        nachher["ohne Fokus weiterlaufen"] = fokus_wert(daten_nachher) == "render"
    except yaml.YAMLError as fehler:
        shutil.copy2(sicherung, CONFIG)
        print("NICHT GESCHAFFT: die Datei war danach kein gueltiges YAML (%s). Sicherung zurueckgespielt." % fehler)
        return 1
    for k, v in nachher.items():
        print("  %-26s %s" % (k, "eingetragen" if v else "FEHLT"))
    if all(nachher.values()):
        print("GESCHAFFT: Modul an allen drei Stellen. Rueckweg: %s" % sicherung)
        return 0
    shutil.copy2(sicherung, CONFIG)
    print("NICHT GESCHAFFT: nicht alle Stellen eingetragen. Sicherung zurueckgespielt.")
    return 1


if __name__ == "__main__":
    was = sys.argv[1] if len(sys.argv) > 1 else "pruefen"
    if was == "pruefen":
        sys.exit(0 if pruefen() else 1)
    if was == "eintragen":
        sys.exit(eintragen())
    print(__doc__); sys.exit(2)
