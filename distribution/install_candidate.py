"""Install an unsigned test candidate into an explicitly named game copy.

This is a development probe, not the Store installation path. Secure mode is
never changed. Every existing configuration is backed up before modification.
"""
import argparse
import datetime
from pathlib import Path
import shutil
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'werkzeug'))
import yaml
from lernbuch import atomar


def package_module(root):
    # Build exact module packaging layout used by UCP (no enclosing folder).
    files={'definition.yml':root/'definition.yml','init.lua':root/'init.lua',
           'bridge.lua':root/'distribution/bridge.lua','bootstrap.ps1':root/'distribution/bootstrap.ps1',
           'README.md':root/'distribution/README.md'}
    files.update({n:root/'build'/n for n in ('runtime.zip','logik.lua','sai_launcher.dll','samurai_kern.dll')})
    package=root/'build/selfaware-runtime-0.1.0.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_STORED) as z:
        for name,source in files.items():z.write(source,name)
    return package


def install(game):
    root=Path(__file__).resolve().parents[1]
    game=Path(game).resolve()
    if not (game/'Stronghold Crusader.exe').is_file():raise ValueError('Not a Crusader game directory')
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    config=game/'ucp-config.yml'
    raw=config.read_bytes();data=yaml.safe_load(raw)
    package=package_module(root)
    plugin=game/'ucp/plugins/Selfaware-AI-0.1.0'
    if plugin.exists():raise ValueError('Candidate plugin already exists; preserve it and choose a new version')
    target=game/'ucp/modules/selfaware-runtime-0.1.0.zip'
    if target.exists():shutil.copy2(target,target.with_name(target.name+'.before-'+stamp))
    shutil.copy2(package,target)
    shutil.copytree(root/'Selfaware-AI',plugin)
    value={'name':'SamurAI','root':'ucp/plugins/Selfaware-AI-0.1.0/resources/ai/SamurAI/','active':True}
    for section in ('config-sparse','config-full'):
        block=data.setdefault(section,{})
        mods=block.setdefault('modules',{})
        mods['selfaware-runtime']={'config':{}}
        block.setdefault('plugins',{})['Selfaware-AI']={'config':{}}
        mods.setdefault('aiSwapper',{'config':{}})['config'].setdefault('ai',{})['abbot']={k:{'contents':{'value':dict(value)}} for k in ('lines','portrait','aiv')}
        order=block.setdefault('load-order',[])
        for name in ('selfaware-runtime','Selfaware-AI'):
            if not any(o.get('extension')==name for o in order):order.append({'extension':name,'version':'0.1.0'})
    backup=config.with_name(config.name+'.before-selfaware-candidate-'+stamp)
    with backup.open('xb') as f:f.write(raw)
    text=yaml.safe_dump(data,sort_keys=False,allow_unicode=True)
    if yaml.safe_load(text)!=data:raise ValueError('Config roundtrip failed')
    temp=config.with_name(config.name+'.candidate.tmp');temp.write_text(text,encoding='utf-8');temp.replace(config)
    print('Unsigned candidate installed; secure mode was not changed:',game)
    print('Config backup:',backup)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('game',nargs='?');p.add_argument('--development',action='store_true');p.add_argument('--package-only',action='store_true');a=p.parse_args()
    if a.package_only:print(package_module(Path(__file__).resolve().parents[1]))
    elif not a.development or not a.game:p.error('Unsigned candidate requires explicit --development and a game directory; not a Store release')
    else:install(a.game)
