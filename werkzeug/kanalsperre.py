"""Betriebssystem-Sperre: lebende Besitzer werden nie nach Dateialter bestohlen.

Windows-Semantik: https://docs.python.org/3/library/msvcrt.html#msvcrt.locking
Die Datei bleibt bestehen; Freigabe durch Entsperren/Schliessen, auch bei Absturz.
"""
import os
import time


class Sperre:
    def __init__(self, pfad, timeout=30):
        self.pfad, self.timeout, self.f = pfad, timeout, None

    def __enter__(self):
        f = open(self.pfad, 'a+b', buffering=0)
        ende = time.monotonic() + self.timeout
        while True:
            try:
                f.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.f = f
                return self
            except OSError:
                if time.monotonic() >= ende:
                    f.close()
                    raise TimeoutError('SENDESPERRE: %s belegt' % self.pfad)
                time.sleep(.002)

    def __exit__(self, *exc):
        try:
            self.f.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.f.fileno(), fcntl.LOCK_UN)
        finally:
            self.f.close()
            self.f = None
