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
PAUSE_S = 0.5                # waehrend unser Lenker spielt (20:46: 0,5 s - Taskleiste schnell wieder verdecken)
NEUSTARTS_MAX = 5            # so oft startet die Wache SamurAI je Partie neu, wenn er aussteigt (20:42)
SCHNELL_S = 0.25             # vor der Partie: so oft nachsehen, ob ein Gefecht begonnen hat
STOP = os.path.join(HIER, "STOP_SAMURAI")
# 20:31: regel50=nein - gegen einen Menschen hoert SamurAI bei Beliebtheit unter 50 NICHT auf (Testlauf 20:28: Regelbruch bei
# Tick 4.607, die Beliebtheit 48,25 hatte noch die Ratte vor der Uebernahme verursacht; Daniel: "hoert die KI auf nach ein paar Ticks")
LENKER_ARGS = ("leere_ki=nein experiment=ja regel50=nein minuten=600 tempo=40 bis_tick=900000 ziel_tick=offen streitkolben=30 "
               "weg=feldzug produktion=ja bier=ja abriss=nein assassinen=20 aufloesen=ende b_versatz=600 bevoelkerung_ziel=90 "
               "einzelkauf=nein entscheider=kausal gegner=1 gute_dinge=0 haushalt_rand=650 holz_kaufen=ja holz_spam=20 "
               "holzfaeller_je_baum=4 holzfaeller_max=30 holzfaeller_vorab=4 huetten_voraus=nein je_arbeiter=ja "
               "joch_nach_stein=ja kasse=nein kasse_grenze=0 kasse_stufe=11 nahrung_ausbau=nein notwerbung=ja penner=20 "
               "rationen=doppelt schub=nein stein_max=nein stein_parallel=ja steinbruch_zuerst=nein steuer_ende=nein "
               "steuer_runter=90 umzug=frueh v14=nein vollbeschaeftigung=ja wachstum_boden=9500 waechter=ja stopp_tote=0 "
               "uebernehmen=ja").split()


# 19.10. 22:35 (Daniel 22:33 "spielen kann ich nicht, weil das Spiel haengt"; 21:25 "wenn ich Markt oder Soeldnerposten
# benutze, haengt er"): im Spiel gibt es ZWEI Ansichten - 14 MVT_BUILD_MENU (Baumenue) und 16 MVT_BUILDING_AND_STATUS_MENU
# (ein Gebaeude angeklickt, z. B. Markt oder Soeldnerposten); abgelesen OpenSHC-Enum MenuViewType (daten/enum_ansicht.txt),
# der Lenker kannte beide schon (erstes_spiel.py). Die Wache kannte nur 14: oeffnete Daniel ein Gebaeude, hielt sie die
# Partie fuer verlassen, beendete SamurAI und stellte die Tick-Pause scharf - die hielt dann sein Spiel an.
IM_SPIEL = (14, 16)


def im_spiel(ansicht, gameover):
    return ansicht in IM_SPIEL and gameover == 0


def entscheide(ansicht, gameover, ai, lenker_laeuft, partie_bedient):
    """ai: {sp: KI-Nummer}. Gibt ("starten", sp) | ("beenden", None) | ("warten", None) | ("neue_partie_frei", None)."""
    if not im_spiel(ansicht, gameover):
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


# B-127 (20.10.): Kartenname der Partie - GameSynchronyState.shortMapName (OpenSHC, daten/strukturen_global.txt:
# GSS 0x0191D768 + 0x1057B8, char[120]). Ohne ihn liess sich die Partie 19.10. 22:40 nicht nachspielen.
KARTE_KURZ = 0x0191D768 + 0x1057B8


def zeichen(worte):
    """32-Bit-Worte (little endian, wie peek sie liefert) -> Text bis zum ersten Nullbyte."""
    b = b"".join((int(w) & 0xFFFFFFFF).to_bytes(4, "little") for w in worte)
    return b.split(b"\0")[0].decode("latin-1")


def kartenname():
    try:
        from laden import peek
        return zeichen(peek(KARTE_KURZ, 30)) or None
    except Exception as e:
        return "nicht lesbar (%r)" % (e,)


