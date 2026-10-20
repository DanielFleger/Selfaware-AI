# -*- coding: utf-8 -*-
"""Lord-Sperre fuer ALLE Befehlswege (SAI 12.10., Daniels Regeln 11.10.: "unser Lord darf den gegnerischen Lord nicht
toeten" (16:11) und "der gegnerische Lord darf im ersten Spieljahr keinen Schaden nehmen" (16:41/16:44)).

Anlass (Frage-Agent 12.10. 00:08, Rot): die 9.600-Sperre sass nur im Streitkolben-Angriff des Lenkers; der Assassinen-
Lordtrupp (assassinen.py), der Waechter (waechter.py) und lord_sturm.py konnten den Lord ohne Pruefung angreifen.
Darum sitzt die Sperre jetzt in befehl.sende - durch diese Stelle geht jeder Befehl an das Spiel:
  - Angriff (angriff.ziel) auf einen gegnerischen Lord vor Tick BIS: Befehl verworfen.
  - Unser Lord in einem Angriff auf einen gegnerischen Lord: aus dem Befehl genommen (immer, auch nach BIS).
Den Stand (Tick, Lord-Nummern) setzt erstes_spiel.runde_lesen jede Runde. Ohne Stand wird ein Angriff auf eine
bekannte Lord-Nummer verworfen (sicherer Rueckfall).
GRENZE: Einheiten, die von selbst in den Nahkampf geraten, faengt keine Befehlssperre - dagegen hilft nur Abstand."""
from parteien import freunde_von   # B-133: Freund/Feind aus den Mannschaften des Spiels (2v2)

BIS = 9600
STAND = {"t": None, "feind": set(), "eigen": set()}
MELDUNGEN = []


def aktualisieren(t, L, sp=1):
    STAND["t"] = t
    STAND["feind"] = {n for n, e in L.items() if e.get("typ") == 55 and e.get("besitzer") not in freunde_von(sp)}
    STAND["eigen"] = {n for n, e in L.items() if e.get("typ") == 55 and e.get("besitzer") == sp}


def pruefe(cmd):
    """Gibt (Befehl oder None, Meldung oder None)."""
    a = cmd.get("angriff") if isinstance(cmd, dict) else None
    if not isinstance(a, dict) or a.get("ziel") not in STAND["feind"]:
        return cmd, None
    t = STAND["t"]
    if t is None or t < BIS:
        return None, "LORDSPERRE: Angriff auf den gegnerischen Lord %s vor Tick %d verworfen (Tick %s, %d Einheiten)" % (
            a["ziel"], BIS, t, len(a.get("einheiten", [])))
    einheiten = list(a.get("einheiten", []))
    ohne = [n for n in einheiten if n not in STAND["eigen"]]
    if len(ohne) == len(einheiten):
        return cmd, None
    if not ohne:
        return None, "LORDSPERRE: unser Lord allein gegen den gegnerischen Lord - Befehl verworfen (Tick %s)" % t
    c = dict(cmd)
    c["angriff"] = dict(a, einheiten=ohne)
    return c, "LORDSPERRE: unser Lord aus dem Angriff auf den gegnerischen Lord genommen (Tick %s)" % t


def filtern(paket):
    """Fuer befehl.sende: {"befehle": [...]} durch pruefe() schicken. Gibt (Paket oder None, Meldungen)."""
    if not isinstance(paket, dict) or "befehle" not in paket:
        return paket, []
    neu, meld = [], []
    for c in paket["befehle"]:
        c2, m = pruefe(c)
        if m:
            meld.append(m)
        if c2 is not None:
            neu.append(c2)
    MELDUNGEN.extend(meld)
    return (dict(paket, befehle=neu) if neu else None), meld
