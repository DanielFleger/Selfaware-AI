# -*- coding: utf-8 -*-
"""B-166 Spielmechanik aus dem LAUFENDEN Spielcode gelesen, nicht geschaetzt (Daniel 21.10.2026 22:35: "ich will, dass du im
Code genau rausliest, wie viel die Einheit pro Tick haut - das muss da stehen. Die Messung dann abgleichen mit der Realitaet").
Abgelesen 21.10. 22:40 (Ghidra OpenSHC-ref, Basis-SHC): UpdateMaceman 0x00560700, Fall US_MELEE_ATTACK_WALL; Verteiler
UnitsState::updateUnits 0x00579300; TileMapState::processDamageToBuilding 0x00516B80. Das laufende Spiel (Extreme + UCP) hat an
zwei Stellen ANDERE Zahlen als die Referenz (Mauer 5 statt 6, Torhaus/Turm 15 statt 4, Gebaeude 80 statt 35) - darum liest dieses
Modul die Zahlen aus dem Speicher des laufenden Spiels, an den Stellen, deren Bedeutung der Referenzcode zeigt:
  - Schwung: updateUnits zaehlt animationTicker je Durchlauf +1; uebersteigt er animationSpeed + animationLeapTicksTotal, ruecke
    animationCycleNumber +1 -> ein Bild je (animationSpeed + 1) Durchlaeufe. Im Mauerangriff ist animationSpeed = Konstante bei
    0x00560D76; Bild = Tabelle 0x00B57E4C[animationCycleNumber]; der erste Eintrag < 1 beendet den Schwung (Schlag),
    animationCycleNumber faengt wieder bei 0 an.
  - Nur jeder 2. Schlag trifft: nextAttackHurtsWall (Einheit +0x3EE) wird je Schlag +1 und ueber 1 wieder 0; ist er nicht 0,
    setzt processDamageToBuilding den Schaden auf 0.
  - Schaden je Treffer: Mauerkachel = Konstante bei 0x00560E80; Gebaeude: (Torhaus/Turm ? AND-Maske : 0) + ADD-Wert
    (0x00560EB4 / 0x00560EB7, je 1 Byte mit Vorzeichen).
  - Mauerkachel (processDamageToBuilding): Mauernachbarn in den 4 Hauptrichtungen (LogicLayer & 0x10000100) < 2 ->
    Schaden + Schaden // 2; > 2 -> Schaden // 2. Erster Treffer auf eine unbeschaedigte Kachel (DamageLayer 0, LogicLayer-Bit
    0x10000 nicht gesetzt) mit Hoehe > Boden + 60: Hoehe zusaetzlich -20. Je Schadenspunkt Hoehe -1; ist die Hoehe beim
    naechsten Punkt schon auf dem Boden, faellt die Kachel.
"""
import math

import speicher

ADR_ANIM_SPEED = 0x00560D76      # imm32 in "MOV dword [ESI+animationSpeed], imm32" (Fall US_MELEE_ATTACK_WALL)
ADR_BILDER = 0x00B57E4C          # Bildtabelle des Mauerschlags (signed byte, Index = animationCycleNumber)
ADR_MAUER = 0x00560E80           # imm32 in "MOV ECX, imm32" - Schaden je Treffer auf eine Mauerkachel
ADR_GEB_AND, ADR_GEB_ADD = 0x00560EB4, 0x00560EB7   # imm8 in "AND ECX, imm8" / "ADD ECX, imm8"
E_ZYKLUS, E_TREFFER = 0x2B0, 0x3EE   # Einheit: animationCycleNumber (int), nextAttackHurtsWall (byte)


def _s8(b):
    return b - 256 if b > 127 else b


def streitkolben():
    """Die Zahlen des Mauerangriffs aus dem laufenden Spiel."""
    speed = int.from_bytes(speicher.lies(ADR_ANIM_SPEED, 4), "little")
    tab = [_s8(b) for b in speicher.lies(ADR_BILDER, 64)]
    bilder = next(i for i, v in enumerate(tab) if v < 1)
    mauer = int.from_bytes(speicher.lies(ADR_MAUER, 4), "little")
    und, plus = _s8(speicher.lies(ADR_GEB_AND, 1)[0]), _s8(speicher.lies(ADR_GEB_ADD, 1)[0])
    schwung = bilder * (speed + 1)
    return {"animation_speed": speed, "bilder": bilder, "takte_je_schwung": schwung, "takte_je_treffer": 2 * schwung,
            "mauer": mauer, "tor_turm": und + plus, "gebaeude": plus}


