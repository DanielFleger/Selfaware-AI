# -*- coding: utf-8 -*-
"""Spielmechanik - EIN Werkzeug fuer alles, was ein Versuch braucht (Daniel 15.11.2026 21:11: "spielmechanik (schnellster
start/speichern laden/aufstellung, Testing/Creativemode Sandkasten etc.)").

Uebernommen aus dem alten Zweig (archiv/alt-main-20261104, werkzeug/shc.py, B-150; Daniel 21.10.2026 18:42 "idiotensicher und
instant ... ich kann nicht jedes Mal von vorne anfangen") und auf den heutigen Stand gebracht:
  - start: tools/windows/spiel_starten.ps1 (rechter Bildschirm) und SOFORT ins Hauptmenue (Daniel 15.11. 20:42 "warum klickst du
    am anfang nicht zum menue?").
  - aufstellen: ueber die Lobby wie ein Mensch (Menue-Knoepfe, Mausposition), nie per Skript-Gefecht (Daniel 15.11., startsperre.py):
    Karte per Name, KIs, Teams am Runden Tisch, Schilder tauschen. Gemessen 15.11. 20:42-20:47 (Partie 36).
  - starten: nur mit Daniels Freigabe (data/research/partie_freigabe.json, prueft startsperre.py), haelt bei Takt 1.
  - In Lobby-Partien ist der Mensch KEIN Spieler: bespielbar heisst hier Ansicht 14 und gameOver 0 (der alte Weg verlangte
    zusaetzlich "wir auf Platz 1 als Mensch" - das gilt nur fuer Skript-Gefechte).
Jede Ausgabe beginnt mit "OK:" oder "FEHLER:"; Rueckgabewert 0 bzw. 1.

Aufruf:  uv run selfaware run shc <befehl> [schluessel=wert ...]     (Instanz ueber SHC_INSTANZ, Vorgabe team-liga)
  zustand                      was laeuft gerade (Ansicht, Takt, Pause, Spielende)
  start                        Spiel starten (falls es nicht laeuft) und sofort ins Hauptmenue
  menue                        laufende oder beendete Partie -> Hauptmenue, angehalten
  karten [teil=...]            Kartenliste der Lobby (englische Namen, z. B. Kykladen = Cyclades)
  aufstellen karte=Cyclades kis=8,16,16 [teams=0,1,1] [plaetze=oben_rechts,unten,unten] [art=1] [gold=3]
                               art = Spielart 1 Normal, 2 (mittel), 3 Deathmatch; gold = Regler 1 (menschlicher Vorteil)
                               bis 5 (Computervorteil), 3 ausgeglichen. Gemessen 15.11. 21:38: 20 verschiedene in je 2,8-3,6 s
                               Lobby aufstellen: KIs in dieser Reihenfolge = Spieler 1, 2, 3 ...; teams gleiche Zahl = verbuendet
                               (0 = allein); plaetze je Spieler ein Wort (oben, unten, links, rechts, oben_rechts, ...) oder s1..s8
  starten                      Start-Knopf mit Daniels Freigabe, haelt bei Takt 1
  speichern name=...           laufende Partie speichern (hoechstens 32 Zeichen)
  laden name=...               Spielstand laden - IMMER ueber das Hauptmenue, haelt beim ersten Takt
  editor [groesse=4]           Sandbox: leere Karte im Landschaftseditor, Zeit laeuft, keine KI
  setze spieler= typ= x= y= [anzahl=1]     Einheiten setzen (nur Test: Spiel veraendern, FAIRNESS R2)
  spielende [n=5]              letzte Meldungen des Spielende-Melders
  partie karte=... kis=... [teams= plaetze= art= gold=] [aufstellung=lobby_wie_partie34]
                               aufstellen + mit Daniels Freigabe starten, haelt bei Takt 1 (ohne Freigabe: Lobby bleibt)
  losspielen [pruef_takt=410]  nach Daniels Ja: Lenker je SamurAI-Platz, bis Takt 410, Starttruppen zaehlen, weiter oder halt
Als Baustein: from selfaware.game.ucp import shc; shc.zustand()
"""

import os
import re
import subprocess
import sys
import time

from selfaware import workspace

ANSICHT, GAMEOVER, PAUSE, TICK = 0x01FE7D1C, 0x0117D500, 0x01FEA054, 0x0117CADC
IN_PARTIE, HAUPTMENUE, ENDBILD = 14, 41, 30
# Lobby (gemessen 15.11.2026 20:42-20:47, Partie 36; VillageStudio/doku/Partie-starten.md Schritt 2a/2b/3)
KARTEN_INDEX, KARTEN_NAME, NAME_LAENGE = (
    0x01126E28,
    0x11BFCF8,
    0x3E9,
)  # Eintrag n -> Namensnummer k; Name bei NAME + k*LAENGE
KARTEN_ZEILEN = 8  # sichtbare Zeilen der Kartentabelle (Rollstand n-7)
BELEGUNG, SCHILDER, RAND = (
    0x01A275D0,
    0x1FE9A5C,
    0xF98358,
)  # Schild -> Listenzeile (0xF6 leer); x,y je Schild; Rand
SPIELART, VORTEIL = (
    0x01A245A4,
    0x01A24A4C,
)  # GameSynchronyState 0x0191D768 +0x106E3C / +0x1072E4: 1 Normal .. 3 Deathmatch; Regler 1..5
TEAMS = 0x01A275B5  # Team-Byte je Spieler (Index = Spielernummer)
MAUS_X, MAUS_Y = 0xF2C9C0, 0xF2C9C4
TREFFER_DX, TREFFER_DY = 583, 19  # Trefferpunkt = Schild + Rand + (583, 19)
LEER = 0xF6
WOERTER = {"oben": (0, -1), "unten": (0, 1), "links": (-1, 0), "rechts": (1, 0)}


