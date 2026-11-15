"""Portable path adapter for the existing controller, no desktop automation."""
import os


def spielordner(instanz=1):
    return os.path.abspath(os.environ['SHC_GAME_DIR'])


def pids(instanz=1):
    from pathlib import Path
    from speicher import _programm
    root = spielordner(instanz)
    result = []
    for file in Path(root).glob('ucp-pid-*'):
        pid = int(file.name.rsplit('-', 1)[1])
        exe = _programm(pid)
        if exe and os.path.normcase(os.path.dirname(exe)) == os.path.normcase(root):
            result.append(pid)
    return result
