# -*- coding: utf-8 -*-
"""B-142 Lauf K: Gefecht mit 8 KI-Lords, ohne Maus und ohne eigene Befehle, alles aufgezeichnet. Plan: docs/plans/Plan_Lauf_K.md.

  python -m selfaware.tools.experiments.auge_lauf_k probe --instanz 2 --karte "<Karte>"      kleine Probe: Friedenszeit 500 Takte, Fenster 200 Takte
  python -m selfaware.tools.experiments.auge_lauf_k los --instanz 2 --karte "<Karte>" --daniel-ja

Bausteine aus Lauf F: Kanal, Speicher, Rekorder, Anhalten. Gerechnet wird in Takten, echte Zeit nur gegen Haengen.
"""
import argparse
import json
import os
import struct
import sys
import time

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments.auge_lauf_f import Abbruch, Fehler

KIS = (14, 15, 1, 9, 2, 5, 7, 4)  # die 8 verschiedensten der 16 KI-Saetze, gerechnet aus den Kennwerten in Lauf F
LORD = 55
FRIEDEN_NORMAL, FENSTER_NORMAL = 1, 2000  # Stufe 1 = 12.000 Takte = 5 Minuten bei Tempo 40; Fenster laut Checkliste
FRIEDEN_PROBE, FENSTER_PROBE, ENDE_PROBE = 6, 200, 2000  # Stufe 6 der Spieltabelle = 500 Takte
FRIEDEN_TAKTE = {1: 12000, 6: 500}
TOTAL_NORUSH = 0x0117EF7C  # mapAndTime.totalNoRushTicks
FRIST, FRIST_ENDE = 900, 840  # 15 Minuten hart; ab 14 Minuten endet der Lauf normal, auch ohne letzten Lord
STILLSTAND_K = 5.0  # Massenschlachten sind nicht gemessen, in Lauf F lag die laengste Luecke bei 0,098 s im Dorf
BREMS_ALLE = 150000  # rund 3 Minuten auf Tempo 1000
ENDE_ANSICHTEN = {30, 58, lf.HAUPTMENUE}  # Spiel verloren, Rangliste, Hauptmenue
KERNFELDER = ("units[].x", "units[].y", "units[].unitType", "buildings[].buildingType", "currentResources[]", "mapAndTime.month")


class SpeicherK(lf.Speicher):
    def lords(self):
        n = min(self.i32(lf.EINHEITEN_ANZAHL), 2500)
        roh = self.q.lies(lf.EINHEITEN, n * lf.E_SCHRITT) if n > 0 else b""
        return sum(1 for i in range(1, n) if struct.unpack_from("<h", roh, i * lf.E_SCHRITT + lf.E_DA)[0] and struct.unpack_from("<h", roh, i * lf.E_SCHRITT + lf.E_TYP)[0] == LORD)

    def ansicht(self):
        return self.i32(lf.ANSICHT)

    def frieden(self):
        return self.i32(TOTAL_NORUSH)


class LaufK(lf.Lauf):
    def __init__(self, *a, speichern=None, laden=None, a5=None, frieden=FRIEDEN_NORMAL, fenster=FENSTER_NORMAL, ende_takte=None, frist_ende=FRIST_ENDE, **kw):
        super().__init__(*a, **kw)
        self.speichern, self.laden, self.a5 = speichern, laden, a5
        self.frieden_stufe, self.fenster, self.ende_takte = frieden, fenster, ende_takte
        self.weich = self.uhr() + frist_ende

    def stillstand_grenze(self):
        return max(STILLSTAND_K, 10.0 / self.tempo)

    def puls_neu(self):
        self.puls = (self.s.takt(), self.uhr())


def gefecht_starten(k, karte, frieden, warte=60, ruhe=time.sleep):
    if k.peek(lf.ANSICHT)[0] != lf.HAUPTMENUE:
        k.befehl({"menue": lf.HAUPTMENUE}, 1.5)
        lf.warte_auf(lambda: k.peek(lf.ANSICHT)[0] == lf.HAUPTMENUE, 10, "Hauptmenue (Ansicht 41)", ruhe=ruhe)
    k.befehl({"pause": False}, lf.KANAL)  # sonst startet das neue Gefecht eingefroren (selbstspiel.py)
    k.befehl({"eigenesGefecht": True, "karte": karte, "kis": list(KIS), "friedenszeit": frieden, "gegner": 0, "trotzdem": True}, 5.0)
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
    if not l.warte_takte(200, lambda: s.lords() == len(KIS)):
        raise Abbruch(f"Nur {s.lords()} von {len(KIS)} Lords: Die Karte hat zu wenig Plaetze")
    return {"lords": s.lords(), "frieden": s.frieden()}


def abschnitt_frieden(l):
    grenze = FRIEDEN_TAKTE[l.frieden_stufe] + lf.ABLESEN
    if not l.warte_takte(grenze, lambda: l.s.frieden() == 0):
        raise Abbruch(f"Friedenszeit endet nicht: noch {l.s.frieden()} nach {grenze} Takten")
    bremsprobe_k(l, "am Ende der Friedenszeit")
    return {"takt": l.s.takt()}