class Fehler(RuntimeError):
    pass


def _kanal():
    from selfaware.game.ucp import befehl as B

    return B


def senden(liste, warte=2.5, bis=None):
    """Befehlsliste (mit ids) in EINEM Aufruf schicken - im Menue kommen Knoepfe nur als Liste an (Partie-starten.md, gemessen
    15.11.). Gibt die neuen Modul-Logzeilen zurueck."""
    B = _kanal()
    for c in liste:
        c.setdefault("id", B.neue_id())
    return B.sende({"befehle": liste}, warte, bis=bis)


def lesen(stellen, warte=4.0):
    """Mehrere Speicherstellen in EINEM Befehl lesen: stellen = [(adresse, worte)] -> {adresse: [int, ...]} (vorzeichenlos)."""
    z = senden(
        [{"peek": a, "worte": n} for a, n in stellen], warte, bis="PEEK 0x%08X" % stellen[-1][0]
    )
    aus = {}
    for zeile in z:
        m = re.search(r"PEEK 0x([0-9A-F]{8}): ([0-9A-F ]+)", zeile)
        if m:
            aus[int(m.group(1), 16)] = [int(w, 16) & 0xFFFFFFFF for w in m.group(2).split()]
    fehlt = [hex(a) for a, _ in stellen if a not in aus]
    if fehlt:
        raise Fehler("keine Antwort auf peek %s" % ", ".join(fehlt))
    return aus


def bytes_von(worte, n):
    return [b for w in worte for b in w.to_bytes(4, "little")][:n]


def text_von(worte):
    return b"".join(w.to_bytes(4, "little") for w in worte).split(b"\0")[0].decode("latin-1")


# ---------------------------------------------------------------- reine Rechnungen (ohne Spiel pruefbar)


def karten_eintrag(namen, teil):
    """Eintrag einer Karte nach einem Namensteil (ohne Gross/klein). Gibt (n, rollstand, zeile). Mehrdeutig oder fehlend -> Fehler."""
    t = teil.lower()
    treffer = [i for i, nm in enumerate(namen) if t == nm.lower()] or [
        i for i, nm in enumerate(namen) if t in nm.lower()
    ]
    if not treffer:
        raise Fehler(
            "Karte '%s' steht nicht in der Lobby-Liste (%d Karten; Namen sind englisch, z. B. Kykladen = Cyclades)"
            % (teil, len(namen))
        )
    if len(treffer) > 1:
        raise Fehler("Karte '%s' ist mehrdeutig: %s" % (teil, ", ".join(namen[i] for i in treffer)))
    n = treffer[0]
    roll = max(0, n - (KARTEN_ZEILEN - 1))
    return n, roll, n - roll


def schilder_nach_woertern(schilder, woerter):
    """schilder = {schild: (x, y)} (benutzte Schilder der Karte), woerter = je Spieler ein Wort ("oben_rechts", "unten", "s3").
    Gibt je Spieler das Schild - der Reihe nach das noch freie Schild, das am weitesten in Wortrichtung liegt."""
    frei = dict(schilder)
    aus = []
    for w in woerter:
        w = w.strip().lower()
        if re.fullmatch(r"s\d", w):
            s = int(w[1:])
            if s not in frei:
                raise Fehler(
                    "Schild %s gibt es nicht oder ist schon vergeben (frei: %s)" % (w, sorted(frei))
                )
        else:
            teile = [p for p in re.split(r"[_\s-]+", w) if p]
            if not teile or any(p not in WOERTER for p in teile):
                raise Fehler(
                    "Platz '%s' unbekannt - erlaubt: %s oder s1..s8" % (w, ", ".join(WOERTER))
                )
            rx = sum(WOERTER[p][0] for p in teile)
            ry = sum(WOERTER[p][1] for p in teile)
            s = max(frei, key=lambda k: (rx * frei[k][0] + ry * frei[k][1], -k))
        aus.append(s)
        del frei[s]
    return aus


def tauschzuege(belegung, ziel):
    """belegung = {schild: zeile} (aktuelle Lobby), ziel = {zeile: schild}. Ein Zug (von, nach) zieht das Schild der Zeile auf das
    Zielschild; steht dort jemand, tauschen beide (gemessen 15.11. 20:46: Kriegsfuerst auf das besetzte Schild 2 -> SamurAI kam auf
    Schild 4; auf ein leeres Schild = verschieben). Gibt die Zuege und die Belegung danach."""
    b = dict(belegung)
    zuege = []
    for zeile, nach in ziel.items():
        von = next((s for s, z in b.items() if z == zeile), None)
        if von is None:
            raise Fehler("Zeile %d steht auf keinem Schild (Belegung %s)" % (zeile, b))
        if von == nach:
            continue
        anderer = b.get(nach)
        b[nach] = zeile
        if anderer is None:
            del b[von]
        else:
            b[von] = anderer
        zuege.append((von, nach))
    return zuege, b


def trefferpunkt(xy, rand):
    return xy[0] + rand[0] + TREFFER_DX, xy[1] + rand[1] + TREFFER_DY


