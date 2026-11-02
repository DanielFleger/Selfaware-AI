# -*- coding: utf-8 -*-
"""B-142 A6: Rechnet das Spiel festgelegt, wenn der eine Eingang aus der echten Zeit gleich ist? Zweimal denselben Stand laden, 2.000 Takte aufzeichnen.
counterForUpdatingSeparateAreaTileMaps laeuft auch in der Pause (updateSeparateAreaTileMap im Pausenteil von processGameTick): Gemessen stand er nach dem Laden bei 12 und 43. Hier wird er im selben Auftrag wie das Weiter gesetzt.

Aufruf: PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/a6_festgelegt.py 2 "<Stand>" <basis> [Takte] [Zaehlerwert]                  Fenster t4, t5
        PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/a6_festgelegt.py 2 "<Stand>" <basis> [Takte] [Zaehlerwert] --kampf <Takt>   erst bis zu diesem Takt laufen und dort neu speichern, Fenster t6, t7
        PYTHONPATH=src python data/research/auge_plan/lauf_k_20261102/a6_festgelegt.py 2 "<Stand>" <basis> [Takte] [Zaehlerwert] --zeiger 25       auch den Suchzeiger des Geschosses vor dem Laden setzen, Fenster t8, t9
Grenze: 8 Minuten. Am Ende steht das Spiel, die Sperre ist frei. Das setzt einen Wert im Spiel: nur fuer Messlaeufe auf einer Laufinstanz.
"""
import argparse
import os
import time

from selfaware.game.ucp import laden as laden_mod
from selfaware.game.ucp import speichern as speichern_mod
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_k as lk
from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz, standard_bereiche

p = argparse.ArgumentParser()
p.add_argument("instanz", type=int)
p.add_argument("stand")
p.add_argument("basis")
p.add_argument("takte", type=int, nargs="?", default=2000)
p.add_argument("wert", type=int, nargs="?", default=100)
p.add_argument("--kampf", type=int)
p.add_argument("--zeiger", type=int, help="every10Ticks ist der Suchzeiger fuer den naechsten freien Geschossplatz (spawnProjectileEntity), das Laden setzt ihn nicht")
a = p.parse_args()
n, stand, basis, takte, wert = a.instanz, a.stand, a.basis, a.takte, a.wert
lf.pruefe_laufinstanz(n)
os.environ["SHC_INSTANZ"] = str(n)
karte = Feldkarte.laden(feldliste=FELDLISTE)
ZAEHLER = karte.adresse("DAT_GameState", "mapAndTime.counterForUpdatingSeparateAreaTileMaps")[0]
ZEIGER = karte.adresse("DAT_EntityState", "every10Ticks")[0]
quelle = ProzessQuelle(pid_der_instanz(n))
s = lk.SpeicherK(quelle)
k = lf.EchterKanal()
rek = lf.Rekorder(n, os.path.dirname(basis), os.path.basename(basis), quelle, standard_bereiche(karte))
rek.basis = basis
rek.stop_datei, rek.aus_datei, rek.felder_datei = basis + ".stop", basis + ".aussetzen", basis + ".felder.json"
ende_uhr = time.time() + 480


def warte_bis(ziel):
    while s.takt() < ziel:
        if time.time() > ende_uhr:
            raise lf.Fehler("Frist von 8 Minuten ist um")
        if rek.fehler():
            raise lf.Fehler(f"Aufzeichnung: {rek.fehler()}")
        time.sleep(0.05)


lf.sperre_holen("A6 festgelegt (B-142)")
steht = False
try:
    if a.kampf:
        lk.gefecht_starten(k, "Green Haven", 1, warte=15, startpause=1)
        laden_mod.lade_stand(stand, mit_bild=False)
        k.befehl({"tempo": lf.TEMPO_LAUF}, lf.KANAL)
        k.liste([{"poke": ZAEHLER, "wert": wert}, {"pause": False}], lf.KANAL)
        warte_bis(a.kampf)
        steht, t = lf.anhalten_und_pruefen(k, s)
        if not steht:
            raise lf.Fehler("Der Takt steht nicht")
        stand = f"AugeK {time.strftime('%H%M%S')} T{t}"
        speichern_mod.speichere(stand)
        print("Kampfstand", stand, "Lords", s.lord_besitzer(), flush=True)
    for name in (("t8", "t9") if a.zeiger is not None else ("t6", "t7") if a.kampf else ("t4", "t5")):
        lk.gefecht_starten(k, "Green Haven", 1, warte=15, startpause=1)
        t = laden_mod.lade_stand(stand, mit_bild=False, zuvor=[{"poke": ZEIGER, "wert": a.zeiger}] if a.zeiger is not None else ())
        k.befehl({"tempo": lf.TEMPO_JEDER_TAKT}, lf.KANAL)
        rek.starten(name, lf.TEMPO_JEDER_TAKT, streng=True, messen=False, warte_ms=lk.WARTE_MS)
        lf.warte_auf(rek.laeuft, 60, f"Aufzeichnung {name} laeuft")
        k.liste([{"poke": ZAEHLER, "wert": wert}, {"pause": False}], lf.KANAL)
        warte_bis(t + takte)
        steht, tt = lf.anhalten_und_pruefen(k, s)
        print(name, "von", t, "bis", tt, "steht", steht, rek.beenden(), "Lords", s.lord_besitzer(), flush=True)
finally:
    try:
        rek.beenden()
    finally:
        steht, tt = lf.anhalten_und_pruefen(k, s)
        print("angehalten", steht, tt, flush=True)
        if steht:
            lf.sperre_freigeben()
