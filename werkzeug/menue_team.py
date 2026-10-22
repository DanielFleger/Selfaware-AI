"""Neue Partien ausschliesslich ueber den bestehenden Menue-Befehlskanal. Keine Eingabesimulation."""
import os,sys,time,struct,json
from pathlib import Path
os.environ.setdefault('SHC_INSTANZ','5');os.environ.setdefault('SHC_PARTNER','ja')
from befehl import sende
from speicher import lies
ROOT=Path(__file__).resolve().parents[1]
def zahlen(a,n=1):return list(struct.unpack('<'+'i'*n,lies(a,n*4)))
def knopf(name,nr):return sende({'knopf':name,'nr':nr},6,bis='KNOPF')
def warten(adresse,wert,sekunden=10):
 ende=time.monotonic()+sekunden
 while time.monotonic()<ende:
  if zahlen(adresse)[0]==wert:return
  time.sleep(.1)
 raise RuntimeError('Menuezustand nicht erreicht: %x soll %s ist %s'%(adresse,wert,zahlen(adresse)))
def vorbereiten(gegner=(9,10),karte='Liga_Branching Fortunes'):
 if zahlen(0x01FE7D1C)[0]!=41:raise RuntimeError('Hauptmenue erforderlich; laufende Partie bleibt unangetastet')
 sende({'hauptmenue':2},3,bis='HAUPTMENUE');warten(0x01FE7D1C,55)
 knopf('SelectCrusade_Main',2);warten(0x01FE7D1C,20)
 knopf('LobbyMenu_PlayerListAndNpcButtons',-101)
 for typ in (16,*gegner,16):knopf('AiLordSelect_Main',typ)
 knopf('AiLordSelect_Main',100)
 count=zahlen(0x01A24A68)[0]
 if not 0<count<=500:raise RuntimeError('Unplausible Kartenliste')
 indices=zahlen(0x01126E28,count)
 candidates=[n for n,k in enumerate(indices) if lies(0x11BFCF8+k*0x3e9,120).split(b'\0')[0].decode('latin1')==karte]
 if len(candidates)!=1:raise RuntimeError('Karte nicht eindeutig: %r'%candidates)
 knopf('LobbyMenu_MapSelectTable',candidates[0])
 ende=time.monotonic()+5
 while time.monotonic()<ende and lies(0x01A22F9C,120).split(b'\0')[0].decode('latin1')!=karte:time.sleep(.05)
 if lies(0x01A22F9C,120).split(b'\0')[0].decode('latin1')!=karte:raise RuntimeError('Kartenauswahl ohne Wirkung')
 order=lambda:list(lies(0x01A275AC,9))
 knopf('LobbyMenu_PlayerListAndNpcButtons',-102)
 for sp in (1,2,3,4):
  knopf('Roundtable_Main',order().index(sp));knopf('Roundtable_Main',21)
 for a,b in ((1,4),(2,3)):
  o=order();knopf('Roundtable_Main',o.index(a));knopf('Roundtable_Main',10+o.index(b))
 knopf('Roundtable_Main',100)
 knopf('LobbyMenu_SkirmishTypeAndBalance',12);knopf('LobbyMenu_SkirmishTypeAndBalance',1)
 ai=zahlen(0x0191DE7C,9);groups=list(lies(0x01A275B5,9));positions=list(lies(0x01A275D0,8))
 if ai[1:5]!=[16,*gegner,16] or not(groups[1]==groups[4]!=groups[2]==groups[3]):raise RuntimeError('KI/Team-Gegenlesen gescheitert')
 return {'map':karte,'ai':ai,'groups':groups,'positions':positions,'method':'menu_handlers','no_ui_input':True,'no_saved_game':True}
def starten(gegner=(9,10)):
 result=vorbereiten(gegner);stamp=time.strftime('%Y%m%d_%H%M%S')
 path=ROOT/'daten'/('menue_team_'+stamp+'.json');path.write_text(json.dumps(result,indent=2))
 sende({'eigenerPlatz':1},3);knopf('LobbyMenu_LobbyscreenStartButtonClick',4)
 warten(0x01FE7D1C,14,20)
 result['start_tick']=zahlen(0x0117CADC)[0];result['status']='started';path.write_text(json.dumps(result,indent=2))
 print('MATCH',stamp,result,flush=True)
 return result
if __name__=='__main__':starten(tuple(map(int,sys.argv[1].split(','))) if len(sys.argv)>1 else (9,10))
