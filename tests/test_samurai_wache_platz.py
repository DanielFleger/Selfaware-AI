"""S172 (Daniel 15.11.2026 12:27): die Wache uebernimmt SamurAIs eigenen Platz (KI 16, Paket auf dem Abt-Platz), nicht die Ratte - ohne Spiel."""
from selfaware.runtime.live import samurai_wache as W


def test_wache_nimmt_samurai_platz_16_und_nicht_die_ratte():
    keine = {sp: 0 for sp in range(1, 9)}
    assert W.SAMURAI_KI == 16
    assert W.entscheide(14, 0, {**keine, 1: 8, 2: 16}, False, False) == ("starten", 2)     # Partie 34: Kriegsfuerst 1, SamurAI 2
    assert W.entscheide(14, 0, {**keine, 1: 8, 2: 1}, False, False) == ("warten", None)    # Rotkaeppchen (Ratte) ist nicht SamurAI


def test_wache_startet_samurai_mit_den_raid_einstellungen():
    args = dict(a.split("=", 1) for a in W.LENKER_ARGS)
    assert args["uebernehmen"] == "ja" and args["bestellung"] == "raid" and args["kernweg"] == "ja" and args["streitkolben"] == "0"


def test_lenker_findet_sein_paket_auch_mit_relativem_pfad(monkeypatch):
    # Partie 34: PYTHONPATH=src (relativ) + cwd=HIER -> "No module named 'selfaware'"
    import os
    import subprocess
    import sys
    monkeypatch.setenv("PYTHONPATH", "src")
    umgebung = W.lenker_umgebung(2)
    r = subprocess.run([sys.executable, "-c", "import selfaware.runtime.live.samurai_wache"], cwd=W.HIER, env=umgebung,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-300:]
    assert umgebung["SHC_SPIELER"] == "2" and os.path.isdir(os.path.join(umgebung["PYTHONPATH"].split(os.pathsep)[0], "selfaware"))
