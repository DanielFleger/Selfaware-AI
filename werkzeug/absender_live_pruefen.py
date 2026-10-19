# -*- coding: utf-8 -*-
"""B-94 im Spiel pruefen (19.10.2026, Daniel 21:52: "SamurAIs Befehle sollen niemals einen anderen Spieler beeinflussen").
Braucht logik.lua mit Absender je Befehl (logik_stand_20261019.lua ab 22:40) in der Instanz (SHC_INSTANZ), Lenker aus.

Aufbau wie spieler2_pruefen.py: frisches Gefecht Green Haven, wir Platz 4 (Spieler 1), Nomade Platz 3 (Spieler 2), KI von
Spieler 2 aus. Dann:
  A. Absender eingebaut (logik.lua meldet es)
  B. EIN Paket: Holzfaeller fuer Spieler 2 (wie SamurAI) + Holzfaeller OHNE Spieler (wie ein Klick des Menschen)
     -> Besitzer 2 bzw. 1
  C. "ich" (0x01A275DC) direkt nach dem Paket = 1 (gelesen ohne Spieler, also ohne Umschalten)
  D. Auswahl des Menschen: ein Muster in der Auswahl-Leiste (letztes Wort, Einheiten 3168-3199) uebersteht einen
     Angriffsbefehl von Spieler 2 - nach dem Einreihen UND nach dem Ausfuehren
  E. GEGENPROBE: {"absender": "aus"} (alter Weg: "ich" einen Takt auf Spieler 2) - derselbe Paket-Aufbau wie B muss den
     alten Fehler zeigen: der Klick-Holzfaeller gehoert dann Spieler 2. Danach wieder {"absender": "an"}.
  F. "ich" am Ende 1
Aufruf: SHC_INSTANZ=5 python werkzeug/absender_live_pruefen.py"""
import re
import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import befehl as kanal
import spieler2_pruefen as S2
from serie import zuruecksetzen

SLOT, AI, FULL = 0x01A275DC, 0x0191DE7C, 0x0191DE10
AITYP2 = 0x0115BDF8 + 2 * 0x39F4 + 0x2300
LETZTES_WORT = 0x01387F38 + 116 + 99 * 4
MUSTER = 0x5A5A5A5A
ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%-4s %s %s" % ("OK" if bed else "ROT", nr, text), flush=True)


def peek_roh(adr):
    """ohne "player" - liest, ohne "ich" umzustellen"""
    for z in kanal.sende({"peek": adr, "worte": 1}, 1.0, bis="PEEK"):
        m = re.search(r"PEEK 0x%08X: (\w+)" % adr, z)
        if m:
            return int(m.group(1), 16)


def absender(was):
    # als Liste: im Hauptmenue reicht das Modul nur Listen und ausgewaehlte Befehle an logik.lua weiter (init.lua)
    z = " ".join(kanal.sende({"befehle": [{"id": kanal.neue_id(), "absender": was}]}, 1.5, bis="ABSENDER %s" % was))
    m = re.search(r"ABSENDER %s: [^\n]*" % was, z)
    return m.group(0) if m else z[-200:]


def stelle(sp, um, belegt, versaetze):
    """erster freie Holzfaeller-Platz bei einem der Versaetze (der Test braucht mehrere Bauten nebeneinander)"""
    for dx, dy in versaetze:
        p = S2.frei(sp, 51, 3, um[0] + dx, um[1] + dy, belegt)
        if p:
            return p
    raise SystemExit("kein freier Platz fuer Spieler %d bei %s" % (sp, um))


def paket_bau(lord2, lord1, belegt, runde=0):
    v2 = [(-20, 25), (20, -25), (-25, -20), (25, 20), (0, 30), (30, 0)]
    v1 = [(10, 20), (-10, 20), (20, -10), (-20, -10), (0, 25), (25, 0)]
    a2 = stelle(2, lord2, belegt, v2[runde:] + v2[:runde])
    b1 = stelle(1, lord1, belegt + [a2], v1[runde:] + v1[:runde])
    kanal.sende({"befehle": [{"player": 2, "id": kanal.neue_id(), "baue": {"mapper": 51, "x": a2[0], "y": a2[1], "groesse": 3}},
                             {"id": kanal.neue_id(), "baue": {"mapper": 51, "x": b1[0], "y": b1[1], "groesse": 3}}]}, 1.5)
    ich_danach = peek_roh(SLOT)
    S2.lauf()
    E, G = S2.lage()
    return a2, b1, S2.an(G, a2), S2.an(G, b1), ich_danach, G


