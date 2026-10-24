# -*- coding: utf-8 -*-
"""Einen Befehl an unser Modul schicken und die Antwort aus dem Log lesen.

Die Nummern-Regel ist fest eingebaut (Meilenstein M2.03): Das Modul
ueberspringt jeden Befehl, dessen 'id' es schon kennt. Darum vergibt dieses
Werkzeug jede Nummer nur einmal - stetig steigend ueber alle Laeufe hinweg,
die letzte vergebene steht in .letzte_id neben diesem Skript.

Aufruf:    python befehl.py '<json>' [wartesekunden]
Beispiel:  python befehl.py '{"player": 1, "tempo": 90}' 3
Als Baustein:  from befehl import sende; zeilen = sende({"zeit": True})

Zwei Spielinstanzen (05.10.2026): SHC_INSTANZ=2 waehlt die Spielkopie
"<Instanz 1> Instanz2" - mit eigener befehl.json, eigenem ucp3.log, eigener
Kanalsperre (.lauf2) und eigenem Nummernzaehler (.letzte_id2). Ohne Angabe gilt
Instanz 1, alles wie bisher. Dieselbe Ordner-Regel steht in
VillageStudio/werkzeug/instanz.py (spiel.py prueft, dass beide gleich sind). Andere Werkzeuge nehmen
SPIEL und ABZUG von hier, nie einen eigenen Pfad - sonst liest ein Lauf auf
Instanz 2 still die Lagebilder von Instanz 1.
"""
import io, json, os, re, sys, time, threading
from kanalsperre import Sperre

_ROH = os.environ.get("SHC_INSTANZ", "").strip() or "1"
if not _ROH.isdigit() or int(_ROH) < 1:
    raise RuntimeError("SHC_INSTANZ=%r ist keine Instanznummer (1, 2, ...)" % _ROH)
INSTANZ = int(_ROH)
_STAMM = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"
SPIEL  = os.path.abspath(os.environ.get("SHC_GAME_DIR") or (_STAMM if INSTANZ == 1 else "%s Instanz%d" % (_STAMM, INSTANZ)))
if not os.path.isdir(SPIEL):
    raise RuntimeError("Instanz %d gibt es nicht: %s" % (INSTANZ, SPIEL))
_ENDUNG = "" if INSTANZ == 1 else str(INSTANZ)
BEFEHL = os.path.join(SPIEL, "ucp", "villagestudio", "befehl.json")
LOG    = os.path.join(SPIEL, "ucp3.log")
MEMORY = os.environ.get('SHC_TRANSPORT')=='memory'
if MEMORY:
    if not os.environ.get('SHC_STATE_DIR') or not os.environ.get('SHC_GAME_PID','').isdigit():
        raise RuntimeError('Memory transport requires an explicit external state directory and game PID')
    KANAL_ORDNER=os.path.join(os.path.abspath(os.environ['SHC_STATE_DIR']),'ipc',os.environ['SHC_GAME_PID'])
else:
    KANAL_ORDNER=os.path.dirname(BEFEHL)
# 19.10.2026 (1v1, Selfaware gegen sich selbst): SHC_SPIELER waehlt den Spieler dieses Prozesses - jeder Befehl traegt dann
# "player" = SPIELER (das Modul stellt den Platz je Befehl um, logik.lua 19.10.), Abzuege (Lagebild, Gebaeude, Karten)
# kommen in einen eigenen Ordner abzug_sp<N>. SHC_PARTNER=ja: zwei Lenker teilen sich den Kanal - statt der Sperre fuer
# den ganzen Lauf eine kurze Sperre je Befehl (Schreiben bis zur eigenen Quittung).
_SP = os.environ.get("SHC_SPIELER", "").strip() or "1"
if not _SP.isdigit() or not 1 <= int(_SP) <= 8:
    raise RuntimeError("SHC_SPIELER=%r ist keine Spielernummer (1-8)" % _SP)
SPIELER = int(_SP)
PARTNER = os.environ.get("SHC_PARTNER", "").strip().lower() in ("ja", "1", "true")
ABZUG  = os.path.join(KANAL_ORDNER, "abzug" if SPIELER == 1 else "abzug_sp%d" % SPIELER)
os.makedirs(ABZUG, exist_ok=True)      # auch eine frische Installation braucht den Ordner fuer Spieler 1
# 18.10. (1v1-Lauf 1018a): je Spieler ein eigener Merker - im gemeinsamen las ein Lenker die kleinere Nummer des anderen und
# vergab eigene Nummern doppelt (Gegenprobe ids_pruefen: 5.754 doppelte von 6.000)
MERKER = os.path.join(KANAL_ORDNER, ".letzte_id_sp%d" % SPIELER)
SENDE  = os.path.join(KANAL_ORDNER, ".sende")   # ein Spielkanal, unabhaengig von Checkout und Instanz-Alias