def kachel_schaden(basis, nachbarn):
    """Schaden eines Treffers auf eine Mauerkachel mit nachbarn Mauerkacheln in den 4 Hauptrichtungen."""
    if nachbarn < 2:
        return basis + basis // 2
    if nachbarn > 2:
        return basis // 2
    return basis


def treffer_bis_zerstoert(hoehe, boden, schaden, unbeschaedigt=True, bit_10000=False):
    """Zahl der Treffer, bis die Kachel faellt (je Treffer schaden Punkte; erster Treffer evtl. zusaetzlich -20)."""
    h = hoehe - (20 if unbeschaedigt and not bit_10000 and boden + 0x3C < hoehe else 0)
    return int(math.ceil((h - boden + 1) / float(schaden)))


# --- B-167 Welche Mauerkachel greift das Spiel an? (abgelesen 21.10. 23:05) ---------------------------------------------------
# setDestinationNearTargetedBuilding 0x0053DCC0 setzt das Gebiet der angefragten Kachel R auf das Gebiet des Manns und ruft
# findFreeSpaceNextToEnemyDefensiveStructureInSameAreaWithinDistance 0x004A7F50 mit seiner BLICKRICHTUNG: Breitensuche ab R ueber
# Felder seines Gebiets (Richtungen Tabelle 0x00B49048: N, NO, O, SO, S, SW, W, NW), hoechstens 10 Schritte (3 bei "verkuerzt").
# In Suchreihenfolge das erste Feld ohne Mauer/Turm/Tor/Bergfried (LogicLayer & 0x10000300 == 0), das in der Reihenfolge
# 0x00B39238[Blickrichtung] (je 4 gerade Richtungen, 32 Byte) ein feindliches Ziel neben sich hat: LogicLayer & 0x10000300, nicht
# & 2, kein Gebaeude oder Gebaeudetyp nicht 10 und nicht 40-42. Der Mann laeuft auf dieses Feld und hackt DIESES Ziel
# (targetedBuildingTile wird ueberschrieben). Test B 22:53: angefragt (149,129), gehackt (148,128) und (149,128); Test C 22:55:
# 20 Mann, Mehrheit auf (169,122) statt der angefragten (170,120) - je nach Blickrichtung ein anderes Ziel.
ADR_RICHT8, ADR_BLICK = 0x00B49048, 0x00B39238


def richtungen():
    """(8 Richtungen der Breitensuche, je Blickrichtung 0-7 die 4 Richtungen der Zielwahl) aus dem laufenden Spiel."""
    import struct
    a, b = speicher.lies(ADR_RICHT8, 64), speicher.lies(ADR_BLICK, 8 * 32)
    acht = [(struct.unpack_from("<h", a, 8 * i)[0], struct.unpack_from("<h", a, 8 * i + 4)[0]) for i in range(8)]
    blick = [[struct.unpack_from("<ii", b, 32 * r + 8 * i) for i in range(4)] for r in range(8)]
    return acht, blick


def ist_ziel(q, logik, bau, bautyp, besitz, spieler):
    """Feindliches Mauerziel laut Code (findFreeSpace...: LogicLayer & 0x10000300, nicht & 2, Gebaeudetyp nicht 10/40-42)."""
    if not logik[q] & 0x10000300 or logik[q] & 2:
        return False
    b = int(bau[q])
    if b and (bautyp.get(b) == 10 or 40 <= (bautyp.get(b) or 0) <= 42):
        return False
    return (int(besitz[q]) & 7) + 1 != spieler


