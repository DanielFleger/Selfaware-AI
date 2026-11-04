# -*- coding: utf-8 -*-
"""Startet Szene korb_g auf Instanz 2 und gibt ihr die Frage an die Oberflaeche: getHeightAtTileIncludingOwnersBuildings (004fff10), ueber 0 heisst erlaubt, nur lesend.

Der Direktaufruf gehoert in die Proben, nicht nach src: SamurAI darf ihn nie benutzen (test_das_werkzeug_bleibt_im_messlauf).
Aufruf: python data/research/auge_plan/streuung_20261104/korb_lauf.py > data/research/auge_plan/streuung_20261104/lauf_korb_g.log 2>&1
Auswertung: korb_pruefen.py
"""
import json
import os

os.environ["SHC_INSTANZ"] = "2"
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402
from selfaware.tools.experiments import auge_lauf_s as ls  # noqa: E402
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz  # noqa: E402
from selfaware.tools.experiments.spielcode_rufen import Rufer  # noqa: E402

F_HOEHE = 0x4fff10

if __name__ == "__main__":
    tm = Feldkarte.laden(feldliste=FELDLISTE).struktur("DAT_TileMapState")[0]
    with Rufer(pid_der_instanz(2)) as r:
        ls.KORB_OBERFLAECHE = lambda feld: r.rufe(F_HOEHE, feld, 1, this=tm)
        ergebnis = ls.los(2, ["korb_g"])
    print(json.dumps({"schritt": "ende", "ergebnis": ergebnis}, ensure_ascii=False, default=str)[:3000], flush=True)
