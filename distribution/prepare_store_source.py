"""Prepare a self-contained, inspectable Store source tree, without external runtime.

Generated copies carry source hashes and are checked against canonical sources.
Only the IO boundary/module root is adapted; tactical algorithms remain shared.
"""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'store-module'


def text_bytes(data):
    """Git's Windows checkout may convert LF to CRLF; source semantics do not."""
    return data.replace(b'\r\n',b'\n')


def files():
    result={}
    for name in ('starttroops.lua','command_owner.lua','engine_contract.lua','options.yml'):
        result[name]=(ROOT/name).read_bytes()
    result['options.yml']=result['options.yml'].replace(b'selfaware-runtime.',b'selfaware-bridge.')
    source=(ROOT/'werkzeug/logik_menue_backend.lua').read_text(encoding='utf-8')
    assert source.count('local VS = ...')==1
    source=source.replace('local VS = ...','local log=VS.log\nlocal storage=VS.storage',1)
    source=source.replace('io.open(', 'storage.open(')
    literal='local KERN_ORDNER = "ucp/modules/villagestudio-0.1.0/"'
    assert source.count(literal)==1
    source=source.replace(literal,'local KERN_ORDNER = VS.moduleRoot',1)
    # Reuse the exact proxied DLL instance that owns the memory endpoint.
    loader='local h = core.openLibraryHandle(pfad)'
    assert source.count(loader)==1
    source=source.replace(loader,'local h = VS.nativeHandle',1)
    result['game_logic.lua']=('-- Generated from werkzeug/logik_menue_backend.lua; see source-manifest.json.\nreturn function(VS)\n'+source+'\nend\n').encode()
    takeover=(ROOT/'takeover.lua').read_text(encoding='utf-8')
    writer="local PATH='ucp/villagestudio/uebernahme.json'\nlocal function save(value)\n  local f=assert(io.open(PATH,'w'))\n  f:write(json:encode(value));f:close()\nend\n"
    assert takeover.count(writer)==1
    takeover=takeover.replace(writer,'',1)
    result['takeover.lua']=('-- Shared takeover semantics, injected volatile status writer.\nreturn function(save)\n'+takeover+'\nend\n').encode()
    cargo=(ROOT/'distribution/kernel/Cargo.toml').read_text(encoding='utf-8')
    cargo=cargo.replace('[features]\n','[features]\ndefault = ["store-bridge"]\n')
    cargo=cargo.replace('crate-type = [','path = "native/lib.rs"\ncrate-type = [',1)
    cargo=cargo.replace('path = "src/ipc_probe.rs"','path = "native/ipc_probe.rs"')
    result['Cargo.toml']=cargo.encode()
    result['Cargo.lock']=(ROOT/'distribution/kernel/Cargo.lock').read_bytes()
    for p in sorted((ROOT/'distribution/kernel/src').glob('*.rs')):result['native/'+p.name]=p.read_bytes()
    origins=[ROOT/'werkzeug/logik_menue_backend.lua',ROOT/'takeover.lua']
    origins.extend(ROOT/name for name in ('starttroops.lua','command_owner.lua','engine_contract.lua','options.yml'))
    origins.extend(sorted((ROOT/'distribution/kernel/src').glob('*.rs')))
    result['source-manifest.json']=json.dumps({
        'generator':'distribution/prepare_store_source.py',
        'canonical_sources':{p.relative_to(ROOT).as_posix():hashlib.sha256(text_bytes(p.read_bytes())).hexdigest() for p in origins},
        'hash_normalization':'CRLF to LF for canonical text sources',
        'changes':'Dependency-injected volatile streams/module root and status writer; Store kernel feature removes filesystem output',
        'not_store_approval':True},indent=2).encode()
    return {name:text_bytes(data) for name,data in result.items()}


def prepare(check=False):
    for name,data in files().items():
        target=DEST/name
        if check:
            assert target.is_file() and text_bytes(target.read_bytes())==data,'Stale generated Store source: '+name
        else:
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Pure-data Store entry; the external runtime is not shipped in either UCP ZIP.
    plugin=ROOT/'store-content'
    for path in (ROOT/'Selfaware-AI').rglob('*'):
        if not path.is_file():continue
        name=path.relative_to(ROOT/'Selfaware-AI')
        target=plugin/name
        data=path.read_bytes()
        if path.suffix in ('.yml','.md'):
            text=data.decode('utf-8-sig').replace('Selfaware-AI-0.1.0/','Selfaware-AI-0.2.0/').replace('selfaware-runtime','selfaware-bridge')
            if name.as_posix()=='definition.yml':
                text=text.replace('version: 0.1.0','version: 0.2.0',1).replace('selfaware-runtime:','selfaware-bridge:')
            data=text.encode('utf-8')
        locale=name.as_posix()
        if locale in ('locale/description-de.md','locale/description-en.md'):
            language='de' if locale.endswith('-de.md') else 'en'
            data=(ROOT/('distribution/store-description-'+language+'.md')).read_bytes()
        is_text=path.suffix in ('.yml','.md','.lua','.json','.txt')
        if is_text:data=text_bytes(data)
        if check:
            assert target.is_file(),'Missing Store content: '+str(name)
            actual=target.read_bytes()
            assert (text_bytes(actual) if is_text else actual)==data,'Stale Store content: '+str(name)
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)


if __name__=='__main__':
    import sys
    prepare('--check' in sys.argv)
