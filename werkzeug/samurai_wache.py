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


AI_IDS = dict(zip(('rat','snake','pig','wolf','saladin','caliph','sultan','richard','frederick','phillip','wazir','emir','nizar','sheriff','marshal','abbot'),range(1,17)))


def konfigurierte_ki(config):
    """Die sichtbare SamurAI-Auswahl bestimmt den Platzhalter, nicht ein alter Zahlenwert."""
    ai=config['config-full']['modules']['aiSwapper']['config']['ai']
    result=[]
    for name,parts in ai.items():
        v=parts.get('lines',{}).get('contents',{}).get('value',{})
        if v.get('active') and v.get('name')=='SamurAI' and v.get('root','').rstrip('/')=='ucp/resources/ai/SamurAI':
            result.append(AI_IDS[name])
    if len(result)!=1:
        raise RuntimeError('SamurAI-Menuezuordnung muss eindeutig sein: %r'%result)
    return result[0]


def auswahl(ai, samurai_id, mensch=False):
    slots={sp for sp,k in ai.items() if k==samurai_id}
    if slots and mensch:slots.add(1)
    return sorted(slots)


def main():
    import json,yaml
    from pathlib import Path
    from laden import befehl
    from befehl import SPIEL
    if os.environ.get('SHC_PARTNER')!='ja':raise SystemExit('SHC_PARTNER=ja erforderlich')
    config=yaml.safe_load((Path(SPIEL)/'ucp-config.yml').read_text(encoding='utf-8'))
    samurai_id=konfigurierte_ki(config)
    # Nur der ausdrueckliche KI-Testmodus steuert auch den menschlichen ersten Platz.
    mensch=os.environ.get('SHC_STEUERE_MENSCH')=='ja'
    schreib('SamurAI-Wache: sichtbarer Platzhalter KI %d, Teamsteuerung, Mensch steuern %s'%(samurai_id,mensch))
    aktiv={};bedient=set();scharf=False;zuletzt_im_spiel=False
    if os.path.exists(STOP):os.remove(STOP)
    try:
        while not os.path.exists(STOP):
            try:
                ansicht,over,ai=lies(mit_ai=False)
            except Exception as ex:
                schreib('Warte auf Spiel: %r'%ex);time.sleep(2);continue
            ingame=im_spiel(ansicht,over)
            if not ingame:
                for sp,(proc,handle) in list(aktiv.items()):
                    if proc.poll() is None:proc.terminate()
                    proc.wait(timeout=10);handle.close()
                aktiv.clear();bedient.clear()
                if not scharf:
                    befehl({'tickpause':{'bei':1}},.5);scharf=True
                zuletzt_im_spiel=False
            else:
                if not zuletzt_im_spiel:
                    ai=lies()[2]
                    slots=auswahl(ai,samurai_id,mensch)
                    schreib('Neue Menue-Partie %r, KI-Nummern %r, SamurAI-Plaetze %r'%(kartenname(),ai,slots))
                    if slots:
                        befehl({'pause':True},.5)
                        # Erst alle ausgewaehlten Platzhalter abschalten, dann beide Lenker starten.
                        for sp in slots:ki_aus(sp)
                        for sp in slots:
                            log=Path(D)/('samurai_%s_sp%d_konsole.txt'%(time.strftime('%Y%m%d_%H%M%S'),sp))
                            handle=log.open('w',encoding='utf-8')
                            env=dict(os.environ,SHC_SPIELER=str(sp),SHC_PARTNER='ja')
                            proc=subprocess.Popen([sys.executable,'-u',str(Path(HIER)/'erstes_spiel.py')]+LENKER_ARGS,cwd=HIER,env=env,stdout=handle,stderr=subprocess.STDOUT)
                            aktiv[sp]=(proc,handle);bedient.add(sp)
                            schreib('SamurAI gestartet fuer Spieler %d: Prozess %d, %s'%(sp,proc.pid,log))
                    befehl({'tickpause':'aus'},.5)
                    befehl({'pause':False},.5);scharf=False;zuletzt_im_spiel=True
                for sp,(proc,handle) in aktiv.items():
                    if proc.poll() is not None and not handle.closed:
                        schreib('SamurAI Spieler %d beendet, Rueckgabe %s; kein verdeckter Neustart'%(sp,proc.returncode));handle.close()
            time.sleep(SCHNELL_S if not ingame else PAUSE_S)
    finally:
        for proc,handle in aktiv.values():
            if proc.poll() is None:proc.terminate()
            proc.wait(timeout=10);handle.close()


if __name__=='__main__':main()
