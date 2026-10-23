"""Fresh menu-started experiment; existing native bridge only, no input/window APIs."""
import contextlib
import gzip
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import time

from pipeline import ROOT
os.environ['SHC_INSTANZ']='5'
os.environ['SHC_PARTNER']='ja'
sys.path.insert(0,str(ROOT.parent/'sai-live/werkzeug'))
from befehl import sende
from speicher import lies, _griff
from menue_team import starten

def main():
    stamp=time.strftime('%Y%m%d_%H%M%S')
    out=ROOT/'evidence'/('live-'+stamp);out.mkdir()
    with (out/'console.txt').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log):
        print('START-BEFEHL Instanz 5: python work/engine-knowledge/live_probe.py',flush=True)
        print('CODE-KENNUNG',hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),flush=True)
        scene=starten()
        print(sende({'pause':True},5),flush=True)
        tick=struct.unpack('<i',lies(0x0117CADC,4))[0]
        mask=lies(0x021AEC98,160000)
        if mask!=lies(0x021AEC98,160000):raise RuntimeError('mask changed during capture')
        (out/'viewport-mask.bin').write_bytes(mask)
        (out/'xy-original.bin').write_bytes(lies(0x00401000,54))
        patches=[];same=0
        for path in sorted((ROOT/'exports/reference/functions').glob('*.json')):
            f=json.loads(path.read_text(encoding='utf-8'))
            changed=[]
            for r in f['raw']:
                expected=bytes.fromhex(r['hex']);actual=lies(int(r['start'],16),len(expected))
                if actual!=expected:
                    changed.append(dict(start=r['start'],reference_sha256=hashlib.sha256(expected).hexdigest(),runtime_sha256=hashlib.sha256(actual).hexdigest()))
            if changed:patches.append(dict(address=f['address'],name=f['name'],changed=changed))
            else:same+=1
        print(sende({'status':1},5),flush=True)
        print(sende({'lagebild':True},10),flush=True)
        tick_after=struct.unpack('<i',lies(0x0117CADC,4))[0]
        if tick!=tick_after:raise RuntimeError('tick advanced during paused capture')
        state=dict(scene=scene,pid=_griff['pid'],tick=tick,tick_after=tick_after,unpatched_functions=same,patched_functions=patches,mask_sha256=hashlib.sha256(mask).hexdigest(),valid_cells=sum(x!=0 for x in mask),mode='fresh-menu-start; paused observation; no policy performance claim')
        (out/'state.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
        print(json.dumps(dict(tick=tick,unchanged=same,patched=len(patches))),flush=True)
    (ROOT/'evidence/latest-live.txt').write_text(str(out),encoding='utf-8')
    print(out)

if __name__=='__main__':main()
