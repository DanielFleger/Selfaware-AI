"""Local, resumable Ghidra evidence pipeline. No game actions or network calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import struct
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(os.environ.get('SHC_KNOWLEDGE_ROOT', str(Path(__file__).resolve().parent))).resolve()
WORK = ROOT.parent
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz5')
GHIDRA = Path(r'C:\Users\danie\ghidra\ghidra_12.1.2_PUBLIC')

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)

def pe(path):
    data = path.read_bytes()
    if data[:2] != b'MZ':
        raise ValueError('not MZ')
    off = struct.unpack_from('<I', data, 0x3c)[0]
    if data[off:off+4] != b'PE\0\0':
        raise ValueError('not PE')
    machine, count, stamp = struct.unpack_from('<HHI', data, off+4)
    size = struct.unpack_from('<H', data, off+20)[0]
    opt = off+24
    magic = struct.unpack_from('<H', data, opt)[0]
    if magic not in (0x10b,0x20b): raise ValueError('unsupported PE optional header')
    base = struct.unpack_from('<I' if magic == 0x10b else '<Q', data, opt+(28 if magic == 0x10b else 24))[0]
    sections = []
    for i in range(count):
        s = opt+size+i*40
        vs, va, rs, rp = struct.unpack_from('<IIII', data, s+8)
        flags = struct.unpack_from('<I', data, s+36)[0]
        sections.append(dict(name=data[s:s+8].split(b'\0')[0].decode('ascii', 'replace'), virtual_size=vs, rva=va, raw_size=rs, raw_pointer=rp, flags=flags))
    return dict(machine=hex(machine), bits=32 if magic == 0x10b else 64, image_base=base, pe_timestamp=stamp, sections=sections)

def inventory():
    started = time.monotonic()
    paths = set()
    for name in ['sai-live', 'Selfaware-AI-kern', 'VillageStudio', 'sai-context']:
        for p in (WORK/name).rglob('*'):
            if p.is_file() and not any(x in p.parts for x in ['.git', '.venv', '__pycache__', 'target', 'node_modules']):
                paths.add(p)
    for p in GAME.rglob('*'):
        if p.is_file() and (p.suffix.lower() in ['.exe', '.dll', '.lua', '.yml', '.yaml', '.zip'] or p.name=='kern_aktuell.txt'):
            paths.add(p)
    paths.add(Path(r'C:\Users\danie\shc-ref\StrongholdCrusader.exe'))
    records = []
    for p in sorted(paths):
        before = p.stat()
        r = dict(path=str(p), size=before.st_size, sha256=digest(p))
        r['stable_during_read'] = before.st_mtime_ns == p.stat().st_mtime_ns
        if p.suffix.lower() in ['.exe', '.dll']:
            try: r['pe'] = pe(p)
            except (ValueError, struct.error) as e: r['pe_error'] = str(e)
        records.append(r)
    repos = []
    for name in ['sai-live', 'Selfaware-AI-kern']:
        def git(*args):
            return subprocess.run(['git', '-C', str(WORK/name), *args], capture_output=True, text=True).stdout.strip()
        repos.append(dict(path=str(WORK/name), commit=git('rev-parse', 'HEAD'), branch=git('branch', '--show-current'), status=git('status', '--porcelain'), remotes=git('remote', '-v')))
    save(ROOT/'evidence/inventory.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), command='python pipeline.py inventory', elapsed_seconds=time.monotonic()-started, scope='All non-build/non-git files in four requested work folders; all EXE/DLL/Lua/YAML in instance 5. File hashes do not prove loaded memory identity.', files=records, repositories=repos))
    print(json.dumps(dict(files=len(records), elapsed_seconds=time.monotonic()-started)))

def export(limit):
    env = os.environ.copy()
    env.update(APPDATA=str(ROOT/'settings'), LOCALAPPDATA=str(ROOT/'settings'), JAVA_HOME=r'C:\Program Files\Eclipse Adoptium\jdk-21.0.12.8-hotspot')
    # Annotation changes anywhere in the project conservatively invalidate the export.
    h = hashlib.sha256()
    for p in sorted((ROOT/'projects/OpenSHC-ref.rep').rglob('*')):
        if p.is_file() and p.suffix not in ['.lock']:
            h.update(str(p.relative_to(ROOT)).encode()); h.update(digest(p).encode())
    h.update(digest(ROOT/'scripts/KnowledgeExport.java').encode())
    revision = h.hexdigest()
    cmd = [str(GHIDRA/'support/analyzeHeadless.bat'), str(ROOT/'projects'), 'OpenSHC-ref', '-process', '-readOnly', '-noanalysis', '-scriptPath', str(ROOT/'scripts'), '-postScript', 'KnowledgeExport.java', str(ROOT/'exports/reference'), str(limit), revision, '-log', str(ROOT/'evidence/ghidra.log')]
    started = time.monotonic()
    with (ROOT/'evidence/export-console.log').open('w', encoding='utf-8') as out:
        result = subprocess.run(cmd, env=env, stdout=out, stderr=subprocess.STDOUT)
    text = (ROOT/'evidence/export-console.log').read_text(encoding='utf-8')
    success = result.returncode == 0 and 'KNOWLEDGE_EXPORT_DONE' in text
    save(ROOT/'evidence/export-run.json', dict(command=cmd, elapsed_seconds=time.monotonic()-started, returncode=result.returncode, success=success))
    print(json.dumps(dict(success=success, elapsed_seconds=time.monotonic()-started)))
    if not success: raise SystemExit('Ghidra export failed: see evidence/export-console.log')

def mapped_bytes(data, header, address, size):
    rva = address-header['image_base']
    for s in header['sections']:
        delta = rva-s['rva']
        if 0 <= delta and delta+size <= s['raw_size']:
            start = s['raw_pointer']+delta
            result = data[start:start+size]
            if len(result) != size: raise ValueError('truncated PE section')
            return result
    raise ValueError('range not backed by file bytes')

def validate_function(f):
    raw=b''.join(bytes.fromhex(r['hex']) for r in f['raw'])
    if len(raw)!=f['size'] or hashlib.sha256(raw).hexdigest()!=f['sha256']:
        raise ValueError('corrupt function bytes: '+f['address'])
    for i in f['assembly']:
        address=int(i['address'],16);code=bytes.fromhex(i['bytes'])
        if not any(0<=address-int(r['start'],16) and bytes.fromhex(r['hex'])[address-int(r['start'],16):address-int(r['start'],16)+len(code)]==code for r in f['raw']):
            raise ValueError('assembly bytes outside body: '+i['address'])

def rule_status(rule,function_sha,reference_sha):
    if function_sha!=rule['function_sha256'] or reference_sha!=rule['reference_sha256']:return 'stale'
    for dep in rule.get('evidence_files',[]):
        path=ROOT/dep['path']
        if not path.exists() or digest(path)!=dep['sha256']:return 'stale'
    return rule['status']

def index():
    started = time.monotonic()
    folder = ROOT/'exports/reference'
    program = json.loads((folder/'program.json').read_text())
    live = GAME/'Stronghold Crusader.exe'
    binary, header = live.read_bytes(), pe(live)
    db = sqlite3.connect(ROOT/'knowledge.sqlite')
    db.executescript('''
      CREATE TABLE IF NOT EXISTS functions(address TEXT PRIMARY KEY,name TEXT,size INTEGER,sha256 TEXT,decompiled INTEGER,byte_mapping TEXT,path TEXT,pseudocode TEXT);
      CREATE TABLE IF NOT EXISTS refs(owner TEXT,source TEXT,target TEXT,kind TEXT);
      CREATE TABLE IF NOT EXISTS rules(id TEXT PRIMARY KEY,status TEXT,record TEXT);
      CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(address,name,pseudocode);
      DELETE FROM functions; DELETE FROM refs; DELETE FROM search; DELETE FROM rules;
    ''')
    counts = dict(captured=0, disassembled=0, decompiled=0, semantic_examined=0, counterexample_confirmed=0, same_address_identical_bytes=0, different_bytes=0, indirect_instructions=0)
    failures=[]
    for path in sorted((folder/'functions').glob('*.json')):
        f = json.loads(path.read_text(encoding='utf-8'))
        if f['identity'] != program['identity']: continue
        validate_function(f)
        counts['captured']+=1
        counts['disassembled']+=bool(f['assembly'])
        counts['decompiled']+=bool(f['decompiled'])
        counts['indirect_instructions']+=sum(bool(i['indirect']) for i in f['assembly'])
        try:
            same = all(mapped_bytes(binary, header, int(r['start'],16),len(bytes.fromhex(r['hex']))) == bytes.fromhex(r['hex']) for r in f['raw'])
            mapping = 'same_address_identical_bytes' if same else 'different_bytes'
            counts[mapping]+=1
        except ValueError: mapping='unmapped'
        if not f['decompiled']:failures.append(dict(address=f['address'],error=f['error']))
        db.execute('INSERT INTO functions VALUES(?,?,?,?,?,?,?,?)',(f['address'],f['name'],f['size'],f['sha256'],f['decompiled'],mapping,str(path),f.get('pseudocode')))
        db.execute('INSERT INTO search VALUES(?,?,?)',(f['address'],f['name'],f.get('pseudocode') or ''))
        db.executemany('INSERT INTO refs VALUES(?,?,?,?)',[(f['address'],r['from'],r['to'],r['kind']) for r in f['references']])
    rule_path=ROOT/'rules.json'
    if rule_path.exists():
        for rule in json.loads(rule_path.read_text(encoding='utf-8')):
            found=db.execute('SELECT sha256 FROM functions WHERE address=?',(rule['address'],)).fetchone()
            status=rule_status(rule,found[0] if found else None,program['sha256'])
            db.execute('INSERT INTO rules VALUES(?,?,?)',(rule['id'],status,json.dumps(rule,ensure_ascii=False)))
            if status!='stale':
                counts['semantic_examined']+=1
                counts['counterexample_confirmed']+=status=='confirmed'
    db.commit(); db.close()
    report = dict(command='python pipeline.py index',program=program,instance_file_sha256=digest(live),counts=counts,recognized_function_count=program['function_count'],internal_function_count=len(json.loads((folder/'index.json').read_text())),unassigned_executable=json.loads((folder/'unassigned-executable.json').read_text()),decompilation_failures=failures,elapsed_seconds=time.monotonic()-started,export_bytes=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file()),limits=['Byte match is static only; callees, global data and in-process patches still require validation.','Instruction classification and boundaries are Ghidra analysis, not ground truth.','Semantic counts are scoped by rules.json, not proof of whole-function gameplay behavior.','Original comparison uses the isolated leaf routine with a fresh paused game snapshot, not tactical outcomes.'])
    save(ROOT/'evidence/coverage.json',report)
    print(json.dumps(counts))

def query(term):
    db=sqlite3.connect(f'file:{(ROOT/"knowledge.sqlite").as_posix()}?mode=ro',uri=True)
    rows=db.execute('SELECT address,name,size,decompiled,byte_mapping,path FROM functions WHERE name LIKE ? OR address=? LIMIT 30',('%'+term+'%',term)).fetchall()
    print(json.dumps(rows,ensure_ascii=False,indent=2))

def rule_query(term):
    db=sqlite3.connect(f'file:{(ROOT/"knowledge.sqlite").as_posix()}?mode=ro',uri=True)
    rows=db.execute('SELECT id,status,record FROM rules WHERE id=? OR record LIKE ?',(term,'%'+term+'%')).fetchall()
    print(json.dumps([dict(id=r[0],effective_status=r[1],rule=json.loads(r[2])) for r in rows],ensure_ascii=False,indent=2))

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['inventory','export','index','query','rule']);p.add_argument('value',nargs='?',default='0');a=p.parse_args()
    if a.command=='inventory':inventory()
    elif a.command=='export':export(int(a.value))
    elif a.command=='index':index()
    elif a.command=='rule':rule_query(a.value)
    else:query(a.value)
