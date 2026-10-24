"""Install the separate local app. This does not create a Store-compatible bridge."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import zipfile
import yaml
from desktop_shortcut import absolute_link, desktop_directory

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def checked_names(z,target):
    target=Path(target).resolve()
    for name in z.namelist():
        p=PurePosixPath(name.replace('\\','/'))
        if p.is_absolute() or '..' in p.parts or ':' in name:
            raise ValueError('Unsafe archive path: '+name)
        if not (target/str(p)).resolve().is_relative_to(target):raise ValueError(name)
    return z.namelist()

def safe_extract(archive,target):
    target=Path(target).resolve()
    with zipfile.ZipFile(archive) as z:
        checked_names(z,target)
        z.extractall(target)

def runtime_path(game,archive,local=None):
    game=Path(game).resolve()
    key=hashlib.sha256(str(game).lower().encode('utf-8')).hexdigest().upper()[:16]
    # MSIX child processes can see a private AppData overlay that Explorer cannot.
    # Documents is shared with the ordinary desktop process; do not put entrypoints
    # in LocalAppData or a Codex package cache.
    local=Path(local) if local else Path.home()/'Documents'
    return local/'Selfaware AI'/key/sha(archive).upper()[:16]

def backup(path,stamp):
    path=Path(path)
    if path.is_file():shutil.copy2(path,path.with_name(path.name+'.before-local-app-'+stamp))

def install(game,packages=None,local=None,shortcut=True):
    game=Path(game).resolve();packages=Path(packages or ROOT/'build').resolve()
    manifest=packages/'application.json'
    spec=json.loads(manifest.read_text(encoding='utf-8')) if manifest.is_file() else {}
    transport=spec.get('transport','file')
    if transport not in ('file','memory'):raise ValueError('Unsupported local application transport')
    module='selfaware-bridge' if transport=='memory' else 'selfaware-runtime'
    content_version='0.2.0' if transport=='memory' else '0.1.0'
    unsigned=spec.get('unsigned_development',transport=='file')
    if not (game/'Stronghold Crusader.exe').is_file():raise ValueError('Crusader executable missing')
    config=game/'ucp-config.yml'
    raw=config.read_bytes();data=yaml.safe_load(raw)
    archive=packages/'runtime.zip'
    bridge=packages/(module+'-0.1.0.zip')
    if transport=='memory' and not unsigned:
        # Production app never replaces the Store's certificate-signed module.
        bridge=game/'ucp/modules'/bridge.name
    plugin=packages/('Selfaware-AI-'+content_version+'.zip')
    for path in (archive,bridge,plugin):
        if not path.is_file():raise ValueError('Required package missing; install Selfaware AI from the UCP Store first: '+str(path))
    with zipfile.ZipFile(bridge) as z:
        assert not {'runtime.zip','bootstrap.ps1','sai_launcher.dll'} & set(z.namelist()),'Runtime must be separate from bridge'
    runtime=runtime_path(game,archive,local)
    if not (runtime/'ready').is_file():
        if runtime.exists():raise ValueError('Incomplete runtime preserved for diagnosis: '+str(runtime))
        legacy=Path.home()/'AppData/Local/Selfaware AI'/runtime.parent.name/runtime.name
        if local is None and (legacy/'ready').is_file():
            # Copy, never move/delete the working runtime and its measured models.
            runtime.parent.mkdir(parents=True,exist_ok=True)
            shutil.copytree(legacy,runtime)
        else:
            runtime.mkdir(parents=True)
            safe_extract(archive,runtime)
            (runtime/'ready').write_text(runtime.name,encoding='utf-8')
    if not all((runtime/'python'/name).is_file() for name in ('python.exe','pythonw.exe')):raise ValueError('Installed portable Python or its windowless starter missing')
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    starter=runtime.parent/'starter';starter.mkdir(exist_ok=True)
    scripts=packages if (packages/'local_start.ps1').is_file() else ROOT/'distribution'
    for name in ('local_start.ps1','bootstrap.ps1','local_launcher.py'):
        target=starter/name
        if target.exists() and target.read_bytes()==(scripts/name).read_bytes():continue
        backup(target,stamp);shutil.copy2(scripts/name,target)
    target=game/'ucp/modules'/bridge.name
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists() or sha(target)!=sha(bridge):
        backup(target,stamp);shutil.copy2(bridge,target)
    target_plugin=game/('ucp/plugins/Selfaware-AI-'+content_version)
    # Preserve old customized files before upgrading the plugin; no recursive deletion.
    with zipfile.ZipFile(plugin) as z:
        for name in checked_names(z,target_plugin):
            target_file=target_plugin/name
            if target_file.is_file() and not name.endswith('/') and target_file.read_bytes()!=z.read(name):backup(target_file,stamp)
    safe_extract(plugin,target_plugin)
    value={'name':'SamurAI','root':'ucp/plugins/Selfaware-AI-'+content_version+'/resources/ai/SamurAI/','active':True}
    for section in ('config-sparse','config-full'):
        block=data.setdefault(section,{})
        modules=block.setdefault('modules',{})
        if transport=='memory':
            old=modules.pop('selfaware-runtime',None)
            modules.setdefault(module,old or {'config':{}})
            block['load-order']=[row for row in block.get('load-order',[]) if row.get('extension')!='selfaware-runtime']
        else:modules.setdefault(module,{'config':{}})
        block.setdefault('plugins',{}).setdefault('Selfaware-AI',{'config':{}})
        ai=modules.setdefault('aiSwapper',{'config':{}})['config'].setdefault('ai',{})
        abbot=ai.setdefault('abbot',{})
        for k in ('lines','portrait','aiv'):abbot[k]={'contents':{'value':dict(value)}}
        order=block.setdefault('load-order',[])
        for name in (module,'Selfaware-AI'):
            version=content_version if name=='Selfaware-AI' else '0.1.0'
            existing=next((row for row in order if row.get('extension')==name),None)
            if existing is None:order.append({'extension':name,'version':version})
            else:existing['version']=version
    if yaml.safe_load(raw)!=data:
        backup(config,stamp)
        temp=config.with_name(config.name+'.local-app.tmp')
        temp.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True),encoding='utf-8');temp.replace(config)
    if transport=='file':
        ipc=game/'ucp/villagestudio';ipc.mkdir(exist_ok=True)
    launcher=runtime/'python/pythonw.exe'
    arguments=subprocess.list2cmdline([str(starter/'local_launcher.py'),str(starter/'installation.json')])
    result={'game':str(game),'runtime':str(runtime),'starter':str(starter),'arguments':arguments,'shortcut_target':str(launcher),
            'module_sha256':sha(target),'runtime_sha256':sha(archive),'store_compatible':None if transport=='memory' else False,
            'module_extracts_runtime':False,'external_app_owns_learning':True,'transport':transport,
            'unsigned_development':unsigned}
    if shortcut:
        link=desktop_directory()/'Selfaware AI (lokal).lnk'
        raw=absolute_link(launcher,arguments,starter,game/'Stronghold Crusader.exe',
                          'Selfaware AI - eigenstaendige lokale Entwicklungsfassung')
        backup(link,stamp)
        temporary=link.with_name(link.name+'.local-app.tmp')
        temporary.write_bytes(raw);temporary.replace(link)
        result['shortcut']=str(link)
    (starter/'installation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('game');p.add_argument('--packages');a=p.parse_args()
    print(json.dumps(install(a.game,a.packages),indent=2))
