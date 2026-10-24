"""Whole-command counterexamples at the new IO boundary, without a game."""
import json
import struct
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import befehl as kanal


def frame(kind,key,data):
    key=key.encode();return struct.pack('<BII',kind,len(key),len(data))+key+data


class Peer:
    def __init__(self,replies):self.replies=iter(replies);self.requests=[];self.consumed=[]
    def transact(self,payload,timeout):
        self.requests.append(json.loads(payload));return len(self.requests),next(self.replies),0
    def consume(self,sequence):self.consumed.append(sequence)


class MemoryCommands(unittest.TestCase):
    def test_memory_and_framework_logs_preserve_semantic_pipe_separators(self):
        body='[selfaware-runtime]: ZEIT: Tick 75 | Tag 25/50 | Woche 0/200'
        expected=['[villagestudio]: ZEIT: Tick 75 | Tag 25/50 | Woche 0/200']
        self.assertEqual(kanal.logzeilen(body),expected)
        self.assertEqual(kanal.logzeilen('logging.cpp:102 INFO| '+body),expected)

    def test_delayed_effect_is_polled_without_repeating_action(self):
        reply=frame(1,'',b'[selfaware-runtime]: QUITTUNG 123\n')
        snapshot=frame(2,'ucp/villagestudio/abzug/lagebild.txt',b'\0\xffactual snapshot')
        effect=frame(1,'',b'[selfaware-runtime]: GEBAUT\n')
        peer=Peer([reply,snapshot+effect])
        with tempfile.TemporaryDirectory() as t,patch.multiple(kanal,KANAL_ORDNER=t,PARTNER=False),patch.object(kanal,'memory_channel',return_value=peer):
            result=kanal._send_memory({'id':123,'befehle':[{'bauen':True}]},.2,'GEBAUT')
            self.assertTrue(any('GEBAUT' in z for z in result))
            self.assertEqual(peer.requests,[{'id':123,'befehle':[{'bauen':True}]},{'poll':True}])
            self.assertEqual(peer.consumed,[1,2])
            self.assertEqual((Path(t)/'abzug/lagebild.txt').read_bytes(),b'\0\xffactual snapshot')

    def test_longer_id_cannot_acknowledge_our_command(self):
        peer=Peer([frame(1,'',b'[selfaware-runtime]: QUITTUNG 1239 GEBAUT\n')])
        with tempfile.TemporaryDirectory() as t,patch.multiple(kanal,KANAL_ORDNER=t,PARTNER=False),patch.object(kanal,'memory_channel',return_value=peer):
            with self.assertRaises(TimeoutError):kanal._send_memory({'id':123},0,'GEBAUT')
        self.assertEqual(len(peer.requests),1)

    def test_invalid_late_record_prevents_all_snapshot_writes(self):
        first=frame(2,'ucp/villagestudio/abzug/lagebild.txt',b'not published')
        bad=frame(2,'ucp/villagestudio/../escape',b'bad')
        peer=Peer([first+bad])
        with tempfile.TemporaryDirectory() as t,patch.object(kanal,'KANAL_ORDNER',t),patch.object(kanal,'memory_channel',return_value=peer):
            with self.assertRaises(ValueError):kanal._send_memory({'id':123},.2,None)
            self.assertEqual(list(Path(t).rglob('*')),[])
            self.assertEqual(peer.consumed,[],'Do not consume a corrupt response as successful')


if __name__=='__main__':unittest.main()