def main():
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    start = [246] * 8
    start[4], start[3] = 0, 1
    kanal.sende({"eigenesGefecht": True, "karte": "Green Haven", "ki": 7, "gegner": 1, "ausgleich": 3, "startliste": start}, 4,
                bis="LaunchSkirmishGame zurueck")
    S2.s({"player": 1, "tempo": 300}, 1.0, "TEMPO")
    S2.s({"player": 1, "pause": False}, 0.5)
    t0 = time.time()
    while time.time() - t0 < 60 and len(S2.lords()) < 2:
        time.sleep(0.5)
    S2.s({"player": 1, "pause": True}, 0.5)
    S2.s({"player": 1, "eigenerPlatz": 1}, 0.8)
    for adr, wert in ((AI + 8, 0), (AITYP2, 0), (FULL + 8, 1)):
        S2.s({"player": 1, "poke": adr, "wert": wert}, 1.0, "POKE")
    E, G = S2.lage()
    lord2 = [(int(x), int(y)) for sp, x, y in S2.lords() if sp == "2"][0]
    lord1 = [(int(x), int(y)) for sp, x, y in S2.lords() if sp == "1"][0]
    belegt = [(int(g[3]), int(g[4])) for g in G]
    # A (19.10. 23:05: ein abgebrochener Lauf liess den Absender nach der Gegenprobe aus - darum hier sicher einschalten)
    absender("an")
    st = absender("status")
    pruefe("A", "Absender: %s" % st, "eingebaut" in st and "nicht eingebaut" not in st)
    # B + C
    a2, b1, own_a, own_b, ich, G = paket_bau(lord2, lord1, belegt)
    pruefe("B", "ein Paket: Spieler-2-Bau an %s -> Besitzer %s; Klick-Bau (ohne Spieler) an %s -> Besitzer %s" % (
        a2, own_a, b1, own_b), own_a == [2] and own_b == [1])
    pruefe("C", "'ich' direkt nach dem Paket: %s" % ich, ich == 1)
    belegt += [a2, b1]
    # D
    E, G = S2.lage()
    # jede Einheit von Spieler 2 ausser dem Lord (55) - fuer die Auswahl-Pruefung zaehlt nur, dass ein Angriffsbefehl laeuft
    e2 = [k for k, e in E.items() if e[1] == "2" and e[2] != "55"]
    S2.s({"player": 1, "poke": LETZTES_WORT, "wert": MUSTER}, 1.0, "POKE")
    if e2:
        n2 = e2[0]
        z2 = list(S2.frei(2, 51, 3, int(E[n2][3]) - 8, int(E[n2][4]) + 8) or (int(E[n2][3]), int(E[n2][4])))
        kanal.sende({"player": 2, "angriff": {"einheiten": [int(n2)], "lauf": z2}}, 1.0, "ANGRIFF")
        nach_einreihen = peek_roh(LETZTES_WORT)
        S2.lauf(2.0)
        nach_ausfuehren = peek_roh(LETZTES_WORT)
        E, G = S2.lage()
        pruefe("D", "Auswahl-Muster 0x%X: nach dem Einreihen 0x%X, nach dem Ausfuehren 0x%X; Einheit %s von Spieler 2 lief %s -> Ziel %s" % (
            MUSTER, nach_einreihen or 0, nach_ausfuehren or 0, n2, E[n2][3:5], z2),
            nach_einreihen == MUSTER and nach_ausfuehren == MUSTER)
    else:
        pruefe("D", "keine Einheit von Spieler 2 zum Pruefen", False)
    S2.s({"player": 1, "poke": LETZTES_WORT, "wert": 0}, 1.0, "POKE")
    # G + H: Laufen und Angreifen (Ausfuehrer, die "ich" lesen: createTribe, giveTribeAnInstruction) - eine Kampfeinheit fuer
    # Spieler 2 setzen (arab. Bogen 70), dann im selben Paket je eine Einheit beider Spieler laufen lassen, danach Angriff
    kanal.sende({"setzeEinheit": {"spieler": 2, "typ": 70, "x": lord2[0] + 4, "y": lord2[1] + 4, "anzahl": 1}}, 1.0, "SETZE")
    E, G = S2.lage()
    b2 = [k for k, e in E.items() if e[1] == "2" and e[2] == "70"]
    e1 = [k for k, e in E.items() if e[1] == "1" and e[2] in ("22", "24", "71", "26")]
    if b2 and e1:
        n2, n1 = b2[0], e1[0]
        z2 = list(S2.frei(2, 51, 3, int(E[n2][3]) - 10, int(E[n2][4]) + 10) or (int(E[n2][3]), int(E[n2][4])))
        z1 = list(S2.frei(1, 51, 3, int(E[n1][3]) + 10, int(E[n1][4]) + 10) or (int(E[n1][3]), int(E[n1][4])))
        kanal.sende({"befehle": [{"player": 2, "id": kanal.neue_id(), "angriff": {"einheiten": [int(n2)], "lauf": z2}},
                                 {"player": 1, "id": kanal.neue_id(), "angriff": {"einheiten": [int(n1)], "lauf": z1}}]}, 1.5)
        S2.lauf(4.0)
        E, G = S2.lage()
        nah = lambda n, z: max(abs(int(E[n][3]) - z[0]), abs(int(E[n][4]) - z[1])) <= 2
        pruefe("G", "Laufen im selben Paket: Spieler-2-Bogen %s jetzt %s (Ziel %s), Spieler-1-Einheit %s jetzt %s (Ziel %s)" % (
            n2, E[n2][3:5], z2, n1, E[n1][3:5], z1), nah(n2, z2) and nah(n1, z1))
        kanal.sende({"player": 2, "angriff": {"einheiten": [int(n2)], "ziel": int(n1)}}, 1.0, "ANGRIFF")
        S2.lauf(2.0)
        E, G = S2.lage()
        pruefe("H", "Angriff: Spieler-2-Bogen %s hat Zieleinheit %s (soll %s)" % (n2, E[n2][8], n1), E[n2][8] == n1)
    else:
        pruefe("G", "keine Einheiten zum Pruefen (Bogen Spieler 2: %d, Spieler 1: %d)" % (len(b2), len(e1)), False)
    # E Gegenprobe
    aus = absender("aus")
    a2g, b1g, own_ag, own_bg, ich_g, G = paket_bau(lord2, lord1, belegt, runde=1)
    an = absender("an")
    pruefe("E", "GEGENPROBE (%s): Klick-Bau an %s -> Besitzer %s (alter Fehler = 2), Spieler-2-Bau %s -> %s; danach: %s" % (
        aus[:40], b1g, own_bg, a2g, own_ag, an[:60]), own_bg == [2] and "eingebaut" in an)
    # F
    pruefe("F", "'ich' am Ende %s" % peek_roh(SLOT), peek_roh(SLOT) == 1)
    print("%d von %d gruen" % (sum(ok), len(ok)), flush=True)
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
