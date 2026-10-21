# -*- coding: utf-8 -*-
"""Spielstand laden ohne Klick (M7.02) - per Name, mit Beleg: Spielzeit und Bild.

Weg (Menue-Handbuch 02.09. + gemessen 30.09.2026):
  Im Spiel oeffnet {"optionen": 2} den Lade-Dialog; im Hauptmenue erst
  {"hauptmenue": 8} (Einstellungen), dann {"optionen": 2}.
  Liste im Speicher: Anzahl 0x0112661C; Eintrag n (0 = oben) ist die Namens-
  nummer k = [0x01126E28 + 4n]; der Name steht bei 0x11BFCF8 + k*0x3E9
  (getLoadedMapNameForIndex, 0x0046C2E0). Geladen wird Eintrag
  n = markierte Zeile [0x01126624] + Scrollstand [0x01126628], dann {"laden": 2}.
  Alles in EINEM Auftrag, sonst greift der Poll dazwischen.
Laden hebt die Pause auf: vorher die Lade-Pause scharf machen ({"ladepause": true},
haelt beim ersten Tick an, an dem die Spielzeit springt ODER die Pause aufgehoben
ist - so auch beim Wiederladen eines Stands mit derselben Spielzeit),
danach zur Sicherheit noch einmal pausieren und pruefen, dass die Spielzeit steht.
(Eine Tick-Pause auf "jetzt + 1" greift nur, wenn der geladene Stand spaeter liegt.)
Jeder Befehl geht als Liste ({"befehle": [...]}) raus: im Hauptmenue reicht das
Modul nur Listen und wenige Einzelbefehle an die Logik durch (init.lua).

Aufruf:  python laden.py "<Name>"      (Name wie in der Liste, ohne .sav)
         python laden.py --liste       (nur die Liste zeigen)
Als Baustein:  from laden import lade_stand; tick = lade_stand("M7-01 ...")
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from befehl import sende, neue_id, SPIEL

ANZAHL, MARKIERT, SCROLL, SICHTBAR = 0x0112661C, 0x01126624, 0x01126628, 0x0112662C
LISTE, NAMEN, NAMENSLAENGE = 0x01126E28, 0x11BFCF8, 0x3E9
TICK, PAUSE, ANSICHT = 0x0117CADC, 0x01FEA054, 0x01FE7D1C
HAUPTMENUE = 41
BILDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten", "bilder")

def befehl(cmd, warte=0.8, bis=None):
    """Ein Befehl, in eine Liste verpackt - so kommt er auch im Hauptmenue an.
    bis = Text der Antwortzeile: dann nur so lange warten, bis sie da ist (hoechstens warte s)."""
    c = dict(cmd)
    c.setdefault("player", 1)
    c["id"] = neue_id()
    return sende({"befehle": [c]}, warte, bis=bis)

def peek(adr, n=1):
    # auf die Antwort horchen statt fest 0,6 s zu warten (05.10.: eine Abfrage je Runde machte jede Runde ~600 Ticks lang)
    for z in sende({"player": 1, "peek": adr, "worte": n}, 0.6, bis="PEEK 0x%08X" % adr):
        if "PEEK" in z:
            return [int(x, 16) & 0xFFFFFFFF for x in z.split(": ", 2)[-1].split()]
    raise RuntimeError("keine Antwort auf peek 0x%08X" % adr)

def oeffne_dialog():
    if peek(ANSICHT)[0] == HAUPTMENUE:
        befehl({"hauptmenue": 8}, 1.5)                            # Einstellungen (Schluessel)
    befehl({"optionen": 2}, 1.5)                                  # Lade-Dialog

def liste():
    anz = peek(ANZAHL)[0]
    if not 0 < anz <= 500:
        raise RuntimeError("Liste unplausibel (Anzahl %d) - ist der Lade-Dialog offen?" % anz)
    namen = []
    for k in peek(LISTE, anz):
        roh = b"".join(w.to_bytes(4, "little") for w in peek(NAMEN + k * NAMENSLAENGE, 10))
        namen.append(roh.split(b"\0")[0].decode("latin-1"))
    return namen

def bild(datei):
    befehl({"bild": "karte"}, 2.0)
    from PIL import Image
    os.makedirs(BILDER, exist_ok=True)
    Image.open(os.path.join(SPIEL, "ucp", "villagestudio", "vs_karte.bmp")).save(os.path.join(BILDER, datei))
    return os.path.join(BILDER, datei)

PLATZ_ICH = 0x01A275DC       # GameSynchronyState.currentPlayerSlotID (0x0191D768 + 0x109E74)
MENSCH = 0x0191DE10          # GameSynchronyState.currentPlayerFullIDArray int[9] (-1 = kein Mensch auf dem Platz)
KI = 0x0191DE7C              # GameSynchronyState.currentAIArray int[9]
SPIELMODUS = 0x0191DD84      # GameSynchronyState +0x61C: 99 nach jedem Laden/Gefecht, 0 nach einem Spielstart (gemessen 23:58)


def lade_stand(ziel, mit_bild=True, platz=None, platz_vorher=True):
    """Laedt den Stand, haelt beim ersten Tick an und gibt diese Spielzeit zurueck.
    platz_vorher=False nur fuer den Gegenlauf in pruef_laden.py (Pruef-Modus: Platz NICHT vorher setzen)."""
    oeffne_dialog()
    namen = liste()
    if ziel not in namen:
        raise RuntimeError("'%s' steht nicht in der Liste (%d Eintraege)" % (ziel, len(namen)))
    n = namen.index(ziel)
    scroll = max(0, n - 15)
    zeile = n - scroll
    vorher = peek(TICK)[0]
    print("Eintrag %d '%s' -> Scrollstand %d, Zeile %d; Spielzeit vorher %d" % (n, ziel, scroll, zeile, vorher))

    # (B-150: platz=1 traegt den Menschen schon im ersten geladenen Takt ein - sonst setzt die Niederlage-Pruefung gameOver 1)
    print(befehl(dict({"ladepause": True}, **({"platz": platz} if platz else {}))))   # haelt beim ersten Tick nach dem Laden
    antwort = sende({"befehle": [
        {"id": neue_id(), "player": 1, "poke": SCROLL, "wert": scroll},
        {"id": neue_id(), "player": 1, "poke": MARKIERT, "wert": zeile}]
        # B-159 (21.10. 23:55, laden_spur_20261021_233820 + _234313): kurz vor dem Wechsel in die Partie stehen wieder die Werte
        # von VOR dem Laden - Platz und Mensch-Eintraege (nach einem Spielstart Platz 0, Mensch alle -1 -> Niederlage-Pruefung
        # ohne Menschen). Jedes Laden nach einer gespielten Partie (Platz 1, Mensch[1] 1) kippte nicht. Darum beides vorher
        # setzen - OHNE "player", sonst legt alsSpieler den alten Platz gleich wieder zurueck (Spur 233820: 16.800 ms)
        # 21.10. 23:56: Platz + Mensch vorher (Fix A) kippte nach einem echten Neustart trotzdem -> widerlegt. Fix B: Spielmodus
        # 0x0191DD84 = 99 (Einzelspieler-Gefecht; nach jedem Laden 99, nach einem Spielstart 0 - abbild_menue_*.npz). Der Ladecode
        # traegt den Menschen nur bei diesem Spielmodus selbst ein (LoadAndSaveGameButtonLogic 0x00495704)
        + ([{"id": neue_id(), "poke": SPIELMODUS, "wert": 99}] if platz and platz_vorher else [])
        + [{"id": neue_id(), "player": 1, "laden": 2}]}, 4.0, bis="LADEPAUSE: Laden erkannt")
    # 06.10.: auf die Lade-Meldung warten, nicht auf die Quittung - die kommt im selben Tick wie der Knopfdruck, das
    # Laden selbst erst danach (seit der Quittung 05.10. 23:01 meldete jedes Laden "kein Laden erkannt")
    print(antwort)
    befehl({"pause": True})                                       # Sicherheitsnetz
    befehl({"ladepause": "aus"})                                  # nichts scharf zuruecklassen
    erkannt = [z for z in antwort if "LADEPAUSE: Laden erkannt" in z]
    # (21.10. 23:45, Daniel: "jedes Mal 2-3 Minuten"): keine Sekunde mehr fest warten - die Pause-Marke ist der Zustand, der die
    # Spielzeit anhaelt (gemessen 30.09.: der Taktgeber laeuft in der Pause weiter, die Spielzeit steht)
    t2 = peek(TICK)[0]
    pause = peek(PAUSE)[0]
    print("Spielzeit nachher %d, Pause %d" % (t2, pause))
    if not erkannt:
        raise RuntimeError("die Lade-Pause hat kein Laden erkannt (Tick jetzt %d) - Stand unsicher" % t2)
    if pause != 1:
        raise RuntimeError("Spiel steht nicht still (Tick %d, Pause %d)" % (t2, pause))
    if mit_bild:
        print("Bild:", bild("m7-02_%s_t%d.png" % (ziel.replace(" ", "_"), t2)))
    return t2

def main():
    if sys.argv[1] == "--liste":
        oeffne_dialog()
        for n, name in enumerate(liste()):
            print(n, name)
        return
    try:
        t = lade_stand(sys.argv[1])
    except RuntimeError as e:
        print("NICHT GESCHAFFT:", e); sys.exit(1)
    print("GELADEN: '%s' bei Tick %d" % (sys.argv[1], t))

if __name__ == "__main__":
    main()
