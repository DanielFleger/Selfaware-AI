# -*- coding: utf-8 -*-
"""B-142 Lauf K: Gefecht mit 8 KI-Lords, ohne Maus und ohne eigene Befehle, alles aufgezeichnet. Plan: docs/plans/Plan_Lauf_K.md.

  python -m selfaware.tools.experiments.auge_lauf_k probe --instanz 2 --karte "<Karte>"      kleine Probe: Fenster 200 Takte, Kampf 2.000 Takte
  python -m selfaware.tools.experiments.auge_lauf_k los --instanz 2 --karte "<Karte>" --daniel-ja

Bausteine aus Lauf F: Kanal, Speicher, Rekorder, Anhalten. Gerechnet wird in Takten, echte Zeit nur gegen Haengen.
"""
import argparse
import glob
import json
import os
import struct
import sys
import time

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments.auge_lauf_f import Abbruch, Fehler

KIS = (14, 15, 1, 9, 2, 5, 7, 4)  # die 8 verschiedensten der 16 KI-Saetze, gerechnet aus den Kennwerten in Lauf F
SOLL_LORDS = list(range(1, len(KIS) + 1))  # je Spieler genau ein Lord
LORD = 55
ALLE_PLAETZE = 2500  # maxUnitCount taugt nicht: updateUnits setzt ihn in jedem Takt auf 0 und zaehlt hoch, mitten im Takt fehlen Einheiten (Fehlalarm "letzter Lord" 02.11.)
LORD_PRUEFUNG = 50  # Takte; so genau muss das Ende nicht sein, und jedes Nachsehen liest alle Plaetze
WARTE_MS = 5  # gemessen auf Tempo 40: Die Spielfelder aendern sich in den ersten 5 ms nach dem Hochzaehlen, die Takte liegen 26 ms auseinander (takt_dauer_messen.py)
LORDS_STEHEN = 200  # gemessen: spaetestens Takt 100 auf allen 24 Karten mit 8 Spielern (02.11.), die Grenze ist das Doppelte
FRIEDEN_NORMAL, FENSTER_NORMAL = 1, 2000  # Stufe 1 = 12.000 Takte = 5 Minuten bei Tempo 40; Fenster laut Checkliste
FENSTER_PROBE, ENDE_PROBE = 200, 2000
FRIEDEN_TAKTE = {1: 12000}  # am Start gemessen. Stufe 6 ergibt 0 Takte (02.11.), eine kuerzere Friedenszeit gibt es nicht
TOTAL_NORUSH = 0x0117EF7C  # mapAndTime.totalNoRushTicks
FRIST, FRIST_ENDE = 900, 720  # 15 Minuten hart; ab 12 Minuten endet der Kampf auch ohne letzten Lord. Die 3 Minuten danach: zweimal laden und je 2.000 Takte auf Tempo 40, das sind 50 s
STILLSTAND_K = 5.0  # Massenschlachten sind nicht gemessen, in Lauf F lag die laengste Luecke bei 0,098 s im Dorf
BREMS_ALLE = 150000  # rund 3 Minuten auf Tempo 1000
ENDE_ANSICHTEN = {30, 58, lf.HAUPTMENUE}  # Spiel verloren, Rangliste, Hauptmenue


def karten_kopf(pfad):
    """Wie readMapHeader 0x004752D0: Vor jedem Abschnitt steht seine Laenge. Rueckgabe: typ, spieler, startplaetze (belegte keepPositions); leer, wenn der Kopf nicht so weit reicht."""
    aus = {}
    with open(pfad, "rb") as f:
        def zahl():
            return struct.unpack("<i", f.read(4))[0]

        if zahl() >= 0:
            return aus
        for _ in range(3):  # Vorschaubild, Beschreibung, Takt und Pruefsumme
            n = zahl()
            if n == 0:
                return aus
            f.seek(n, 1)
        if zahl() == 0:
            return aus
        aus["typ"] = zahl()
        f.seek(0x14, 1)
        aus["spieler"] = zahl()
        n = zahl()
        if n == 0:
            return aus
        f.seek(n, 1)
        n = zahl()
        if n >= 16 + 0x40:
            plaetze = struct.unpack_from("<16i", f.read(n), 16)
            aus["startplaetze"] = sum(1 for x in plaetze[::2] if x >= 0)
    return aus


