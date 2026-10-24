"""Exercise real Lua against a native-table sentinel, including a rejected config."""
from pathlib import Path
import unittest
from lupa import LuaRuntime

ROOT=Path(__file__).resolve().parents[1]

class Starttruppen(unittest.TestCase):
    def run_lua(self,config):
        lua=LuaRuntime(unpack_returned_tuples=True)
        memory={}; writes=[]
        lua.globals().core=lua.table_from({
            'AOBScan':lambda pattern,begin:0x400100,
            'readInteger':lambda p:0x1000000-0x140,
            'writeInteger':lambda p,v:(memory.__setitem__(p,v),writes.append(p))[-1]})
        lua.globals().log=lambda *args:None
        api=lua.execute((ROOT/'starttroops.lua').read_text(encoding='utf-8'))
        return api,lua,memory,writes

    def test_native_defaults_and_neighbouring_lords(self):
        api,lua,memory,writes=self.run_lua({})
        api.configure(lua.table())
        self.assertEqual(len(writes),60)
        for mode in range(3):
            base=0x1000000+(15*60+mode*20)*4
            self.assertEqual(memory[base+13*4],4)
            self.assertEqual(memory[base+10*4],6)
            self.assertEqual(memory[base+9*4],0) # no inherited monks
            self.assertEqual(sum(memory[base+i*4] for i in range(20)),10)
        self.assertTrue(all(0x1000000+15*240<=p<0x1000000+16*240 for p in writes))

    def test_custom_counts_include_explicit_zero(self):
        api,lua,memory,writes=self.run_lua({})
        api.configure(lua.table_from({'startTroops':lua.table_from({'Assassin':0,'ArabArcher':0,'Spearman':8})}))
        base=0x1000000+15*240
        self.assertEqual(memory[base+13*4],0)
        self.assertEqual(memory[base+2*4],8)
        self.assertEqual(sum(memory[base+i*4] for i in range(20)),8)

    def test_invalid_config_does_not_partially_write(self):
        for bad in ({'Assassin':-1},{'Assassin':1.5},{'Assassin':100,'ArabArcher':100},{'Unknown':1}):
            api,lua,memory,writes=self.run_lua({})
            with self.assertRaises(Exception):api.configure(lua.table_from({'startTroops':lua.table_from(bad)}))
            self.assertEqual(writes,[])

if __name__=='__main__':unittest.main()
