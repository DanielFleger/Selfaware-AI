"""Isolated native-menu smoke test; no save loading or desktop input.

Requires an explicitly supplied start record from the isolated review app.
Never run this against a user match: the initial menu state must be 41.
"""
import argparse,os,sys,json,time,traceback,struct,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--start-record',required=True);p.add_argument('--output',required=True)
p.add_argument('--map',default='!KOphase Map 1');p.add_argument('--minimum-tick',type=int,default=4000)
args=p.parse_args()
start=json.loads(Path(args.start_record).read_text())
config=start['installation'];game=Path(config['game']);runtime=Path(config['runtime'])
os.environ.update(SHC_INSTANZ='4',SHC_GAME_DIR=str(game),SHC_GAME_PID=str(start['game_pid']),SHC_PARTNER='ja',SHC_TRANSPORT='memory',SHC_STATE_DIR=str(runtime.parent))
sys.path.insert(0,str(runtime/'Selfaware-AI/werkzeug'))
def ipc_hashes():return {f.relative_to(game).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in (game/'ucp/villagestudio').rglob('*') if f.is_file()}
before_ipc=ipc_hashes()
result={'START-BEFEHL':' '.join(sys.argv),'game_pid':start['game_pid'],'map':args.map,
        'runtime_sha256':config['runtime_sha256'],'module_sha256':config['module_sha256'],
        'test_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'method':'fresh native menu handlers; no saved game, no input simulation'}
try:
    from befehl import sende,session_record,KANAL_ORDNER
    from speicher import lies
    def numbers(a,n=1):return list(struct.unpack('<'+'i'*n,lies(a,n*4)))
    def wait(a,value,seconds=20):
        deadline=time.monotonic()+seconds
        while numbers(a)[0]!=value:
            assert time.monotonic()<deadline,(a,value,numbers(a));time.sleep(.1)
    def button(name,n):return sende({'knopf':name,'nr':n},6,bis='KNOPF')
    wait(0x01FE7D1C,41)
    result['initial_clock']=sende({'zeit':True},3)
    # A banned operation must fail without disabling the bridge or opening files.
    try:sende({'foto':True},3)
    except RuntimeError as e:result['banned_file_command_rejected']=str(e)
    else:raise AssertionError('Disk screenshot request was accepted')
    result['after_rejection_clock']=sende({'zeit':True},3)
    sende({'hauptmenue':2},3,bis='HAUPTMENUE');wait(0x01FE7D1C,55)
    button('SelectCrusade_Main',2);wait(0x01FE7D1C,20)
    button('LobbyMenu_PlayerListAndNpcButtons',-101)
    for ai in (16,16):button('AiLordSelect_Main',ai)
    button('AiLordSelect_Main',100)
    count=numbers(0x01A24A68)[0];indices=numbers(0x01126E28,count)
    rows=[i for i,k in enumerate(indices) if lies(0x11BFCF8+k*0x3e9,120).split(b'\0')[0].decode('latin1')==result['map']]
    assert len(rows)==1,rows;button('LobbyMenu_MapSelectTable',rows[0])
    # Map selection returns before the native menu finishes its next refresh.
    # Developer fixture only: allow that refresh before requesting game start.
    time.sleep(1)
    result['lobby_ai']=numbers(0x0191DE7C,9)
    result['local_slot_before']=numbers(0x01A275DC)[0]
    button('LobbyMenu_LobbyscreenStartButtonClick',4);wait(0x01FE7D1C,14)
    result['takeover']=session_record();result['local_slot_after']=numbers(0x01A275DC)[0]
    assert result['takeover']['tick']==0,result
    slots=result['takeover']['slots']
    assert len(slots)==2,result
    assert result['local_slot_after']==result['local_slot_before'],result
    result['snapshot_reply']=sende({'player':slots[0],'lagebild':True},10,bis='LAGEBILD')
    result['external_snapshot_files']=[str(p.relative_to(runtime.parent)) for p in Path(KANAL_ORDNER).rglob('*.txt')]
    deadline=time.monotonic()+60
    while True:
        raw=lies(0xF98520,2000*0x32c);types={sp:{} for sp in slots}
        for i in range(1,2000):
            b=i*0x32c;state,typ=struct.unpack_from('<HH',raw,b+0xe4);owner=struct.unpack_from('<H',raw,b+0xea)[0]
            if state not in (0,3) and owner in types:
                types[owner][typ]=types[owner].get(typ,0)+1
        result['building_types']=types;result['tick']=numbers(0x0117CADC)[0]
        # Actual built economy, excluding starting keep/stockpile/camp/piles.
        counts={sp:sum(n for typ,n in group.items() if typ not in (41,71,72,73,55,10)) for sp,group in types.items()}
        result['non_start_building_objects']=counts
        if min(counts.values())>=3 and result['tick']>=args.minimum_tick:break
        assert time.monotonic()<deadline,result
        time.sleep(.5)
    result['watcher_log']=(runtime.parent/('worker-%d.log'%start['game_pid'])).read_text(encoding='utf-8',errors='replace')[-10000:]
    assert 'beendet, Rueckgabe 1' not in result['watcher_log'],'Controller stopped unexpectedly'
    result['active_unit_types']={sp:{} for sp in slots}
    units=lies(0x0138854C,2500*1168)
    for i in range(1,2500):
        offset=i*1168;state,typ=struct.unpack_from('<HH',units,offset+0x8c);owner=struct.unpack_from('<H',units,offset+0x96)[0]
        if state!=0 and owner in result['active_unit_types']:
            group=result['active_unit_types'][owner];group[typ]=group.get(typ,0)+1
    sende({'optionen':7},6,bis='OPTIONEN');sende({'dialogJa':True},6,bis='DIALOG');time.sleep(3)
    result['restored_lobby_ai']=numbers(0x0191DE7C,9)
    result['takeover_after_match']=session_record()
    assert all(result['restored_lobby_ai'][sp]==16 for sp in slots),result
    assert not result['takeover_after_match']['active'],result
    result['unchanged_game_ipc_files']=ipc_hashes()==before_ipc
    assert result['unchanged_game_ipc_files'],'The game-side file IPC tree changed'
except BaseException:result['error']=traceback.format_exc()
finally:
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
if 'error' in result:raise SystemExit(1)
