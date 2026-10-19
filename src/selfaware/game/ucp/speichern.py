# -*- coding: utf-8 -*-
"""Spielstand speichern ohne Klick (M7.01) - mit Beweis: die neue .sav-Datei.

Weg (gemessen/abgelesen 30.09.2026): {"optionen": 3} oeffnet im laufenden Spiel
den Speichern-Dialog; der Knopf {"laden": 3} speichert nur, wenn im aktiven
Textfeld ein Name mit Laenge > 0 steht. Die Textablage des Spiels:
  DAT_UserTextHandlerState = 0x01652740   (+0x0 textArrayIndex)
  textContentLengthArray   = 0x016527D0   (int[16])
  textCursorIndexArray     = 0x01652810   (int[16])
  textArray                = 0x01652890   (char[16][250])
Namensregel (Daniel): <Meilenstein> <Was getestet wird> <Karte> T<Tick>, <= 32 Zeichen.
Gibt es den Namen schon, fragt das Spiel "Datei ueberschreiben?" - {"dialogJa": true}
beantwortet das (gemessen). Jede gespeicherte Fassung wird mit Uhrzeit nach
data/research/spielstaende/ kopiert.

Aufruf:  uv run python -m selfaware.game.ucp.speichern "M7-01 Speichertest Grumpy T1100"
Als Baustein:  from speichern import speichere; pfad = speichere("M7-03 ...")
"""

from selfaware import workspace as _workspace
import os, shutil, struct, sys, time

from selfaware.game.ucp.laden import befehl, peek

TEXT_INDEX, LAENGEN, CURSOR, TEXTE = 0x01652740, 0x016527D0, 0x01652810, 0x01652890
ORDNER = os.path.expandvars(r"%USERPROFILE%\Documents\Stronghold Crusader\Saves")
SAMMLUNG = os.path.join(_workspace.DATA, 'spielstaende')

def speichere(name):
    """Speichert unter diesem Namen; gibt den Pfad der Kopie in data/research/spielstaende/ zurueck."""
    roh = name.encode("latin-1") + b"\0"
    if len(roh) > 33:
        raise RuntimeError("Name zu lang (%d Zeichen, hoechstens 32)" % (len(roh) - 1))
    ziel = os.path.join(ORDNER, name + ".sav")
    vorher = os.path.getmtime(ziel) if os.path.exists(ziel) else None

    print(befehl({"optionen": 3}, 1.5))                               # Dialog oeffnen
    idx = peek(TEXT_INDEX)[0]
    print("aktives Textfeld:", idx)
    if idx > 15:
        raise RuntimeError("aktives Textfeld unbrauchbar (%s)" % idx)
    basis = TEXTE + idx * 250
    roh += b"\0" * (-len(roh) % 4)
    for i in range(0, len(roh), 4):                                   # Name wortweise schreiben
        befehl({"poke": basis + i, "wert": struct.unpack("<i", roh[i:i + 4])[0]}, 0.5)
    befehl({"poke": LAENGEN + idx * 4, "wert": len(name)}, 0.5)
    befehl({"poke": CURSOR + idx * 4, "wert": len(name)}, 0.5)
    print("Laenge im Feld jetzt:", peek(LAENGEN + idx * 4)[0])
    print(befehl({"laden": 3}, 3.0))                                  # Knopf Speichern
    if vorher is not None:                                            # Name gibt es: Spiel fragt "Ueberschreiben?"
        print(befehl({"dialogJa": True}, 3.0))

    for _ in range(10):
        if os.path.exists(ziel) and os.path.getmtime(ziel) != vorher:
            time.sleep(1)                                             # Schreiben abwarten
            kopie = os.path.join(SAMMLUNG, "%s_%s.sav" % (name, time.strftime("%Y%m%d-%H%M%S")))
            os.makedirs(SAMMLUNG, exist_ok=True)
            shutil.copy2(ziel, kopie)                                 # jede Fassung aufheben, auch beim Ueberschreiben
            # nur Dateinamen ausgeben: Mitschriften landen im oeffentlichen Repo (keine persoenlichen Pfade)
            print("GESCHAFFT: %s (%d Byte), Kopie data/research/spielstaende/%s" % (
                os.path.basename(ziel), os.path.getsize(ziel), os.path.basename(kopie)))
            return kopie
        time.sleep(1)
    raise RuntimeError("keine neue Datei %s nach 10 s" % ziel)

if __name__ == "__main__":
    try:
        speichere(sys.argv[1])
    except RuntimeError as e:
        print("NICHT GESCHAFFT:", e); sys.exit(1)
