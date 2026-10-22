"""Weg zum Lord: normales Gehen, zerstoerbare Hindernisse und Gegenfaelle."""
import unittest,numpy as np
import durchbruch,mechanik,parteien
from weggraph import RICHTUNGEN

MK={'mauer':5,'tor_turm':15,'gebaeude':80,'takte_je_treffer':96}
class Gebaeudepfad(unittest.TestCase):
 def scene(self,typ=11,owner=2,zwei=False,umweg=False):
  n=24;link=np.zeros((n,n),np.uint8);bau=np.zeros((n,n),np.int32)
  frei={(x,12) for x in range(2,22)}
  if umweg:frei|={(x,16) for x in range(2,22)}|{(x,y) for x in (2,21) for y in range(12,17)}
  bau[8:10,11:14]=90
  if zwei:bau[12:14,11:14]=91
  for x,y in frei:
   if bau[x,y]:continue
   for bit,dx,dy in RICHTUNGEN:
    q=x+dx,y+dy
    if q in frei and not bau[q]:link[x,y]|=bit
  e={'link':link,'bau':bau,'gebiet':(link>0).astype(np.int32),'logik':np.zeros((n,n),np.uint32),'besitz':np.zeros((n,n),np.uint8),'hoehe':np.zeros((n,n),int),'boden':np.zeros((n,n),int)}
  G={90:{'typ':typ,'besitzer':owner,'x':8,'y':11,'leben':80}}
  if zwei:G[91]={'typ':11,'besitzer':2,'x':12,'y':11,'leben':80}
  return e,G
 def plan(self,**kw):
  e,G=self.scene(**kw);parteien.setzen(1,{1})
  return durchbruch.plane(1,(2,12),5,(21,12),mk=MK,L={},G=G,gf=np.zeros((24,24)),e=e)
 def test_building_on_only_route(self):
  p=self.plan();self.assertEqual(p['art'],'gebaeude');self.assertEqual(p['ziel'],90);self.assertEqual(p['zug'],(7,12))
 def test_multiple_buildings_on_route(self):
  p=self.plan(zwei=True);self.assertEqual(p['art'],'gebaeude');self.assertEqual(p['ziel'],90)
  self.assertGreaterEqual(p['takte'],2*96)
 def test_stockpile_is_never_demolition_target(self):self.assertIsNone(self.plan(typ=10))
 def test_allied_building_is_never_demolition_target(self):self.assertIsNone(self.plan(owner=1))
 def test_existing_walk_route_wins_when_faster(self):
  p=self.plan(umweg=True);self.assertEqual(p['art'],'lord')
 def test_building_does_not_create_a_ramp(self):
  e,G=self.scene();e['boden'][8:10,:]=60
  p=durchbruch.plane(1,(2,12),5,(21,12),mk=MK,L={},G=G,gf=np.zeros((24,24)),e=e)
  self.assertIsNone(p)
 def test_rejected_building_is_not_retried(self):
  e,G=self.scene();p=durchbruch.plane(1,(2,12),5,(21,12),mk=MK,L={},G=G,gf=np.zeros((24,24)),e=e,verworfen={90})
  self.assertIsNone(p)
 def test_feldzug_keeps_and_targets_ordinary_building_plan(self):
  import feldzug as F,gefahr as GF
  e,G=self.scene();f=F.Feldzug(1,(2,12),lord_schutz_bis=0,n=5)
  f.ziel=500;f.phase='angriff';f._orte_f=[];f._gebaeudebild=G
  f._karte=GF.Karte([],n=24,gebiete=e['gebiet'],links=e['link'])
  f.mauerkarte=lambda sp:(np.zeros((24,24),bool),np.zeros((24,24),int))
  f.durchbruch=lambda sp,start,anzahl,ziel,**kw:durchbruch.plane(sp,start,anzahl,ziel,mk=MK,L={},G=G,gf=np.zeros((24,24)),e=e,**kw)
  L={1:{'typ':26,'besitzer':1,'x':2,'y':12,'leben':15000,'zustand':1}}
  f._lagebild=L
  ll=f._lage_lord(L,(21,12),[1],2,(2,12))
  self.assertIsNone(ll['frei']);self.assertEqual(ll['tor'],90)
  self.assertEqual(f.dplan['art'],'gebaeude')
  self.assertTrue(f._schwachstelle(G,(21,12),[(2,12)],[],'Gegenprobe'))
  self.assertEqual(f.bresche,90)
  cached=f._durchbruch_neu(np.zeros((24,24),bool),(3,12),(21,12),5)
  self.assertEqual(cached['ziel'],90)
 def test_opening_one_gate_does_not_open_unrelated_missing_edges(self):
  n=24;link=np.zeros((n,n),np.uint8);link[:,12]=1
  z=np.zeros((n,n),int);frei=np.zeros((n,n),bool);frei[1,1]=True
  p=mechanik.durchbruch_schritte(link,z,z,z,z,z,1,5,(2,12),(21,12),mk=MK,frei=frei,frei_kosten=96)
  self.assertIsNone(p['weg'])
if __name__=='__main__':unittest.main()
