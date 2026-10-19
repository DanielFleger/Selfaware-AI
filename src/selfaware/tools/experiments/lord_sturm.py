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

Aufruf: SHC_INSTANZ=4 uv run python -m selfaware.tools.experiments.lord_sturm [mit_lord=ja] [tempo=40] [bis=9000] [rueckzug=rechnung|0.5] [neu=5]"""
import os
import sys
import time

import selfaware.game.ucp.befehl as kanal

# Rueckzug nach Rechnung (Daniel 11.10. 16:11 "ja bau den Rueckzug nach Rechnung"). Gemessen in den Laeufen 1011a/b:
# der Rueckweg kostete unseren Lord 4.950 bzw. 4.223 Leben -> BODEN = gut das Vierfache.
BODEN = 20000          # unter diese Lebenspunkte darf unser Lord im Kampf nicht fallen
FENSTER = 200          # Ticks, ueber die die Schadensraten gemessen werden
SICHERHEIT = 1.5       # die Zeit bis zum Tod seines Lords zaehlt 1,5-fach (Raten schwanken in Stoessen)
HORIZONT = 200         # erst wenn unser Lord in so vielen Ticks am Boden waere, wird ueber den Rueckzug entschieden.
                       # Gegenprobe 16:15: ohne diese Schwelle haette die Rechnung bei Kampfbeginn (Tick 1.524, 147.000 Leben,
                       # kaum gemessener Schaden am Gegner) sofort den Rueckzug befohlen und beide gewonnenen Laeufe verloren.


def rueckzug_rechnung(verlauf, lord_max, boden=BODEN, fenster=FENSTER, sicherheit=SICHERHEIT, horizont=HORIZONT):
    """verlauf: [(tick, leben_gegnerlord, leben_unser_lord), ...] der letzten Runden, aelteste zuerst.
    Gibt (zurueck, grund). Weiterkaempfen nur, wenn sein Lord bei der gemessenen Rate (mit Sicherheitsfaktor) stirbt,
    bevor unserer auf den Boden faellt. Ohne Messwert (zu kurze Reihe oder kein Schaden am Gegner) gilt die alte
    50-%-Regel - sie ist in zwei Laeufen gutgegangen."""
    t, hp_g, hp_w = verlauf[-1]
    if hp_w <= boden:
        return True, "unser Lord %d <= Boden %d" % (hp_w, boden)
    alt = [v for v in verlauf if v[0] >= t - fenster]
    dt = alt[-1][0] - alt[0][0]
    if dt < fenster // 2:
        return hp_w < 0.5 * lord_max, "zu kurze Messreihe (%d Ticks) - 50-%%-Regel" % dt
    r_g = (alt[0][1] - hp_g) / float(dt)
    r_w = (alt[0][2] - hp_w) / float(dt)
    if r_w <= 0:
        return False, "unser Lord verliert nichts"
    t_sicher = (hp_w - boden) / r_w
    if t_sicher > horizont:
        return False, "unser Lord erst in ~%d Ticks am Boden - weiter" % t_sicher
    if r_g <= 0:
        return hp_w < 0.5 * lord_max, "sein Lord verliert nichts - 50-%%-Regel (bis Boden %d Ticks)" % t_sicher
    t_tot = hp_g / r_g
    return t_tot * sicherheit > t_sicher, "sein Lord tot in ~%d Ticks (x%.1f), unserer am Boden in ~%d Ticks" % (
        t_tot, sicherheit, t_sicher)


def laufe(E, einheiten, x, y):
    """Echter Laufbefehl wie ein Mausklick (Modul: angriff mit lauf = Spielbefehl 17 ClickMoveUnit). SAI 11.10.: "halten"
    setzt nur das Laufziel - im Nahkampf blieb unser Lord in Lauf 1011a 35 Ticks lang stehen und schlug weiter."""
    E.befehl({"angriff": {"einheiten": list(einheiten), "lauf": [int(x), int(y)]}}, 1.0, bis="ANGRIFF")


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    import selfaware.runtime.live.erstes_spiel as E
    from selfaware.telemetry.lageprotokoll import Lageprotokoll
    from selfaware.micro.tasks.waechter import TRUPPE, LORD
    mit_lord, tempo = arg.get("mit_lord", "ja") == "ja", int(arg.get("tempo", 40))
    bis, neu = int(arg.get("bis", 9000)), int(arg.get("neu", 5))
    rueckzug = arg.get("rueckzug", "rechnung")       # "rechnung" oder fester Anteil wie 0.5
    # Regel Daniel 11.10. 16:11: unser Lord darf den gegnerischen Lord nicht toeten ("mit lord angreifen ist sehr cheezy"),
    # sonst darf er alles. "schild" (Standard): Lord greift nur Wachen an, nie den Lord. "lord" nur fuer Altvergleiche.
    lord_rolle = arg.get("lord_rolle", "schild")
    verstoesse, letzter_lordschlag, hatte_truppe = 0, -10 ** 9, False
    flucht_bis, bogen_runter = -1, False
    kampf = TRUPPE - {LORD}
    E.LIGA_GEFECHT = dict(E.LIGA_GEFECHT, ki=int(arg.get("ki", 7)))
    E.GEGNER_ERWARTET, E.LEERE_KI = arg.get("erwartet", "Nomade"), False
    stempel = time.strftime("%Y%m%d_%H%M%S")
    protokoll = Lageprotokoll(os.path.join(E.D, "lage_%s_i%d_sturm.jsonl.gz" % (stempel, kanal.INSTANZ)))
    verstaerkung = arg.get("verstaerkung", "keine")
    if verstaerkung == "assassinen":
        # Daniel 16:26 "ja bau die Assassinen-Verstaerkung": die erprobte Eroeffnung des Lenkers (phase1 mit Posten) startet
        # das Gefecht samt Gegnerpruefung, baut Markt und Soeldnerposten, verkauft Start-Nahrung bis zum Puffer und wirbt
        # Assassinen an, solange Gold (70) und Bauern am Feuer reichen. Danach greifen alle gemeinsam an.
        import json
        import selfaware.micro.tasks.waechter as waechter
        plan = json.load(open(os.path.join(E.D, arg.get("plan", "eroeffnung_plan_M19.json")), encoding="utf-8"))
        plan["_datei"] = arg.get("plan", "eroeffnung_plan_M19.json")
        E.BERGFRIED = tuple(plan.get("bergfried_eingang", E.BERGFRIED))
        waechter.BERGFRIED_EINGANG = E.BERGFRIED
        E.phase1(plan, tempo, mit_posten=True)
    else:
        for versuch in range(1, 6):
            try:
                E.gefecht_starten(tempo)
                break
            except SystemExit as e:
                if versuch == 5 or not any(s in str(e) for s in ("beide Lords", "STARTPLATZ FALSCH")):
                    raise
                E.schreib("NEUSTART Gefecht (Versuch %d): %s" % (versuch, e))
    E.schreib("STURM: mit_lord=%s (Rolle %s), Verstaerkung %s, Tempo %d, Rueckzug %s, Befehl alle %d Runden" % (
        mit_lord, lord_rolle, verstaerkung, tempo, rueckzug, neu))
    runde, lord_max, zurueck, naechste_zeile, start_t, verlauf = 0, None, False, 0, None, []
    while True:
        kanal.belege()          # Sperre je Runde auffrischen (gilt 15 s; zuruecksetzen() gibt sie zwischendurch frei)
        st, L, G = E.runde_lesen()
        protokoll.schreibe(st)
        t = st.get("t", 0)
        start_t = t if start_t is None else start_t
        feind = next((n for n, e in L.items() if e["typ"] == LORD and e["besitzer"] not in (0, E.SP)), None)
        mein_lord = next((n for n, e in L.items() if e["typ"] == LORD and e["besitzer"] == E.SP), None)
        if feind is None or L[feind]["leben"] <= 0:
            if lord_rolle == "schild" and t - letzter_lordschlag <= 50:
                E.schreib("STURM SIEG UNGUELTIG bei Tick %d: unser Lord schlug den gegnerischen Lord noch bei Tick %d (Lord-Regel)" % (
                    t, letzter_lordschlag))
                return 4
            E.schreib("STURM SIEG bei Tick %d: gegnerischer Lord tot (Verstoesse gegen die Lord-Regel: %d)" % (t, verstoesse))
            return 0
        if mein_lord is None:
            E.schreib("STURM NIEDERLAGE bei Tick %d: unser Lord tot" % t)
            return 1
        lord_max = lord_max or L[mein_lord]["leben"]
        beliebt = st.get("beliebt")
        if beliebt is not None and beliebt < 5000:       # Daniel: nie unter 50 Beliebtheit
            E.schreib("STURM REGELBRUCH bei Tick %d: Beliebtheit %.2f unter 50" % (t, beliebt / 100.0))
            return 5
        alle_truppen = [n for n, e in L.items() if e["besitzer"] == E.SP and e["typ"] in kampf]
        truppe = list(alle_truppen)          # wer gerade auf seinen Lord geht (Bogen erst nach dem Abstieg)
        hatte_truppe = hatte_truppe or bool(alle_truppen)     # Starttruppen erscheinen erst nach Tick ~110 (Lauf 1011d brach bei 109 ab)
        verlauf.append((t, L[feind]["leben"], L[mein_lord]["leben"]))
        if rueckzug == "rechnung":
            noetig, grund = rueckzug_rechnung(verlauf, lord_max)
        else:
            noetig, grund = L[mein_lord]["leben"] < float(rueckzug) * lord_max, "unter %s des Anfangslebens" % rueckzug
        if mit_lord and not zurueck and noetig:
            zurueck = True
            laufe(E, [mein_lord], E.BERGFRIED[0], E.BERGFRIED[1])
            E.schreib("STURM Tick %d: Rueckzug unseres Lords (%d Leben, Gegner-Lord %d): %s" % (
                t, L[mein_lord]["leben"], L[feind]["leben"], grund))
        elif mit_lord and not zurueck and rueckzug == "rechnung" and L[mein_lord]["leben"] < 0.5 * lord_max and t >= naechste_zeile:
            E.schreib("STURM Tick %d: unser Lord unter 50 %% (%d), kaempft weiter: %s" % (t, L[mein_lord]["leben"], grund))
        lx, ly = L[feind]["x"], L[feind]["y"]
        # Bogenschuetzen standen in allen Laeufen am Bergfried (141/269) und liefen trotz Angriffsbefehl nicht los
        # (1011e: Zielart 4, Zieleinheit = sein Lord, Laufziel 141/266). Erst mit Laufbefehl herunter, dann angreifen.
        bogen = [n for n in truppe if L[n]["typ"] in (22, 23, 70)]
        if bogen and not bogen_runter:
            laufe(E, bogen, E.BERGFRIED[0] + 8, E.BERGFRIED[1])
            bogen_runter = t
            E.schreib("STURM Tick %d: %d Bogenschuetzen per Laufbefehl vom Bergfried nach (%d,%d)" % (
                t, len(bogen), E.BERGFRIED[0] + 8, E.BERGFRIED[1]))
        if bogen_runter and t - bogen_runter < 150:
            truppe = [n for n in truppe if n not in bogen]      # erst unten ankommen lassen
        elif bogen_runter:
            # 1011g: unten angekommen blieben sie bei 148/270 stehen - der Angriffsbefehl bringt Fernkaempfer nicht in
            # Schussweite. Wer weiter als 15 Felder weg ist, laeuft auf 12 Felder vor seinen Lord (Linie zu unserem Bergfried).
            fern = [n for n in bogen if max(abs(L[n]["x"] - lx), abs(L[n]["y"] - ly)) > 15]
            if fern:
                bdx, bdy = E.BERGFRIED[0] - lx, E.BERGFRIED[1] - ly
                bd = max(abs(bdx), abs(bdy)) or 1
                if runde % neu == 0:
                    laufe(E, fern, lx + round(12 * bdx / bd), ly + round(12 * bdy / bd))
                truppe = [n for n in truppe if n not in fern]
        lord_kaempft = mit_lord and not zurueck
        angreifer = truppe + ([mein_lord] if lord_kaempft and lord_rolle == "lord" else [])
        if angreifer and runde % neu == 0:
            E.befehl({"angriff": {"einheiten": angreifer, "ziel": feind}}, 1.0, bis="ANGRIFF")
        if lord_kaempft and lord_rolle == "schild":
            # Abstandspunkt 8 Felder vor seinem Lord, auf der Linie zu unserem Bergfried - dort steht unser Lord, wenn keine
            # Wache zu schlagen ist (direkt daneben wuerde er den Lord von selbst angreifen)
            dx, dy = E.BERGFRIED[0] - lx, E.BERGFRIED[1] - ly
            d = max(abs(dx), abs(dy)) or 1
            px, py = lx + round(12 * dx / d), ly + round(12 * dy / d)
            wl = L[mein_lord]
            abstand_lords = max(abs(wl["x"] - lx), abs(wl["y"] - ly))
            if wl.get("nahziel") == feind:
                verstoesse, letzter_lordschlag = verstoesse + 1, t
                E.schreib("STURM VERSTOSS Tick %d: unser Lord schlug den gegnerischen Lord" % t)
            # 1011e: an einer Wache direkt neben seinem Lord griff der gegnerische Lord an, danach hing unser Lord im
            # Nahkampf fest. Darum: kommen sich die Lords auf 5 Felder nahe (oder schlagen sich), sofort nach Hause laufen.
            if (abstand_lords <= 5 or wl.get("nahziel") == feind or L[feind].get("nahziel") == mein_lord) and t >= flucht_bis:
                laufe(E, [mein_lord], E.BERGFRIED[0], E.BERGFRIED[1])
                flucht_bis = t + 300
                E.schreib("STURM Tick %d: Lords %d Felder auseinander - unser Lord laeuft fuer 300 Ticks nach Hause" % (t, abstand_lords))
            elif t >= flucht_bis and runde % neu == 0:
                wachen = sorted((max(abs(e["x"] - wl["x"]), abs(e["y"] - wl["y"])), n)
                                for n, e in L.items() if e["besitzer"] not in (0, E.SP) and e["typ"] in kampf
                                and 6 <= max(abs(e["x"] - lx), abs(e["y"] - ly)) <= 25)
                if wachen:
                    E.befehl({"angriff": {"einheiten": [mein_lord], "ziel": wachen[0][1]}}, 1.0, bis="ANGRIFF")
                else:
                    laufe(E, [mein_lord], px, py)
        if t >= naechste_zeile:
            nah = sorted(max(abs(L[n]["x"] - lx), abs(L[n]["y"] - ly)) for n in angreifer) if angreifer else [-1]
            wache = sum(1 for e in L.values() if e["besitzer"] not in (0, E.SP) and e["typ"] in kampf
                        and max(abs(e["x"] - lx), abs(e["y"] - ly)) <= 15)
            ass = sum(1 for n in alle_truppen if L[n]["typ"] == 73)
            E.schreib("STURM Tick %5d | Gegner-Lord %6d Leben, Wache<=15: %2d | wir: %2d Truppen (%d Assassinen), Lord %6d%s | naechster %d Felder vom Lord | Beliebtheit %s" % (
                t, L[feind]["leben"], wache, len(truppe), ass, L[mein_lord]["leben"], " (zurueck)" if zurueck else "", nah[0],
                "%.1f" % (beliebt / 100.0) if beliebt is not None else "?"))
            naechste_zeile = t + 100
        # 1011f: die Bogenschuetzen waren fuer den Abstieg aus "truppe" genommen - Abbruch nur, wenn wirklich keiner mehr lebt
        if hatte_truppe and not alle_truppen and (zurueck or not mit_lord or lord_rolle == "schild"):
            if mit_lord and not zurueck:
                laufe(E, [mein_lord], E.BERGFRIED[0], E.BERGFRIED[1])
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
            import selfaware.runtime.live.erstes_spiel as E
            E.befehl({"pause": True}, 0.5)
        except Exception:
            pass
        kanal.freigeben()
    raise SystemExit(rc)