_LETZTE = 0
ACK_POLL = .002
_ID_MUTEX = threading.Lock()
_ID_BLOCK = iter(())
_ID_PID = None
_ID_BLOCK_GROESSE = 128


def _veroeffentlichen(temp, ziel):
    """Nur VOR der Veroeffentlichung warten: Windows-Leser sperren kurz das Umbenennen."""
    ende = time.monotonic() + .5
    while True:
        try:
            os.replace(temp, ziel)
            return
        except PermissionError:
            if time.monotonic() >= ende:
                raise
            time.sleep(.002)


def letztes_spielende(n=1):
    """B-154: die letzten n Zeilen des Spielende-Melders (logik.lua schreibt ucp/villagestudio/spielende.txt: BEWUSST/UNBEWUSST,
    Grund, gameOver, Ansicht, Lords) - [] ohne Datei."""
    try:
        with open(os.path.join(KANAL_ORDNER, "spielende.txt"), encoding="utf-8", errors="replace") as f:
            return [z.rstrip("\n") for z in f.readlines()[-n:]]
    except OSError:
        return []


def neue_id():
    # Derselbe Spieler darf auch aus mehreren Prozessen keine Nummer doppelt vergeben.
    # Ganze Bloecke reservieren: unbenutzte Nummern nach einem Absturz werden ausgelassen.
    global _ID_BLOCK, _ID_PID
    with _ID_MUTEX:
        if _ID_PID != os.getpid():
            _ID_BLOCK, _ID_PID = iter(()), os.getpid()
        try:
            return next(_ID_BLOCK)
        except StopIteration:
            with Sperre(MERKER + '.lock'):
                erste = _neue_id_gesperrt(_ID_BLOCK_GROESSE)
            _ID_BLOCK = iter(range(erste + 8, erste + 8 * _ID_BLOCK_GROESSE, 8))
            return erste


def _neue_id_gesperrt(anzahl=1):
    """Befehlsnummer. 18.10. (1v1-Lauf 1018a): beide Lenker zaehlten im selben Merker ohne Sperre hoch - gleiche Nummern,
    das Modul hielt den zweiten Befehl fuer "schon erledigt" und antwortete nicht (Spieler 1: Spieltakt None, Absturz).
    Jetzt hat jeder Spieler eigene Nummern (Rest SPIELER beim Teilen durch 8, eigener Merker) - steigend und nie dieselbe."""
    global _LETZTE
    try:
        with io.open(MERKER) as f:
            letzte = int(f.read().strip())
    except (OSError, ValueError):
        letzte = 0
    nummer = max(int(time.time()) * 8, letzte + 1, _LETZTE + 1)
    nummer += (SPIELER - nummer) % 8
    _LETZTE = nummer + 8 * (anzahl - 1)
    with io.open(MERKER, "w") as f:
        f.write(str(_LETZTE))
    return nummer


STRENG = False   # True (z. B. im Lenker): Modulfehler in der Antwort brechen sofort laut ab (Daniel 23:48)
# Lua-Fehler meldet das Modul als "logik: <ort>:<zeile>: <text>" (pcall), eine Befehlsliste mit
# "logik: <gut> von <alle> Befehlen ausgefuehrt" - weniger gut als alle heisst: mindestens einer ist gescheitert.
# Anlass 04.10.2026: eine globale Variable liess jeden Angriffsbefehl scheitern, vier Partien lang unbemerkt.
LUA_FEHLER = re.compile(r"logik: .*:\d+: ")
BILANZ = re.compile(r"logik: (\d+) von (\d+) Befehlen ausgefuehrt")

def pruefe(zeilen):
    for z in zeilen:
        b = BILANZ.search(z)
        if LUA_FEHLER.search(z) or (b and int(b.group(1)) < int(b.group(2))):
            raise RuntimeError("MODULFEHLER (Antwort des Moduls): " + z[:240])
    return zeilen

LAUF = os.path.join(KANAL_ORDNER, ".lauf")   # Kanal belegt: alle Clients desselben Spiels teilen dieselbe Kennung

