"""18.10. (1v1-Lauf 1018a). Gegenprobe Befehlsnummern: zwei Prozesse (Spieler 1 und 2) ziehen gleichzeitig je 3000 Nummern aus demselben Merker.
Aufruf: python werkzeug/ids_pruefen.py werkzeug [alt]. Vorher festgelegt: neue Fassung -> 0 doppelte; alte Fassung (Argument alt) -> mehr als 0 doppelte."""
import os, subprocess, sys, json, tempfile
W = sys.argv[1]; alt = len(sys.argv) > 2
code = r'''
import os, sys, json
sys.path.insert(0, %r)
import befehl
if %r:
    import io, time
    def neue_id():
        try: letzte = int(io.open(befehl.MERKER).read().strip())
        except (OSError, ValueError): letzte = 0
        n = max(int(time.time()), letzte + 1)
        try: io.open(befehl.MERKER, "w").write(str(n))
        except OSError: pass
        return n
else:
    neue_id = befehl.neue_id
print(json.dumps([neue_id() for _ in range(3000)]))
''' % (W, alt)
merker = os.path.join(tempfile.gettempdir(), "ids_test_merker")
umg = []
for sp in (1, 2):
    e = dict(os.environ, SHC_SPIELER=str(sp), SHC_INSTANZ="4")
    umg.append(subprocess.Popen([sys.executable, "-c", code.replace("befehl.MERKER", repr(merker)) if False else code], env=e, stdout=subprocess.PIPE))
alle = []
for p in umg:
    alle += json.loads(p.communicate()[0])
print("%s Fassung: %d Nummern, %d doppelt" % ("alte" if alt else "neue", len(alle), len(alle) - len(set(alle))))