def karten_ordner(n):
    """Dort sucht das Spiel (resolveResourceFileName, Fall FRT_MAPS): erst maps, dann der Kartenordner in Dokumente, das Plugin der Liga legt seine dazu."""
    return [os.path.join(lf.ordner(n), "maps"), os.path.join(os.path.expandvars("%USERPROFILE%"), "Documents", "Stronghold Crusader", "Maps")] + glob.glob(os.path.join(lf.ordner(n), "ucp", "plugins", "Mod-KI-Team-Liga-*", "resources", "maps"))


def passt_fuer_acht(kopf):
    return kopf.get("typ") == 1 and kopf.get("spieler") == len(KIS) and kopf.get("startplaetze") == len(KIS)


def karten_fuer_acht(n):
    """Alle Karten, deren Kopf 8 Spieler und 8 Startplaetze nennt. Name auf Pfad, der erste Ordner gewinnt wie im Spiel."""
    aus = {}
    for o in karten_ordner(n):
        for f in sorted(os.listdir(o)) if os.path.isdir(o) else ():
            if f.endswith(".map") and f[:-4] not in aus and passt_fuer_acht(karten_kopf(os.path.join(o, f))):
                aus[f[:-4]] = os.path.join(o, f)
    return aus


def karte_pruefen(n, karte):
    """Vor dem Start, nicht erst am fehlenden Lord: Das steht in der Kartendatei."""
    for o in karten_ordner(n):
        p = os.path.join(o, karte + ".map")
        if os.path.exists(p):
            kopf = karten_kopf(p)
            if not passt_fuer_acht(kopf):
                raise Fehler(f"Karte {karte} passt nicht fuer {len(KIS)} Lords: {kopf}")
            return kopf
    raise Fehler(f"Karte {karte} liegt in keinem Kartenordner des Spiels")


class SpeicherK(lf.Speicher):
    def lord_besitzer(self):
        roh = self.q.lies(lf.EINHEITEN, ALLE_PLAETZE * lf.E_SCHRITT)

        def feld(i, o):
            return struct.unpack_from("<h", roh, i * lf.E_SCHRITT + o)[0]
        return sorted(feld(i, lf.E_BESITZER) for i in range(1, ALLE_PLAETZE) if feld(i, lf.E_DA) and feld(i, lf.E_TYP) == LORD)

    def lords(self):
        return len(self.lord_besitzer())

    def ansicht(self):
        return self.i32(lf.ANSICHT)

    def frieden(self):
        return self.i32(TOTAL_NORUSH)


class LaufK(lf.Lauf):
    def __init__(self, *a, karte="", speichern=None, laden=None, frieden=FRIEDEN_NORMAL, fenster=FENSTER_NORMAL, ende_takte=None, frist_ende=FRIST_ENDE, **kw):
        super().__init__(*a, **kw)
        self.karte, self.speichern, self.laden = karte, speichern, laden
        self.frieden_stufe, self.fenster, self.ende_takte = frieden, fenster, ende_takte
        self.weich = self.uhr() + frist_ende

    def stillstand_grenze(self):
        return max(STILLSTAND_K, 10.0 / self.tempo)

    def puls_neu(self):
        self.puls = (self.s.takt(), self.uhr())


def gefecht_starten(k, karte, frieden, warte=60, ruhe=time.sleep, startpause=None):
    if k.peek(lf.ANSICHT)[0] != lf.HAUPTMENUE:
        k.befehl({"menue": lf.HAUPTMENUE}, 1.5)
        lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == lf.HAUPTMENUE, 10, "Hauptmenue (Ansicht 41)", ruhe=ruhe)
    k.befehl({"pause": False}, lf.KANAL)  # sonst startet das neue Gefecht eingefroren (selbstspiel.py)
    start = {"eigenesGefecht": True, "karte": karte, "kis": list(KIS), "friedenszeit": frieden, "gegner": 0, "trotzdem": True}
    if startpause is not None:
        start["startpause"] = startpause  # das Spiel haelt bei diesem Takt an, so sieht die Aufzeichnung den Anfang
    k.befehl(start, 5.0)
    lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == lf.IN_PARTIE, warte, "Partie laeuft (Ansicht 14)", ruhe=ruhe)


def anhalten(l):
    steht, t = lf.anhalten_und_pruefen(l.k, l.s, ruhe=l.ruhe)
    if not steht:
        raise Abbruch(f"Der Takt steht nach dem Anhalten nicht (Takt {t})")
    return t


