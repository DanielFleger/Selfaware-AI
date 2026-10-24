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
    local=Path(local) if local else Path.home()/'AppData/Local'
    return local/'Selfaware AI'/key/sha(archive).upper()[:16]

def backup(path,stamp):
    path=Path(path)
    if path.is_file():shutil.copy2(path,path.with_name(path.name+'.before-local-app-'+stamp))

def install(game,packages=None,local=None,shortcut=True):
    game=Path(game).resolve();packages=Path(packages or ROOT/'build').resolve()
    if not (game/'Stronghold Crusader.exe').is_file():raise ValueError('Crusader executable missing')
    config=game/'ucp-config.yml'
    raw=config.read_bytes();data=yaml.safe_load(raw)
    archive=packages/'runtime.zip'
    bridge=packages/'selfaware-runtime-0.1.0.zip'
    plugin=packages/'Selfaware-AI-0.1.0.zip'
    for path in (archive,bridge,plugin):
        if not path.is_file():raise ValueError('Missing local application package: '+str(path))
    with zipfile.ZipFile(bridge) as z:
        assert not {'runtime.zip','bootstrap.ps1','sai_launcher.dll'} & set(z.namelist()),'Runtime must be separate from bridge'
    runtime=runtime_path(game,archive,local)
    if not (runtime/'ready').is_file():
        if runtime.exists():raise ValueError('Incomplete runtime preserved for diagnosis: '+str(runtime))
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
    target_plugin=game/'ucp/plugins/Selfaware-AI-0.1.0'
    # Preserve old customized files before upgrading the plugin; no recursive deletion.
    with zipfile.ZipFile(plugin) as z:
        for name in checked_names(z,target_plugin):
            target_file=target_plugin/name
            if target_file.is_file() and not name.endswith('/') and target_file.read_bytes()!=z.read(name):backup(target_file,stamp)
    safe_extract(plugin,target_plugin)
    value={'name':'SamurAI','root':'ucp/plugins/Selfaware-AI-0.1.0/resources/ai/SamurAI/','active':True}
    for section in ('config-sparse','config-full'):
        block=data.setdefault(section,{})
        modules=block.setdefault('modules',{})
        modules.setdefault('selfaware-runtime',{'config':{}})
        block.setdefault('plugins',{}).setdefault('Selfaware-AI',{'config':{}})
        ai=modules.setdefault('aiSwapper',{'config':{}})['config'].setdefault('ai',{})
        abbot=ai.setdefault('abbot',{})
        for k in ('lines','portrait','aiv'):abbot[k]={'contents':{'value':dict(value)}}
        order=block.setdefault('load-order',[])
        for name in ('selfaware-runtime','Selfaware-AI'):
            if not any(row.get('extension')==name for row in order):order.append({'extension':name,'version':'0.1.0'})
    if yaml.safe_load(raw)!=data:
        backup(config,stamp)
        temp=config.with_name(config.name+'.local-app.tmp')
        temp.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True),encoding='utf-8');temp.replace(config)
    ipc=game/'ucp/villagestudio';ipc.mkdir(exist_ok=True)
    powershell=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'
    launcher=runtime/'python/pythonw.exe'
    arguments=subprocess.list2cmdline([str(starter/'local_launcher.py'),str(starter/'installation.json')])
    result={'game':str(game),'runtime':str(runtime),'starter':str(starter),'arguments':arguments,'shortcut_target':str(launcher),
            'module_sha256':sha(target),'runtime_sha256':sha(archive),'store_compatible':False,
            'module_extracts_runtime':False,'external_app_owns_learning':True}
    if shortcut:
        ps=("$s=New-Object -ComObject WScript.Shell; $p=Join-Path ([Environment]::GetFolderPath('Desktop')) 'Selfaware AI (lokal).lnk'; "
            "if(Test-Path -LiteralPath $p){Copy-Item -LiteralPath $p -Destination ($p+'.before-local-app-"+stamp+"')}; "
            "$l=$s.CreateShortcut($p); $l.TargetPath='"+str(launcher).replace("'","''")+"'; $l.Arguments='"+arguments.replace("'","''")+"'; "
            "$l.WorkingDirectory='"+str(starter).replace("'","''")+"'; $l.IconLocation='"+str(game/'Stronghold Crusader.exe').replace("'","''")+",0'; "
            "$l.WindowStyle=7; $l.Description='Selfaware AI - eigenstaendige lokale Entwicklungsfassung'; $l.Save(); Write-Output $p")
        result['shortcut']=subprocess.check_output([str(powershell),'-NoProfile','-NonInteractive','-Command',ps],text=True).strip()
    (starter/'installation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('game');p.add_argument('--packages');a=p.parse_args()
    print(json.dumps(install(a.game,a.packages),indent=2))
