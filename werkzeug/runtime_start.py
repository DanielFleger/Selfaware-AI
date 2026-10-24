"""Autonomous entry point, separating learned models by effective UCP profile."""
import hashlib
import json
import os
from pathlib import Path
import runpy


def profilkennung(config):
    canonical=json.dumps(config,sort_keys=True,separators=(',',':'),ensure_ascii=True)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:24]


def main():
    import sys
    if os.environ.get('SHC_START_LOG'):
        stream=open(os.environ['SHC_START_LOG'],'a',encoding='utf-8',buffering=1)
        sys.stdout=sys.stderr=stream
    import yaml
    game=Path(os.environ['SHC_GAME_DIR']).resolve()
    config=game/'ucp/.ucp-final-config-cache'
    if not config.is_file():config=game/'ucp-config.yml'
    profile=profilkennung(yaml.safe_load(config.read_text(encoding='utf-8')))
    data=Path(__file__).resolve().parents[1]/'daten'
    learning=data/'lernprofile'/profile
    learning.mkdir(parents=True,exist_ok=True)
    os.environ['SHC_LEARNING_DIR']=str(learning)
    os.environ['SHC_LEARNING_PROFILE']=profile
    print('Lernprofil '+profile,flush=True)
    runpy.run_module('samurai_wache',run_name='__main__')


if __name__=='__main__':main()
