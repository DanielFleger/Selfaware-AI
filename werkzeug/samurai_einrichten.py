# -*- coding: utf-8 -*-
"""SamurAI in eine Spielinstanz einrichten (Daniel 19.10. 19:55: "nimm die Ratte ... nimm ein cooles Foto von einer KI als
sein Profilbild, nenne es auch SamurAI").

1. Paket samurai_ki/SamurAI/ (meta.json, lines.json, portrait.png 72x72, portrait_small.png 36x36) nach
   <Instanz>/ucp/resources/ai/SamurAI/ kopieren - der Standardort des aiSwappers (init.lua AI_ROOT_FOLDER), ausserhalb der
   Plugin-Ordner (die ein Plugin-Update zuruecksetzt, Fehlerhub mp-11).
2. In ucp-config.yml unter aiSwapper.config.ai einen Block "rat" mit lines + portrait -> SamurAI eintragen (Name und Texte
   kommen aus lines.json "ai_name", das Bild aus portrait.png; scripts/lines.lua, scripts/portrait.lua). Burg, Truppen,
   Sprache, Verhalten der Ratte bleiben - gespielt wird der Platz ohnehin von samurai_wache.py.
   ucp-config.yml hat EINEN Schreiber (VillageStudio Betriebsregeln Regel 2): vorher datierte Sicherung, danach gegenlesen
   (villagestudio 3-mal, continueOutOfFocus da, YAML lesbar, rat -> SamurAI). Wirkt beim naechsten Spielstart.
Rueckweg: --aus (Block entfernen; das Paket bleibt liegen, schadet ohne Eintrag nicht).
Aufruf: python werkzeug/samurai_einrichten.py [instanz=4] [--aus]"""
import os
import shutil
import sys
import time

import yaml

HIER = os.path.dirname(os.path.abspath(__file__))
PAKET = os.path.join(HIER, "..", "samurai_ki", "SamurAI")
ANFANG, ENDE = "          # SamurAI anfang (samurai_einrichten.py)", "          # SamurAI ende"
BLOCK = """{anfang}
          rat:
            lines:
              contents:
                value:
                  name: SamurAI
                  root: ucp/resources/ai/SamurAI/
                  active: true
            portrait:
              contents:
                value:
                  name: SamurAI
                  root: ucp/resources/ai/SamurAI/
                  active: true
            aiv:
              contents:
                value:
                  name: SamurAI
                  root: ucp/resources/ai/SamurAI/
                  active: true
{ende}
""".format(anfang=ANFANG, ende=ENDE)


def instanz_ordner(n):
    basis = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"
    return basis if n == 1 else "%s Instanz%d" % (basis, n)


def gegenlesen(text):
    fehler = []
    if text.count("villagestudio") != 3:
        fehler.append("villagestudio %d-mal statt 3" % text.count("villagestudio"))
    if "continueOutOfFocus" not in text:
        fehler.append("continueOutOfFocus fehlt")
    try:
        y = yaml.safe_load(text)
    except yaml.YAMLError as ex:
        return fehler + ["YAML nicht lesbar: %s" % ex], None
    return fehler, y


def rat_name(y):
    try:
        return y["config-full"]["modules"]["aiSwapper"]["config"]["ai"]["rat"]["lines"]["contents"]["value"]["name"]
    except (KeyError, TypeError):
        pass
    # die Datei kann den Baum unter einem anderen Schluessel fuehren - suchen statt raten
    def suche(k):
        if isinstance(k, dict):
            if "aiSwapper" in k and isinstance(k["aiSwapper"], dict) and "config" in k["aiSwapper"]:
                try:
                    return k["aiSwapper"]["config"]["ai"]["rat"]["lines"]["contents"]["value"]["name"]
                except (KeyError, TypeError):
                    return None
            for v in k.values():
                r = suche(v)
                if r:
                    return r
        return None
    return suche(y)


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    aus = "--aus" in sys.argv
    ordner = arg.get("ordner") or instanz_ordner(int(arg.get("instanz", 4)))      # ordner=: Probe an einer Kopie
    cfg = os.path.join(ordner, "ucp-config.yml")
    # 20:03 (Probe an einer Kopie): Zeilenenden unveraendert lassen - der Textmodus unter Windows haette beim Schreiben jedes
    # LF der ganzen Datei in CRLF umgewandelt (Rueckweg war nicht mehr byte-gleich)
    text = open(cfg, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in text else "\n"
    f0, _ = gegenlesen(text)
    if f0:
        raise SystemExit("ucp-config.yml schon VORHER nicht in Ordnung, nichts geaendert: %s" % f0)
    sicherung = cfg + ".vor-samurai-" + time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(cfg, sicherung)
    if aus:
        if ANFANG not in text:
            print("kein SamurAI-Block - nichts zu tun")
            return
        a, e = text.index(ANFANG), text.index(ENDE) + len(ENDE) + len(nl)
        neu = text[:a] + text[e:]
    else:
        ziel = os.path.join(ordner, "ucp", "resources", "ai", "SamurAI")
        os.makedirs(ziel, exist_ok=True)
        for name in os.listdir(PAKET):
            q = os.path.join(PAKET, name)
            if os.path.isdir(q):                    # 20:26: aiv/ (leere Burgvorlage)
                shutil.copytree(q, os.path.join(ziel, name), dirs_exist_ok=True)
            else:
                shutil.copy2(q, os.path.join(ziel, name))
        fehlt = [n for n in ("meta.json", "lines.json", "portrait.png", "portrait_small.png") if not os.path.exists(os.path.join(ziel, n))]
        print("Paket nach %s kopiert%s" % (ziel, (" - FEHLT: %s (dann bleibt das Bild der Ratte)" % fehlt) if fehlt else ""))
        if ANFANG in text:
            # 20:26: steht ein aelterer Block, wird er ersetzt (nicht doppelt) - sonst nur das Paket
            alt = text[text.index(ANFANG):text.index(ENDE) + len(ENDE) + len(nl)]
            if alt == BLOCK.replace("\n", nl):
                print("SamurAI-Block steht schon so in ucp-config.yml - nur das Paket aktualisiert")
                return
            text = text.replace(alt, "")
        kopf = text.index("    aiSwapper:")
        marke = nl + "        ai:" + nl
        ai = text.index(marke, kopf) + len(marke)
        neu = text[:ai] + BLOCK.replace("\n", nl) + text[ai:]
    f1, y = gegenlesen(neu)
    if f1:
        raise SystemExit("Gegenlesen ROT, nichts geschrieben (Sicherung %s): %s" % (sicherung, f1))
    name = rat_name(y)
    if (name != "SamurAI") != aus:
        raise SystemExit("Gegenlesen ROT: rat -> %r, erwartet %s - nichts geschrieben" % (name, "nichts" if aus else "SamurAI"))
    open(cfg, "w", encoding="utf-8", newline="").write(neu)
    print("ucp-config.yml %s (Sicherung %s); gegengelesen: villagestudio 3, continueOutOfFocus da, rat -> %s" % (
        "zurueckgesetzt" if aus else "ergaenzt", os.path.basename(sicherung), name))


if __name__ == "__main__":
    main()