def team_klicks(teams):
    """teams je Spieler (Liste, Spieler 1 zuerst; gleiche Zahl > 0 = verbuendet). Runder Tisch: Sitz i waehlen, Sitz j dazusetzen
    (Ghidra MenuItemActionHandler_Roundtable_Main 0x004AEA50; gemessen 15.11.: Sitze 2 und 3 -> Team-Bytes 00 01 01).
    Sitz = Spielernummer ist nur fuer diesen einen Fall gemessen - aufstellen liest die Team-Bytes danach nach."""
    klicks = []
    for t in sorted({t for t in teams if t > 0}):
        mit = [i + 1 for i, x in enumerate(teams) if x == t]
        if len(mit) >= 2:
            klicks += [mit[0], mit[1]]  # beide ohne Team -> sie bekommen eine neue Teamnummer
        for j in mit[2:]:
            # der Neue zuerst, dann ein Mitglied, das schon ein Team hat (andersherum zog der Klick Spieler mit[0] in ein
            # NEUES Team - gemessen 15.11. 21:36, Lauf 7 und 17 von lobby20: soll 1,2,2,2, Team-Bytes 0,0,1,1)
            klicks += [j, mit[0]]
    return klicks


# ---------------------------------------------------------------- Spiel


def zustand():
    """dict: antwortet, ansicht, text, gameover, pause, tick."""
    try:
        w = lesen([(ANSICHT, 1), (GAMEOVER, 1), (PAUSE, 1), (TICK, 1)])
    except Exception as e:  # Kanal antwortet nicht: Spiel aus oder Modul nicht aktiv
        return {"antwortet": False, "text": "Spiel antwortet nicht (%s)" % str(e)[:80]}
    a, g, p, t = w[ANSICHT][0], w[GAMEOVER][0], w[PAUSE][0], w[TICK][0]
    if a == IN_PARTIE:
        text = (
            "Partie VORBEI (gameOver 1)" if g else "Partie laeuft" + (" (angehalten)" if p else "")
        )
    else:
        text = {HAUPTMENUE: "Hauptmenue", ENDBILD: "Endbildschirm (Partie vorbei)"}.get(
            a, "Ansicht %d" % a
        )
    return {"antwortet": True, "ansicht": a, "text": text, "gameover": g, "pause": p, "tick": t}


def partie_sicher(z=None):
    z = z or zustand()
    if not (z.get("antwortet") and z["ansicht"] == IN_PARTIE and z["gameover"] == 0):
        raise Fehler("keine bespielbare Partie: %s" % z)
    return z


def _instanz_nummer():
    from selfaware.game.ucp import instanzen

    return instanzen.eintrag()["nummer"]


def start():
    """Spiel starten (falls es nicht antwortet) und SOFORT ins Hauptmenue - im selben Aufruf."""
    z = zustand()
    if not z["antwortet"]:
        skript = os.path.join(workspace.ROOT, "tools", "windows", "spiel_starten.ps1")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                skript,
                "-Instanz",
                str(_instanz_nummer()),
                "-Rechts",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        ende = time.time() + 120
        while time.time() < ende and not z["antwortet"]:
            time.sleep(0.3)
            z = zustand()
        if not z["antwortet"]:
            raise Fehler("Spiel antwortet 120 s nach dem Start nicht")
    if z["ansicht"] != HAUPTMENUE:
        menue()
    return "Spiel laeuft, Hauptmenue: %s" % zustand()["text"]


def warte_ansicht(soll, frist=5.0):
    """Statt fester Wartezeit: alle 0,05 s nachsehen, bis die Ansicht soll ist (Daniel 15.11. 21:25 "jede sekunde hier entsprechend
    stunden"; gemessen 21:29: ein Menue-Befehl ist nach 0,3 s quittiert). soll: Zahl oder Pruefung auf die Ansicht."""
    pruefe = soll if callable(soll) else (lambda a: a == soll)
    ende = time.time() + frist
    while True:
        z = zustand()
        if z.get("antwortet") and pruefe(z["ansicht"]):
            return z
        if time.time() > ende:
            raise Fehler("Ansicht %s nach %.0f s nicht erreicht: %s" % (soll, frist, z))
        time.sleep(0.05)


def menue():
    """Laufende oder beendete Partie (oder Startbild, Editor) -> Hauptmenue, angehalten. Angehalten, damit ein folgendes Laden
    im ersten Takt stehen bleibt (05.10.: ohne Pause setzte die Niederlage-Pruefung gameOver 1)."""
    vorher = zustand()
    if not vorher.get("antwortet"):
        raise Fehler(vorher["text"])
    z = vorher
    if vorher["ansicht"] != HAUPTMENUE:
        # Anhalten und Wechsel in EINEM Aufruf (gemessen 21:31: im Menue kostet jeder Aufruf 0,33 s, in der Partie 0,04 s)
        senden([{"pause": True}, {"menue": HAUPTMENUE}], 3.0)
        z = warte_ansicht(HAUPTMENUE)
    if z["pause"] != 1:
        senden([{"pause": True}], 2.0)
        z = zustand()
        if z["pause"] != 1:
            raise Fehler("Spiel laesst sich nicht anhalten: %s" % z)
    return "Ansicht %d -> Hauptmenue, angehalten" % vorher["ansicht"]


def _kartenliste_datei():
    return os.path.join(_kanal().SPIEL, "ucp", "villagestudio", "samurai_kartenliste.json")


def kartenliste(neu=False):
    """Namen der Lobby-Karten (Eintrag n). Einmal je Spielordner gemerkt - sie aendern sich nur mit neuen Karten; aufstellen prueft
    die gewaehlte Zeile im selben Aufruf nach (Namensnummer) und liest bei Abweichung neu."""
    import json

    pfad = _kartenliste_datei()
    if not neu:
        try:
            with open(pfad, encoding="utf-8") as f:
                d = json.load(f)
            return d["namen"], d["k"]
        except (OSError, ValueError, KeyError):
            pass
    k = lesen([(KARTEN_INDEX, 200)])[KARTEN_INDEX]
    n = next((i for i, v in enumerate(k) if v == 0 and i > 0), len(k))
    stellen = [(KARTEN_NAME + kk * NAME_LAENGE, 10) for kk in k[:n]]
    namen = lesen(stellen, 6.0)
    erg = [text_von(namen[a]) for a, _ in stellen], k[:n]
    try:
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump({"namen": erg[0], "k": erg[1]}, f, ensure_ascii=False)
    except OSError:
        pass
    return erg