def bremsprobe_k(l, wann):
    """Ein Abzug ist in Lauf K ein Fund, die Massenschlacht misst Lauf S."""
    try:
        lf.bremsprobe(l, wann)
    except Abbruch as e:
        if "bremst" not in str(e):
            raise
        l.wirkung(f"Bremsprobe {wann}", False, text=str(e))


def abschnitt_start(l):
    s = l.s
    if not l.warte_takte(LORDS_STEHEN, lambda: s.lord_besitzer() == SOLL_LORDS):
        b = s.lord_besitzer()
        raise Abbruch(f"Nur {len(set(b))} von {len(KIS)} Lords nach {LORDS_STEHEN} Takten, bei Spieler {b}")
    if s.frieden() <= 0:
        raise Abbruch(f"Friedenszeit greift nicht: Stufe {l.frieden_stufe}, noch {s.frieden()} Takte")
    return {"lords": s.lords(), "frieden": s.frieden()}


def abschnitt_frieden(l):
    grenze = FRIEDEN_TAKTE[l.frieden_stufe] + lf.ABLESEN
    if not l.warte_takte(grenze, lambda: l.s.frieden() == 0):
        raise Abbruch(f"Friedenszeit endet nicht: noch {l.s.frieden()} nach {grenze} Takten")
    bremsprobe_k(l, "am Ende der Friedenszeit")
    return {"takt": l.s.takt()}


def aufnahme_im_stand(l, name, tempo, streng, warte_ms=0):
    """Das Spiel steht: Tempo setzen, Aufzeichnung starten, dann erst weiter. Erst weiter und dann Tempo hiesse 0,3 s auf dem alten Tempo: Die Probe brach daran ab, der erste strenge Takt kam gemischt an (02.11.)."""
    l.k.befehl({"tempo": tempo}, lf.KANAL)
    l.rek.starten(name, tempo, streng=streng, messen=False, warte_ms=warte_ms)  # im stehenden Spiel laeuft kein Takt zum Messen
    lf.warte_auf(l.rek.laeuft, 60, f"Aufzeichnung {name} laeuft", uhr=l.uhr, ruhe=l.ruhe)
    a = l.s.takt()
    l.k.befehl({"pause": False}, lf.KANAL)
    l.tempo = tempo
    l.puls_neu()
    return a


def fenster_aufzeichnen(l, name):
    """Das Spiel steht. Strenge Aufzeichnung, Fenster auf Tempo 40 laufen lassen, wieder anhalten."""
    a = aufnahme_im_stand(l, name, lf.TEMPO_JEDER_TAKT, streng=True, warte_ms=WARTE_MS)
    l.warte_takte(l.fenster)
    b = anhalten(l)
    stand = l.rek.beenden()
    if stand.get("fehlend") or stand.get("gemischt"):
        raise Abbruch(f"Fenster {name}: {stand}")
    return {"von": a, "bis": b, "stand": stand, "datei": l.rek.pfad}


def abschnitt_sichern(l):
    """Am Ende der Friedenszeit speichern, dann das erste Fenster. Geladen wird erst nach dem Kampf: Das Laden rechnet einen Schritt ohne Takt
    und setzt Einheiten mit vollem Leben auf den Tabellenwert, KI-Lords verlieren so ihren Faktor (prepareMap, Probe 02.11.)."""
    t = anhalten(l)
    l.rek.beenden()
    name = f"AugeK {time.strftime('%H%M%S')} T{t}"  # eindeutig: Ein vorhandener Name fragt nach dem Ueberschreiben
    l.speichern(name)
    if l.s.takt() != t:
        raise Abbruch(f"Das Speichern hat den Takt bewegt: {t} auf {l.s.takt()}")
    l.ergebnis["sicherung"] = {"name": name, "t": t}
    return {"name": name, "t": t, "t1": fenster_aufzeichnen(l, "t1")}


def laden_und_fenster(l, name, t, fenster):
    """Aus einer frisch gestarteten Partie, beide Male derselbe Weg. Im Hauptmenue blieb das Laden nach dem Kampf im Ladefenster haengen, erst eine laufende Partie liess es weiter (Lauf K 02.11.)."""
    gefecht_starten(l.k, l.karte, l.frieden_stufe, ruhe=l.ruhe, startpause=1)
    t2 = l.laden(name)
    if t2 != t:
        raise Abbruch(f"Geladen auf Takt {t2} statt {t}")
    return fenster_aufzeichnen(l, fenster)