def belege():
    """Der Lenker meldet sich als Besitzer des Kanals (je Runde aufrufen). 05.10.: eine Nebenabfrage aus einem zweiten
    Prozess lief mitten in Partie 9f in den Kanal - zwei Schreiber auf befehl.json verlieren Befehle. 19.10.: mit PARTNER
    "<pid> partner" - ein zweiter Lenker mit PARTNER darf dann mitsenden (Sperre je Befehl, _sperren)."""
    io.open(LAUF, "w").write(str(os.getpid()) + (" partner" if PARTNER else ""))

def freigeben():
    try:
        with io.open(LAUF) as f:
            besitzer = f.read().strip()
        if besitzer in (str(os.getpid()), str(os.getpid()) + ' partner'):
            os.remove(LAUF)
    except OSError:
        pass

def _kanal_frei():
    try:
        pid = io.open(LAUF).read().strip()
        alter = time.time() - os.path.getmtime(LAUF)
    except OSError:
        return
    if not pid.split():
        return                                 # 18.10. (1v1-Lauf 1018c): der andere Lenker schreibt die Meldung gerade neu (leer) - IndexError
    if PARTNER and pid.endswith(" partner"):
        return                                 # 19.10.: zwei Lenker im 1v1 - die Sperre je Befehl regelt den Zugriff
    if pid.split()[0] != str(os.getpid()) and alter < 15:
        raise RuntimeError("KANAL BELEGT: ein Lauf (Prozess %s) benutzt den Befehlskanal von Instanz %d gerade (vor %.0f s gemeldet)" % (pid, INSTANZ, alter))

_SENDE_LOKAL = threading.local()
_MEMORY_CHANNEL = None


def memory_channel():
    global _MEMORY_CHANNEL
    if not MEMORY:raise RuntimeError('Memory channel was not explicitly selected')
    if _MEMORY_CHANNEL is None:
        from speicherkanal import Channel
        _MEMORY_CHANNEL=Channel(int(os.environ['SHC_GAME_PID']))
    return _MEMORY_CHANNEL


def session_record():
    if MEMORY:
        raw=memory_channel().status()
        return json.loads(raw.decode('utf-8')) if raw else {'active':False}
    with open(os.path.join(KANAL_ORDNER,'uebernahme.json'),encoding='utf-8') as f:return json.load(f)


def _materialize_memory_reply(data):
    from pathlib import Path
    from speicherkanal import records
    decoded=records(data) # Validate the entire frame before any external writes.
    root=Path(KANAL_ORDNER).resolve();lines=[]
    for kind,key,payload in decoded:
        if kind==1:
            lines.append(payload.decode('utf-8',errors='replace'));continue
        target=(root/key).resolve()
        if not target.is_relative_to(root):raise RuntimeError('Snapshot resource escaped external state')
        target.parent.mkdir(parents=True,exist_ok=True)
        if kind==3:
            with target.open('ab') as f:f.write(payload)
        else:
            temp=target.with_name(target.name+'.%s.tmp'%os.getpid())
            temp.write_bytes(payload);_veroeffentlichen(str(temp),str(target))
    return ''.join(lines)


def _send_memory(command,warte,bis):
    channel=memory_channel();own='QUITTUNG %s'%command['id']
    expected=bis or own
    deadline=time.monotonic()+(max(warte,20.0) if PARTNER else warte)
    payload=json.dumps(command).encode('utf-8');answer=''
    while True:
        sequence,data,error=channel.transact(payload,max(.001,deadline-time.monotonic()))
        answer+=_materialize_memory_reply(data)
        channel.consume(sequence) # Acknowledge only after external snapshots are safe.
        if error:raise RuntimeError('MODULFEHLER (memory bridge): '+answer[-1800:])
        if re.search(r'\b'+re.escape(own)+r'(?!\d)',answer) and expected in answer:
            lines=logzeilen(answer)
            return pruefe(lines) if STRENG else lines
        if time.monotonic()>=deadline:
            raise TimeoutError('BEFEHL %s: Wirkung/Quittung fehlt; nicht blind wiederholen'%command['id'])
        # Collect asynchronous effect markers/events; never repeat the original action.
        payload=b'{"poll":true}'
        time.sleep(ACK_POLL)


def _sperren():
    """Alle Schreiber muessen diese Fassung nutzen; keine altersbasierte Uebernahme."""
    lock = Sperre(SENDE + '.lock')
    lock.__enter__()
    _SENDE_LOKAL.lock = lock


def _entsperren():
    lock = _SENDE_LOKAL.lock
    del _SENDE_LOKAL.lock
    lock.__exit__(None, None, None)


