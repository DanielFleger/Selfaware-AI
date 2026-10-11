# -*- coding: utf-8 -*-
"""Versuch Fruehsturm auf den gegnerischen Lord (SAI 11.10., Daniel: "so frueh wie moeglich raiden, ohne Ruecksicht auf
Verluste"; gewinnen = der gegnerische Lord stirbt).

Messgrundlage (nomade_nachschau.py, Laeufe 1011j/k): Um Tick 2.000 stehen 1-6 Nomade-Truppen bis 15 Felder um seinen
Lord, 14-18 bis 45 Felder; sein Lord hat 30.000 Leben, unserer 150.000. Wir haben ab Start 5 Bogen + 7 Speer.

Ablauf: Gefecht wie im Lenker starten (gefecht_starten: Saat, Startplatz, Gegnerpruefung), dann sofort alle eigenen
Kampftruppen - mit mit_lord=ja auch unseren Lord - auf den gegnerischen Lord. Der Befehl wird alle <neu> Runden
wiederholt (Nachzuegler, abgelenkte Einheiten). Unser Lord zieht sich unter <rueckzug> seines Anfangslebens zum
Bergfried zurueck (verlieren wir ihn, ist die Partie verloren). Keine Wirtschaft - reiner Messversuch.
Jede Runde ins Lageprotokoll; alle ~100 Ticks eine Messzeile.

Vorher festgelegt (Totschlagtest): WIDERLEGT, wenn das Leben seines Lords bis zum Ende unserer Truppen nicht unter
75 % (22.500) faellt. BESTAETIGT, wenn sein Lord stirbt. Dazwischen: Schadensrate je 100 Ticks ist der Messwert.

Aufruf: SHC_INSTANZ=4 python lord_sturm.py [mit_lord=ja] [tempo=40] [bis=9000] [rueckzug=0.5] [neu=5]"""
import os
import sys
import time

import befehl as kanal


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    import erstes_spiel as E
    from lageprotokoll import Lageprotokoll
    from waechter import TRUPPE, LORD
    mit_lord, tempo = arg.get("mit_lord", "ja") == "ja", int(arg.get("tempo", 40))
    bis, rueckzug, neu = int(arg.get("bis", 9000)), float(arg.get("rueckzug", 0.5)), int(arg.get("neu", 5))
    kampf = TRUPPE - {LORD}
    E.LIGA_GEFECHT = dict(E.LIGA_GEFECHT, ki=int(arg.get("ki", 7)))
    E.GEGNER_ERWARTET, E.LEERE_KI = arg.get("erwartet", "Nomade"), False
    stempel = time.strftime("%Y%m%d_%H%M%S")
    protokoll = Lageprotokoll(os.path.join(E.D, "lage_%s_i%d_sturm.jsonl.gz" % (stempel, kanal.INSTANZ)))
    for versuch in range(1, 6):
        try:
            E.gefecht_starten(tempo)
            break
        except SystemExit as e:
            if versuch == 5 or not any(s in str(e) for s in ("beide Lords", "STARTPLATZ FALSCH")):
                raise
            E.schreib("NEUSTART Gefecht (Versuch %d): %s" % (versuch, e))
    E.schreib("STURM: mit_lord=%s, Tempo %d, Rueckzug unter %d %%, Befehl alle %d Runden" % (mit_lord, tempo, rueckzug * 100, neu))
    runde, lord_max, zurueck, naechste_zeile, start_t = 0, None, False, 0, None
    while True:
        kanal.belege()          # Sperre je Runde auffrischen (gilt 15 s; zuruecksetzen() gibt sie zwischendurch frei)
        st, L, G = E.runde_lesen()
        protokoll.schreibe(st)
        t = st.get("t", 0)
        start_t = t if start_t is None else start_t
        feind = next((n for n, e in L.items() if e["typ"] == LORD and e["besitzer"] not in (0, E.SP)), None)
        mein_lord = next((n for n, e in L.items() if e["typ"] == LORD and e["besitzer"] == E.SP), None)
        if feind is None or L[feind]["leben"] <= 0:
            E.schreib("STURM SIEG bei Tick %d: gegnerischer Lord tot" % t)
            return 0
        if mein_lord is None:
            E.schreib("STURM NIEDERLAGE bei Tick %d: unser Lord tot" % t)
            return 1
        lord_max = lord_max or L[mein_lord]["leben"]
        truppe = [n for n, e in L.items() if e["besitzer"] == E.SP and e["typ"] in kampf]
        if mit_lord and not zurueck and L[mein_lord]["leben"] < rueckzug * lord_max:
            zurueck = True
            E.befehl({"halten": {"nr": [mein_lord], "x": E.BERGFRIED[0], "y": E.BERGFRIED[1]}}, 1.0, bis="HALTEN")
            E.schreib("STURM Tick %d: unser Lord unter %d %% (%d) - Rueckzug zum Bergfried" % (t, rueckzug * 100, L[mein_lord]["leben"]))
        angreifer = truppe + ([mein_lord] if mit_lord and not zurueck else [])
        if angreifer and runde % neu == 0:
            E.befehl({"angriff": {"einheiten": angreifer, "ziel": feind}}, 1.0, bis="ANGRIFF")
        lx, ly = L[feind]["x"], L[feind]["y"]
        if t >= naechste_zeile:
            nah = sorted(max(abs(L[n]["x"] - lx), abs(L[n]["y"] - ly)) for n in angreifer) if angreifer else [-1]
            wache = sum(1 for e in L.values() if e["besitzer"] not in (0, E.SP) and e["typ"] in kampf
                        and max(abs(e["x"] - lx), abs(e["y"] - ly)) <= 15)
            E.schreib("STURM Tick %5d | Gegner-Lord %6d Leben, Wache<=15: %2d | wir: %2d Truppen, Lord %6d%s | naechster %d Felder vom Lord" % (
                t, L[feind]["leben"], wache, len(truppe), L[mein_lord]["leben"], " (zurueck)" if zurueck else "", nah[0]))
            naechste_zeile = t + 100
        if not truppe and (zurueck or not mit_lord):
            E.schreib("STURM GESCHEITERT bei Tick %d: keine Truppen mehr, Gegner-Lord %d Leben" % (t, L[feind]["leben"]))
            return 2
        if t - start_t > bis:
            E.schreib("STURM ZEIT UM bei Tick %d: Gegner-Lord %d Leben, %d Truppen" % (t, L[feind]["leben"], len(truppe)))
            return 3
        runde += 1


if __name__ == "__main__":
    kanal.belege()
    try:
        rc = main()
    finally:
        try:
            import erstes_spiel as E
            E.befehl({"pause": True}, 0.5)
        except Exception:
            pass
        kanal.freigeben()
    raise SystemExit(rc)
