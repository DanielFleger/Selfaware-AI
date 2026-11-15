"""Prepare an explicit, small source/evidence allowlist for the existing repo.
Never copies the executable, Ghidra database, full exports or captured machine code.
"""
import gzip
import json
import shutil
from pathlib import Path
from pipeline import ROOT, WORK, save, digest

repo=WORK/'sai-live'
source=repo/'werkzeug/engine_knowledge'
evidence=repo/'daten/engine_knowledge_20261023'
source.mkdir(exist_ok=True);evidence.mkdir(exist_ok=True)
files=[]
for name in ['pipeline.py','live_probe.py','record_findings.py','test_pipeline.py','archive_evidence.py','verify.ps1','WEITER.txt']:
    target=source/name;shutil.copy2(ROOT/name,target);files.append(target)
for item in sorted((ROOT/'scripts').glob('*')):
    if item.suffix not in ['.java','.rs']:continue
    target=source/'scripts'/item.name;target.parent.mkdir(exist_ok=True);shutil.copy2(item,target);files.append(target)
live=Path((ROOT/'evidence/latest-live.txt').read_text())
for name in ['console.txt','state.json','lagebild.txt','gebaeude.txt']:
    target=evidence/name;shutil.copy2(live/name,target);files.append(target)
for name in ['viewport-comparison.json','rea-check.json','pipeline-tests.txt','export-run.json','native-negative-test.json','project-preservation.json','annotation-test.log']:
    target=evidence/name;shutil.copy2(ROOT/'evidence'/name,target);files.append(target)
for name in ['rules.json','remaining.json','annotations.json']:
    target=evidence/name;shutil.copy2(ROOT/name,target);files.append(target)
coverage=json.loads((ROOT/'evidence/coverage.json').read_text())
coverage['unassigned_executable']={k:v for k,v in coverage['unassigned_executable'].items() if k!='ranges'}
target=evidence/'coverage-summary.json';save(target,coverage);files.append(target)
inventory=json.loads((ROOT/'evidence/inventory.json').read_text())
environment=dict(captured_on=inventory['timestamp'],game_files=[dict(name=Path(f['path']).name,sha256=f['sha256'],size=f['size'],pe=f.get('pe')) for f in inventory['files'] if 'Instanz5' in f['path']],random_seed='not set or identified; snapshot comparison only',training_eligible=False,reason='Fresh paused measurement, not a completed policy match')
target=evidence/'environment.json';save(target,environment);files.append(target)
target=evidence/'observation.jsonl.gz'
with gzip.open(target,'wt',encoding='utf-8') as out:
    out.write(json.dumps(dict(schema='engine-knowledge-observation-v1',tick=8,units=(live/'lagebild.txt').read_text(),buildings=(live/'gebaeude.txt').read_text(),state=json.loads((live/'state.json').read_text())))+'\n')
files.append(target)
target=evidence/'artifact-hashes.json';save(target,[dict(path=str(f.relative_to(repo)),sha256=digest(f)) for f in files]);files.append(target)
save(ROOT/'evidence/git-allowlist.json',[str(f.relative_to(repo)) for f in files])
print(f'{len(files)} explicit source/evidence files prepared; no full binary or program export included.')
