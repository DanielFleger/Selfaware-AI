"""64-bit controller <-> actual 32-bit Rust peer, including failure cases."""
import ctypes
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from speicherkanal import Channel,REQUEST_CAP,records

ROOT=Path(__file__).resolve().parents[1]
PEER=Path(os.environ.get('SAI_IPC_PEER',ROOT/'build/store-native/i686-pc-windows-gnu/release/ipc_probe.exe'))


class MemoryChannel(unittest.TestCase):
    def start(self):
        process=subprocess.Popen([str(PEER)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        def cleanup():
            if process.poll() is None:process.terminate()
            process.wait(timeout=5)
        self.addCleanup(cleanup)
        self.addCleanup(process.stdout.close);self.addCleanup(process.stderr.close)
        pid=int(process.stdout.readline().strip());self.assertEqual(pid,process.pid)
        return process

    def test_binary_exchange_and_no_overwrite_before_reply_is_consumed(self):
        process=self.start()
        with Channel(process.pid) as c:
            payload=bytes(range(256))*31
            seq,data,error=c.transact(payload)
            self.assertEqual((data,error),(payload,0))
            with self.assertRaisesRegex(RuntimeError,'unresolved'):c.transact(b'cannot overwrite')
            c.consume(seq)
            for _ in range(100):
                seq,data,error=c.transact(b'next');self.assertEqual(data,b'next');c.consume(seq)
            seq,data,error=c.transact(b'stop');c.consume(seq)
            self.assertEqual(process.wait(timeout=5),0)

    def test_missing_peer_is_not_silently_created_and_request_bounds_hold(self):
        with self.assertRaises(RuntimeError):Channel(os.getpid())
        process=self.start()
        with Channel(process.pid) as c:
            with self.assertRaises(ValueError):c.transact(b'x'*REQUEST_CAP)
            self.assertEqual(c.u32(16),0)

    def test_game_death_fails_fast_and_never_retries(self):
        process=self.start()
        with Channel(process.pid) as c:
            process.terminate();process.wait(timeout=5)
            with self.assertRaisesRegex(RuntimeError,'no longer available'):c.transact(b'closed')
            self.assertEqual(c.u32(16),0)

    def test_snapshot_namespace_and_binary_framing(self):
        def record(kind,key,data):
            key=key.encode();return struct.pack('<BII',kind,len(key),len(data))+key+data
        data=record(2,'ucp/villagestudio/abzug/lagebild.txt',b'\0\xffdata')
        self.assertEqual(records(data),[(2,'abzug/lagebild.txt',b'\0\xffdata')])
        for key in ('C:/outside.txt','ucp/villagestudio/../outside','ucp/villagestudio//bad'):
            with self.assertRaises(ValueError):records(record(2,key,b'data'))
        with self.assertRaises(ValueError):records(data[:-1])


if __name__=='__main__':unittest.main()