def karten(teil=""):
    namen = kartenliste(neu=True)[0]
    zeigen = [(i, nm) for i, nm in enumerate(namen) if teil.lower() in nm.lower()]
    return "%d Karten%s: %s" % (
        len(zeigen),
        " mit '%s'" % teil if teil else "",
        "; ".join("%d %s" % x for x in zeigen),
    )


def lesen_nach(befehle, warte=3.0):
    """Befehle und peeks in EINEM Aufruf; gibt die gelesenen Stellen {adresse: [worte]} (vorzeichenlos)."""
    aus = {}
    for zeile in senden(befehle, warte):
        m = re.search(r"PEEK 0x([0-9A-F]{8}): ([0-9A-F ]+)", zeile)
        if m:
            aus[int(m.group(1), 16)] = [int(w, 16) & 0xFFFFFFFF for w in m.group(2).split()]
    return aus


def lobby():
    """Belegung, Schilder, Rand und Teams der Lobby."""
    w = lesen([(BELEGUNG, 2), (SCHILDER, 16), (RAND, 2), (TEAMS, 3)])
    bel = {i + 1: b for i, b in enumerate(bytes_von(w[BELEGUNG], 8)) if b != LEER}
    sch = {
        i + 1: (w[SCHILDER][2 * i], w[SCHILDER][2 * i + 1])
        for i in range(8)
        if w[SCHILDER][2 * i] != 0xFFFFFFFF
    }
    return {
        "belegung": bel,
        "schilder": sch,
        "rand": tuple(w[RAND]),
        "teams": bytes_von(w[TEAMS], 9),
    }


def aufstellen(karte, kis, teams="", plaetze="", art="1", gold="3", _wieder=False):
    """Lobby wie ein Mensch aufstellen: Hauptmenue -> Eigenes Gefecht, Karte, KIs, Teams, Schilder. Startet NICHT (das macht
    starten mit Daniels Freigabe). Prueft am Ende Karte, Belegung und Teams aus dem Speicher."""
    ki = [int(x) for x in str(kis).split(",") if x.strip()]
    tm = [int(x) for x in str(teams).split(",") if x.strip()] if teams else []
    pl = [x for x in str(plaetze).split(",") if x.strip()] if plaetze else []
    if not ki:
        raise Fehler("kis=... fehlt (KI-Nummern je Spieler, z. B. kis=8,16,16)")
    if tm and len(tm) != len(ki) or pl and len(pl) != len(ki):
        raise Fehler("teams und plaetze brauchen je %d Eintraege (einen je KI)" % len(ki))
    t0 = time.time()
    if zustand().get("ansicht") != HAUPTMENUE:
        menue()
    senden([{"kreuzzug": 2}], 3.0)
    warte_ansicht(
        lambda a: a != HAUPTMENUE
    )  # Lobby (Ansicht 20, gemessen 21:29)  # eigener Aufruf, sonst zu frueh (gemessen 15.11.)
    namen, kliste = kartenliste()
    n, roll, zeile = karten_eintrag(namen, karte)
    # Aufruf 1: Karte, Spielart, Gold-Regler; im selben Aufruf die gemerkte Liste und die Platzzahl der Karte pruefen
    a = lesen_nach(
        [
            {"peek": KARTEN_INDEX + 4 * n, "worte": 1},
            {"knopf": "LobbyMenu_MapSelectScrollbar", "nr": 0, "art": 3, "wert": roll},
            {"knopf": "LobbyMenu_MapSelectTable", "nr": zeile},
            {"knopf": "LobbyMenu_SkirmishTypeAndBalance", "nr": int(art)},
            {"knopf": "LobbyMenu_SkirmishTypeAndBalance", "nr": 9 + int(gold)},
            {"peek": SPIELART, "worte": 1},
            {"peek": VORTEIL, "worte": 1},
        ]
    )
    if a.get(KARTEN_INDEX + 4 * n, [None])[0] != kliste[n]:
        if _wieder:
            raise Fehler(
                "Kartenliste passt nicht: Eintrag %d hat Nummer %s statt %s"
                % (n, a.get(KARTEN_INDEX + 4 * n), kliste[n])
            )
        kartenliste(
            neu=True
        )  # gemerkte Liste veraltet (neue Karten) - neu lesen und noch einmal aufstellen
        return aufstellen(karte, kis, teams, plaetze, art, gold, _wieder=True)
    # Schilder erst lesen, wenn die neue Karte steht - im selben Aufruf wie die Kartenwahl stehen noch die alten (gemessen 21:50:
    # "0 Plaetze" auf Battle Brother's Strife)
    ende = time.time() + 3.0
    while True:
        sch = lesen([(SCHILDER, 16)])[SCHILDER]
        platz = sum(1 for i in range(8) if sch[2 * i] != 0xFFFFFFFF)
        if platz or time.time() > ende:
            break
        time.sleep(0.05)
    if len(ki) > platz:
        raise Fehler("Karte '%s' hat %d Plaetze, verlangt sind %d KIs" % (namen[n], platz, len(ki)))
    if (a[SPIELART][0], a[VORTEIL][0]) != (int(art), int(gold)):
        raise Fehler(
            "Spielart/Gold stehen nicht: soll %s/%s, ist %s/%s"
            % (art, gold, a[SPIELART][0], a[VORTEIL][0])
        )
    # Aufruf 2: KIs und Runder Tisch
    befehle = []
    for k in ki:
        befehle += [
            {"knopf": "LobbyMenu_PlayerListAndNpcButtons", "nr": -101},
            {"knopf": "AiLordSelect_Main", "nr": k},
            {"knopf": "AiLordSelect_Main", "nr": 100},
        ]
    klicks = team_klicks(tm) if tm else []
    if klicks:
        befehle += [{"knopf": "LobbyMenu_PlayerListAndNpcButtons", "nr": -102}]
        befehle += [{"knopf": "Roundtable_Main", "nr": s} for s in klicks] + [
            {"knopf": "Roundtable_Main", "nr": 100}
        ]
    senden(befehle, 3.0)
    lb = lobby()
    if tm:
        ist = lb["teams"][1 : 1 + len(ki)]
        gleich = all(
            (tm[a] == tm[b]) == (ist[a] == ist[b] and tm[a] > 0)
            for a in range(len(ki))
            for b in range(len(ki))
            if a != b
        )
        if not gleich:
            raise Fehler("Teams stehen nicht wie verlangt: soll %s, Team-Bytes %s" % (tm, ist))
    zuege = []
    if pl:
        soll = schilder_nach_woertern(lb["schilder"], pl)
        zuege, _ = tauschzuege(lb["belegung"], {z: s for z, s in enumerate(soll)})
        b = []
        for von, nach in zuege:
            x1, y1 = trefferpunkt(lb["schilder"][von], lb["rand"])
            x2, y2 = trefferpunkt(lb["schilder"][nach], lb["rand"])
            b += [
                {"poke": MAUS_X, "wert": x1},
                {"poke": MAUS_Y, "wert": y1},
                {"knopf": "LobbyMenu_LobbyscreenStartButtonClick", "nr": -200},
                {"poke": MAUS_X, "wert": x2},
                {"poke": MAUS_Y, "wert": y2},
                {"knopf": "LobbyMenu_LobbyscreenStartButtonClick", "nr": -201},
            ]
        if b:
            senden(b, 3.0)
        lb = lobby()
        ist = {z: s for s, z in lb["belegung"].items()}
        falsch = {z: (soll[z], ist.get(z)) for z in range(len(ki)) if ist.get(z) != soll[z]}
        if falsch:
            raise Fehler("Schilder stehen nicht wie verlangt (Spieler: soll, ist): %s" % falsch)
    return (
        "Lobby steht in %.1f s: Karte '%s', Spielart %s, Gold-Regler %s, KIs %s, Teams %s, Schilder %s (Zuege %s) - Start nur mit Daniels Freigabe: shc starten"
        % (
            time.time() - t0,
            namen[n],
            art,
            gold,
            ki,
            lb["teams"][1 : 1 + len(ki)],
            lb["belegung"],
            zuege,
        )
    )


