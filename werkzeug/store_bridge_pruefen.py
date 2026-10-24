"""Store boundary counterexamples; no game or filesystem callback is provided."""
from pathlib import Path
import sys
import unittest
from lupa import LuaRuntime,LuaError
from speicherkanal import records

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'distribution'))
from prepare_store_source import prepare


class StoreBoundary(unittest.TestCase):
    def lua(self):
        lua=LuaRuntime(unpack_returned_tuples=True,encoding=None)
        lua.globals().package.path=(str(ROOT/'store-module').replace('\\','/')+'/?.lua;').encode()+lua.globals().package.path
        lua.globals()[b'io']=lua.table_from({b'open':lambda *a:self.fail('Native module attempted filesystem access')})
        return lua

    def test_streams_preserve_binary_payload_without_opening_files(self):
        lua=self.lua();factory=lua.execute((ROOT/'store-module/streams.lua').read_bytes())
        storage=factory(b'ucp/modules/selfaware-bridge-0.1.0/')
        sink=storage[b'open'](b'ucp/villagestudio/abzug/lagebild.txt',b'wb')
        sink[b'write'](sink,b'\0\xffbinary',123)
        sink[b'close']()
        self.assertEqual(records(storage[b'drain']()),[(2,'abzug/lagebild.txt',b'\0\xffbinary123')])
        append=storage[b'open'](b'ucp/villagestudio/spielende.txt',b'a')
        append[b'write'](append,b'outcome\n');append[b'close']()
        self.assertEqual(records(storage[b'drain']()),[(3,'spielende.txt',b'outcome\n')])

    def test_external_and_traversal_names_are_rejected_before_a_sink_exists(self):
        lua=self.lua();storage=lua.execute((ROOT/'store-module/streams.lua').read_bytes())(b'module/')
        for key in (b'outside.txt',b'C:/outside',b'ucp/villagestudio/../outside',b'ucp/villagestudio/a\0bad'):
            with self.assertRaises(LuaError):storage[b'open'](key,b'w')
        self.assertEqual(storage[b'drain'](),b'')
        self.assertIsNone(storage[b'open'](b'ucp/villagestudio/kern_aktuell.txt',b'r'))

    def test_policy_checks_nested_deferred_batches_before_execution(self):
        lua=self.lua();policy=lua.execute((ROOT/'store-module/policy.lua').read_bytes())
        policy[b'check'](lua.execute(b'return {befehle={{player=1,zeit=true},{beiTick={player=1,angriff={}}}}}'))
        for source in (b'return {foto=true}',b'return {befehle={{kette={{fenster={x=2}}}}}}',
                       b'return {kern={laden="other.dll"}}',b'return {knopf="SaveGame_Main"}'):
            with self.assertRaises(LuaError):policy[b'check'](lua.execute(source))

    def test_generated_sources_are_current_and_all_lua_is_syntactically_valid(self):
        prepare(check=True)
        lua=self.lua()
        compile_lua=lua.eval(b'function(s,n) local f,e=load(s,n);assert(f,e);return true end')
        for path in (ROOT/'store-module').glob('*.lua'):
            self.assertTrue(compile_lua(path.read_bytes(),path.name.encode()))
            self.assertNotIn(b'io.open(',path.read_bytes())


if __name__=='__main__':unittest.main()