def spiel_wahl(r, gebiet_mann, gebiet, logik, bau, bautyp, besitz, spieler, acht, reihenfolge, weit=10):
    """(freies Feld, Ziel), die das Spiel fuer die Anfrage r bei dieser Ziel-Reihenfolge (Blickrichtung) waehlt."""
    from collections import deque
    schlange, gesehen, reihe = deque([(tuple(r), 1)]), {tuple(r)}, []
    while schlange:
        t, d = schlange.popleft()
        if d > weit:
            break
        reihe.append(t)
        for dx, dy in acht:
            n = (t[0] + dx, t[1] + dy)
            if n not in gesehen and int(gebiet[n]) == gebiet_mann:
                gesehen.add(n)
                schlange.append((n, d + 1))
    for t in reihe:
        if logik[t] & 0x10000300:
            continue
        for dx, dy in reihenfolge:
            w = (t[0] + dx, t[1] + dy)
            if ist_ziel(w, logik, bau, bautyp, besitz, spieler):
                return t, w
    return None, None


def anfrage_fuer(ziel, gebiet_mann, gebiet, logik, bau, bautyp, besitz, spieler, acht, blick, kandidaten):
    """Die Anfrage-Kachel (ziel selbst zuerst, dann kandidaten), fuer die das Spiel bei JEDER Blickrichtung genau ziel waehlt -
    (Anfrage, Zugangsfeld); sonst (None, {Blickrichtung: Wahl fuer ziel})."""
    for r in [tuple(ziel)] + [tuple(k) for k in kandidaten if tuple(k) != tuple(ziel)]:
        wahl = [spiel_wahl(r, gebiet_mann, gebiet, logik, bau, bautyp, besitz, spieler, acht, blick[i]) for i in range(8)]
        if all(w == tuple(ziel) for _, w in wahl):
            return r, wahl[0][0]
    return None, {i: spiel_wahl(ziel, gebiet_mann, gebiet, logik, bau, bautyp, besitz, spieler, acht, blick[i])
                  for i in range(8)}


# --- B-167 Durchbruch-Weg ueber die Schrittbits (21.10. 23:08) ------------------------------------------------------------------
# Test C 23:02: nach zwei gehackten Kacheln "Weg frei", aber der Bergfried ist ein eigenes Gebiet (38) ohne Schritt vom Hof aus -
# der alte Weg sah jedes begehbare Feld als Nachbarn. Jetzt nur, was das Spiel erlaubt:
#   Laufen  t -> t+d, wenn PathLinkageLayer[t] das Bit der Richtung d hat (Bits im Uhrzeigersinn ab N: 1,2,4,...,0x80);
#           Kosten TAKTE_JE_FELD (gemessen 23:06, augen_laufen.py: 12 Takte je Feld, gerade und schraeg gleich).
#   Hacken  t -> w nur gerade (handleUnitMovementWhenTargetingBuildings), w = Mauerkachel, die processDamageToBuilding als Mauer
#           behandelt (LogicLayer & 0x100, nicht & 0x10000400, kein Gebaeude) und nicht dem Spieler gehoert; Kosten =
#           ceil(Treffer bis zur Zerstoerung / Maenner) x takte_je_treffer + ein Feld Laufen hinein; danach von w gerade weiter.
TAKTE_JE_FELD = 12
RICHT_BITS = [((0, -1), 0x01), ((1, -1), 0x02), ((1, 0), 0x04), ((1, 1), 0x08), ((0, 1), 0x10), ((-1, 1), 0x20),
              ((-1, 0), 0x40), ((-1, -1), 0x80)]