def starten():
    """Start-Knopf - startsperre.py laesst ihn nur mit Daniels Freigabe durch; haelt bei Takt 1."""
    z = senden(
        [{"tickpause": {"bei": 1}}, {"knopf": "LobbyMenu_LobbyscreenStartButtonClick", "nr": 4}],
        3.0,
    )
    if any("STARTSPERRE" in x and "verbraucht" not in x for x in z):
        raise Fehler("Startsperre: %s" % [x for x in z if "STARTSPERRE" in x][-1][-200:])
    ende = time.time() + 30
    while time.time() < ende:
        s = zustand()
        if s.get("ansicht") == IN_PARTIE and s.get("tick", 0) >= 1:
            return "Partie gestartet, haelt bei Takt %d: %s" % (s["tick"], s["text"])
        time.sleep(0.5)
    raise Fehler("Partie nach 30 s nicht gestartet: %s" % zustand())


def speichern(name):
    from selfaware.game.ucp.speichern import speichere

    partie_sicher()
    if len(name) > 32:
        raise Fehler("Name hat %d Zeichen, hoechstens 32" % len(name))
    pfad = speichere(name)
    partie_sicher()
    return "gespeichert als '%s' (%s)" % (name, os.path.basename(str(pfad)))


def laden(name):
    """Spielstand IMMER ueber das Hauptmenue laden (aus der laufenden Partie geladen setzte die Niederlage-Pruefung gameOver 1,
    gemessen 05.10.); haelt beim ersten Takt und prueft die Partie."""
    from selfaware.game.ucp import laden as LD

    menue()
    senden(
        [{"hauptmenue": 8}, {"optionen": 2}], 3.0
    )  # Einstellungen, dann Lade-Dialog - in EINEM Aufruf
    anzahl = 0
    ende = time.time() + 5.0
    while not 0 < anzahl <= 500:
        anzahl = lesen([(LD.ANZAHL, 1)])[LD.ANZAHL][0]
        if time.time() > ende:
            raise Fehler("Lade-Dialog nicht offen (Anzahl %d)" % anzahl)
    k = lesen([(LD.LISTE, anzahl)])[LD.LISTE]
    stellen = [(LD.NAMEN + kk * LD.NAMENSLAENGE, 10) for kk in k]
    roh = lesen(stellen, 6.0)  # alle Namen in EINEM Befehl (vorher ein Befehl je Name)
    namen = [text_von(roh[a]) for a, _ in stellen]
    if name not in namen:
        raise Fehler("'%s' steht nicht in der Liste (%d Spielstaende)" % (name, len(namen)))
    n = namen.index(name)
    roll = max(0, n - 15)
    antwort = senden(
        [
            {"ladepause": True},
            {"poke": LD.SCROLL, "wert": roll},
            {"poke": LD.MARKIERT, "wert": n - roll},
            {"laden": 2},
        ],
        8.0,
        bis="LADEPAUSE: Laden erkannt",
    )
    senden(
        [{"pause": True}, {"ladepause": "aus"}], 2.0
    )  # Sicherheitsnetz, nichts scharf zuruecklassen
    # Als Partner wartet der Kanal nur auf die Quittung, die vor der Lade-Meldung kommt (gemessen 22:04) - im Protokoll weiterlesen
    erkannt = any("LADEPAUSE: Laden erkannt" in x for x in antwort)
    frist = time.time() + 8.0
    while not erkannt and time.time() < frist:
        with open(_kanal().LOG, encoding="utf-8", errors="replace") as f:
            f.seek(max(0, os.path.getsize(_kanal().LOG) - 20000))
            erkannt = "LADEPAUSE: Laden erkannt" in f.read()
        time.sleep(0.1)
    if not erkannt:
        raise Fehler("die Lade-Pause hat kein Laden erkannt - Stand unsicher: %s" % zustand())
    t1 = zustand()
    time.sleep(0.3)
    z = partie_sicher()
    if z["tick"] != t1["tick"] or z["pause"] != 1:
        raise Fehler(
            "Spiel steht nicht still (Tick %d / %d, Pause %d)" % (t1["tick"], z["tick"], z["pause"])
        )
    return "'%s' geladen, haelt bei Takt %d: %s" % (name, z["tick"], z["text"])


