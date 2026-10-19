# -*- coding: utf-8 -*-
"""SamurAI-Wache (Daniel 19.10. 19:30 "wenn ich die KI in der Lobby haette und selbst das Spiel starten kann"; 19:55 "ja nimm
die Ratte ... nenne es auch SamurAI").

Laeuft im Hintergrund neben dem Spiel. Alle PAUSE_S Sekunden: laeuft ein Gefecht (Ansicht 14, gameOver 0)? Sitzt auf einem
Platz die Ratte (currentAIArray[sp] == RATTE)? Dann sofort deren eingebaute KI aus (currentAIArray, PlayerData.aiType,
Mensch-Eintrag - dieselben drei Stellen wie ki_aus im 1v1, gemessen 19.10.) und unseren Lenker fuer diesen Spieler starten
(erstes_spiel.py uebernehmen=ja: Platz live vermessen, nie pausieren, nie Tempo oder Kamera aendern). Verlaesst der Mensch die
Partie (Ansicht nicht mehr 14), wird der Lenker beendet. Je Partie hoechstens ein Lenker - stuerzt er ab, spielt der Platz
nicht weiter (kein Neustart im Kreis).

Die Entscheidung ist eine reine Funktion (entscheide) - Pruefung ohne Spiel: werkzeug/samurai_wache_pruefen.py.
Aufruf: SHC_INSTANZ=4 SHC_PARTNER=ja python werkzeug/samurai_wache.py   (Ende: Datei werkzeug/STOP_SAMURAI anlegen)"""
import os
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
RATTE = 1                    # KI-Nummer der Ratte in currentAIArray (1 Ratte, 2 Schlange, 3 Schwein, 4 Wolf ...)
ANSICHT, GAMEOVER = 0x01FE7D1C, 0x0117D500
AI_ARRAY, AI_TYP, MENSCH = 0x0191DE7C, 0x0115BDF8 + 0x2300, 0x0191DE10
PD_SCHRITT = 0x39F4
SPIELER = range(1, 9)
PAUSE_S = 2.0                # waehrend unser Lenker spielt
SCHNELL_S = 0.25             # vor der Partie: so oft nachsehen, ob ein Gefecht begonnen hat
STOP = os.path.join(HIER, "STOP_SAMURAI")
LENKER_ARGS = ("leere_ki=nein experiment=ja regel50=ja minuten=600 tempo=40 bis_tick=900000 ziel_tick=900000 streitkolben=30 "
               "weg=feldzug produktion=ja bier=ja abriss=nein assassinen=20 aufloesen=ende b_versatz=600 bevoelkerung_ziel=90 "
               "einzelkauf=nein entscheider=kausal gegner=1 gute_dinge=0 haushalt_rand=650 holz_kaufen=ja holz_spam=20 "
               "holzfaeller_je_baum=4 holzfaeller_max=30 holzfaeller_vorab=4 huetten_voraus=nein je_arbeiter=ja "
               "joch_nach_stein=ja kasse=nein kasse_grenze=0 kasse_stufe=11 nahrung_ausbau=nein notwerbung=ja penner=20 "
               "rationen=doppelt schub=nein stein_max=nein stein_parallel=ja steinbruch_zuerst=nein steuer_ende=nein "
               "steuer_runter=90 umzug=frueh v14=nein vollbeschaeftigung=ja wachstum_boden=9500 waechter=ja stopp_tote=0 "
               "uebernehmen=ja").split()


def entscheide(ansicht, gameover, ai, lenker_laeuft, partie_bedient):
    """ai: {sp: KI-Nummer}. Gibt ("starten", sp) | ("beenden", None) | ("warten", None) | ("neue_partie_frei", None)."""
    im_spiel = ansicht == 14 and gameover == 0
    if not im_spiel:
        if lenker_laeuft:
            return ("beenden", None)
        if partie_bedient:
            return ("neue_partie_frei", None)
        return ("warten", None)
    if lenker_laeuft or partie_bedient:
        return ("warten", None)
    ratten = sorted(sp for sp, k in ai.items() if k == RATTE)
    if ratten:
        return ("starten", ratten[0])
    return ("warten", None)


def schreib(text):
    zeile = time.strftime("%H:%M:%S ") + text
    print(zeile, flush=True)
    with open(os.path.join(D, "samurai_wache.log"), "a", encoding="utf-8") as f:
        f.write(zeile + "\n")


