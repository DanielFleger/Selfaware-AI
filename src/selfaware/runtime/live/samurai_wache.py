# -*- coding: utf-8 -*-
"""SamurAI-Wache (Daniel 19.10. 19:30 "wenn ich die KI in der Lobby haette und selbst das Spiel starten kann"; 19:55 "ja nimm
die Ratte ... nenne es auch SamurAI").

Laeuft im Hintergrund neben dem Spiel. Alle PAUSE_S Sekunden: laeuft ein Gefecht (Ansicht 14, gameOver 0)? Sitzt auf einem
Platz die Ratte (currentAIArray[sp] == RATTE)? Dann sofort deren eingebaute KI aus (currentAIArray, PlayerData.aiType,
Mensch-Eintrag - dieselben drei Stellen wie ki_aus im 1v1, gemessen 19.10.) und unseren Lenker fuer diesen Spieler starten
(erstes_spiel.py uebernehmen=ja: Platz live vermessen, nie pausieren, nie Tempo oder Kamera aendern). Verlaesst der Mensch die
Partie (Ansicht nicht mehr 14), wird der Lenker beendet. Je Partie hoechstens ein Lenker - stuerzt er ab, spielt der Platz
nicht weiter (kein Neustart im Kreis).

Die Entscheidung ist eine reine Funktion (entscheide) - Pruefung ohne Spiel: src/selfaware/tools/checks/samurai_wache_pruefen.py.
Aufruf: SHC_INSTANZ=4 SHC_PARTNER=ja uv run python -m selfaware.runtime.live.samurai_wache   (Ende: Datei var/legacy/STOP_SAMURAI anlegen)"""

from selfaware import workspace as _workspace
import os
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(_workspace.DATA)
RATTE = 1                    # KI-Nummer der Ratte in currentAIArray (1 Ratte, 2 Schlange, 3 Schwein, 4 Wolf ...)
ANSICHT, GAMEOVER = 0x01FE7D1C, 0x0117D500
AI_ARRAY, AI_TYP, MENSCH = 0x0191DE7C, 0x0115BDF8 + 0x2300, 0x0191DE10
PD_SCHRITT = 0x39F4
SPIELER = range(1, 9)
PAUSE_S = 0.5                # waehrend unser Lenker spielt (20:46: 0,5 s - Taskleiste schnell wieder verdecken)
NEUSTARTS_MAX = 5            # so oft startet die Wache SamurAI je Partie neu, wenn er aussteigt (20:42)
SCHNELL_S = 0.25             # vor der Partie: so oft nachsehen, ob ein Gefecht begonnen hat
STOP = os.path.join(_workspace.STATE, 'STOP_SAMURAI')
# 20:31: regel50=nein - gegen einen Menschen hoert SamurAI bei Beliebtheit unter 50 NICHT auf (Testlauf 20:28: Regelbruch bei
# Tick 4.607, die Beliebtheit 48,25 hatte noch die Ratte vor der Uebernahme verursacht; Daniel: "hoert die KI auf nach ein paar Ticks")
LENKER_ARGS = ("leere_ki=nein experiment=ja regel50=nein minuten=600 tempo=40 bis_tick=900000 ziel_tick=900000 streitkolben=30 "
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


def spiel_ueber_taskleiste():
    """20:46 (Daniel: "immer noch die Leiste"): ist das Spielfenster DIESER Instanz das aktive Fenster, wird es wieder ueber die
    Taskleiste gelegt (HWND_TOPMOST, ohne Fokus/Groesse/Ort zu aendern). Gemessen 20:43: wirkt, solange das Spiel nicht
    erhoeht laeuft; die Taskleiste schob sich aber wieder davor - darum in jeder Runde. Andere Programme bleiben unberuehrt."""
    import ctypes
    from ctypes import wintypes
    u, k = ctypes.windll.user32, ctypes.windll.kernel32
    # 20:50: Typen setzen - ohne sie gingen HWND_TOPMOST (-1) und das Fenster-Handle als 32-Bit-Zahl durch (64-Bit-Python),
    # SetWindowPos wirkte nicht (Vordergrund-Protokoll 20:48: Spiel 35 s vorn, Taskleiste trotzdem davor)
    u.GetForegroundWindow.restype = wintypes.HWND
    u.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    u.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    k.OpenProcess.restype = wintypes.HANDLE
    k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    h = u.GetForegroundWindow()
    if not h:
        return
    pid = wintypes.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(pid))
    hp = k.OpenProcess(0x1000, False, pid.value)
    if not hp:
        return
    try:
        buf = ctypes.create_unicode_buffer(1024)
        n = wintypes.DWORD(1024)
        if not k.QueryFullProcessImageNameW(hp, 0, buf, ctypes.byref(n)):
            return
        pfad = buf.value.lower()
    finally:
        k.CloseHandle(hp)
    inst = os.environ.get("SHC_INSTANZ", "1")
    if "stronghold crusader.exe" in pfad and (("instanz%s" % inst) in pfad if inst != "1" else "instanz" not in pfad):
        u.SetWindowPos(h, wintypes.HWND(-1), 0, 0, 0, 0, 0x13)      # HWND_TOPMOST, NOMOVE|NOSIZE|NOACTIVATE


