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