def abschnitt_laden_vergleichen(l):
    """Zweimal denselben Stand laden, dieselben Takte aufzeichnen. t1 gegen t2 zeigt, was das Laden aendert, t2 gegen t3, ob das Spiel ab dem Laden gleich laeuft. Verglichen wird in der Auswertung."""
    anhalten(l)
    l.rek.beenden()
    g = l.ergebnis["sicherung"]
    f2 = laden_und_fenster(l, g["name"], g["t"], "t2")
    f3 = laden_und_fenster(l, g["name"], g["t"], "t3")
    return {"t2": f2, "t3": f3}


def abschnitt_bis_zum_ende(l):
    s = l.s
    a = aufnahme_im_stand(l, "danach", lf.TEMPO_LAUF, streng=False)
    naechste_probe = a + BREMS_ALLE
    grund = None
    while grund is None:
        if s.ansicht() in ENDE_ANSICHTEN:
            grund = f"Ansicht {s.ansicht()}"
        elif s.lords() <= 1:
            grund = "letzter Lord"
        elif l.ende_takte and s.takt() - a >= l.ende_takte:
            grund = "Probe zu Ende"
        elif l.uhr() >= l.weich:
            grund = "Zeit um, letzter Lord nicht erreicht"
        elif s.takt() >= naechste_probe:
            naechste_probe = s.takt() + BREMS_ALLE
            bremsprobe_k(l, f"bei Takt {s.takt()}")
        else:
            l.warte_takte(LORD_PRUEFUNG)
    return {"grund": grund, "von": a, "bis": s.takt(), "lords": s.lords()}


ABSCHNITTE = (("start", abschnitt_start), ("frieden", abschnitt_frieden), ("sichern", abschnitt_sichern), ("bis_zum_ende", abschnitt_bis_zum_ende), ("laden_vergleichen", abschnitt_laden_vergleichen))


def schluss(aus):
    d = {e["abschnitt"]: e["daten"] for e in aus}
    g, z = d.get("sichern") or {}, d.get("laden_vergleichen") or {}
    gut = d.get("start", {}).get("lords") == len(KIS) and "frieden" in d and "t1" in g and "grund" in d.get("bis_zum_ende", {}) and "t2" in z and "t3" in z
    return {"gueltig": bool(gut), "lords_start": d.get("start", {}).get("lords"), "lords_ende": d.get("bis_zum_ende", {}).get("lords"), "ende": d.get("bis_zum_ende", {}).get("grund"), "t": g.get("t")}