def schreib(text):
    zeile = time.strftime("%H:%M:%S ") + text
    print(zeile, flush=True)
    with open(os.path.join(D, "samurai_wache.log"), "a", encoding="utf-8") as f:
        f.write(zeile + "\n")


def lies(mit_ai=True):
    """20:25 (Daniel: "du muesstest es literally Tick 1 machen, sonst baut sich die KI auf"): vor der Partie nur Ansicht und
    gameOver lesen (2 Abfragen, alle SCHNELL_S) - die 9 KI-Felder erst, wenn ein Gefecht laeuft."""
    from selfaware.game.ucp.laden import peek
    ai = {sp: peek(AI_ARRAY + sp * 4)[0] for sp in SPIELER} if mit_ai else {}
    return peek(ANSICHT)[0], peek(GAMEOVER)[0], ai


def ki_aus(sp):
    from selfaware.game.ucp.laden import befehl
    # 20:22 REIHENFOLGE gemessen (uebernahme_probe.py, data/research/uebernahme_probe_20261019_2020*.json/_202135.json): zuerst
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
    # 20:56 AUS (Daniel: "ich brauche keinen Fix, ich will, dass du den Ursprung loest - es liegt an einem Skript, das du
    # gemacht hast, bitte ausschalten"): spiel_ueber_taskleiste() wird nicht mehr aufgerufen - das Spiel wird nicht mehr
    # ueber die Taskleiste gelegt. Die Funktion bleibt nur zum Nachlesen stehen.
    lenker, bedient, log, scharf = None, False, None, False
    sp_aktiv, neustarts = None, 0
    from selfaware.game.ucp.laden import befehl as befehl_w
    while not os.path.exists(STOP):
        try:
            ansicht, gameover, ai = lies(mit_ai=False)
            # 20:39 (Daniel: "das sollte Tick 0 oder 1 passieren, nicht 38"): im Menue die Tick-Pause des Moduls scharf
            # stellen - das Spiel haelt beim ersten Takt selbst an (logik.lua tickpause), umgeschaltet wird in der Pause
            if ansicht != 14 and not scharf:
                befehl_w({"tickpause": {"bei": 1}}, 0.5)
                scharf = True
                schreib("Tick-Pause bei Tick 1 scharf (Ansicht %s)" % ansicht)
            if ansicht == 14 and scharf and not bedient:
                scharf = False            # die Pause hat gegriffen oder die Partie lief schon - beim naechsten Menue neu
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
            # 20:42 (Daniel: "bitte schaue, dass es wirklich dauerhaft durchlaeuft fuer das ganze Spiel"): laeuft die Partie
            # weiter, SamurAI sofort neu starten (hoechstens NEUSTARTS_MAX je Partie) - er vermisst nichts doppelt (Plan liegt)
            if ansicht == 14 and gameover == 0 and sp_aktiv and neustarts < NEUSTARTS_MAX:
                neustarts += 1
                log = os.path.join(D, "samurai_%s_sp%d_konsole.txt" % (time.strftime("%Y%m%d_%H%M%S"), sp_aktiv))
                umgebung = dict(os.environ, SHC_SPIELER=str(sp_aktiv), SHC_PARTNER="ja")
                lenker = subprocess.Popen(_workspace.module_command("erstes_spiel") + LENKER_ARGS,
                                          cwd=_workspace.ROOT, env=umgebung, stdout=open(log, "w", encoding="utf-8"), stderr=subprocess.STDOUT)
                laeuft = True
                schreib("NEUSTART %d von %d: SamurAI fuer Spieler %d wieder gestartet (Prozess %d, Mitschrift %s)" % (
                    neustarts, NEUSTARTS_MAX, sp_aktiv, lenker.pid, log))
        tat, sp = entscheide(ansicht, gameover, ai, laeuft, bedient)
        # einmal je Partie die KI-Nummern aller Plaetze mitschreiben (Gegenprobe der Annahme "Ratte = 1")
        gesehen = (ansicht == 14 and gameover == 0)
        if gesehen and not getattr(main, "gemeldet", False):
            schreib("Partie erkannt - KI-Nummern je Spieler: %s" % {s: k for s, k in ai.items() if k})
            main.gemeldet = True
        elif not gesehen:
            main.gemeldet = False
        if tat == "starten":
            from selfaware.game.ucp.laden import befehl
            from selfaware.game.ucp.steuerkarte import tick
            t_vor = tick()
            befehl({"pause": True}, 0.5)          # kurz anhalten (steht meist schon durch die Tick-Pause)
            ki_aus(sp)
            befehl({"pause": False}, 0.5)
            schreib("Umschaltung bei Tick %s (Spiel waehrenddessen angehalten)" % t_vor)
            log = os.path.join(D, "samurai_%s_sp%d_konsole.txt" % (time.strftime("%Y%m%d_%H%M%S"), sp))
            umgebung = dict(os.environ, SHC_SPIELER=str(sp), SHC_PARTNER="ja")
            lenker = subprocess.Popen(_workspace.module_command("erstes_spiel") + LENKER_ARGS,
                                      cwd=_workspace.ROOT, env=umgebung, stdout=open(log, "w", encoding="utf-8"), stderr=subprocess.STDOUT)
            bedient, sp_aktiv, neustarts = True, sp, 0
            schreib("Ratte auf Spieler %d gefunden - KI aus, SamurAI uebernimmt (Prozess %d, Mitschrift %s)" % (sp, lenker.pid, log))
        elif tat == "beenden":
            lenker.terminate()
            schreib("Partie verlassen (Ansicht %s) - Lenker beendet" % ansicht)
            lenker = None
        elif tat == "neue_partie_frei":
            bedient, sp_aktiv = False, None
        elif tat == "warten" and ansicht == 14 and gameover == 0 and not bedient and not laeuft and ai and RATTE not in ai.values():
            # Partie ohne Ratte: die Tick-Pause wieder aufheben (sonst stuende Daniels Spiel bei Tick 1)
            from selfaware.game.ucp.steuerkarte import tick as tick_w
            if (tick_w() or 0) <= 2:
                befehl_w({"pause": False}, 0.5)
            bedient = True
        time.sleep(PAUSE_S if bedient else SCHNELL_S)
    # 20:44: beim Aufhoeren der Wache spielt SamurAI weiter (vorher beendete ein Neustart der Wache die laufende KI mit)
    schreib("SamurAI-Wache aus (STOP_SAMURAI) - SamurAI spielt weiter" if lenker is not None and lenker.poll() is None
            else "SamurAI-Wache aus (STOP_SAMURAI)")


if __name__ == "__main__":
    main()
