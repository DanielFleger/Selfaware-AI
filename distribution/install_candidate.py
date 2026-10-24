"""Install an unsigned test candidate into an explicitly named game copy.

This is a development probe, not the Store installation path. Secure mode is
never changed. Every existing configuration is backed up before modification.
"""
import argparse
from pathlib import Path
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'werkzeug'))


def package_module(root):
    # Build exact module packaging layout used by UCP (no enclosing folder).
    files={'definition.yml':root/'definition.yml','init.lua':root/'init.lua',
           'options.yml':root/'options.yml','starttroops.lua':root/'starttroops.lua',
           'command_owner.lua':root/'command_owner.lua','takeover.lua':root/'takeover.lua',
           'engine_contract.lua':root/'engine_contract.lua',
           'bridge.lua':root/'distribution/bridge.lua',
           'README.md':root/'distribution/README.md'}
    files.update({n:root/'build'/n for n in ('logik.lua','samurai_kern.dll')})
    package=root/'build/selfaware-runtime-0.1.0.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_STORED) as z:
        for name,source in files.items():z.write(source,name)
    return package


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('game',nargs='?');p.add_argument('--development',action='store_true');p.add_argument('--package-only',action='store_true');a=p.parse_args()
    if a.package_only:print(package_module(Path(__file__).resolve().parents[1]))
    elif not a.development or not a.game:p.error('Unsigned candidate requires explicit --development and a game directory; not a Store release')
    else:
        from package_local import package
        from local_setup import install as install_app
        import json
        package()
        print(json.dumps(install_app(a.game),indent=2))