def durchbruch_schritte(link, logik, bau, besitz, hoehe, boden, spieler, maenner, start, ziel, mk=None, sperre=None, gefahr=None,
                        frei=None, frei_kosten=0.0):
    """Billigster Weg (Takte) von start zum ziel ueber Laufen und Hacken; Rueckgabe {"weg", "mauern" (in Reihenfolge), "takte"}.
    Ohne Weg: weg = None. sperre: Felder, die fuer uns kein Weg sind (feindliche Tore/Tuerme mit Rand, B-164).
    gefahr: Schuetzen je Feld (gefahr.Karte.g). Rangfolge nach Daniels Regel "maximale Sicherheit, dann minimaler Widerstand"
    (22.10. 00:40: "kompletter Frontalangriff ist bei den ganzen Schuetzen bescheuert ... dort angreifen, wo nur eine Mauer dick
    ist - das muss die KI selbst rausfinden"): zuerst die BESCHUSS-TAKTE (Schuetzen am Zielfeld x Takte der Kante - Laufen 12,
    Hauen/Torhaus die ganze Hackzeit), erst bei Gleichstand die Takte. (Frueher: nur Schuetzen je Feld ohne die Zeit dort -> Umwege;
    danach Zeit vor Gefahr -> Frontalangriff.) Vorrang-Faktor: groesser als jede Takt-Summe eines Wegs (Felder x teuerste Kante).
    frei / frei_kosten (Daniel 22.10. 00:31 "das Torhaus vorne rechts schlagen waere viel leichter gewesen"): ein Gebiet, das
    nach dem Einschlagen begehbar ist (Torhaus mit Rand) - wer von aussen hineingeht, zahlt einmal frei_kosten Takte."""
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    mk = mk or streitkolben()
    n = link.shape[0]
    idx = lambda x, y: x * n + y
    wand = ((logik & 0x100) != 0) & ((logik & 0x10000400) == 0) & (bau == 0) & ((besitz & 7) + 1 != spieler) & (hoehe > boden)
    nb = np.zeros(link.shape, int)
    for (dx, dy), _ in RICHT_BITS[::2]:
        nb += (np.roll(np.roll(logik, -dx, 0), -dy, 1) & 0x10000100) != 0
    schaden = np.where(nb < 2, mk["mauer"] + mk["mauer"] // 2, np.where(nb > 2, mk["mauer"] // 2, mk["mauer"]))
    punkte = hoehe.astype(int) - np.where(((logik & 0x10000) == 0) & (boden.astype(int) + 0x3C < hoehe), 20, 0) - boden + 1
    treffer = np.ceil(np.maximum(punkte, 1) / np.maximum(schaden, 1))
    hack = np.ceil(treffer / max(1, maenner)) * mk["takte_je_treffer"] + TAKTE_JE_FELD
    xs, ys = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    sp = np.zeros(link.shape, bool) if sperre is None else sperre
    von, nach, kosten = [], [], []
    for (dx, dy), bit in RICHT_BITS:
        x2, y2 = xs + dx, ys + dy
        ok = (x2 >= 0) & (x2 < n) & (y2 >= 0) & (y2 < n)
        x2c, y2c = np.clip(x2, 0, n - 1), np.clip(y2, 0, n - 1)
        lauf = ok & ((link & bit) != 0) & ~wand & ~wand[x2c, y2c] & ~sp & ~sp[x2c, y2c]
        if frei is not None:
            lauf = lauf | (ok & (frei | frei[x2c, y2c]) & ~wand & ~wand[x2c, y2c] & ((link != 0) | frei) &
                           ((link[x2c, y2c] != 0) | frei[x2c, y2c]))
        von.append(idx(xs[lauf], ys[lauf])); nach.append(idx(x2c[lauf], y2c[lauf]))
        kl = np.full(int(lauf.sum()), float(TAKTE_JE_FELD))
        if frei is not None:
            kl = kl + np.where(~frei[xs[lauf], ys[lauf]] & frei[x2c[lauf], y2c[lauf]], float(frei_kosten), 0.0)
        kosten.append(kl)
        if dx == 0 or dy == 0:
            frei = ((link != 0) & ~sp) | wand                           # von einem freien oder gehackten Feld gerade weiter
            rein = ok & frei & wand[x2c, y2c]
            von.append(idx(xs[rein], ys[rein])); nach.append(idx(x2c[rein], y2c[rein]))
            kosten.append(hack[x2c[rein], y2c[rein]].astype(float))
            # (22.10. 00:03, Test C: hinter (176,113) lag (175,113) = Bergfried, Logik 0x10000000 - der Plan sah 1 Mauer, es waren 4
            # hintereinander): aus dem Schutt nur auf ebenen Boden, nicht auf Bergfried/Gebaeude/erhoehte Flaechen
            raus = ok & wand & (link[x2c, y2c] != 0) & ~wand[x2c, y2c] & ((logik[x2c, y2c] & 0x10000000) == 0) &                 (bau[x2c, y2c] == 0) & (hoehe[x2c, y2c] <= boden[x2c, y2c]) & ~sp[x2c, y2c]
            von.append(idx(xs[raus], ys[raus])); nach.append(idx(x2c[raus], y2c[raus]))
            kosten.append(np.full(int(raus.sum()), float(TAKTE_JE_FELD)))
    v, z, k = np.concatenate(von), np.concatenate(nach), np.concatenate(kosten)
    takt_k = k.copy()
    if gefahr is not None:
        gf = np.asarray(gefahr, float)
        vorrang = float(n) * float(k.max())                     # > Takte eines Wegs (hoechstens n Felder lang x teuerste Kante)
        k = k + vorrang * gf.ravel()[z] * k / float(k.max())    # Beschuss-Takte, auf die teuerste Kante normiert
    g = coo_matrix((k, (v, z)), shape=(n * n, n * n)).tocsr()
    dist, vor = dijkstra(g, directed=True, indices=idx(*start), return_predecessors=True)
    zi = idx(*ziel)
    if not np.isfinite(dist[zi]):
        return {"weg": None, "mauern": [], "takte": None}
    weg, p = [], zi
    while p != idx(*start) and p >= 0:
        weg.append((int(p // n), int(p % n)))
        p = vor[p]
    weg = [tuple(start)] + weg[::-1]
    tk = {(int(a), int(b)): float(c) for a, b, c in zip(v, z, takt_k)}
    takte = sum(tk.get((idx(*a), idx(*b)), 0.0) for a, b in zip(weg, weg[1:]))
    # Beschuss-Last des Wegs: Schaden je Takt am Zielfeld x Takte der Kante (Laufen, Hauen, Torhaus) - damit Kandidaten
    # (Mauerweg, Torhaeuser) mit DEMSELBEN Mass verglichen werden wie die Felder im Weg (Lauf 00:50: Wahl nur nach Zeit)
    belastung = None
    if gefahr is not None:
        gfl = np.asarray(gefahr, float).ravel()
        belastung = sum(gfl[idx(*b)] * tk.get((idx(*a), idx(*b)), 0.0) for a, b in zip(weg, weg[1:]))
    gef = float(sum(np.asarray(gefahr)[q] for q in weg[1:])) if gefahr is not None else None
    return {"weg": weg, "mauern": [q for q in weg if wand[q]], "takte": takte, "gefahr": gef, "belastung": belastung}


def lauf_takte_zu(link, ziel, sperre=None):
    """Takte, die jedes Feld zu Fuss bis ziel braucht (Schrittbits, 12 Takte je Feld gemessen - augen_laufen), np.inf = nicht
    erreichbar. B-167 (22.10. 00:39): die Luftlinie unterschaetzte die Wege zum Sammelfeld - nach ihrer Frist waren 11 von 51 da."""
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    n = link.shape[0]
    sp = np.zeros(link.shape, bool) if sperre is None else sperre
    xs, ys = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    von, nach = [], []
    for (dx, dy), bit in RICHT_BITS:
        x2, y2 = xs + dx, ys + dy
        ok = (x2 >= 0) & (x2 < n) & (y2 >= 0) & (y2 < n)
        x2c, y2c = np.clip(x2, 0, n - 1), np.clip(y2, 0, n - 1)
        lauf = ok & ((link & bit) != 0) & ~sp & ~sp[x2c, y2c]
        # rueckwaerts eintragen: Abstand VON jedem Feld ZUM Ziel = Abstand vom Ziel im umgedrehten Netz
        von.append(x2c[lauf] * n + y2c[lauf]); nach.append(xs[lauf] * n + ys[lauf])
    v, z = np.concatenate(von), np.concatenate(nach)
    g = coo_matrix((np.full(len(v), float(TAKTE_JE_FELD)), (v, z)), shape=(n * n, n * n)).tocsr()
    return dijkstra(g, directed=True, indices=ziel[0] * n + ziel[1]).reshape(n, n)