def lernen_starten(log, sp, karte=None):
    """19.10. 22:55 (Daniel 22:48: "in Zukunft kann so eine Partie gerne fuer mehr Trainingsdaten genutzt werden", B-119):
    nach jeder Partie partie_lernen.py im Hintergrund - Mitschrift + das Lageprotokoll dieses Spielers aus dieser Partie."""
    import glob
    if not log or not os.path.exists(log) or not sp:
        schreib("LERNEN: keine Mitschrift (%s) - nichts ausgewertet" % log)
        return
    seit = os.path.getmtime(log) - 3600      # Lageprotokoll dieser Partie: zuletzt geschrieben nach Start der Mitschrift
    lagen = [p for p in glob.glob(os.path.join(D, "lage_*_sp%d.jsonl.gz" % sp)) if os.path.getmtime(p) >= seit]
    if not lagen:
        schreib("LERNEN: kein Lageprotokoll fuer Spieler %s - nichts ausgewertet" % sp)
        return
    lage = max(lagen, key=os.path.getmtime)
    ziel = os.path.join(D, "lernen_%s.txt" % os.path.basename(log).replace("_konsole.txt", ""))
    subprocess.Popen([sys.executable, "-P", os.path.join(HIER, "partie_lernen.py"), log, lage, "gegner=Mensch",
                      "anmerkung=Karte %s" % (karte or "unbekannt")],
                     cwd=HIER, stdout=open(ziel, "w", encoding="utf-8"), stderr=subprocess.STDOUT)
    schreib("LERNEN: Auswertung gestartet (%s + %s -> %s)" % (os.path.basename(log), os.path.basename(lage), os.path.basename(ziel)))


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
    # 20:56 AUS (Daniel: "ich brauche keinen Fix, ich will, dass du den Ursprung loest - es liegt an einem Skript, das du
    # gemacht hast, bitte ausschalten"): spiel_ueber_taskleiste() wird nicht mehr aufgerufen - das Spiel wird nicht mehr
    # ueber die Taskleiste gelegt. Die Funktion bleibt nur zum Nachlesen stehen.
    lenker, bedient, log, scharf = None, False, None, False
    sp_aktiv, neustarts = None, 0
    from laden import befehl as befehl_w
    while not os.path.exists(STOP):
        try:
            ansicht, gameover, ai = lies(mit_ai=False)
            # 20:39 (Daniel: "das sollte Tick 0 oder 1 passieren, nicht 38"): im Menue die Tick-Pause des Moduls scharf
            # stellen - das Spiel haelt beim ersten Takt selbst an (logik.lua tickpause), umgeschaltet wird in der Pause
            # 22:35: nur AUSSERHALB einer Partie (vorher "Ansicht != 14" - auch beim Klick auf ein Gebaeude, Ansicht 16)
            if ansicht not in IM_SPIEL and not scharf:
                befehl_w({"tickpause": {"bei": 1}}, 0.5)
                scharf = True
                schreib("Tick-Pause bei Tick 1 scharf (Ansicht %s)" % ansicht)
            if ansicht in IM_SPIEL and scharf and not bedient:
                scharf = False            # die Pause hat gegriffen oder die Partie lief schon - beim naechsten Menue neu
            if im_spiel(ansicht, gameover) and not bedient:
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
            if im_spiel(ansicht, gameover) and sp_aktiv and neustarts < NEUSTARTS_MAX:
                neustarts += 1
                log = os.path.join(D, "samurai_%s_sp%d_konsole.txt" % (time.strftime("%Y%m%d_%H%M%S"), sp_aktiv))
                umgebung = dict(os.environ, SHC_SPIELER=str(sp_aktiv), SHC_PARTNER="ja")
                lenker = subprocess.Popen([sys.executable, "-u", os.path.join(HIER, "erstes_spiel.py")] + LENKER_ARGS,
                                          cwd=HIER, env=umgebung, stdout=open(log, "w", encoding="utf-8"), stderr=subprocess.STDOUT)
                laeuft = True
                schreib("NEUSTART %d von %d: SamurAI fuer Spieler %d wieder gestartet (Prozess %d, Mitschrift %s)" % (
                    neustarts, NEUSTARTS_MAX, sp_aktiv, lenker.pid, log))
        tat, sp = entscheide(ansicht, gameover, ai, laeuft, bedient)
        # einmal je Partie die KI-Nummern aller Plaetze mitschreiben (Gegenprobe der Annahme "Ratte = 1")
        gesehen = im_spiel(ansicht, gameover)
        if gesehen and not getattr(main, "gemeldet", False):
            main.karte = kartenname()
            schreib("Partie erkannt - Karte %r, KI-Nummern je Spieler: %s" % (main.karte, {s: k for s, k in ai.items() if k}))
            main.gemeldet = True
        elif not gesehen:
            main.gemeldet = False
        if tat == "starten":
            from laden import befehl
            from steuerkarte import tick
            t_vor = tick()
            befehl({"pause": True}, 0.5)          # kurz anhalten (steht meist schon durch die Tick-Pause)
            ki_aus(sp)
            befehl({"pause": False}, 0.5)
            schreib("Umschaltung bei Tick %s (Spiel waehrenddessen angehalten)" % t_vor)
            log = os.path.join(D, "samurai_%s_sp%d_konsole.txt" % (time.strftime("%Y%m%d_%H%M%S"), sp))
            umgebung = dict(os.environ, SHC_SPIELER=str(sp), SHC_PARTNER="ja")
            lenker = subprocess.Popen([sys.executable, "-u", os.path.join(HIER, "erstes_spiel.py")] + LENKER_ARGS,
                                      cwd=HIER, env=umgebung, stdout=open(log, "w", encoding="utf-8"), stderr=subprocess.STDOUT)
            bedient, sp_aktiv, neustarts = True, sp, 0
            schreib("Ratte auf Spieler %d gefunden - KI aus, SamurAI uebernimmt (Prozess %d, Mitschrift %s)" % (sp, lenker.pid, log))
        elif tat == "beenden":
            lenker.terminate()
            schreib("Partie verlassen (Ansicht %s, Partie vorbei %s) - Lenker beendet" % (ansicht, gameover))
            lenker = None
            try:
                lernen_starten(log, sp_aktiv, getattr(main, "karte", None))
            except Exception as ex_l:
                schreib("LERNEN fehlgeschlagen: %r" % (ex_l,))
        elif tat == "neue_partie_frei":
            bedient, sp_aktiv = False, None
        elif tat == "warten" and im_spiel(ansicht, gameover) and not bedient and not laeuft and RATTE not in (ai or {}).values():
            # Partie ohne Ratte: die Tick-Pause wieder aufheben (sonst stuende Daniels Spiel bei Tick 1)
            from steuerkarte import tick as tick_w
            if (tick_w() or 0) <= 2:
                befehl_w({"pause": False}, 0.5)
            bedient = True
        time.sleep(PAUSE_S if bedient else SCHNELL_S)
    # 20:44: beim Aufhoeren der Wache spielt SamurAI weiter (vorher beendete ein Neustart der Wache die laufende KI mit)
    schreib("SamurAI-Wache aus (STOP_SAMURAI) - SamurAI spielt weiter" if lenker is not None and lenker.poll() is None
            else "SamurAI-Wache aus (STOP_SAMURAI)")


if __name__ == "__main__":
    main()
