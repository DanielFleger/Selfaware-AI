"""Vier echte Prozesse desselben Spielers; reservierte Bloecke duerfen sich nie ueberlappen."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    with tempfile.TemporaryDirectory() as d:
        module_path = str(Path(__file__).resolve().parent)
        counter = str(Path(d)/'nummer')
        code = ('import sys,json;sys.path.insert(0,%r);import befehl;'
                'befehl.MERKER=%r;print(json.dumps([befehl.neue_id() for _ in range(300)]))') % (module_path, counter)
        children = [subprocess.Popen([sys.executable, '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(4)]
        values = []
        try:
            for child in children:
                out, err = child.communicate(timeout=15)
                if child.returncode:
                    raise RuntimeError(err)
                values.extend(json.loads(out))
        finally:
            for child in children:
                if child.poll() is None:
                    child.terminate()
                    child.wait(5)
        assert len(values) == 1200 and len(set(values)) == 1200
        assert all(n % 8 == 1 for n in values)
        assert int(Path(counter).read_text()) >= max(values)
        print('1200 Nummern, vier Prozesse, derselbe Spieler: keine Ueberlappung; Reservierungen gesichert')


if __name__ == '__main__':
    main()
