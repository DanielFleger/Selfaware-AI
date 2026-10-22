"""Unabhaengige Nur-Lese-Kontrolle fuer Breschenwirkung und Zielwechsel."""
import sys,os,time,json,gzip,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'werkzeug'),str(ROOT.parent/'Selfaware-AI-kern/src')]
os.environ['SHC_INSTANZ']='5'
from selfaware.game.kern_leitung import Leitung
from befehl import SPIEL
from menue_team import zahlen
from feldzug import HEER
stamp=sys.argv[1];logs=sorted((ROOT/'daten').glob('samurai_'+sys.argv[2]+'_sp*_konsole.txt'))
handles={p.name:p.open(encoding='utf-8',errors='replace') for p in logs}
seen=set();targets=set();last={};link=Leitung(SPIEL)
with gzip.open(ROOT/'daten/benchmarks'/('zugang_'+stamp+'.jsonl.gz'),'wt',encoding='utf-8') as f:
 end=time.monotonic()+1800
 while time.monotonic()<end:
  events=[]
  for name,h in handles.items():
   for line in h:
    for event in line.split('; '):
     if any(s in event for s in ('FELDZUG DURCHBRUCH','FELDZUG SCHWACHSTELLE','FELDZUG NACH DEM SIEG','FELDZUG: Ziel Lord','FELDZUG BRESCHE:')):
      events.append({'log':name,'tick':line.split('|')[0].strip(),'event':event.strip()})
      match=re.search(r'(?:Gebaeude|Torhaus) (\d+)',event)
      if match:targets.add(int(match[1]))
  try:
   w=link.lesen();changes=[]
   for nr in targets:
    g=w.gebaeude.get(nr);prev=last.get(nr)
    hp=g.get('leben') if g else None
    if prev and hp!=prev.get('leben'):
     changes.append({'nr':nr,'previous':prev,'now':g,'targeting':[u for u in w.einheiten.values() if u.get('besitzer') in (1,4) and u.get('zielgebaeude')==nr]})
    last[nr]=g
   troops=[u for u in w.einheiten.values() if u.get('typ')==55 or (u.get('besitzer') in (1,4) and u.get('typ') in HEER)]
   r={'tick':w.tick,'events':events,'building_changes':changes,'targets':{str(n):w.gebaeude.get(n) for n in targets},'troops':troops,'over':zahlen(0x0117D500)[0]}
   f.write(json.dumps(r)+'\n');f.flush()
   if r['over']:break
  except Exception as ex:
   f.write(json.dumps({'error':str(ex),'events':events})+'\n');f.flush()
  time.sleep(2)
print('feature observer complete',flush=True)
