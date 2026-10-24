"""Desktop entry point for portable pythonw: no terminal and no silent handoff."""
import ctypes
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback


def show_error(text):
    ctypes.windll.user32.MessageBoxW(None, text, 'Selfaware AI: Startfehler', 0x10)


def start_command(config_file):
    config_file = Path(config_file).resolve()
    config = json.loads(config_file.read_text(encoding='utf-8'))
    starter = Path(config['starter'])
    game = Path(config['game'])
    runtime = Path(config['runtime'])
    powershell = Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    for required in (starter/'local_start.ps1', starter/'bootstrap.ps1',
                     game/'Stronghold Crusader.exe', runtime/'python/python.exe', powershell):
        if not required.is_file():
            raise FileNotFoundError('Startdatei fehlt: '+str(required))
    return [str(powershell), '-NoProfile', '-NonInteractive', '-WindowStyle', 'Hidden',
            '-ExecutionPolicy', 'Bypass', '-File', str(starter/'local_start.ps1'),
            '-Game', str(game), '-Runtime', str(runtime)]


def launch(config_file, run=subprocess.run, notify=show_error):
    config_file = Path(config_file).resolve()
    state = config_file.parent.parent
    trace = state/'launcher.log'
    try:
        state.mkdir(parents=True, exist_ok=True)
        with trace.open('a', encoding='utf-8') as log:
            log.write('%s Start requested; launcher PID %s\n' %
                      (datetime.datetime.now().isoformat(timespec='seconds'), os.getpid()))
        command = start_command(config_file)
        output = state/('launcher-%s-output.log' % os.getpid())
        with output.open('ab') as stream:
            result = run(command, cwd=str(config_file.parent), stdin=subprocess.DEVNULL,
                         stdout=stream, stderr=subprocess.STDOUT,
                         creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if result.returncode:
            detail = output.read_bytes()[-1600:].decode('utf-8', errors='replace').strip()
            raise RuntimeError('Spielstart fehlgeschlagen (Code %s).\n%s\nProtokoll: %s' %
                               (result.returncode, detail, output))
        with trace.open('a', encoding='utf-8') as log:
            log.write('Launcher PID %s: game session finished successfully\n' % os.getpid())
        return 0
    except Exception as error:
        try:
            with trace.open('a', encoding='utf-8') as log:
                log.write(traceback.format_exc()+'\n')
        finally:
            notify(str(error)+'\nStartprotokoll: '+str(trace))
        return 1


if __name__ == '__main__':
    config = sys.argv[1] if len(sys.argv) == 2 else Path(__file__).with_name('installation.json')
    raise SystemExit(launch(config))
