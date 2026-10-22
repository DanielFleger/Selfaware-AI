"""Nur-Lese-Endnachweis; verwirft waehrend des Lesens wechselnde Spieltakte."""
import os,sys,pathlib,struct,json,time,gzip
root=pathlib.Path(__file__).resolve().parents[1]
os.environ['SHC_INSTANZ']='5';sys.path.insert(0,str(root/'werkzeug'))
from speicher import lies
stamp=sys.argv[1] if len(sys.argv)>1 else '20261022_192955'
out=root/('daten/benchmarks/branching_'+stamp+'_observed.jsonl.gz')
def number(a):return struct.unpack('<I',lies(a,4))[0]
last=-1
with gzip.open(out,'at',encoding='utf-8') as f:
 deadline=time.monotonic()+2100
 while time.monotonic()<deadline:
  start=number(0x0117CADC)
  if start==last:time.sleep(.1);continue
  maxunits=min(number(0x01387F38),2500)
  raw=lies(0x0138854C,maxunits*1168)
  lords={}
  for i in range(1,maxunits):
   off=i*1168;state,typ=struct.unpack_from('<hh',raw,off+0x8C)
   if state and typ==55 and struct.unpack_from('<h',raw,off+0x2A0)[0]==0:
    owner=struct.unpack_from('<h',raw,off+0x96)[0]
    lords[owner]={'nr':i,'uid':struct.unpack_from('<i',raw,off+0x98)[0],'health':struct.unpack_from('<i',raw,off+0x3C8)[0]}
  alive=list(struct.unpack('<8h',lies(0x0117EF42,16)))
  ai=list(struct.unpack('<8i',lies(0x0191DE80,32)))
  over=number(0x0117D500);view=number(0x01FE7D1C);end=number(0x0117CADC)
  if end!=start:continue
  r={'tick':start,'over':over,'view':view,'alive':alive,'ai':ai,'lords':lords,'coherent':True}
  f.write(json.dumps(r)+'\n');f.flush();last=start
  if over or view not in (14,16):print(json.dumps(r),flush=True);break
  time.sleep(.5)
print('observer complete',out.name,flush=True)