def fenster_aufzeichnen(l, name):
    """Das Spiel steht. Strenge Aufzeichnung starten, Fenster auf Tempo 40 laufen lassen, wieder anhalten."""
    l.rek.starten(name, lf.TEMPO_JEDER_TAKT, streng=True, messen=False)
    lf.warte_auf(l.rek.laeuft, 60, f"Aufzeichnung {name} laeuft", uhr=l.uhr, ruhe=l.ruhe)
    a = l.s.takt()
    lf.tempo_setzen(l.k, lf.TEMPO_JEDER_TAKT)
    l.tempo = lf.TEMPO_JEDER_TAKT
    l.puls_neu()
    l.warte_takte(l.fenster)
    b = anhalten(l)
    stand = l.rek.beenden()
    if stand.get("fehlend") or stand.get("gemischt"):
        raise Abbruch(f"Fenster {name}: {stand}")
    return {"von": a, "bis": b, "stand": stand, "datei": l.rek.pfad}


def abschnitt_laden_vergleichen(l):
    """Checkliste A5 und A6: speichern, Fenster, laden, Vergleich, dasselbe Fenster noch einmal."""
    t = anhalten(l)
    l.rek.beenden()
    name = f"AugeK T{t}"
    l.speichern(name)
    if l.s.takt() != t:
        raise Abbruch(f"Das Speichern hat den Takt bewegt: {t} auf {l.s.takt()}")
    f1 = fenster_aufzeichnen(l, "t1")
    t2 = l.laden(name)
    f2 = fenster_aufzeichnen(l, "t2")
    daten = {"name": name, "t": t, "t2": t2, "t1": f1, "t2_fenster": f2}
    if l.a5:
        abweichend = l.a5(f1, f2)
        daten["a5_abweichend"] = len(abweichend)
        kern = sorted(f for f in abweichend if f in KERNFELDER)
        if kern:
            raise Abbruch(f"Nach dem Laden weichen Kernfelder ab: {kern}")
    return daten


def abschnitt_bis_zum_ende(l):
    s = l.s
    l.rek.starten("danach", lf.TEMPO_LAUF)
    lf.warte_auf(l.rek.laeuft, 60, "Aufzeichnung danach laeuft", uhr=l.uhr, ruhe=l.ruhe)
    lf.tempo_setzen(l.k, lf.TEMPO_LAUF)
    l.tempo = lf.TEMPO_LAUF
    l.puls_neu()
    a = s.takt()
    naechste_probe = a + BREMS_ALLE
    grund = None
    while grund is None:
        def fertig():
            return s.ansicht() in ENDE_ANSICHTEN or s.lords() <= 1
        if l.warte_takte(1000, fertig):
            grund = f"Ansicht {s.ansicht()}" if s.ansicht() in ENDE_ANSICHTEN else "letzter Lord"
        elif l.ende_takte and s.takt() - a >= l.ende_takte:
            grund = "Probe zu Ende"
        elif l.uhr() >= l.weich:
            grund = "Zeit um, letzter Lord nicht erreicht"
        elif s.takt() >= naechste_probe:
            naechste_probe = s.takt() + BREMS_ALLE
            bremsprobe_k(l, f"bei Takt {s.takt()}")
    return {"grund": grund, "von": a, "bis": s.takt(), "lords": s.lords()}


ABSCHNITTE = (("start", abschnitt_start), ("frieden", abschnitt_frieden), ("laden_vergleichen", abschnitt_laden_vergleichen), ("bis_zum_ende", abschnitt_bis_zum_ende))


def schluss(aus):
    d = {e["abschnitt"]: e["daten"] for e in aus}
    z = d.get("laden_vergleichen") or {}
    gut = d.get("start", {}).get("lords") == len(KIS) and "frieden" in d and "t1" in z and "t2_fenster" in z
    return {"gueltig": bool(gut), "lords_start": d.get("start", {}).get("lords"), "lords_ende": d.get("bis_zum_ende", {}).get("lords"), "ende": d.get("bis_zum_ende", {}).get("grund"), "t": z.get("t"), "t2": z.get("t2")}


def los(n, karte, ziel=None, laeuft_schon=True, frieden=FRIEDEN_NORMAL, fenster=FENSTER_NORMAL, ende_takte=None, frist=FRIST, frist_ende=FRIST_ENDE, name="lauf_k"):
    lf.pruefe_laufinstanz(n)
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
        from selfaware.tools.analysis import auge_auswertung as aw
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
        gefecht_starten(k, karte, frieden)
        schreib({"schritt": "gefecht", "karte": karte, "kis": KIS, "friedenszeit": frieden})
        lf.tempo_setzen(k, lf.TEMPO_LAUF)
        rek.starten(None, lf.TEMPO_LAUF)
        lf.warte_auf(rek.laeuft, 60, "Aufzeichnung laeuft")

        def a5(f1, f2):
            e = aw.a5_laden_gleich_sichern(aw.Aufzeichnung(f1["datei"]), f1["von"], aw.Aufzeichnung(f2["datei"]), f2["von"], karte_felder)
            schreib({"schritt": "a5", "status": e.status, "text": e.text})
            return [x[1] for x in e.daten.get("abweichend", [])]

        l = LaufK(k, s, {}, rek, schreib, frist=frist, stop=lambda: os.path.exists(stop), speichern=speichern_mod.speichere, laden=lambda st: laden_mod.lade_stand(st, mit_bild=False),
                  a5=a5, frieden=frieden, fenster=fenster, ende_takte=ende_takte, frist_ende=frist_ende)
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
        e, _ = los(a.instanz, a.karte, frieden=FRIEDEN_PROBE, fenster=FENSTER_PROBE, ende_takte=ENDE_PROBE, frist=180, frist_ende=150, name="probe_k")
    else:
        if not a.daniel_ja:
            raise Fehler("Lauf K startet nur mit --daniel-ja")
        e, _ = los(a.instanz, a.karte)
    print("gueltig:", e.get("gueltig") if e else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
