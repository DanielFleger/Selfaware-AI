# -*- coding: utf-8 -*-
"""B-142 Lauf F: Burgenbau auf "Eine praechtige Oase" (A Mighty Oasis.map), ohne Maus, alles aufgezeichnet.

  python -m selfaware.tools.experiments.auge_lauf_f pruefen --instanz 2     Trockenprobe, startet nichts, aendert nichts
  python -m selfaware.tools.experiments.auge_lauf_f los --instanz 2 --daniel-ja

Menueweg aus dem Export: Hauptmenue Knopf 3 setzt GM_BUILDERUnk und oeffnet die Kartenwahl (Ansicht 35),
SingleplayerMapChoice_ButtonsAndHands(0x41) startet die markierte Karte (LaunchSinglePlayerGameUnk). Den Knopf-Handler
kennt logik.lua noch nicht; "los" spielt ihn in die Laufinstanz ein, die alte Datei bleibt mit Datum liegen.
Die Laufinstanz bekommt die logik.lua von Instanz 4 (nur gelesen): Sie lief mit demselben Modulordner villagestudio-0.1.0.
Instanz 5 nutzt seit 24.10. ein anderes Modul (selfaware-runtime, mit Uebernahme-Logik) und wird nie angefasst.
Die Ladeliste der Laufinstanz enthaelt das Modul seit der Startreparatur vom 24.10. nicht mehr; "los" traegt es wieder ein.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

KARTE = "A Mighty Oasis"
STAMM = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"
DANIELS_INSTANZ = 5
QUELL_INSTANZ = 4
SPERRE_NAME = "SRE_auge"
HAUPTMENUE, KARTENWAHL, IN_PARTIE = 41, 35, 14
ANSICHT, TICK, PAUSE, GAMEOVER = 0x01FE7D1C, 0x0117CADC, 0x01FEA054, 0x0117D500
GESAMT, SCROLL, MARKIERT = 0x01A24A68, 0x01A24A64, 0x01A24A6C  # DAT_MapSelection... in GameSynchronyState
LISTE, NAMEN, NAMENSLAENGE = 0x01126E28, 0x11BFCF8, 0x3E9      # Eintrag n = Zeile + Scrollstand (wie im Ladedialog)
KARTENNAME = 0x01A22F9C                                        # mapName, ohne .map
JAHR_ADRESSE_FELD = ("DAT_GameState", "mapAndTime.year")
KNOPF_START = 0x41
ANKER = "CustomScenarios_Main = 0x00440770,"
NEU = "SingleplayerMapChoice_ButtonsAndHands = 0x0042D640,"
FRUEH_TAKTE = 200  # nach so vielen Takten zum ersten Mal auf fehlende Takte pruefen
ABBRUCH_ANTEIL = 0.05  # selbst gesetzt: Einzelne fehlende Takte stehen nur in A3, erst darueber taugt die Aufzeichnung nicht
STUFEN = (1, 10, 40, 100, 200, 500, 1000)  # Daniel 02.11.2026: auf Tempo 1 bis 1000 kein Abzug vom normalen Tempo
TREPPE_SEKUNDEN = 20


class Fehler(RuntimeError):
    pass


def ordner(n):
    return STAMM if n == 1 else f"{STAMM} Instanz{n}"


def pruefe_laufinstanz(n):
    if n == DANIELS_INSTANZ:
        raise Fehler("Instanz 5 ist Daniels Spiel und bleibt unberuehrt")
    return n


def logik_text(quelle):
    """Die logik.lua der Quelle mit dem neuen Knopf; Zeilenenden bleiben, wie sie sind."""
    roh = open(quelle, "rb").read().decode("latin-1")
    if roh.count(NEU):
        return roh
    if roh.count(ANKER) != 1:
        raise Fehler(f"{quelle}: Stelle fuer den neuen Knopf nicht eindeutig ({roh.count(ANKER)} Treffer)")
    i = roh.index(ANKER)
    anfang = roh.rfind("\n", 0, i) + 1
    ende = "\r\n" if "\r\n" in roh[i:i + 200] else "\n"
    return roh[:i + len(ANKER)] + ende + roh[anfang:i] + NEU + roh[i + len(ANKER):]


def logik_einspielen(ziel, quelle, stempel=None):
    """Sichert die alte Datei mit Datum und schreibt die neue. Rueckweg: die Sicherung zurueckkopieren."""
    if "instanz5" in ziel.replace(" ", "").lower():
        raise Fehler("Instanz 5 ist Daniels Spiel und bleibt unberuehrt")
    neu = logik_text(quelle).encode("latin-1")
    if os.path.exists(ziel):
        if open(ziel, "rb").read() == neu:
            return None
        sicherung = f"{ziel[:-4]}.vor_auge_{stempel or time.strftime('%Y%m%d_%H%M%S')}.lua"
        shutil.copy2(ziel, sicherung)
    else:
        sicherung = None
    with open(ziel, "wb") as f:
        f.write(neu)
    return sicherung


def lua_fehler(text):
    """Syntaxfehler der logik.lua, sonst None. Ohne lupa ungeprueft (dann "nicht geprueft")."""
    try:
        import lupa
    except ImportError:
        return "nicht geprueft: lupa fehlt"
    lua = lupa.LuaRuntime(unpack_returned_tuples=True, encoding="latin-1")
    return lua.eval("function(t) local f, e = load(t); return e end")(text)


def modul_eintragen(pfad, stempel=None):
    """Traegt villagestudio in die Ladelisten von ucp-config.yml ein, sichert vorher, prueft danach. Rueckgabe: Sicherung oder None."""
    import yaml

    if "instanz5" in pfad.replace(" ", "").lower():
        raise Fehler("Instanz 5 ist Daniels Spiel und bleibt unberuehrt")
    roh = open(pfad, "rb").read().decode("utf-8")
    alt = yaml.safe_load(roh)
    drin = lambda d, teil: any(e.get("extension") == "villagestudio" for e in d[teil]["load-order"])
    if drin(alt, "config-sparse") and drin(alt, "config-full") and "villagestudio" in (alt["config-sparse"].get("modules") or {}):
        return None
    nl = "\r\n" if "\r\n" in roh else "\n"
    eintrag = f"  - extension: villagestudio{nl}    version: 0.1.0{nl}"
    t = roh
    leer = f"  modules: {{}}{nl}"
    if leer not in t[:t.index("config-full:")]:
        raise Fehler(f"{pfad}: config-sparse.modules ist nicht leer, von Hand ansehen")
    t = t.replace(leer, f"  modules:{nl}    villagestudio:{nl}      config: {{}}{nl}", 1)
    t = t.replace(f"config-full:{nl}", eintrag + f"config-full:{nl}", 1)
    t = t.rstrip("\r\n") + nl + eintrag
    neu = yaml.safe_load(t)
    if not (drin(neu, "config-sparse") and drin(neu, "config-full")):
        raise Fehler(f"{pfad}: Eintrag ist nicht in beiden Ladelisten angekommen")
    for teil in ("config-sparse", "config-full"):
        neu[teil]["load-order"] = [e for e in neu[teil]["load-order"] if e.get("extension") != "villagestudio"]
    neu["config-sparse"]["modules"] = {k: v for k, v in neu["config-sparse"]["modules"].items() if k != "villagestudio"} or {}
    if neu != alt:
        raise Fehler(f"{pfad}: Das Eintragen haette noch etwas anderes geaendert")
    sicherung = f"{pfad}.vor_auge_{stempel or time.strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(pfad, sicherung)
    with open(pfad, "wb") as f:
        f.write(t.encode("utf-8"))
    return sicherung


def warte_auf(bedingung, sekunden, was, schlaf=0.25, uhr=time.time, ruhe=time.sleep):
    ende = uhr() + sekunden
    while uhr() < ende:
        if bedingung():
            return
        ruhe(schlaf)
    raise Fehler(f"nach {sekunden} s nicht erreicht: {was}")


def name_von(k, nummer):
    roh = b"".join(w.to_bytes(4, "little") for w in k.peek(NAMEN + nummer * NAMENSLAENGE, 12))
    return roh.split(b"\0")[0].decode("latin-1")


def warte_auf_modul(k, sekunden=120, ruhe=time.sleep, uhr=time.time):
    """Das Modul meldet "aktiv", bevor das Spiel im Menue ist und Befehle liest (Lauf F 02.11.2026 18:12, gemessen)."""
    def antwortet():
        try:
            k.peek(ANSICHT)
            return True
        except Exception:  # noqa: BLE001  jede Kanalstoerung heisst hier nur: noch nicht
            return False
    warte_auf(antwortet, sekunden, "Modul antwortet auf Befehle", schlaf=2.0, ruhe=ruhe, uhr=uhr)


def burgenbau_starten(k, karte=KARTE, warte=60, ruhe=time.sleep):
    """Hauptmenue -> Burgenbau -> Karte markieren -> Start; jeder Schritt wird an der Menueansicht geprueft."""
    if k.peek(ANSICHT)[0] != HAUPTMENUE:
        k.befehl({"menue": HAUPTMENUE}, 1.5)
        if k.peek(ANSICHT)[0] != HAUPTMENUE:
            raise Fehler(f"Hauptmenue nicht erreicht: Ansicht {k.peek(ANSICHT)[0]}")
    k.befehl({"hauptmenue": 3}, 1.5)
    warte_auf(lambda: k.peek(ANSICHT)[0] == KARTENWAHL, 10, "Kartenwahl Burgenbau (Ansicht 35)", ruhe=ruhe)
    anzahl = k.peek(GESAMT)[0]
    if not 0 < anzahl <= 500:
        raise Fehler(f"Kartenliste unplausibel: {anzahl} Eintraege")
    namen = [name_von(k, nr) for nr in k.peek(LISTE, anzahl)]
    if karte not in namen:
        raise Fehler(f"'{karte}' steht nicht in der Kartenliste ({anzahl} Eintraege)")
    n = namen.index(karte)
    scroll = max(0, n - 12)
    k.liste([{"poke": SCROLL, "wert": scroll}, {"poke": MARKIERT, "wert": n - scroll},
             {"knopf": "SingleplayerMapChoice_ButtonsAndHands", "nr": KNOPF_START}], 4.0)
    warte_auf(lambda: k.peek(ANSICHT)[0] == IN_PARTIE, warte, "Partie laeuft (Ansicht 14)", ruhe=ruhe)
    k.befehl({"eigenerPlatz": 1}, 0.8)
    return {"karte": karte, "eintrag": n, "von": anzahl}


def baue_ohne_anhalten(k, takt, gebaeude_von, g, typ, stellen, sp=1, ruhe=time.sleep):
    """Wie bauen.baue_irgendwo, aber das Spiel laeuft durch: Daniel 02.11.2026 18:39, Bauen darf das Tempo nicht herausnehmen.
    baue_irgendwo haelt nach jedem Versuch an (laufe), die Tempomessung waere damit wertlos."""
    vorher = {n for n, _, _ in gebaeude_von(sp, typ)}
    for x, y in stellen:
        t0 = takt()
        k.befehl({"baue": {"mapper": g["mapper"], "x": x, "y": y, "groesse": g["b"], "richtung": 0}}, 0.3)
        warte_auf(lambda: takt() >= t0 + 2, 10, "zwei Takte nach dem Bauen", schlaf=0.02, ruhe=ruhe)
        neu = [e for e in gebaeude_von(sp, typ) if e[0] not in vorher]
        if neu:
            return neu[0]
    return None


def kandidaten(mitte, schritt=7, hoechstens=40, radius=140):
    """Stellen in Ringen um die Mitte, gueltige Karte 0 bis 399."""
    x0, y0 = mitte
    aus = []
    r = schritt
    while r <= radius and len(aus) < hoechstens:
        for dx in range(-r, r + 1, schritt):
            for dy in (-r, r):
                aus.append((x0 + dx, y0 + dy))
        for dy in range(-r + schritt, r, schritt):
            for dx in (-r, r):
                aus.append((x0 + dx, y0 + dy))
        r += schritt
    return [p for p in dict.fromkeys(aus) if 8 <= p[0] <= 391 and 8 <= p[1] <= 391][:hoechstens]


# --- Das Programm des Laufs. Eine Phase, die scheitert, wird notiert; ihre Punkte bleiben dann "nicht gesehen". ---
WAREN = [w for w in range(2, 25) if w != 15]  # 15 ist das Gold
STEUERSTUFEN = list(range(0, 12))
RATIONEN = list(range(0, 5))
BURGEN = (41, 42, 43, 44, 40)
ANWERBEN = {9: [22, 23, 24, 25, 26, 27, 28], 8: [70, 71, 72, 73, 74, 75, 76], 24: [29, 30], 25: [5], 38: [37]}


def phase_vorrat(k, w, lage):
    k.befehl({"gold": 100000}, 0.8)
    for t in WAREN:
        k.befehl({"ware": {"typ": t, "menge": 50}}, 0.3)
    return {"gold": 100000, "waren": len(WAREN)}


def phase_burg(k, w, lage):
    for t in BURGEN:
        da = w.gebaeude_von(1, t)
        if da:
            lage["mitte"] = (da[0][1], da[0][2])
            return {"burg": "stand schon", "typ": t, "ort": lage["mitte"]}
    e = w.baue_irgendwo(41, kandidaten((200, 200), 12, 40))
    if not e:
        raise Fehler("Bergfried liess sich auf keiner der Stellen setzen")
    lage["mitte"] = (e[1], e[2])
    return {"burg": "gebaut", "ort": lage["mitte"]}


def phase_bauen(k, w, lage):
    gesetzt, fehl = [], []
    for typ in sorted(set(w.NACH_TYP) - set(BURGEN)):
        e = w.baue_irgendwo(typ, kandidaten(lage["mitte"]))
        if e:
            gesetzt.append([typ, e[0]])
            lage.setdefault("gebaut", {})[typ] = e[0]
        else:
            fehl.append(typ)
    return {"gesetzt": len(gesetzt), "nicht_gesetzt": fehl}


def phase_warenketten(k, w, lage):
    return {"bis_takt": w.laufe_bis(w.takt() + 6000)}


def phase_handel(k, w, lage):
    n = 0
    for t in WAREN:
        for art in (0, 1):  # 0 kaufen, 1 verkaufen
            k.befehl({"spielbefehl": {"nr": 38, "werte": [art, t]}}, 0.4)
            n += 1
    k.befehl({"ware": {"typ": 2, "menge": 100000}}, 0.5)  # volles Lager: kaufen muss wirkungslos bleiben
    k.befehl({"spielbefehl": {"nr": 38, "werte": [0, 2]}}, 0.5)
    w.laufe_bis(w.takt() + 50)
    return {"befehle": n + 1}


def phase_steuern(k, w, lage):
    for s in STEUERSTUFEN:
        k.befehl({"spielbefehl": {"nr": 34, "werte": [s]}}, 0.4)
        w.laufe_bis(w.takt() + 150)
    for r in RATIONEN:
        k.befehl({"spielbefehl": {"nr": 35, "werte": [r]}}, 0.4)
        w.laufe_bis(w.takt() + 150)
    return {"steuern": len(STEUERSTUFEN), "rationen": len(RATIONEN)}


def phase_mauern(k, w, lage):
    x, y = lage["mitte"]
    x, y = x + 24, y + 24
    k.befehl({"spielbefehl": {"nr": 25, "werte": [x, y, x + 12, y, 25, 13]}}, 0.8)
    k.befehl({"spielbefehl": {"nr": 25, "werte": [x, y + 3, x + 12, y + 3, 46, 13]}}, 0.8)
    k.befehl({"spielbefehl": {"nr": 21, "werte": [x, y + 8, 0, 0x40000000, 2]}}, 0.8)
    tore = [t for t in (45, 46) if t in lage.get("gebaut", {})]
    w.laufe_bis(w.takt() + 300)
    return {"mauer": [x, y], "tore_gebaut": tore}


def phase_anwerben(k, w, lage):
    gebaut = lage.get("gebaut", {})
    versucht, ohne = 0, []
    for g, einheiten in ANWERBEN.items():
        if g not in gebaut:
            ohne.append(g)
            continue
        for e in einheiten:
            w.werbe(e, gebaut[g])
            versucht += 1
    w.laufe_bis(w.takt() + 300)
    return {"versucht": versucht, "ohne_gebaeude": ohne}


def phase_abreissen(k, w, lage):
    nr = sorted(lage.get("gebaut", {}).values())[:5]
    for n in nr:
        k.befehl({"abreissen": {"nr": n}}, 0.6)
    w.laufe_bis(w.takt() + 100)
    return {"abgerissen": nr}


def phase_jahre(k, w, lage):
    return {"bis_takt": w.laufe_bis_jahre(2)}


PHASEN = [("vorrat", phase_vorrat), ("burg", phase_burg), ("bauen", phase_bauen), ("warenketten", phase_warenketten), ("handel", phase_handel),
          ("steuern", phase_steuern), ("mauern", phase_mauern), ("anwerben", phase_anwerben), ("abreissen", phase_abreissen), ("jahre", phase_jahre)]


def programm(k, w, protokoll, phasen=PHASEN, wache=None, uhr=time.perf_counter):
    """Alle Phasen nacheinander. wache() darf mit Fehler den Lauf beenden; ein Fehler in einer Phase beendet nur die Phase."""
    lage, aus = {"mitte": (200, 200)}, []
    for name, f in phasen:
        if wache:
            wache()
        t0, s0 = w.takt(), uhr()
        try:
            eintrag = {"phase": name, "ok": True, "daten": f(k, w, lage)}
        except Fehler as e:
            eintrag = {"phase": name, "ok": False, "fehler": str(e)}
        except Exception as e:  # noqa: BLE001  eine kaputte Phase darf die Aufzeichnung nicht beenden
            eintrag = {"phase": name, "ok": False, "fehler": f"{type(e).__name__}: {e}"}
        t1 = w.takt()
        dauer = uhr() - s0
        eintrag.update(takt_von=t0, takt_bis=t1, sekunden=round(dauer, 1), takte_je_s=round((t1 - t0) / dauer, 1) if dauer > 0 else None)
        protokoll(eintrag)
        aus.append(eintrag)
    return aus


def fruehprobe(pfad):
    """Takt-Treue nach den ersten Takten. Das abgeschnittene Dateiende zaehlt hier nicht, die Aufzeichnung laeuft ja noch."""
    from selfaware.tools.analysis.auge_auswertung import Aufzeichnung, a3_takttreue, a4_lesedauer

    auf = Aufzeichnung(pfad)
    a3, a4 = a3_takttreue(auf), a4_lesedauer(auf)
    d = a3.daten
    if d.get("fehlende_takte", 0) > ABBRUCH_ANTEIL * max(d.get("spanne", 0), 1) or d.get("unreine_rahmen", 0) > ABBRUCH_ANTEIL * max(d.get("rahmen", 0), 1):
        return False, a3.text
    return True, f"{a3.text}; {a4.text}"


def tempo_setzen(k, s):
    """Zwei Befehle: Pause und Tempo im selben Befehl setzt das Tempo nicht (gemessen Lauf F 02.11.2026 18:16)."""
    k.befehl({"pause": False}, 0.3)
    k.befehl({"tempo": s}, 0.5)


def tempotreppe(k, takt, lese_runde, stufen=STUFEN, sekunden=TREPPE_SEKUNDEN, ruhe=time.sleep, uhr=time.perf_counter):
    """Je Tempostufe Takte/s ohne Lesen, mit Lesen, wieder ohne Lesen. Die Haupt-Aufzeichnung darf dabei nicht laufen."""
    def zaehle():
        a, t0 = takt(), uhr()
        ruhe(sekunden)
        return (takt() - a) / (uhr() - t0)

    zeilen = []
    for s in stufen:
        tempo_setzen(k, s)
        ruhe(2)
        ohne_1 = zaehle()
        # bis 100 ist die Bildrate keine Grenze: Stimmt das Tempo nicht, misst die Stufe etwas anderes (Lauf F 18:16: ueberall 200)
        if s <= 100 and abs(ohne_1 - s) > max(2.0, 0.2 * s):
            raise Fehler(f"Tempo {s} wirkt nicht: {ohne_1:.1f} Takte/s gemessen")
        r = lese_runde(sekunden, s)
        ohne_2 = zaehle()
        zeilen.append({"tempo": s, "sekunden": sekunden, "ohne_1": ohne_1, "mit": r["takte_je_s"], "ohne_2": ohne_2, "gelesen": r["gelesen"], "gesamt": r["gesamt"]})
    return zeilen


def echte_lese_runde(quelle, bereiche, ordner_aus, kennung):
    """Liest eine Runde wie die Aufzeichnung, in eine eigene Datei."""
    from selfaware.tools.experiments.auge_aufzeichnung import Aufzeichner

    def runde(sekunden, stufe):
        auf = Aufzeichner(quelle, bereiche, os.path.join(ordner_aus, f"{kennung}_tempo{stufe}.auge"), {"lauf": "Treppe", "tempo": stufe})
        a, t0 = auf.takt(), time.perf_counter()
        n = auf.lauf(sekunden=sekunden, pause=0.0002)
        e, t1 = auf.takt(), time.perf_counter()
        auf.schliessen()
        return {"takte_je_s": (e - a) / (t1 - t0), "gelesen": n, "gesamt": e - a + 1}
    return runde


def pruefen(n, quell=QUELL_INSTANZ, laeuft_schon=False):
    """Trockenprobe: liest nur. Jede Zeile (Name, ok, Aussage)."""
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz, prozesspfade
    aus = []

    def pruef(name, ok, text=""):
        aus.append((name, bool(ok), text))

    pruef("Laufinstanz ist nicht Instanz 5", n != DANIELS_INSTANZ, f"Instanz {n}")
    o = ordner(n)
    pruef("Ordner und Programm da", os.path.exists(os.path.join(o, "Stronghold Crusader.exe")), o)
    pruef("Karte da", os.path.exists(os.path.join(o, "maps", KARTE + ".map")), KARTE + ".map")
    pruef("Modul da", os.path.exists(os.path.join(o, "ucp", "modules", "villagestudio-0.1.0", "init.lua")))
    log = os.path.join(o, "ucp3.log")
    # keine Bedingung: Der Lauf traegt das Modul selbst ein; ob es laeuft, zeigt erst seine Antwort im Spiel
    aktiv = os.path.exists(log) and "villagestudio aktiv" in open(log, encoding="utf-8", errors="replace").read()
    pruef("Stand des letzten Starts bekannt", True, ("Modul war aktiv" if aktiv else "Modul war nicht aktiv") + (time.strftime(", %d.%m. %H:%M", time.localtime(os.path.getmtime(log))) if os.path.exists(log) else ""))
    if laeuft_schon:
        pruef("Instanz laeuft schon, wie angegeben", pid_der_instanz(n) is not None)
    else:
        pruef("Instanz laeuft gerade nicht", pid_der_instanz(n) is None)
    pfade = prozesspfade()
    pruef("UCP3-GUI ist zu", not any("ucp3-gui" in p.lower() or "ucp3 gui" in p.lower() for p in pfade))
    q = os.path.join(ordner(quell), "ucp", "villagestudio", "logik.lua")
    try:
        t = logik_text(q)
        pruef("logik.lua laesst sich um den Knopf ergaenzen", t.count(NEU) == 1 and t.count(ANKER) == 1, f"Quelle Instanz {quell}, {len(t)} Zeichen")
        f = lua_fehler(t)
        pruef("logik.lua hat keinen Syntaxfehler", not f or f.startswith("nicht geprueft"), f or "")
    except (OSError, Fehler) as e:
        pruef("logik.lua laesst sich um den Knopf ergaenzen", False, str(e))
    s = subprocess.run([sys.executable, sperre_pfad(), "nachsehen"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, SHC_INSTANZ=str(n)), timeout=30)
    pruef("Sperre frei", "FREI" in s.stdout, s.stdout.strip().splitlines()[-1] if s.stdout.strip() else s.stderr[:100])
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments.auge_aufzeichnung import standard_bereiche
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    bereiche = standard_bereiche(karte)
    pruef("Bereiche aus dem Export", len(bereiche) >= 10, f"{len(bereiche)} Bereiche, jeden Takt {sum(b.laenge for b in bereiche if b.alle == 1) / 1e6:.1f} MB")
    pruef("Jahresfeld gefunden", karte.adresse(*JAHR_ADRESSE_FELD)[0] > 0, hex(karte.adresse(*JAHR_ADRESSE_FELD)[0]))
    frei = shutil.disk_usage(os.path.dirname(os.path.abspath(__file__))).free
    pruef("Freier Plattenplatz bekannt", frei > 0, f"{frei / 1e9:.0f} GB frei")
    return aus


def sperre_pfad():
    from selfaware import workspace
    return os.path.join(workspace.VILLAGE_STUDIO, "werkzeug", "sperre.py")


class EchterKanal:
    def __init__(self):
        from selfaware.game.ucp import laden
        from selfaware.game.ucp.befehl import neue_id, sende
        self._laden, self._neue_id, self._sende = laden, neue_id, sende

    def befehl(self, cmd, warte=0.8, bis=None):
        return self._laden.befehl(cmd, warte, bis=bis)

    def peek(self, adr, n=1):
        # verpackt: unverpackte Lesebefehle kommen in Menues nicht an (gemessen 21.10.)
        kennung = "PEEK 0x%08X" % adr
        for z in self._sende({"befehle": [{"player": 1, "id": self._neue_id(), "peek": adr, "worte": n}]}, 3.0, bis=kennung):
            if kennung in z:
                return [int(x, 16) & 0xFFFFFFFF for x in z.split(": ", 2)[-1].split()]
        raise Fehler(f"keine Antwort auf {kennung}")

    def liste(self, cmds, warte=1.0):
        return self._sende({"befehle": [dict(c, player=1, id=self._neue_id()) for c in cmds]}, warte)


class EchtesWerkzeug:
    def __init__(self, k, jahr_adresse):
        from selfaware.game.ucp import bauen
        self._k, self._bauen, self._jahr = k, bauen, jahr_adresse
        self.NACH_TYP = bauen.NACH_TYP
        self.gebaeude_von, self.werbe = bauen.gebaeude_von, bauen.werbe

    def baue_irgendwo(self, typ, stellen):
        return baue_ohne_anhalten(self._k, self.takt, self.gebaeude_von, self.NACH_TYP[typ], typ, stellen)

    def takt(self):
        return self._k.peek(TICK)[0]

    def laufe_bis(self, ziel, sekunden=1800):
        self._k.befehl({"pause": False}, 0.3)
        warte_auf(lambda: self.takt() >= ziel, sekunden, f"Takt {ziel}", schlaf=1.0)
        return self.takt()

    def laufe_bis_jahre(self, jahre, sekunden=3600):
        a = self._k.peek(self._jahr)[0]
        self._k.befehl({"pause": False}, 0.3)
        warte_auf(lambda: self._k.peek(self._jahr)[0] >= a + jahre, sekunden, f"{jahre} Jahreswechsel", schlaf=2.0)
        return self.takt()


def los(n, tempo=40, ziel=None, laeuft_schon=False, leertreppe=True):
    pruefe_laufinstanz(n)
    os.environ["SHC_INSTANZ"] = str(n)
    from selfaware import workspace
    from selfaware.tools.analysis.auge_feldkarte import Feldkarte

    ziel = ziel or os.path.join(workspace.DATA, "auge_plan", "laeufe")
    os.makedirs(ziel, exist_ok=True)
    stempel = time.strftime("%Y%m%d_%H%M%S")
    aufz = os.path.join(ziel, f"lauf_f_{stempel}.auge")
    prot = os.path.join(ziel, f"lauf_f_{stempel}.protokoll.jsonl")
    stop = aufz + ".stop"
    fehlt = [z for z in pruefen(n, laeuft_schon=laeuft_schon) if not z[1]]
    if fehlt:
        raise Fehler(f"Trockenprobe rot: {fehlt}")
    r = subprocess.run([sys.executable, sperre_pfad(), "holen", SPERRE_NAME, "Lauf F Auge (B-142)"], capture_output=True, text=True, env=dict(os.environ), timeout=30)
    if r.returncode != 0:
        raise Fehler(f"Sperre nicht bekommen: {r.stdout} {r.stderr}")

    def schreib(e):
        with open(prot, "a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(e, flush=True)

    aufzeichner = None
    try:
        q = os.path.join(ordner(QUELL_INSTANZ), "ucp", "villagestudio", "logik.lua")
        schreib({"schritt": "logik", "sicherung": logik_einspielen(os.path.join(ordner(n), "ucp", "villagestudio", "logik.lua"), q, stempel)})
        schreib({"schritt": "ladeliste", "sicherung": modul_eintragen(os.path.join(ordner(n), "ucp-config.yml"), stempel)})
        ps = os.path.join(workspace.ROOT, "tools", "windows", "spiel_starten.ps1")
        if not laeuft_schon:
            s = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps, "-Instanz", str(n)], capture_output=True, text=True, timeout=120)
            schreib({"schritt": "start", "ausgabe": s.stdout.strip()[-200:]})
            if s.returncode != 0:
                raise Fehler(f"Spielstart: {s.stdout} {s.stderr}")
        k = EchterKanal()
        warte_auf_modul(k)
        if "villagestudio aktiv" not in open(os.path.join(ordner(n), "ucp3.log"), encoding="utf-8", errors="replace").read():
            raise Fehler("Modul antwortet, steht aber nicht im neuen ucp3.log")
        karte = Feldkarte.laden()
        schreib({"schritt": "burgenbau", **burgenbau_starten(k)})
        schreib({"schritt": "karte_geladen", "name": b"".join(w.to_bytes(4, "little") for w in k.peek(KARTENNAME, 8)).split(b"\0")[0].decode("latin-1")})
        from selfaware.tools.analysis.auge_auswertung import a4_tempotreppe
        from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, TAKT_ADRESSE, pid_der_instanz, standard_bereiche
        import struct
        quelle = ProzessQuelle(pid_der_instanz(n))
        bereiche = standard_bereiche(karte)
        takt_roh = lambda: struct.unpack("<I", quelle.lies(TAKT_ADRESSE, 4))[0]

        def treppe(kennung):
            z = tempotreppe(k, takt_roh, echte_lese_runde(quelle, bereiche, ziel, f"lauf_f_{stempel}_{kennung}"))
            e = a4_tempotreppe(z)
            schreib({"schritt": f"tempotreppe_{kennung}", "ergebnis": e.status, "text": e.text, "zeilen": e.daten.get("zeilen")})
        if leertreppe:
            treppe("leer")
        tempo_setzen(k, tempo)
        aufzeichner = subprocess.Popen([sys.executable, "-m", "selfaware.tools.experiments.auge_aufzeichnung", "--instanz", str(n), "--ausgabe", aufz, "--lauf", "F", "--stop-datei", stop], env=dict(os.environ))
        w = EchtesWerkzeug(k, karte.adresse(*JAHR_ADRESSE_FELD)[0])
        warte_auf(lambda: os.path.exists(aufz) and os.path.getsize(aufz) > 1000, 60, "Aufzeichnung laeuft")
        t0 = w.takt()
        warte_auf(lambda: w.takt() >= t0 + FRUEH_TAKTE, 300, f"{FRUEH_TAKTE} Takte", schlaf=0.5)

        def wache():
            if aufzeichner.poll() is not None:
                raise Fehler("Aufzeichnung ist beendet")
            ok, text = fruehprobe(aufz)
            schreib({"schritt": "wache", "ok": ok, "text": text})
            if not ok:
                raise Fehler(f"Abbruch: {text}")
        wache()
        programm(k, w, schreib, wache=wache)
        open(stop, "w").close()
        aufzeichner.wait(120)
        treppe("voll")  # zweite Messung im bebauten Spiel; die Haupt-Aufzeichnung ist jetzt aus
    finally:
        open(stop, "w").close()
        if aufzeichner:
            try:
                aufzeichner.wait(60)
            except subprocess.TimeoutExpired:
                aufzeichner.kill()
        subprocess.run([sys.executable, sperre_pfad(), "freigeben", SPERRE_NAME], capture_output=True, env=dict(os.environ), timeout=30)
    subprocess.run([sys.executable, "-m", "selfaware.tools.analysis.auge_auswertung", aufz, "--ausgabe", aufz + ".ergebnis.json"], check=False)
    return aufz


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("was", choices=["pruefen", "los"])
    p.add_argument("--instanz", type=int, required=True)
    p.add_argument("--tempo", type=int, default=40)
    p.add_argument("--daniel-ja", action="store_true", help="Lauf nur nach Daniels Ja")
    p.add_argument("--laeuft-schon", action="store_true", help="Die Instanz laeuft schon, nicht neu starten")
    p.add_argument("--ohne-leertreppe", action="store_true", help="Tempotreppe im leeren Spiel auslassen, sie ist schon gemessen")
    a = p.parse_args(argv)
    pruefe_laufinstanz(a.instanz)
    if a.was == "pruefen":
        aus = pruefen(a.instanz, laeuft_schon=a.laeuft_schon)
        for name, ok, text in aus:
            print(("OK:     " if ok else "FEHLER: ") + name + (f" - {text}" if text else ""))
        return 0 if all(z[1] for z in aus) else 1
    if not a.daniel_ja:
        raise Fehler("Lauf F startet nur mit --daniel-ja")
    print("Aufzeichnung:", los(a.instanz, a.tempo, laeuft_schon=a.laeuft_schon, leertreppe=not a.ohne_leertreppe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
