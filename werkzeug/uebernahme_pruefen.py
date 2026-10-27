"""Real Lua tests for pre-tick takeover and early sender resolution."""
from pathlib import Path
import unittest
from lupa import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]

class Uebernahme(unittest.TestCase):
    def test_sender_is_resolved_before_native_sorting_even_for_observer(self):
        lua=LuaRuntime(unpack_returned_tuples=True);calls=[];hooks=[]
        lua.globals().package.path=str(ROOT/'?.lua').replace('\\','/')+';'+lua.globals().package.path
        expected=[0x8b,0x91,0x18,0x06,0,0]
        def hook(callback,address,args,conv,size):
            self.assertEqual((address,args,conv,size),(0x47eaf0,2,1,6));hooks.append(callback)
            return lambda this,identity:(calls.append(identity),0)[1]
        lua.globals().core=lua.table_from({'AOBScan':lambda pattern,base:0x47eaf0,'readByte':lambda a:expected[a-0x47eaf0],'hookCode':hook})
        lua.execute((ROOT/'command_owner.lua').read_text()).install()
        for player in range(1,9):self.assertEqual(hooks[0](123,0x53414d00+player),player)
        for identity in (0,1,0x53414d00,0x53414d09,0x53414c01):self.assertEqual(hooks[0](123,identity),0)
        self.assertEqual(len(calls),5) # native fallback preserved, including neutral spectator

    def test_native_ai_is_disabled_before_first_turn_without_any_worker(self):
        lua=LuaRuntime(unpack_returned_tuples=True);writes=[];records=[]
        lua.globals().package.path=str(ROOT/'?.lua').replace('\\','/')+';'+lua.globals().package.path
        memory={0x01fe7d1c:14,0x0117d500:0,0x0117cadc:0}
        for sp in range(1,9):memory[0x0191de7c+sp*4]=16 if sp in (2,5) else (1 if sp==3 else 0)
        lua.globals().core=lua.table_from({'readInteger':lambda a:memory.get(a,0),'writeInteger':lambda a,v:(memory.__setitem__(a,v),writes.append((a,v)))[-1]})
        lua.globals().json=lua.table_from({'encode':lambda self,obj:(records.append(obj),'record')[1]})
        lua.execute('io={open=function() return {write=function() end,close=function() end} end}; log=function() end')
        api=lua.execute((ROOT/'takeover.lua').read_text());api.tick()
        self.assertEqual(len(writes),6)
        self.assertEqual(memory[0x0191de7c+2*4],0)
        self.assertEqual(memory[0x0191de7c+5*4],0)
        self.assertEqual(memory[0x0191de7c+3*4],1)
        self.assertEqual(records[-1]['tick'],0)
        self.assertEqual(records[-1]['original_ai']['2'],16)
        api.tick();self.assertEqual(len(writes),6)
        memory[0x01fe7d1c]=20;api.tick()
        self.assertEqual(memory[0x0191de7c+2*4],16)
        self.assertEqual(memory[0x0191de7c+5*4],16)
        memory[0x0191de7c+5*4]=0
        memory[0x01fe7d1c]=14;memory[0x0191de7c+2*4]=16;api.tick()
        self.assertEqual(len(writes),15)

    # B-280 (Daniel 28.10. 00:26/00:39): Neustart und Laden im Spiel
    def lauf(self, memory, dateien):
        lua=LuaRuntime(unpack_returned_tuples=True);records=[];logs=[]
        lua.globals().package.path=str(ROOT/'?.lua').replace(chr(92),'/')+';'+lua.globals().package.path
        lua.globals().core=lua.table_from({'readInteger':lambda a:memory.get(a,0),'writeInteger':lambda a,v:memory.__setitem__(a,v)})
        import json as J
        def enc(self_,obj):
            d=J.loads(J.dumps(lua_to_py(obj)));records.append(d);return J.dumps(d)
        def lua_to_py(o):
            if hasattr(o,'items') and not isinstance(o,dict):
                d={k:lua_to_py(v) for k,v in o.items()}
                if d and all(isinstance(k,int) for k in d):return [d[k] for k in sorted(d)]
                return d
            return o
        lua.globals().json=lua.table_from({'encode':enc,'decode':lambda self_,text:lua.table_from({'plaetze':lua.table_from({i+1:lua.table_from(p) for i,p in enumerate(J.loads(text)['plaetze'])})})})
        lua.globals().py_open=lambda name,mode:dateien.get(name) if mode=='r' else None
        lua.execute('''io={open=function(name,mode)
            if mode=='r' then local text=py_open(name,mode); if not text then return nil end
              return {read=function() return text end,close=function() end} end
            return {write=function(_,text) py_write(name,text) end,close=function() end} end}; log=function(_,m) end''')
        lua.globals().py_write=lambda name,text:dateien.__setitem__(name,text)
        return lua.execute((ROOT/'takeover.lua').read_text()),records

    def test_pause_restore_and_restart_and_load(self):
        AI=0x0191de7c;FULL=0x0191D768+0x6A8;TICK=0x0117cadc
        memory={0x01fe7d1c:14,0x0117d500:0,TICK:0,AI+4:5,AI+8:16,0x0115BDF8+2*0x39F4+0x2300:16,FULL+8:0}
        dateien={}
        api,rec=self.lauf(memory,dateien)
        api.tick()
        self.assertEqual((memory[AI+8],memory[FULL+8]),(0,1))
        self.assertIn('ucp/villagestudio/samurai_plaetze.json',dateien)
        # Pause: die Wache stellt KI 16 zurueck -> vor dem naechsten Takt wieder aus und lebend
        memory[TICK]=500;api.tick();memory[AI+8]=16;memory[FULL+8]=0;api.tick()
        self.assertEqual((memory[AI+8],memory[FULL+8]),(0,1))
        n=len(rec)
        # Neustart: Takt springt zurueck -> neuer Eintrag mit hoeherer Folge
        memory[TICK]=3;memory[AI+8]=16;api.tick()
        self.assertEqual((memory[AI+8],memory[FULL+8]),(0,1))
        self.assertEqual(len(rec),n+1);self.assertTrue(rec[-1]['active']);self.assertGreater(rec[-1]['sequence'],rec[n-1]['sequence'])
        # Laden in einem NEUEN Spielprozess: Spielstand mit KI 0 auf Platz 2, Takt 19815 -> Platz aus der Datei wieder uebernommen
        m2={0x01fe7d1c:14,0x0117d500:0,TICK:19815,AI+4:5,AI+8:0,FULL+8:0}
        api2,rec2=self.lauf(m2,dict(dateien))
        api2.tick()
        self.assertEqual((m2[AI+8],m2[FULL+8]),(0,1))
        self.assertTrue(rec2[-1]['active']);self.assertEqual(rec2[-1]['slots'],[2]);self.assertEqual(rec2[-1]['original_ai']['2'],16)
        # alter Spielstand (vor B-280): Datei nur mit KI-Nummer, ohne Typ/Mensch -> Uebernahme klappt, Verlassen schreibt nur KI 16
        import json as J2
        m4={0x01fe7d1c:14,0x0117d500:0,TICK:19815,AI+4:5,AI+8:0,FULL+8:0}
        api4,rec4=self.lauf(m4,{'ucp/villagestudio/samurai_plaetze.json':J2.dumps({'plaetze':[{'sp':2,'ai':16}]})})
        api4.tick()
        self.assertEqual((m4[AI+8],m4[FULL+8]),(0,1));self.assertEqual(rec4[-1]['slots'],[2])
        m4[0x01fe7d1c]=20;api4.tick()
        self.assertEqual((m4[AI+8],m4[FULL+8]),(16,1))
        # neue Partie aus dem Menue bei Takt 0 mit KI 0 auf Platz 2 (z. B. ein Mensch) -> NICHT uebernehmen
        m3={0x01fe7d1c:14,0x0117d500:0,TICK:0,AI+4:5,AI+8:0,FULL+8:0}
        api3,rec3=self.lauf(m3,dict(dateien))
        api3.tick()
        self.assertEqual(m3[FULL+8],0);self.assertFalse(rec3[-1]['active'])

if __name__=='__main__':unittest.main()
