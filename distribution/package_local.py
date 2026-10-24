"""Assemble a separate local mod, not an installable Store module."""
from pathlib import Path
import shutil
import zipfile
from install_candidate import package_module
ROOT=Path(__file__).resolve().parents[1]

def package():
    build=ROOT/'build'
    module=package_module(ROOT)
    plugin=build/'Selfaware-AI-0.1.0.zip'
    with zipfile.ZipFile(plugin,'w',zipfile.ZIP_DEFLATED) as z:
        for p in (ROOT/'Selfaware-AI').rglob('*'):
            if p.is_file():z.write(p,p.relative_to(ROOT/'Selfaware-AI'))
    bundle=build/'Selfaware-AI-local-0.1.0.zip'
    files=[module,plugin,build/'runtime.zip']
    files.extend(ROOT/'distribution'/n for n in ('setup.ps1','local_setup.py','local_start.ps1','bootstrap.ps1','README.md'))
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_STORED) as z:
        for p in files:z.write(p,p.name)
    return bundle

if __name__=='__main__':print(package())
