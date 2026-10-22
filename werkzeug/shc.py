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
GAMEOVER_ZEIT = 0x0117C888       # gameOverTime: Rechneruhr beim "Spiel vorbei", Endbildschirm 9-10 s spaeter (M4.04)
IN_PARTIE, HAUPTMENUE, ENDBILD = 14, 41, 30
STANDARD_STAND = "B140 Burg Franz T40126"
# Alles, was kaempft oder schiesst (aus dem Typen-Verzeichnis des Spiels, UnitType, 21.10.2026): Truppen 22-28, Moench 37,
# arab. Truppen 70-76, Belagerung/Turmwaffen 39-41 58-61 77 (Feuerballiste 77 toetete in Feuer-Test 4 alle Streitkolben),
# Zelt 50, Ingenieur 30, Leiter 29, Tunnelgraeber 5, Kampfhunde 67. Lord 55 nicht. NICHT dabei (gemessen 19:14, Arbeiter):
# Typ 52 UT_HUNTERDOG = unsere Jaeger aus den Jagdhuetten, Typ 10 Pechmann (arbeitet in der Pechgrube).
SOLDATEN = {5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 39, 40, 41, 50, 58, 59, 60, 61, 67, 70, 71, 72, 73, 74, 75, 76, 77}


class Fehler(RuntimeError):
    pass


def _s32(v):
    v &= 0xFFFFFFFF
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


def neustart():
    """Instanz beenden (spiel.py: Stufe 1 = unser Modul beendet das Spiel, dann Fenster schliessen, dann hart) und starten."""
    r = subprocess.run([sys.executable, os.path.join(HIER, "spiel.py"), "beenden"], capture_output=True, text=True, timeout=120,
                       env=dict(os.environ))
    if r.returncode != 0:
        raise Fehler("Instanz liess sich nicht beenden: %s" % (r.stdout.strip().splitlines() or ["?"])[-1])
    return start()


def menue():
    """Laufende oder beendete Partie -> Hauptmenue, angehalten (serie.zuruecksetzen, gemessen seit 05.10.)."""
    from serie import zuruecksetzen
    text = zuruecksetzen()
    z = zustand()
    if z.get("ansicht") != HAUPTMENUE:
        raise Fehler("Hauptmenue nicht erreicht: %s" % z)
    return text


def laden(name=STANDARD_STAND, platz=1, versuche=1, platz_vorher=True):
    """Laedt den Stand EINMAL (Daniel 21.10. 23:46 "warum laedst du nicht einfach direkt das Richtige"): endet die Partie gleich
    nach dem Laden, ist das ein Fehler, der gemeldet wird - kein stilles Neuladen mehr (vorher bis zu 3 Versuche, B-159).
    versuche > 1 nur, wenn ein Aufrufer das ausdruecklich will."""
    for versuch in range(1, versuche + 1):
        try:
            return _laden_einmal(name, platz, platz_vorher) + ("" if versuch == 1 else " (Versuch %d)" % versuch)
        except Fehler as e:
            if "Partie endete im Probelauf" not in str(e) and "keine bespielbare Partie" not in str(e) or versuch == versuche:
                raise
            print("WARNUNG: Partie endete gleich nach dem Laden (Versuch %d) - noch einmal laden | %s" % (versuch, str(e)[:160]),
                  flush=True)


def _laden_einmal(name=STANDARD_STAND, platz=1, platz_vorher=True):
    """Spielstand IMMER ueber das Hauptmenue laden, dann uns auf platz eintragen; prueft danach die Partie."""
    from laden import lade_stand, befehl
    menue()
    try:
        try:
            tick = lade_stand(name, mit_bild=False, platz=platz, platz_vorher=platz_vorher)
        except (RuntimeError, TimeoutError) as e:
            if "kein Laden erkannt" not in str(e) and "WIRKUNGSMARKE FEHLT: LADEPAUSE: Laden erkannt" not in str(e):
                raise
            # 21.10. 20:06 und 20:33 (L183): nach einer Sandkasten-Partie drueckte das Modul den Laden-Knopf (ok=true), das Spiel
            # lud aber nichts - auch andere Spielstaende nicht; ein Neustart der Instanz half jedes Mal. Darum EINMAL neu starten
            # und noch einmal laden (Daniel 18:42: "idiotensicher und instant")
            print("WARNUNG: Laden hing (%s) - Instanz wird neu gestartet" % e, flush=True)
            neustart()
            menue()
            tick = lade_stand(name, mit_bild=False, platz=platz, platz_vorher=platz_vorher)
        befehl({"eigenerPlatz": platz}, 0.8)
    finally:
        # B-159 (22.10. 00:08): Niederlage-Pruefung erst wieder an, wenn unser Platz steht - und nie ausgeschaltet zuruecklassen
        befehl({"niederlagePruefung": True}, 0.5)
    z = zustand()
    # B-159 (21.10. 23:45): steht gameOver schon auf 1, ist das Sieg/Niederlage-Fenster an - checkSkirmishGameDefeat (0x00486600)
    # setzt beides zusammen, und Zuruecksetzen der Flags half nicht (21.10. 21:08, das Fenster blieb). Darum neu laden statt flicken
    if z.get("ansicht") != IN_PARTIE or z.get("gameover") != 0:
        raise Fehler("Partie endete im Probelauf nach dem Laden: %s | Melder: %s" % (z, letztes_spielende()))
    # Gegenprobe: genau EIN Spieltakt. checkSkirmishGameDefeat laeuft in jedem processGameTick ohne Bedingung davor (Aufruf bei
    # 0x0045CFAF) und schaltet das Endfenster nur zusammen mit gameOver ein - steht nach einem Takt gameOver 0, kommt kein
    # Endbildschirm. (Vorher 200 Takte + 15 s Rechnerzeit, abgeleitet aus den 9-10 s bis zum Endbildschirm nach gameOver 1.)
    t0, beginn = zustand()["tick"], time.time()
    befehl({"pause": False, "tempo": 40}, 0.3)
    while zustand()["tick"] < t0 + 1 and time.time() < beginn + 10:
        time.sleep(0.02)
    befehl({"pause": True}, 0.3)
    z = partie_sicher()
    if z.get("gameover") != 0 or z["tick"] < t0 + 1:
        raise Fehler("Partie endete im Probelauf nach dem Laden: %s | Melder: %s" % (z, letztes_spielende()))
    zurueck = ""
    return "'%s' geladen bei Tick %d%s, Probelauf %d Takte / %.0f s: %s (Tick %d)" % (
        name, tick, zurueck, z["tick"] - t0, time.time() - beginn, z["text"], z["tick"])


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