def editor(groesse="4"):
    """Sandbox im Spiel: Eigene Szenarien -> Neue Karte -> Landschaftseditor; Zeit laeuft, keine KI, keine Arbeiter (Rezept aus
    dem alten Werkzeug, gemessen 21.10. 19 s). groesse: Knopf der Kartengroesse (1 = 160x160, 4 = 400x400)."""
    menue()
    schritte = [
        ({"hauptmenue": 9}, 44, "Eigene Szenarien"),
        ({"knopf": "CustomScenarios_Main", "nr": 2}, 18, "Kartentyp"),
        ({"knopf": "NewMapMaptype_Buttons", "nr": 3}, 31, "Kartengroesse"),
        ({"knopf": "NewMapMapsize_Buttons", "nr": int(groesse)}, 17, "Karteneigenschaften"),
        ({"menue": 12}, None, "Landschaftseditor"),
    ]
    weg = []
    for b, soll, name in schritte:
        vorher = zustand().get("ansicht")
        senden([b], 3.0)
        try:
            a = warte_ansicht(soll if soll is not None else (lambda x, v=vorher: x != v))["ansicht"]
        except Fehler as e:
            raise Fehler(
                "Editor-Weg haengt bei '%s' (%s): %s" % (name, ", ".join(weg), e)
            ) from None
        weg.append("%s=%s" % (name, a))
    senden([{"pause": False}], 2.0)
    t0 = zustand()["tick"]
    ende = time.time() + 3.0
    z = zustand()
    while z["tick"] <= t0 and time.time() < ende:
        time.sleep(0.1)
        z = zustand()
    if z["tick"] <= t0:
        raise Fehler(
            "im Editor laeuft die Zeit nicht (Tick %d -> %d, %s)" % (t0, z["tick"], ", ".join(weg))
        )
    return "Editor offen (Ansicht %d), Zeit laeuft (Tick %d -> %d); Weg: %s" % (
        z["ansicht"],
        t0,
        z["tick"],
        ", ".join(weg),
    )


def setze(spieler="1", typ="26", x="200", y="200", anzahl="1"):
    """Einheiten setzen - veraendert das Spiel, also nur im Test (FAIRNESS R2). Gemessen 17.10.: sie stehen 1 Feld weiter."""
    z = senden(
        [
            {
                "setzeEinheit": {
                    "spieler": int(spieler),
                    "typ": int(typ),
                    "x": int(x),
                    "y": int(y),
                    "anzahl": int(anzahl),
                }
            }
        ],
        1.5,
    )
    for zeile in z:
        m = re.search(r"Nummern ([0-9,]+)", zeile)
        if m:
            nrs = [int(n) for n in m.group(1).split(",") if int(n) > 0]
            if len(nrs) != int(anzahl):
                raise Fehler("nur %d von %s gesetzt: %s" % (len(nrs), anzahl, zeile))
            return "Spieler %s Typ %s x%s bei (%s,%s): Nummern %s" % (
                spieler,
                typ,
                anzahl,
                x,
                y,
                nrs,
            )
    raise Fehler("setzeEinheit ohne Antwort")


def spielende(n="5"):
    """B-154: letzte Zeilen des Spielende-Melders (logik.lua schreibt ucp/villagestudio/spielende.txt)."""
    try:
        with open(
            os.path.join(_kanal().SPIEL, "ucp", "villagestudio", "spielende.txt"),
            encoding="utf-8",
            errors="replace",
        ) as f:
            z = [x.rstrip("\n") for x in f.readlines()[-int(n) :]]
    except OSError:
        z = []
    return "\n".join(z) if z else "noch kein Spielende gemeldet"


def stopp():
    """Daniel 15.11.2026 22:26 "Dein stop kam viel zu spaet, locker 30 sekunden, es sollte instant gehen": EIN Pause-Befehl als
    Allererstes (in der Partie quittiert nach ~0,04 s), erst danach Lenker beenden - der wuerde ein stehendes Spiel sonst fortsetzen."""
    t0 = time.time()
    senden([{"pause": True}], 2.0)
    dt = time.time() - t0
    weg = lenker_stoppen()
    senden([{"pause": True}], 2.0)
    return "angehalten nach %.2f s, %d Lenker beendet: %s" % (dt, weg, zustand()["text"])


def zustand_text():
    z = zustand()
    return "%s | %s" % (z["text"], z)


SAMURAI_KI = 16  # SamurAI sitzt auf dem Abt-Platz (aiSwapper abbot -> SamurAI)
STARTTRUPPEN_SOLL = {
    22: 5,
    24: 7,
}  # Typ: Anzahl je SamurAI (B-189, gemessen 15.11. 20:51: 5 Bogen + 7 Speer)