def _als_spieler(befehl):
    """19.10.: jeder Befehl (und jeder Eintrag einer Befehlsliste) mit "player" wirkt fuer SPIELER."""
    if SPIELER == 1:
        return befehl
    b = dict(befehl)
    if "player" in b:
        b["player"] = SPIELER
    if isinstance(b.get("befehle"), list):
        b["befehle"] = [dict(c, player=SPIELER) if isinstance(c, dict) and "player" in c else c for c in b["befehle"]]
    return b


def sende(befehl, warte=3.0, bis=None):
    """Schickt den Befehl (dict) und gibt die neuen Modul-Logzeilen zurueck.
    bis = Text, auf den gewartet wird (alle 20 ms nachsehen, hoechstens <warte> s) - statt fest zu warten
    (04.10.2026: feste Wartezeit machte eine Lenker-Runde 1,1 s lang)."""
    _kanal_frei()
    # Lord-Sperre fuer jeden Befehlsweg (lordschutz.py; Daniels Regeln 11.10. 16:11 und 16:41)
    import lordschutz
    befehl, meld = lordschutz.filtern(befehl)
    for m in meld:
        print(m, flush=True)
    if befehl is None:
        return meld
    befehl = _als_spieler(dict(befehl))
    _sperren()
    try:
        befehl["id"] = neue_id()
        # Der Menue-Haken akzeptiert nur bestimmte Felder oder eine Befehlsliste.
        # Eine einheitliche Huelle verhindert still verworfene Einzelbefehle.
        if 'befehle' not in befehl:
            befehl = {'id': befehl['id'], 'befehle': [befehl]}
        if MEMORY:return _send_memory(befehl,warte,bis)
        # 19.10.: mit Partner immer auf die EIGENE Quittung warten - sonst schreibt der andere Lenker befehl.json, bevor das
        # Modul diesen Befehl gelesen hat (die Quittung ist die letzte Zeile eines Befehls, nach allen Antwortzeilen)
        # Auch im Partnerbetrieb muss ein ausdruecklicher Wirkungsmarker
        # eintreffen. Die eigene Quittung allein bestaetigt nur den Empfang.
        quittung = re.compile(r'\bQUITTUNG ' + str(befehl['id']) + r'(?!\d)')
        vorher = os.path.getsize(LOG)
        temp = BEFEHL + '.%s.tmp' % os.getpid()
        with io.open(temp, 'wb') as f:
            f.write(json.dumps(befehl).encode('utf-8'))
        _veroeffentlichen(temp, BEFEHL)
        if bis is None:
            # Daniel 05.10. 23:01: "loesch das feste Zeit-Warten - Sekunden sind Killer". Die Logik quittiert jeden Befehl mit
            # "QUITTUNG <id>" (gleicher Tick); warte ist nur noch die Notbremse, falls keine Quittung kommt (z. B. Hauptmenue).
            bis = "QUITTUNG %s" % befehl["id"]
        # 19.10. (1v1-Probe 2: "keine Antwort auf peek" - der andere Lenker hielt das Modul mit einer Karte mehrere Sekunden)
        ende = time.monotonic() + (max(warte, 20.0) if PARTNER else warte)
        bestaetigt = False
        quittiert = False
        while time.monotonic() < ende:
            time.sleep(ACK_POLL)
            if os.path.getsize(LOG) > vorher:
                with io.open(LOG, encoding="utf-8", errors="replace") as f:
                    f.seek(vorher)
                    antwort = f.read()
                    quittiert = bool(quittung.search(antwort))
                    if bis in antwort and quittiert:
                        bestaetigt = True
                        break
        if not bestaetigt:
            if quittiert:
                raise TimeoutError('BEFEHL %s QUITTIERT ABER WIRKUNGSMARKE FEHLT: %s; Wirkung unbekannt' % (befehl['id'], bis))
            raise TimeoutError('BEFEHL %s OHNE EIGENE QUITTUNG: Wirkung unbekannt; nicht blind wiederholen' % befehl['id'])
        with io.open(LOG, encoding="utf-8", errors="replace") as f:
            f.seek(vorher)
            neu = f.read()
    finally:
        _entsperren()
    zeilen = logzeilen(neu)
    return pruefe(zeilen) if STRENG else zeilen


def logzeilen(text):
    """One compatibility boundary for the Store module's new log prefix."""
    return [z.split('| ',1)[-1].strip().replace('[selfaware-runtime]','[villagestudio]')
            for z in text.splitlines()
            if ('villagestudio' in z or '[selfaware-runtime]' in z) and 'ZUSTAND' not in z]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    zeilen = sende(json.loads(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 3.0)
    for z in zeilen:
        print(z)
    if not zeilen:
        print("(keine Antwort im Log)")
        sys.exit(1)