def sandkasten(name=STANDARD_STAND, franz_heer="nein", nur_soldaten="nein", frisch="nein"):
    """Laden (ueber das Hauptmenue), beide Heere ohne Lord abraeumen, Spieler 2 ohne Waren, kurz laufen lassen, anhalten.
    Prueft danach: Partie bespielbar und beide Lords leben.
    21.10. 23:07 (Daniel: "jedes Mal locker 2 Minuten, ohne dass du eine einzige Sache testen kannst"): der fertig abgeraeumte
    Sandkasten wird EINMAL als eigener Spielstand gespeichert ("SK <Stand> <Heer> <Soldaten>"); jeder weitere Aufruf laedt ihn
    direkt - ohne Abraeumen und ohne die 400-Takte-Wartezeiten. frisch=ja baut ihn neu."""
    from laden import befehl
    from befehl import SPIEL
    sys.path.insert(0, os.path.join(HIER, "..", "..", "Selfaware-AI-kern", "src"))
    from selfaware.game.kern_leitung import Leitung
    # (Spielstandnamen hoechstens 32 Zeichen - speichern.speichere): mH/oH = mit/ohne Franz' Heer, nS/aS = nur Soldaten/alle
    kurz = "SK %s %s %s" % (name, "mH" if franz_heer == "ja" else "oH", "nS" if nur_soldaten == "ja" else "aS")
    if frisch != "ja":
        t_a = time.time()
        try:
            text = laden(kurz)
            return "Sandkasten aus Spielstand '%s' in %.0f s: %s" % (kurz, time.time() - t_a, text)
        except RuntimeError as e:                   # Nur ein nachweislich fehlender Cache erlaubt Neubau.
            if "steht nicht in der Liste" not in str(e):
                raise
            print("Sandkasten-Spielstand '%s' nicht ladbar (%s) - baue ihn" % (kurz, str(e)[:100]), flush=True)
    laden(name)
    befehl({"pause": False, "tempo": 40}, 0.3)            # ein paar Takte, damit Kern und Lagebild die neue Welt haben
    t0 = zustand()["tick"]
    while zustand()["tick"] < t0 + 5:
        time.sleep(0.1)
    befehl({"pause": True}, 0.3)
    befehl({"leereKI": [2]}, 0.5)
    # nur_soldaten=ja (Daniel 19:07): Arbeiter, Brunnen-Loescher und Stadtvolk bleiben - nur Kaempfer werden abgeraeumt
    welche = {"typen": sorted(SOLDATEN)} if nur_soldaten == "ja" else {}
    # 21.10. 21:00: nach einem Abraeumen stand bei Franz noch 1 Soldat (nachrekrutiert oder nicht erwischt) - bis zu 3 Durchgaenge,
    # jeder geprueft; erst wenn auch der dritte nicht reicht, bricht der Sandkasten ab
    for durchgang in (1, 2, 3):
        befehl({"toeteAlle": dict({"spieler": 1, "ohneLord": True}, **welche)}, 0.8)
        if franz_heer != "ja":
            befehl({"toeteAlle": dict({"spieler": 2, "ohneLord": True}, **welche)}, 0.8)
        befehl({"pause": False, "tempo": 100}, 0.3)            # Steintod abwarten
        t0 = zustand().get("tick", 0)
        ende = time.time() + 60
        while zustand().get("tick", 0) < t0 + 400 and time.time() < ende:
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
        if not (soldaten.get(1) or (franz_heer != "ja" and soldaten.get(2))):
            break
        print("WARNUNG: nach Abraeumen %d stehen noch Soldaten %s - noch einmal" % (durchgang, soldaten), flush=True)
    else:
        raise Fehler("nach 3-mal Abraeumen stehen noch Soldaten: %s" % soldaten)
    try:
        gespeichert = speichern(kurz)
    except Exception as e:
        gespeichert = "NICHT gespeichert (%s)" % str(e)[:100]
    return ("Sandkasten '%s' bereit bei Tick %d, Lords 1+2 leben, Soldaten %s, Arbeiter/Stadtvolk (bleiben) %s | %s"
            % (name, z["tick"], soldaten or "keine", volk, gespeichert))


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


def letztes_spielende(n=1):
    from befehl import letztes_spielende as lese
    return lese(n)


def spielende(n="5"):
    """B-154: die letzten Meldungen des Spielende-Melders (logik.lua) - warum endete die Partie, bewusst oder nicht?"""
    z = letztes_spielende(int(n))
    return "\n".join(z) if z else "noch kein Spielende gemeldet"


BEFEHLE = {"zustand": zustand_text, "start": start, "menue": menue,
           "gefecht": gefecht, "speichern": speichern, "laden": laden, "sandkasten": sandkasten, "editor": editor,
           "setze": setze, "spielende": spielende}


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
