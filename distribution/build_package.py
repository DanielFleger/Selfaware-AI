"""Build the external local runtime; never ship local logs/screenshots/configs."""
import email
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.package-cache'
BUILD = ROOT / 'build'
PYTHON_URL = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip'
PYTHON_SHA = '009d6bf7e3b2ddca3d784fa09f90fe54336d5b60f0e0f305c37f400bf83cfd3b'
SEEDS = ('enums_einheit_gebaeude.txt', 'enum_einheiten.txt', 'gebaeude_arbeit.json', 'gebaeude_schadensregel.json',
         'lord_kampfwerte.json', 'nahkampf_raten.json', 'saat_liga.json', 'schussrate_editor.json')


def run(args, **kw):
    subprocess.run([str(x) for x in args], check=True, **kw)


def msvc_environment():
    vswhere = Path(os.environ.get('ProgramFiles(x86)', 'C:/Program Files (x86)')) / 'Microsoft Visual Studio/Installer/vswhere.exe'
    install = subprocess.check_output([str(vswhere), '-latest', '-products', '*', '-requires',
        'Microsoft.VisualStudio.Component.VC.Tools.x86.x64', '-property', 'installationPath'], text=True).strip()
    if not install:
        raise RuntimeError('Visual C++ x86 build tools missing on build host')
    setup = Path(install) / 'VC/Auxiliary/Build/vcvars32.bat'
    return batch_environment(setup)


def batch_environment(setup):
    # cmd.exe has its own quote grammar; list2cmdline backslash-quoting is wrong
    # for paths containing spaces in a /c command.
    command='"%s" /d /s /c ""%s" >nul && set"' % (os.environ.get('COMSPEC','cmd.exe'),setup)
    output = subprocess.check_output(command, text=True, errors='replace')
    env = {k.upper():v for k,v in os.environ.items()}
    env.update((k.upper(),v) for k,v in (line.split('=',1) for line in output.splitlines() if '=' in line and not line.startswith('=')))
    return env


def wheel_lock():
    """Explicit developer operation, not run when a Store build installs deps."""
    entries = []
    for wheel in sorted((CACHE / 'wheels').glob('*.whl')):
        with zipfile.ZipFile(wheel) as z:
            info = email.message_from_bytes(z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))))
        entries.append('%s==%s --hash=sha256:%s' % (info['Name'], info['Version'], hashlib.sha256(wheel.read_bytes()).hexdigest()))
    if not entries:
        raise RuntimeError('No downloaded wheels')
    (ROOT / 'distribution/requirements-lock.txt').write_text('\n'.join(entries) + '\n', encoding='utf-8')


def build(resume=False):
    CACHE.mkdir(exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    runtime = BUILD / 'runtime'
    if runtime.exists() and not resume:
        raise RuntimeError('build/runtime already exists; use a fresh build directory to preserve the previous result')
    if not resume:
        runtime.mkdir()
    archive = CACHE / 'python-3.11.9-embed-amd64.zip'
    if not archive.exists():
        urllib.request.urlretrieve(PYTHON_URL, archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != PYTHON_SHA:
        raise ValueError('Python runtime checksum mismatch')
    python = runtime / 'python'
    python.mkdir(exist_ok=resume)
    with zipfile.ZipFile(archive) as z:
        z.extractall(python)
    (python / 'python311._pth').write_text('python311.zip\n.\nLib/site-packages\n../Selfaware-AI/werkzeug\nimport site\n', encoding='utf-8')
    args = [sys.executable, '-m', 'pip', 'install', '--require-hashes', '--only-binary=:all:',
            '--platform', 'win_amd64', '--implementation', 'cp', '--python-version', '3.11', '--abi', 'cp311',
            '--target', python / 'Lib/site-packages', '-r', ROOT / 'distribution/requirements-lock.txt']
    if (CACHE / 'wheels').exists():
        args += ['--no-index', '--find-links', CACHE / 'wheels']
    if not resume:
        run(args)
    code = runtime / 'Selfaware-AI/werkzeug'
    data = runtime / 'Selfaware-AI/daten'
    code.mkdir(parents=True,exist_ok=resume)
    data.mkdir(exist_ok=resume)
    for source in sorted((ROOT / 'werkzeug').glob('*.py')):
        shutil.copy2(source, code / source.name)
    shutil.copy2(ROOT / 'werkzeug/logik_menue_backend.lua', code / 'logik_menue_backend.lua')
    for name in SEEDS:
        source = ROOT / 'daten' / name
        if source.is_file():
            shutil.copy2(source, data / name)
    # Preserve the catalog layout the existing controller already consumes.
    catalog = runtime / 'VillageStudio/lib'
    catalog.mkdir(parents=True,exist_ok=resume)
    shutil.copy2(ROOT / 'distribution/catalog/gebaeude.json', catalog / 'gebaeude.json')
    shutil.copy2(ROOT / 'distribution/catalog/LICENSE', catalog / 'LICENSE')
    if (ROOT/'LICENSE').is_file():shutil.copy2(ROOT/'LICENSE',runtime/'Selfaware-AI/LICENSE')
    helpers = runtime / 'VillageStudio/werkzeug'
    helpers.mkdir(exist_ok=resume)
    shutil.copy2(ROOT / 'distribution/instanz.py', helpers / 'instanz.py')
    # Compile exactly the kernel already deployed in the development instance.
    cargo = shutil.which('cargo') or str(Path.home() / '.cargo/bin/cargo.exe')
    rustup = shutil.which('rustup') or str(Path.home() / '.cargo/bin/rustup.exe')
    # Local development uses GNU; the official Windows build host has MSVC.
    target = os.environ.get('SAI_RUST_TARGET', 'i686-pc-windows-msvc')
    env = msvc_environment() if target.endswith('msvc') else dict(os.environ)
    run([rustup, 'target', 'add', target],env=env)
    for name, crate in [('samurai_kern','kernel')]:
        run([cargo, 'build', '--locked', '--release', '--target', target,
             '--manifest-path', ROOT / ('distribution/%s/Cargo.toml'%crate), '--target-dir', BUILD / 'native-target'],env=env)
        shutil.copy2(BUILD / ('native-target/%s/release/%s.dll'%(target,name)), BUILD / (name+'.dll'))
    logic = (ROOT / 'werkzeug/logik_menue_backend.lua').read_text(encoding='utf-8')
    logic = logic.replace('ucp/modules/villagestudio-0.1.0/', 'ucp/modules/selfaware-runtime-0.1.0/')
    # Release uses its bundled kernel, never a development hot-reload descriptor.
    logic = logic.replace('local fa = io.open("ucp/villagestudio/kern_aktuell.txt", "r")', 'local fa = nil')
    if 'io.open("ucp/villagestudio/kern_aktuell.txt"' in logic:
        raise ValueError('Development kernel descriptor still active in release logic')
    (BUILD / 'logik.lua').write_text(logic, encoding='utf-8')
    manifest = {str(p.relative_to(runtime)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(runtime.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    (runtime / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    with zipfile.ZipFile(BUILD / 'runtime.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(runtime.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                z.write(p, p.relative_to(runtime))
    print('Runtime built:', BUILD / 'runtime.zip')


if __name__ == '__main__':
    wheel_lock() if '--lock-wheels' in sys.argv else build('--resume' in sys.argv)
