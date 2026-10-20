# -*- coding: utf-8 -*-
"""Spielmodus umschalten: selbst mitspielen oder nur KI zuschauen (Daniel 19.10. 20:13: "mit der Modifikation kann ich nicht
selbst mitspielen, sondern nur zusehen - kannst du den Mod durch ein leicht umschaltbares Modul anpassen, dass ich auch ein
Spieler bin?").

Gefunden 20:14: ucp-config.yml, Modul ucp2-legacy, Option o_onlyai ("nur KI spielt") = true auf Instanz 1, 2, 3 und 4 - damit ist
der Mensch in der Lobby Zuschauer. Kein Werkzeug in Selfaware-AI/VillageStudio liest die Option (Suche 20:14); unsere Laeufe
setzen die Spielerplaetze selbst (Modul "menschen", Mensch-Eintrag).
  modus=spielen    o_onlyai aus -> du bist Spieler 1 in der Lobby
  modus=zuschauen  o_onlyai an  -> wie bisher (KI gegen KI)
Aendert NUR die eine Zeile "value:" unter o_onlyai. ucp-config.yml hat EINEN Schreiber (VillageStudio Betriebsregeln Regel 2):
datierte Sicherung, Zeilenenden bleiben, gegenlesen (villagestudio 3-mal, continueOutOfFocus, YAML, neuer Wert). Wirkt beim
naechsten Spielstart. Rueckweg: der andere Modus.
Aufruf: uv run python -m selfaware.tools.setup.spielmodus [instanz=4] modus=spielen|zuschauen   (ohne modus: zeigt den Stand)"""
import os
import re
import shutil
import sys
import time

import yaml


from selfaware.tools.setup.samurai_einrichten import instanz_ordner, gegenlesen

MUSTER = re.compile(r"(\n        o_onlyai:\r?\n          enabled:\r?\n            contents:\r?\n              value: )(true|false)")


def onlyai(y):
    def suche(k):
        if isinstance(k, dict):
            if "o_onlyai" in k:
                try:
                    return k["o_onlyai"]["enabled"]["contents"]["value"]
                except (KeyError, TypeError):
                    return None
            for v in k.values():
                r = suche(v)
                if r is not None:
                    return r
        return None
    return suche(y)


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    ordner = arg.get("ordner") or instanz_ordner(int(arg.get("instanz", 4)))
    cfg = os.path.join(ordner, "ucp-config.yml")
    text = open(cfg, encoding="utf-8", newline="").read()
    m = MUSTER.findall(text)
    if len(m) != 1:
        raise SystemExit("o_onlyai %d-mal gefunden statt 1 - nichts geaendert" % len(m))
    jetzt = m[0][1]
    modus = arg.get("modus")
    print("Instanz %s: o_onlyai = %s -> %s" % (arg.get("instanz", 4), jetzt, "zuschauen (nur KI)" if jetzt == "true" else "spielen"))
    if not modus:
        return
    soll = {"spielen": "false", "zuschauen": "true"}[modus]
    if soll == jetzt:
        print("schon so - nichts zu tun")
        return
    f0, _ = gegenlesen(text)
    if f0:
        raise SystemExit("ucp-config.yml schon VORHER nicht in Ordnung, nichts geaendert: %s" % f0)
    neu = MUSTER.sub(lambda mm: mm.group(1) + soll, text)
    f1, y = gegenlesen(neu)
    if f1 or onlyai(y) is not (soll == "true"):
        raise SystemExit("Gegenlesen ROT, nichts geschrieben: %s, o_onlyai -> %r" % (f1, onlyai(y)))
    sicherung = cfg + ".vor-spielmodus-" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(cfg, sicherung)
    open(cfg, "w", encoding="utf-8", newline="").write(neu)
    print("umgeschaltet: o_onlyai = %s (%s); Sicherung %s; gegengelesen: villagestudio 3, continueOutOfFocus da. Wirkt beim "
          "naechsten Spielstart." % (soll, modus, os.path.basename(sicherung)))


if __name__ == "__main__":
    main()