def _laufend_datei():
    return os.path.join(workspace.DATA, "partie_laufend.json")


def freigabe_offen():
    """Daniels Freigabe (data/research/partie_freigabe.json) liegt vor und ist nicht verbraucht? (startsperre.py verbraucht sie)."""
    import json

    try:
        with open(os.path.join(workspace.DATA, "partie_freigabe.json"), encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    return d if d.get("daniel") and not d.get("verbraucht") else None


def samurai_spieler(kis):
    """Spielernummern (1-basiert, Reihenfolge der KIs = Spieler 1, 2, ...) der SamurAI-Plaetze."""
    return [
        i + 1
        for i, k in enumerate(int(x) for x in str(kis).split(",") if x.strip())
        if k == SAMURAI_KI
    ]


def partie(karte, kis, teams="", plaetze="", art="1", gold="3", aufstellung="lobby_wie_partie34"):
    """Ganzer Weg bis Takt 1: aufstellen, mit Daniels Freigabe starten, bei Takt 1 halten. Ohne Freigabe bleibt die Lobby stehen.
    Danach (nach Daniels Ja): shc losspielen."""
    import json

    t0 = time.time()
    alte = (
        lenker_stoppen()
    )  # Konsistenz (Daniel 21:50): jeder Start beginnt ohne Lenker einer frueheren Partie
    text = aufstellen(karte, kis, teams, plaetze, art, gold)
    sp = samurai_spieler(kis)
    if not freigabe_offen():
        return (
            "%s | KEINE offene Freigabe in data/research/partie_freigabe.json - Daniel fragen, dann: shc starten"
            % text
        )
    s = starten()
    with open(_laufend_datei(), "w", encoding="utf-8") as f:
        json.dump(
            {
                "karte": karte,
                "kis": kis,
                "teams": teams,
                "samurai": sp,
                "aufstellung": aufstellung,
                "zeit": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            f,
            ensure_ascii=False,
        )
    warnung = (
        " | ACHTUNG: %d SamurAI - der Lenker kennt noch keine Verbuendeten (Modulzuordnung Teil 6)"
        % len(sp)
        if len(sp) > 1
        else ""
    )
    # Daniel 15.11. 21:49 "das spiel auch wirklich starten ... es muss sofort samurai uebernehmen": kein Halt mehr bei Takt 1 -
    # die Freigabe gilt fuer den Start, losspielen laeuft gleich weiter (Lenker uebernehmen, dann laeuft das Spiel)
    los = losspielen()
    return "%s | %s | %s in %.1f s | SamurAI auf Spieler %s%s%s" % (
        text,
        s,
        los,
        time.time() - t0,
        sp,
        warnung,
        " | %d alte Lenker beendet" % alte if alte else "",
    )


def _lebt(pid):
    r = subprocess.run(
        ["tasklist", "/FI", "PID eq %d" % pid, "/NH"],
        capture_output=True,
        text=True,
        encoding="cp850",
        errors="replace",
    )
    return str(pid) in (r.stdout or "")


def _starte_lenker(sp, stempel, aufstellung):
    """Lenker ueber WMI starten: ein Kind dieses Prozesses endet mit dem Befehl, der es gestartet hat (gemessen 22:09, Lenker stand ab
    Takt 9092 still; Loesen aus der Umgebung verweigert Windows). Gibt die Prozessnummer der cmd-Huelle (taskkill /T trifft den Lenker mit)."""
    aus = os.path.join(workspace.DATA, "partie_%s_lenker_sp%d.txt" % (stempel, sp))
    huelle = os.path.join(workspace.DATA, "partie_%s_lenker_sp%d.cmd" % (stempel, sp))
    with open(huelle, "w", encoding="ascii") as f:
        zeilen = [
            "@echo off",
            "set SHC_INSTANZ=%s" % os.environ.get("SHC_INSTANZ", "team-liga"),
            "set SHC_SPIELER=%d" % sp,
            "set SHC_PARTNER=ja",
            "set PYTHONPATH=%s" % os.path.join(workspace.ROOT, "src"),
            '"%s" -u -m selfaware.runtime.live.erstes_spiel aufstellung=%s > "%s" 2>&1'
            % (sys.executable, aufstellung, aus),
        ]
        f.write("".join(z + chr(13) + chr(10) for z in zeilen))
    befehl = (
        "(Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='cmd /c \"%s\"'; "
        "CurrentDirectory='%s'}).ProcessId" % (huelle, workspace.ROOT)
    )
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command", befehl],
        capture_output=True,
        text=True,
        encoding="cp850",
        errors="replace",
    )
    try:
        return int(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise Fehler(
            "Lenker fuer Spieler %d nicht gestartet: %s" % (sp, (r.stderr or r.stdout)[-200:])
        ) from None


def lenker_stoppen():
    """Lenker einer frueheren Partie (PIDs in partie_laufend.json) beenden und nachsehen, dass sie weg sind. Gibt ihre Zahl."""
    import json

    try:
        with open(_laufend_datei(), encoding="utf-8") as f:
            pids = json.load(f).get("lenker_pids", [])
    except (OSError, ValueError):
        return 0
    weg = 0
    for pid in pids:
        r = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            text=True,
            encoding="cp850",
            errors="replace",
        )
        weg += r.returncode == 0
    for pid in pids:
        r = subprocess.run(
            ["tasklist", "/FI", "PID eq %d" % pid, "/NH"],
            capture_output=True,
            text=True,
            encoding="cp850",
            errors="replace",
        )
        if str(pid) in r.stdout:
            raise Fehler("Lenker %d laeuft nach dem Beenden noch" % pid)
    return weg


def einheiten_zaehlen():
    """{(besitzer, typ): anzahl} aller lebenden Einheiten (logik.lua einheitenroh)."""
    zaehl = {}
    for zeile in senden([{"einheitenroh": 2500, "player": 1}], 8.0):
        m = re.search(r"\]\s*zustand=(-?\d+) typ=(\d+) owner=(\d+)", zeile)
        if m:
            k = (int(m.group(3)), int(m.group(2)))
            zaehl[k] = zaehl.get(k, 0) + 1
    return zaehl


def losspielen(pruef_takt="410"):
    """Nach Daniels Ja: je SamurAI-Platz einen Lenker starten (Aufstellung aus partie), bis pruef_takt laufen lassen, die Starttruppen
    je SamurAI zaehlen; stimmen sie, weiterspielen - sonst anhalten und die Lenker beenden (Daniel 15.11. 20:23: vor dem Spiel messen)."""
    import json

    with open(_laufend_datei(), encoding="utf-8") as f:
        lauf = json.load(f)
    B = _kanal()
    B.PARTNER = True  # Lenker und Werkzeug teilen sich den Kanal (je Befehl gesperrt)
    B.belege()
    stempel = time.strftime("%Y%m%d_%H%M%S")
    senden([{"tickpause": {"bei": int(pruef_takt)}}], 2.0)
    prozesse = [_starte_lenker(sp, stempel, lauf["aufstellung"]) for sp in lauf["samurai"]]
    lauf["lenker_pids"] = list(prozesse)
    with open(_laufend_datei(), "w", encoding="utf-8") as f:
        json.dump(lauf, f, ensure_ascii=False)
    # Erst laufen lassen, wenn JEDER Lenker die KI seines Platzes aus hat (Daniel 21:49 "es muss sofort samurai uebernehmen";
    # vorher lief die eingebaute KI bis Takt 438)
    uebernommen = {}
    frist = time.time() + 60
    while len(uebernommen) < len(prozesse) and time.time() < frist:
        for sp in lauf["samurai"]:
            pfad = os.path.join(workspace.DATA, "partie_%s_lenker_sp%d.txt" % (stempel, sp))
            try:
                with open(pfad, encoding="utf-8", errors="replace") as f:
                    m = re.search(
                        r"UEBERNEHMEN: KI von Spieler %d bei Tick (\d+) aus" % sp, f.read()
                    )
            except OSError:
                m = None
            if m:
                uebernommen[sp] = int(m.group(1))
        if not all(_lebt(p) for p in prozesse):
            break
        time.sleep(0.1)
    if len(uebernommen) < len(prozesse):
        lenker_stoppen()
        raise Fehler(
            "Lenker haben nicht uebernommen (gemeldet %s) - Spiel bleibt angehalten, Lenker gestoppt"
            % uebernommen
        )
    senden([{"pause": False}], 2.0)
    ende = time.time() + 180
    z = zustand()
    while not (z.get("tick", 0) >= int(pruef_takt) and z.get("pause") == 1) and time.time() < ende:
        if not all(_lebt(p) for p in prozesse):
            break
        time.sleep(0.5)
        z = zustand()
    zaehl = einheiten_zaehlen()
    ist = {sp: {t: zaehl.get((sp, t), 0) for t in STARTTRUPPEN_SOLL} for sp in lauf["samurai"]}
    falsch = {sp: v for sp, v in ist.items() if v != STARTTRUPPEN_SOLL}
    tot = [sp for sp, p in zip(lauf["samurai"], prozesse, strict=True) if not _lebt(p)]
    if falsch or tot or z.get("tick", 0) < int(pruef_takt):
        lenker_stoppen()
        raise Fehler(
            "ANGEHALTEN bei Takt %s: Starttruppen je SamurAI %s (soll %s), Lenker beendet %s - Lenker gestoppt"
            % (z.get("tick"), ist, STARTTRUPPEN_SOLL, tot)
        )
    senden([{"pause": False}], 2.0)
    return (
        "SamurAI uebernahm bei Takt %s; Partie laeuft ab Takt %d: Starttruppen stimmen %s, Lenker fuer Spieler %s (Mitschrift data/research/partie_%s_lenker_sp*.txt)"
        % (uebernommen, z["tick"], ist, lauf["samurai"], stempel)
    )


BEFEHLE = {
    "zustand": zustand_text,
    "start": start,
    "menue": menue,
    "karten": karten,
    "aufstellen": aufstellen,
    "starten": starten,
    "speichern": speichern,
    "laden": laden,
    "editor": editor,
    "setze": setze,
    "spielende": spielende,
    "partie": partie,
    "stopp": stopp,
    "losspielen": losspielen,
}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in BEFEHLE:
        print(__doc__)
        return 1
    try:
        args = dict(x.split("=", 1) for x in argv[1:])
    except ValueError:
        print("FEHLER: Angaben als schluessel=wert, z. B. karte=Cyclades", flush=True)
        return 1
    B = _kanal()
    # Immer als Partner (je Befehl gesperrt): ein shc-Aufruf neben einem laufenden Lenker darf ihm den Kanal nicht wegnehmen -
    # gemessen 15.11. 21:50: 'shc zustand' belegte den Kanal, der Lenker brach mit KANAL BELEGT ab, SamurAI stand still
    B.PARTNER = True
    B.belege()
    try:
        print("OK:", BEFEHLE[argv[0]](**args), flush=True)
        return 0
    except Fehler as e:
        print("FEHLER:", e, flush=True)
        return 1
    except Exception as e:  # auch Unerwartetes laut melden, nie still
        print("FEHLER: %s: %s | Zustand jetzt: %s" % (type(e).__name__, e, zustand()), flush=True)
        return 1
    finally:
        B.freigeben()


if __name__ == "__main__":
    sys.exit(main())