def los(n, karte, ziel=None, laeuft_schon=True, frieden=FRIEDEN_NORMAL, fenster=FENSTER_NORMAL, ende_takte=None, frist=FRIST, frist_ende=FRIST_ENDE, name="lauf_k"):
    lf.pruefe_laufinstanz(n)
    karte_pruefen(n, karte)
    os.environ["SHC_INSTANZ"] = str(n)
    from selfaware import workspace
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

    ziel = ziel or os.path.join(workspace.DATA, "auge_plan", "laeufe")
    os.makedirs(ziel, exist_ok=True)
    stempel = time.strftime("%Y%m%d_%H%M%S")
    basis = os.path.join(ziel, f"{name}_{stempel}")
    fehlt = [z for z in lf.pruefen(n, laeuft_schon=laeuft_schon) if not z[1]]
    if fehlt:
        raise Fehler(f"Trockenprobe rot: {fehlt}")
    stop = lf.stop_datei(ziel)
    if os.path.exists(stop):
        os.remove(stop)
    lf.sperre_holen(f"Lauf K Auge (B-142) {name}")

    def schreib(e):
        with open(basis + ".protokoll.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")
        print(json.dumps(e, ensure_ascii=False, default=str)[:400], flush=True)

    rek = k = s = None
    ergebnis = None
    try:
        q = os.path.join(lf.ordner(lf.QUELL_INSTANZ), "ucp", "villagestudio", "logik.lua")
        log = os.path.join(lf.ordner(n), "ucp3.log")
        log_vorher = os.path.getsize(log) if os.path.exists(log) else 0
        sicherung = lf.logik_einspielen(os.path.join(lf.ordner(n), "ucp", "villagestudio", "logik.lua"), q, stempel)
        schreib({"schritt": "logik", "sicherung": sicherung})
        from selfaware.game.ucp import laden as laden_mod
        from selfaware.game.ucp import speichern as speichern_mod
        from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz, standard_bereiche

        k = lf.EchterKanal()
        lf.warte_auf_modul(k)
        if laeuft_schon and sicherung:
            def nachgeladen():
                with open(log, encoding="utf-8", errors="replace") as f:
                    f.seek(log_vorher)
                    return "logik.lua neu geladen" in f.read()
            lf.warte_auf(nachgeladen, 20, "Modul hat die logik.lua nachgeladen")
        for rest in lf.ALTE_SCHALTER:
            k.befehl(rest, lf.KANAL)
        karte_felder = Feldkarte.laden(feldliste=FELDLISTE)
        quelle = ProzessQuelle(pid_der_instanz(n))
        s = SpeicherK(quelle)
        rek = lf.Rekorder(n, ziel, f"{name[5:] if name.startswith('lauf_') else name}_{stempel}", quelle, standard_bereiche(karte_felder))
        rek.basis = basis
        rek.stop_datei, rek.aus_datei, rek.felder_datei = basis + ".stop", basis + ".aussetzen", basis + ".felder.json"
        gefecht_starten(k, karte, frieden, startpause=1)
        schreib({"schritt": "gefecht", "karte": karte, "kis": KIS, "friedenszeit": frieden})
        steht, t = lf.anhalten_und_pruefen(k, s)
        if not steht:
            raise Abbruch(f"Der Takt steht am Start nicht (Takt {t})")
        k.befehl({"tempo": lf.TEMPO_LAUF}, lf.KANAL)
        rek.starten(None, lf.TEMPO_LAUF, messen=False)
        lf.warte_auf(rek.laeuft, 60, "Aufzeichnung laeuft")
        k.befehl({"pause": False}, lf.KANAL)

        l = LaufK(k, s, {}, rek, schreib, frist=frist, stop=lambda: os.path.exists(stop), karte=karte, speichern=speichern_mod.speichere, laden=lambda st: laden_mod.lade_stand(st, mit_bild=False),
                  frieden=frieden, fenster=fenster, ende_takte=ende_takte, frist_ende=frist_ende)
        aus = lf.programm(l, ABSCHNITTE)
        ergebnis = schluss(aus)
        schreib({"schritt": "schluss", **ergebnis, "funde": l.funde})
    except Abbruch as e:
        schreib({"schritt": "abbruch", "grund": str(e)})
        ergebnis = {"gueltig": False, "abbruch": str(e)}
    finally:
        # Erst das Spiel anhalten: Das Beenden der Aufzeichnung kann dauern oder scheitern
        steht = False
        if k is not None and s is not None:
            try:
                steht, t = lf.anhalten_und_pruefen(k, s)
                schreib({"schritt": "angehalten", "steht": steht, "takt": t})
            except (OSError, RuntimeError) as e:
                schreib({"schritt": "anhalten_fehlgeschlagen", "grund": str(e)})
        else:
            steht = True  # es lief noch kein Spiel an, das anzuhalten waere
        if rek is not None:
            schreib({"schritt": "aufzeichnung_beendet", "stand": rek.beenden()})
        if steht:
            lf.sperre_freigeben()
        else:
            schreib({"schritt": "sperre_bleibt", "grund": "Der Takt steht nicht, die Sperre bleibt, bis das geklaert ist"})
    print("LAUF ZU ENDE:", json.dumps(ergebnis, ensure_ascii=False, default=str), flush=True)  # das Ende wird sofort gemeldet, die Auswertung kommt danach
    return ergebnis, basis


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("was", choices=["probe", "los"])
    p.add_argument("--instanz", type=int, required=True)
    p.add_argument("--karte", required=True)
    p.add_argument("--daniel-ja", action="store_true", help="Lauf nur nach Daniels Ja")
    a = p.parse_args(argv)
    lf.pruefe_laufinstanz(a.instanz)
    if a.was == "probe":
        e, _ = los(a.instanz, a.karte, fenster=FENSTER_PROBE, ende_takte=ENDE_PROBE, frist=180, frist_ende=150, name="probe_k")
    else:
        if not a.daniel_ja:
            raise Fehler("Lauf K startet nur mit --daniel-ja")
        e, _ = los(a.instanz, a.karte)
    print("gueltig:", e.get("gueltig") if e else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
