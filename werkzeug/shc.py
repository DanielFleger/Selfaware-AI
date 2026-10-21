# -*- coding: utf-8 -*-
"""B-150 SHC-Schnellwerkzeug - EIN Einstieg fuer alles, was ein Versuch braucht (Daniel 21.10.2026 18:42: "Skripte fuer
gewisse Dinge, die schnell funktionieren muessen ... idiotensicher und instant ... ich kann nicht jedes Mal von vorne
anfangen"). Jeder Befehl prueft den Spielzustand VORHER und NACHHER und bricht mit "FEHLER: ..." ab, statt still auf einer
beendeten Partie weiterzumachen (21.10.: ein Sandkasten-Versuch lief auf gameOver 1, weil der Spielstand aus der laufenden
Partie statt ueber das Hauptmenue geladen wurde - die Falle steht seit 05.10. in serie.zuruecksetzen).

Aufruf (Instanz ueber SHC_INSTANZ, ohne Angabe 5):
  python werkzeug/shc.py zustand
  python werkzeug/shc.py start
  python werkzeug/shc.py menue
  python werkzeug/shc.py gefecht karte="Liga_Grumpy Neighbors" gegner=1 [plaetze=0,2] [verbuendete=] [gold=1000]
                         [tempo=40] [startgueter=1] [ausgleich=3]
        gegner      = KI-Nummern der Gegner, z. B. 1,2,3 (1 = Rotkaeppchen ...); Anzahl = Zahl der Eintraege
        plaetze     = Burgplatz je Spieler (Burgnummer der Karte - 1): erst wir, dann die Gegner in Reihenfolge
        verbuendete = welche Gegner (1-basiert in der gegner-Liste) mit uns verbuendet sind, z. B. verbuendete=2
        gold        = Gold je Spieler nach dem Start: eine Zahl fuer alle oder Liste (wir, Gegner 1, ...)
  python werkzeug/shc.py speichern name="S1 Sandkasten Franz T40470"      (hoechstens 32 Zeichen)
  python werkzeug/shc.py laden name="B140 Burg Franz T40126"
  python werkzeug/shc.py editor [groesse=4]       Sandbox im Spiel: leere Karte im Landschaftseditor, Zeit laeuft
  python werkzeug/shc.py setze spieler=2 typ=22 x=240 y=200 [anzahl=1]
  python werkzeug/shc.py sandkasten [name="B140 Burg Franz T40126"] [franz_heer=nein]
        laedt ueber das Hauptmenue, raeumt beide Heere ab (Lords bleiben), Franz' KI ohne Waren, haelt an

Als Baustein:  import shc; shc.laden("..."); z = shc.zustand()
Jede Zeile der Ausgabe beginnt mit "OK:" oder "FEHLER:"; der Rueckgabewert des Programms ist 0 bzw. 1.
"""
import os
import subprocess
import sys
import time

os.environ.setdefault("SHC_INSTANZ", "5")
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

ANSICHT, GAMEOVER, PAUSE, TICK = 0x01FE7D1C, 0x0117D500, 0x01FEA054, 0x0117CADC
PLATZ, MENSCH = 0x01A275DC, 0x0191DE10
IN_PARTIE, HAUPTMENUE, ENDBILD = 14, 41, 30
STANDARD_STAND = "B140 Burg Franz T40126"
# Kaempfer (wie feldzug.TRUPPE ohne Lord 55): Bogen, Armbrust, Speer, Pike, Streitkolben, Schwert, Ritter, Moench, arab. Truppen
SOLDATEN = {22, 23, 24, 25, 26, 27, 28, 37, 70, 71, 72, 73, 74, 75, 76}


class Fehler(RuntimeError):
    pass


def _s32(v):
    return v - (1 << 32) if v & 0x80000000 else v


