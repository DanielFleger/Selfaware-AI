"""Nur explizite Belege eines eigenen Laufs sichern; niemals einen ganzen Ordner stagen."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True, encoding='utf-8').strip()


def sichern(stamp, push=False, modelle=False):
    if not re.fullmatch(r'\d{8}_\d{6}', stamp):
        raise ValueError('Ungueltiger Laufstempel')
    manifest_path = ROOT/'daten'/('branching_'+stamp+'.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest['status'] == 'running':
        raise ValueError('Lauf arbeitet noch')
    files = set((ROOT/'daten').glob('branching_'+stamp+'*'))
    files.update((ROOT/'daten/benchmarks').glob('branching_'+stamp+'*'))
    for console in manifest['consoles']:
        path = (ROOT/console).resolve()
        if not path.is_relative_to(ROOT/'daten'):
            raise ValueError('Mitschrift ausserhalb der Laufdaten')
        text = path.read_text(encoding='utf-8')
        names = re.findall(r'(?:lage|ertrag_live|ertrag_gelernt|vergleich|angriff_live)_[0-9_]+i\d+(?:_sp\d+)?\.(?:jsonl\.gz|jsonl|json)', text)
        for name in names:
            files.add(ROOT/'daten'/name)
            if name.startswith('vergleich_'):
                files.add(ROOT/'daten'/name.replace('vergleich_', 'ertrag_gelernt_', 1))
            if name.startswith('lage_'):
                suffix = name.removeprefix('lage_').removesuffix('.jsonl.gz')
                files.add(ROOT/'daten'/('angriff_live_'+suffix+'.jsonl'))
    if modelle:
        files.update(ROOT/'daten'/n for n in ('verlust_raten.json', 'wissen_ablauf.jsonl'))
    files = {p.resolve() for p in files if p.is_file()}
    if any(not p.is_relative_to(ROOT/'daten') for p in files):
        raise ValueError('Beleg ausserhalb des Datenordners')
    large = {p for p in files if p.stat().st_size >= 50_000_000}
    files -= large
    manifest['archive'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(files) if p != manifest_path}
    manifest['large_local_artifacts'] = [str(p.relative_to(ROOT)) for p in sorted(large)]
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    paths = sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in files)
    staged = set(git('diff','--cached','--name-only').splitlines())
    if staged - set(paths):
        raise RuntimeError('Andere vorgemerkte Aenderungen zuerst getrennt sichern')
    git('add','--',*paths)
    if git('diff','--cached','--name-only'):
        print(git('commit','-m','Preserve match evidence '+stamp))
    if push:
        if git('branch','--show-current') != 'codex/branching-fortunes':
            raise RuntimeError('Nicht der freigegebene Veroeffentlichungszweig')
        if git('remote','get-url','github') != 'https://github.com/UnofficialCrusaderPatch/Selfaware-AI.git':
            raise RuntimeError('Nicht das freigegebene Ziel')
        print(git('push','github','HEAD:refs/heads/codex/branching-fortunes'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stamp')
    parser.add_argument('--push', action='store_true')
    parser.add_argument('--modelle', action='store_true')
    args = parser.parse_args()
    sichern(args.stamp, args.push, args.modelle)
