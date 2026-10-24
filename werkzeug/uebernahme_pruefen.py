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

if __name__=='__main__':unittest.main()