def zustand():
    """Was laeuft gerade? dict mit antwortet, ansicht, text, gameover, pause, tick, platz, mensch (Mensch-Eintrag Platz 1)."""
    try:
        # verpackt ({"befehle": [...]}), sonst kommt der Lesebefehl in Menues nicht an (21.10. 18:51: im Menue "Eigene
        # Szenarien" meldete die unverpackte Abfrage "Spiel antwortet nicht", obwohl es lief - so macht es editor_test.peek)
        from editor_test import peek as _peek

        def peek(adr):
            w = _peek(adr)
            if w is None:
                raise RuntimeError("keine Antwort auf peek 0x%08X" % adr)
            return w
        a, g, p, t, pl, m = (peek(ANSICHT)[0], peek(GAMEOVER)[0], peek(PAUSE)[0], peek(TICK)[0], peek(PLATZ)[0],
                             _s32(peek(MENSCH + 4)[0]))
    except Exception as e:                                   # Kanal antwortet nicht: Spiel aus oder Modul nicht aktiv
        return {"antwortet": False, "text": "Spiel antwortet nicht (%s)" % str(e)[:80]}
    if a == IN_PARTIE:
        text = "Partie VORBEI (gameOver 1)" if g else "Partie laeuft" + (" (angehalten)" if p else "")
    else:
        text = {HAUPTMENUE: "Hauptmenue", ENDBILD: "Endbildschirm (Partie vorbei)"}.get(a, "Ansicht %d" % a)
    return {"antwortet": True, "ansicht": a, "text": text, "gameover": g, "pause": p, "tick": t, "platz": pl, "mensch": m}


def partie_sicher(z=None):
    """Bricht ab, wenn keine bespielbare Partie laeuft (Ansicht 14, gameOver 0, wir auf Platz 1 und als Mensch eingetragen)."""
    z = z or zustand()
    if not (z.get("antwortet") and z["ansicht"] == IN_PARTIE and z["gameover"] == 0 and z["platz"] == 1 and z["mensch"] == 1):
        raise Fehler("keine bespielbare Partie: %s" % z)
    return z


def start():
    """Spiel der Instanz starten, falls es nicht schon antwortet; wartet bis das Modul antwortet (hoechstens 120 s)."""
    z = zustand()
    if z["antwortet"]:
        return "laeuft schon: %s" % z["text"]
    inst = os.environ["SHC_INSTANZ"]
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", os.path.join(HIER, "spiel_starten.ps1"),
                    "-Instanz", inst], check=False, capture_output=True, text=True, timeout=60)
    ende = time.time() + 120
    while time.time() < ende:
        time.sleep(2)
        z = zustand()
        if z["antwortet"]:
            return "gestartet: %s" % z["text"]
    raise Fehler("Instanz %s antwortet 120 s nach dem Start nicht" % inst)


def menue():
    """Laufende oder beendete Partie -> Hauptmenue, angehalten (serie.zuruecksetzen, gemessen seit 05.10.)."""
    from serie import zuruecksetzen
    text = zuruecksetzen()
    z = zustand()
    if z.get("ansicht") != HAUPTMENUE:
        raise Fehler("Hauptmenue nicht erreicht: %s" % z)
    return text


def laden(name=STANDARD_STAND):
    """Spielstand IMMER ueber das Hauptmenue laden, dann uns auf Platz 1 eintragen; prueft danach die Partie."""
    from laden import lade_stand, befehl
    menue()
    tick = lade_stand(name, mit_bild=False, platz=1)
    befehl({"eigenerPlatz": 1}, 0.8)
    partie_sicher()
    # Gegenprobe im Lauf: 200 Takte laufen lassen - die Niederlage-Pruefung darf die Partie dabei nicht beenden
    befehl({"pause": False, "tempo": 40}, 0.3)
    t0 = zustand()["tick"]
    ende = time.time() + 60
    while zustand()["tick"] < t0 + 200 and time.time() < ende:
        time.sleep(0.2)
    befehl({"pause": True}, 0.3)
    z = partie_sicher()
    return "'%s' geladen bei Tick %d, nach 200 Takten Probelauf: %s (Tick %d)" % (name, tick, z["text"], z["tick"])


def speichern(name):
    """Speichert die laufende Partie (nur wenn bespielbar); gibt den Pfad der Kopie."""
    from speichern import speichere
    partie_sicher()
    pfad = speichere(name)
    partie_sicher()
    return "gespeichert als '%s' (%s)" % (name, os.path.basename(str(pfad)))


def _liste(wert, art=int):
    return [art(x) for x in str(wert).split(",") if x.strip() != ""] if wert not in (None, "") else []


