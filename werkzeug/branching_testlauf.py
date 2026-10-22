"""Entwicklungsvergleich mit bestehenden Crusader-Startwerkzeugen; keine Abnahmeserie."""
import os,sys,pathlib,json,time,subprocess,struct,hashlib
root=pathlib.Path(__file__).resolve().parents[1]
os.environ.update(SHC_INSTANZ='5',SHC_SITZUNG='codex-sai-01a1649a',SHC_PARTNER='ja',PYTHONIOENCODING='utf-8')
sys.path.insert(0,str(root/'werkzeug'))
import samurai_wache as existing
import speicher
lock=root.parent/'VillageStudio/werkzeug/sperre.py'
stamp=time.strftime('%Y%m%d_%H%M%S');prefix=root/'daten'/('branching_'+stamp)
base=dict(s.split('=',1) for s in existing.LENKER_ARGS)
base.pop('uebernehmen',None)
base.update(tempo='100',minuten='30',bis_tick='96000',karte='Liga_Branching Fortunes',team_kis='7,8')
for arg in sys.argv[1:]:
 k,v=arg.split('=',1);base[k]=v
manifest={'backlog':'B-209 B-210','stamp':stamp,'map':base['karte'],'opponents':['Gardist','Kriegsfuerst'],'opponent_ids':[7,8],'status':'running','consoles':[], 'start_gate_tick':800,'args':base,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()}
import kennung
manifest['code_identity']=kennung.zeile()
manifest['initial_data_hashes']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'daten').glob('*.json') if not p.name.startswith(('branching_','vergleich_','ertrag_gelernt_'))}
game=pathlib.Path(r'C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz5')
manifest['environment']={str(f.relative_to(game)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [game/'Stronghold Crusader.exe',game/'ucp-config.yml',game/'ucp/villagestudio/logik.lua',game/'ucp/modules/villagestudio-0.1.0/init.lua',game/'ucp/plugins/Mod-KI-Team-Liga-2.0.2/resources/maps/Liga_Branching Fortunes.map']}
path=prefix.with_suffix('.json')
def save():path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
def lockcall(action):
 return subprocess.run([sys.executable,str(lock),action,'SAI-Codex','Branching Fortunes B-209/B-210'],capture_output=True,text=True)
r=lockcall('holen');print(r.stdout,flush=True)
if r.returncode:raise SystemExit('Testinstanz belegt')
ps=[];files=[];observer=None
try:
 for sp,places in [(1,'0,1,2,3'),(2,'1,0,2,3')]:
  args=dict(base,plaetze=places,**({'eins_gegen_eins':'ja'} if sp==1 else {'anhaengen':'ja'}))
  env=dict(os.environ,SHC_PARTNER='ja',SHC_SPIELER=str(sp))
  target=pathlib.Path(str(prefix)+'_sp%d_konsole.txt'%sp);f=target.open('w',encoding='utf-8');files.append(f)
  cmd=[sys.executable,'-u']+(['-m','cProfile','-o',str(prefix)+'_sp%d.prof'%sp] if os.environ.get('SAI_PROFILE')=='ja' else [])+[str(root/'werkzeug/erstes_spiel.py')]+[k+'='+v for k,v in args.items()]
  ps.append(subprocess.Popen(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT));manifest['consoles'].append(str(target.relative_to(root)))
 manifest['profile']=os.environ.get('SAI_PROFILE')=='ja';manifest['pids']=[p.pid for p in ps];save();print('MATCH',stamp,manifest['pids'],flush=True)
 deadline=time.monotonic()+1900;last_lock=0;gate=False;last_tick=0;last_progress=time.monotonic()
 while any(p.poll() is None for p in ps):
  if time.monotonic()>deadline:manifest['status']='invalid';manifest['reason']='wall-clock watchdog';break
  if time.monotonic()-last_lock>30:
   lockcall('holen');last_lock=time.monotonic()
  tick=struct.unpack('<I',speicher.lies(0x0117CADC,4))[0]
  if tick!=last_tick:last_tick=tick;last_progress=time.monotonic()
  if time.monotonic()-last_progress>90:manifest['status']='invalid';manifest['reason']='tick stalled';break
  try:
   signal=json.loads((root/'werkzeug/.eins_gegen_eins_start5.json').read_text())
   current=signal.get('pid')==ps[0].pid
  except (OSError,ValueError):current=False
  if current and tick>=800 and not gate:
   count=struct.unpack('<I',speicher.lies(0xF98520+8,4))[0]
   if count>2000:raise RuntimeError('building count outside measured capacity: %s'%count)
   raw=speicher.lies(0xF98520,(count+1)*0x32C)
   granaries={1:[],2:[]}
   for i in range(1,count+1):
    off=i*0x32C;state,typ=struct.unpack_from('<HH',raw,off+0xE4);owner=struct.unpack_from('<H',raw,off+0xEA)[0]
    if state not in (0,3) and typ==19 and owner in granaries:granaries[owner].append(i)
   manifest['start_gate']={'tick':tick,'granaries':granaries};save()
   if not all(granaries.values()):manifest['status']='invalid';manifest['reason']='observed granary missing by startup gate';break
   gate=True;print('START GATE PASSED',manifest['start_gate'],flush=True)
   obslog=pathlib.Path(str(prefix)+'_observer_konsole.txt').open('w',encoding='utf-8');files.append(obslog)
   observer=subprocess.Popen([sys.executable,'-u',str(pathlib.Path(__file__).with_name('branching_beobachter.py')),stamp],cwd=root,stdout=obslog,stderr=subprocess.STDOUT)
  time.sleep(.5)
 else:
  manifest['status']='finished_unscored';manifest['exit_codes']=[p.returncode for p in ps]
except BaseException as ex:
 manifest['status']='invalid';manifest['reason']=repr(ex);raise
finally:
 if manifest['status']=='invalid':
  # Spielabbruch: vorhandene Fehlerbehandlung darf gzip/Profiler geordnet schliessen.
  grace=time.monotonic()+40
  while any(p.poll() is None for p in ps) and time.monotonic()<grace:time.sleep(.2)
 for p in ps:
  if p.poll() is None:p.terminate()
 for p in ps:
  try:p.wait(timeout=10)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 for f in files:f.close()
 if observer:
  try:observer.wait(timeout=5)
  except subprocess.TimeoutExpired:observer.terminate();observer.wait()
 save()
 # After our writers have stopped, use the existing command route to pause.
 try:
  import befehl
  befehl.sende({'befehle':[{'pause':True}]},3)
 except Exception as ex:manifest['pause_error']=repr(ex);save()
 print(lockcall('freigeben').stdout,flush=True)
 print('MATCH END',manifest['status'],manifest.get('reason',''),flush=True)
