"""Package review module and separate app; production app contains no unsigned DLL ZIP."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
from prepare_store_source import prepare

ROOT=Path(__file__).resolve().parents[1]


def package(native=None,runtime=None):
    prepare(check=True)
    output=ROOT/'build/store';output.mkdir(exist_ok=True)
    native=Path(native or ROOT/'store-module/build/samurai_kern.dll')
    runtime=Path(runtime or ROOT/'build/runtime.zip')
    assert native.is_file() and runtime.is_file(),'Build native module and external runtime first'
    notices=ROOT/'store-module/build/native-notices'
    if not notices.is_dir():
        # Local GNU review build; official MSVC builder creates the same notices.
        rustc=shutil.which('rustc') or str(Path.home()/'.cargo/bin/rustc.exe')
        rust_root=Path(subprocess.check_output([rustc,'--print','sysroot'],text=True).strip())
        notices.mkdir(parents=True)
        shutil.copy2(rust_root/'share/doc/rust/COPYRIGHT-library.html',notices/'Rust-standard-library.html')
        shutil.copytree(rust_root/'share/doc/rust/licenses',notices/'licenses')
        (notices/'toolchain.txt').write_text(subprocess.check_output([rustc,'--version'],text=True),encoding='utf-8')
    module=output/'selfaware-bridge-0.1.0.zip'
    with zipfile.ZipFile(module,'w',zipfile.ZIP_DEFLATED) as z:
        for name in ('definition.yml','init.lua','policy.lua','streams.lua','game_logic.lua','takeover.lua',
                     'command_owner.lua','engine_contract.lua','starttroops.lua','options.yml','README.md','LICENSE'):
            z.write(ROOT/'store-module'/name,name)
        z.write(native,'samurai_kern.dll')
        for path in notices.rglob('*'):
            if path.is_file():z.write(path,'native-notices/'+path.relative_to(notices).as_posix())
    plugin=output/'Selfaware-AI-0.2.0.zip'
    with zipfile.ZipFile(plugin,'w',zipfile.ZIP_DEFLATED) as z:
        for path in (ROOT/'store-content').rglob('*'):
            if path.is_file():z.write(path,path.relative_to(ROOT/'store-content'))
    scripts=('setup.ps1','local_setup.py','desktop_shortcut.py','local_start.ps1','local_launcher.py','bootstrap.ps1','README.md')
    for name in scripts:
        source='store-application-README.md' if name=='README.md' else name
        shutil.copy2(ROOT/'distribution'/source,output/name)
    shutil.copy2(ROOT/'LICENSE',output/'LICENSE')
    # The review directory is explicitly unsigned. Production bundle requires the
    # real signed Store module already installed by UCP; security remains enabled.
    manifest={'transport':'memory','unsigned_development':True}
    (output/'application.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    shutil.copy2(runtime,output/'runtime.zip')
    for review in (False,True):
        target=output/('Selfaware-AI-%s-0.2.0.zip'%('review' if review else 'external'))
        with zipfile.ZipFile(target,'w',zipfile.ZIP_STORED) as z:
            for name in scripts:z.write(output/name,name)
            z.write(ROOT/'LICENSE','LICENSE')
            z.write(runtime,'runtime.zip');z.write(plugin,plugin.name)
            if review:z.write(module,module.name)
            z.writestr('application.json',json.dumps({'transport':'memory','unsigned_development':review},indent=2))
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--native');p.add_argument('--runtime');a=p.parse_args()
    print(package(a.native,a.runtime))