def gefecht(karte="Liga_Grumpy Neighbors", gegner="1", plaetze="", verbuendete="", gold="", tempo="40", startgueter="1",
            ausgleich="3"):
    """Frisches Gefecht ueber das Hauptmenue (eigenesGefecht wie karten_holen.gefecht_frisch), wartet bis alle Bergfriede
    stehen, haelt an, traegt uns auf Platz 1 ein, setzt Gold; prueft danach die Partie."""
    import befehl as kanal
    from laden import befehl, peek
    from karten_holen import bergfriede
    kis = _liste(gegner)
    if not kis:
        raise Fehler("gegner=... fehlt (KI-Nummern, z. B. gegner=1,2)")
    pl = _liste(plaetze)
    freunde = set(_liste(verbuendete))
    menue()
    befehl({"tempo": int(tempo)}, 1.0, bis="TEMPO")
    g = {"eigenesGefecht": True, "karte": karte, "ki": kis[0], "kis": kis, "gegner": len(kis),
         "ausgleich": int(ausgleich), "startgueter": int(startgueter),
         "teams": [0 if i + 1 in freunde else 1 for i in range(len(kis))]}
    if pl:
        if len(pl) != 1 + len(kis):
            raise Fehler("plaetze braucht %d Eintraege (wir + %d Gegner), bekam %d" % (1 + len(kis), len(kis), len(pl)))
        liste = [246] * 8
        for spieler, platz in enumerate(pl):
            liste[platz] = spieler
        g["startliste"] = liste
    z = kanal.sende(g, 4, bis="LaunchSkirmishGame zurueck")
    befehl({"pause": False}, 0.5)
    ende = time.time() + 90
    while time.time() < ende:
        if len(bergfriede()) >= 1 + len(kis) and peek(TICK)[0] >= 150:
            break
        time.sleep(0.5)
    else:
        befehl({"pause": True}, 0.5)
        raise Fehler("nach 90 s stehen nicht alle Bergfriede (%d von %d): %s" % (len(bergfriede()), 1 + len(kis), z[-3:]))
    befehl({"pause": True}, 0.5)
    befehl({"eigenerPlatz": 1}, 0.8)
    golds = _liste(gold)
    if golds:
        for sp in range(1, 2 + len(kis)):
            befehl({"player": sp, "gold": golds[min(sp - 1, len(golds) - 1)]}, 0.5)
    zst = partie_sicher()
    return "Gefecht auf '%s' gegen KI %s (Teams %s), Tick %d, %s" % (karte, kis, g["teams"], zst["tick"], zst["text"])


def sandkasten(name=STANDARD_STAND, franz_heer="nein"):
    """Laden (ueber das Hauptmenue), beide Heere ohne Lord abraeumen, Spieler 2 ohne Waren, kurz laufen lassen, anhalten.
    Prueft danach: Partie bespielbar und beide Lords leben."""
    from laden import befehl
    from befehl import SPIEL
    sys.path.insert(0, os.path.join(HIER, "..", "..", "Selfaware-AI-kern", "src"))
    from selfaware.game.kern_leitung import Leitung
    laden(name)
    befehl({"pause": False, "tempo": 40}, 0.3)            # ein paar Takte, damit Kern und Lagebild die neue Welt haben
    t0 = zustand()["tick"]
    while zustand()["tick"] < t0 + 5:
        time.sleep(0.1)
    befehl({"pause": True}, 0.3)
    befehl({"leereKI": [2]}, 0.5)
    befehl({"toeteAlle": {"spieler": 1, "ohneLord": True}}, 0.8)
    if franz_heer != "ja":
        befehl({"toeteAlle": {"spieler": 2, "ohneLord": True}}, 0.8)
    befehl({"pause": False, "tempo": 100}, 0.3)            # Steintod abwarten
    t0 = zustand()["tick"]
    while zustand()["tick"] < t0 + 400:
        time.sleep(0.2)
    befehl({"pause": True}, 0.3)
    z = partie_sicher()
    w = Leitung(SPIEL).lesen()
    lords = {e["besitzer"] for e in w.einheiten.values() if e["typ"] == 55 and e["leben"] > 0}
    if not {1, 2} <= lords:
        raise Fehler("Lords fehlen nach dem Abraeumen (leben: Spieler %s)" % sorted(lords))
    soldaten, volk = {}, {}
    for e in w.einheiten.values():
        if e["leben"] > 0 and e["typ"] != 55 and e["besitzer"] in (1, 2):
            ziel = soldaten if e["typ"] in SOLDATEN else volk
            ziel[e["besitzer"]] = ziel.get(e["besitzer"], 0) + 1
    if soldaten.get(1) or (franz_heer != "ja" and soldaten.get(2)):
        raise Fehler("nach dem Abraeumen stehen noch Soldaten: %s" % soldaten)
    return ("Sandkasten '%s' bereit bei Tick %d, Lords 1+2 leben, Soldaten %s, Arbeiter/Stadtvolk (bleiben) %s"
            % (name, z["tick"], soldaten or "keine", volk))