def lies(mit_ai=True):
    """20:25 (Daniel: "du muesstest es literally Tick 1 machen, sonst baut sich die KI auf"): vor der Partie nur Ansicht und
    gameOver lesen (2 Abfragen, alle SCHNELL_S) - die 9 KI-Felder erst, wenn ein Gefecht laeuft."""
    from laden import peek
    ai = {sp: peek(AI_ARRAY + sp * 4)[0] for sp in SPIELER} if mit_ai else {}
    return peek(ANSICHT)[0], peek(GAMEOVER)[0], ai


def ki_aus(sp):
    from laden import befehl
    # 20:22 REIHENFOLGE gemessen (uebernahme_probe.py, daten/uebernahme_probe_20261019_2020*.json/_202135.json): zuerst
    # Mensch-Eintrag 1, DANN KI aus - currentAIArray = 0 allein beendet die Partie nach 3 Takten (der Platz hat weder KI
    # noch Menschen -> ausgeschieden; Daniels Partie 20:16 "Samurai gewinnt"). Mensch zuerst: gameOver 0, die Ratte baut
    # in 3.000 Takten nichts mehr (15 -> 15; ohne Eingriff 15 -> 24)
    for adr, wert in ((MENSCH + sp * 4, 1), (AI_TYP + sp * PD_SCHRITT, 0), (AI_ARRAY + sp * 4, 0)):
        befehl({"poke": adr, "wert": wert}, 1.0, bis="POKE")


def main():
    if os.environ.get("SHC_PARTNER") != "ja":
        raise SystemExit("samurai_wache braucht SHC_PARTNER=ja (Wache und Lenker teilen sich den Befehlskanal)")
    if os.path.exists(STOP):
        os.remove(STOP)
    schreib("SamurAI-Wache an (Instanz %s) - wartet auf eine Partie mit der Ratte" % os.environ.get("SHC_INSTANZ", "1"))
    lenker, bedient, log = None, False, None
    while not os.path.exists(STOP):
        try:
            ansicht, gameover, ai = lies(mit_ai=False)
            if ansicht == 14 and gameover == 0 and not bedient:
                ai = lies()[2]
        except Exception as ex:
            schreib("Lesen fehlgeschlagen: %r" % (ex,))
            time.sleep(5)
            continue
        laeuft = lenker is not None and lenker.poll() is None
        if lenker is not None and not laeuft and bedient and log:
            schreib("Lenker beendet (Rueckgabe %s) - Mitschrift %s" % (lenker.returncode, log))
            lenker = None
        tat, sp = entscheide(ansicht, gameover, ai, laeuft, bedient)
        # einmal je Partie die KI-Nummern aller Plaetze mitschreiben (Gegenprobe der Annahme "Ratte = 1")
        gesehen = (ansicht == 14 and gameover == 0)
        if gesehen and not getattr(main, "gemeldet", False):
            schreib("Partie erkannt - KI-Nummern je Spieler: %s" % {s: k for s, k in ai.items() if k})
            main.gemeldet = True
        elif not gesehen:
            main.gemeldet = False
        if tat == "starten":
            from laden import befehl
            from steuerkarte import tick
            t_vor = tick()
            befehl({"pause": True}, 0.5)          # kurz anhalten: umschalten, bevor die KI baut (Daniel 20:21)
            ki_aus(sp)
            befehl({"pause": False}, 0.5)
            schreib("Umschaltung bei Tick %s (Spiel waehrenddessen angehalten)" % t_vor)
            log = os.path.join(D, "samurai_%s_sp%d_konsole.txt" % (time.strftime("%Y%m%d_%H%M%S"), sp))
            umgebung = dict(os.environ, SHC_SPIELER=str(sp), SHC_PARTNER="ja")
            lenker = subprocess.Popen([sys.executable, "-u", os.path.join(HIER, "erstes_spiel.py")] + LENKER_ARGS,
                                      cwd=HIER, env=umgebung, stdout=open(log, "w", encoding="utf-8"), stderr=subprocess.STDOUT)
            bedient = True
            schreib("Ratte auf Spieler %d gefunden - KI aus, SamurAI uebernimmt (Prozess %d, Mitschrift %s)" % (sp, lenker.pid, log))
        elif tat == "beenden":
            lenker.terminate()
            schreib("Partie verlassen (Ansicht %s) - Lenker beendet" % ansicht)
            lenker = None
        elif tat == "neue_partie_frei":
            bedient = False
        time.sleep(PAUSE_S if bedient else SCHNELL_S)
    if lenker is not None and lenker.poll() is None:
        lenker.terminate()
    schreib("SamurAI-Wache aus (STOP_SAMURAI)")


if __name__ == "__main__":
    main()