def editor(groesse="4"):
    """Sandbox im Spiel (Daniel 18:51 "Eigene Szenarien -> Neue Karte: eine leere Karte"): Rezept aus dem Handbuch,
    Abschnitt "Testen im Karteneditor" (17.10.) - jeder Schritt an der Menueansicht geprueft. Im Editor laeuft die Zeit,
    Einheiten handeln und kaempfen, es gibt keine Arbeiter und keine KI. groesse: Knopf der Kartengroesse (1 = 160x160,
    4 = 400x400)."""
    from laden import befehl
    menue()
    schritte = [({"hauptmenue": 9}, 44, "Eigene Szenarien"),
                ({"knopf": "CustomScenarios_Main", "nr": 2}, 18, "Kartentyp"),
                ({"knopf": "NewMapMaptype_Buttons", "nr": 3}, 31, "Kartengroesse"),
                ({"knopf": "NewMapMapsize_Buttons", "nr": int(groesse)}, 17, "Karteneigenschaften"),
                ({"menue": 12}, None, "Landschaftseditor")]
    weg = []
    for b, soll, name in schritte:
        befehl(b, 1.5)
        time.sleep(1.0)
        a = zustand().get("ansicht")
        weg.append("%s=%s" % (name, a))
        if soll is not None and a != soll:
            raise Fehler("Editor-Weg haengt bei '%s': Ansicht %s statt %s (%s)" % (name, a, soll, ", ".join(weg)))
    befehl({"pause": False}, 0.5)
    t0 = zustand()["tick"]
    time.sleep(2.0)
    z = zustand()
    if z["tick"] <= t0:
        raise Fehler("im Editor laeuft die Zeit nicht (Tick %d -> %d, %s)" % (t0, z["tick"], ", ".join(weg)))
    return "Editor offen (Ansicht %d), Zeit laeuft (Tick %d -> %d); Weg: %s" % (z["ansicht"], t0, z["tick"], ", ".join(weg))


def setze(spieler="1", typ="26", x="200", y="200", anzahl="1"):
    """Einheiten setzen (Editor oder Partie). Gemessen 17.10.: sie stehen 1 Feld weiter als angegeben (x/y +1)."""
    import re
    from laden import befehl
    for z in befehl({"setzeEinheit": {"spieler": int(spieler), "typ": int(typ), "x": int(x), "y": int(y),
                                      "anzahl": int(anzahl)}}, 1.5):
        m = re.search(r"Nummern ([0-9,]+)", z)
        if m:
            nrs = [int(n) for n in m.group(1).split(",") if int(n) > 0]
            if len(nrs) != int(anzahl):
                raise Fehler("nur %d von %s gesetzt: %s" % (len(nrs), anzahl, z))
            return "Spieler %s Typ %s x%s bei (%s,%s): Nummern %s" % (spieler, typ, anzahl, x, y, nrs)
    raise Fehler("setzeEinheit ohne Antwort")


def zustand_text():
    z = zustand()
    return "%s | %s" % (z["text"], z)


BEFEHLE = {"zustand": zustand_text, "start": start, "menue": menue,
           "gefecht": gefecht, "speichern": speichern, "laden": laden, "sandkasten": sandkasten, "editor": editor,
           "setze": setze}


def main(argv):
    if not argv or argv[0] not in BEFEHLE:
        print(__doc__)
        return 1
    args = dict(x.split("=", 1) for x in argv[1:])
    try:
        print("OK:", BEFEHLE[argv[0]](**args), flush=True)
        return 0
    except Fehler as e:
        print("FEHLER:", e, flush=True)
        return 1
    except Exception as e:                                   # auch Unerwartetes laut melden, nie still
        print("FEHLER: %s: %s | Zustand jetzt: %s" % (type(e).__name__, e, zustand()), flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
