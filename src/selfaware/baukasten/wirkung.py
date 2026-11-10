"""Wirkung je Gold (B-181, Plan_Gehirn Abschnitte 4 und 5): Was bewirkt eine Einheit dieser Art gegen die sichtbaren Ziele des Gegners?

Eine gedachte Einheit laeuft vom Start Ziel fuer Ziel ab, immer zu dem mit dem meisten Wert je Takt, bis der Zeithorizont um ist oder sie
wahrscheinlich tot ist. Am Ziel zaehlt, ob sie lange genug ueberlebt: ihr Leben gegen den Schaden der feindlichen Schuetzen, die den Ort
erreichen, und (fuer Nahkaempfer) der feindlichen Nahkaempfer daneben. Ohne sie geschieht dort nichts, darum ist ihr Ergebnis die Wirkung.
Gekauft wird immer die Art mit dem meisten Wert je Gold; was sie schon abdeckt, zaehlt fuer die naechste nicht mehr. Eine feste Reihenfolge gibt es nicht.

Wissen, das hineinfliesst (jede Zahl nennt ihre Herkunft):
- Leben je Art: Lagebild der laufenden Partie (eigene Einheiten), sonst Editor-Duelle (services/gefecht.tabelle), sonst Ersatz.
- Schaden je Takt zwischen Arten: Editor-Duelle, Schuetzen aus der Ferne getrennt; fehlt ein Paar, das Mittel der Zeile.
- Gebaeude: Leben und Rate der Assassinen aus Partien (data/research/angriff_raten.json). Andere Nahkaempfer: Ersatz nach ihrer Staerke
  gegen Speertraeger im Verhaeltnis zur Assassine. Sklaven zuenden an (raids.py, gemessen 19.10.: brennt nach 165 Takten von allein ab).
- Reichweite und Lauftempo: services/spielwerte (Lauf S).
- B-182: Erfolgsanteil je Zuweisung und Takte am Ziel je Art und Zielart, gemessen in Partien (baukasten/eichung.py,
  data/research/raid_eichung.json). Wo genug Daten sind, ersetzen sie die Ersatzwerte; mehr Erfolg als gemessen traut die Rechnung keiner Art zu.
- Wert der Ziele: Daniels Startwerte (raids.WERT, raids.ARBEITER). Plan_Gehirn 5.6, Stufe 1: von Hand gesetzte Regler, spaeter gelernt.
Nur Sichtbares (FAIRNESS R3): Art und Ort von Gebaeuden und Einheiten, kein fremdes Leben, kein fremdes Ziel.
"""

import collections
import dataclasses
import json
import os

import selfaware.services.spielwerte as SW
from selfaware import workspace
from selfaware.baukasten import eichung as EI
from selfaware.baukasten import einheiten as EH
from selfaware.micro.tasks import raids as RA

HORIZONT = 5000  # Plan_Gehirn 5.3: Zeitraum "mittel"
FEUER_TAKTE = 165  # raids.py, gemessen 19.10.: so lange bis das Gebaeude des Sklaven brennt, danach brennt es allein ab
ARBEITER_TAKTE = 50  # Ersatz: Arbeiter fallen schnell (Assassine rund 250 Schaden je Takt, angriff_raten.json), es zaehlt vor allem der Weg
LEBEN_ERSATZ = 10000  # Ersatz, wenn weder Lagebild noch Duell die Art kennen
DPS_ERSATZ = 20.0  # wie gefecht.dps ohne jede Messung
REST = 0.05  # darunter gilt die gedachte Einheit als verloren
ABGEDECKT = 0.5  # Startwert: hat ein Ziel schon so viel Aussicht, erledigt zu werden, zaehlt es fuer die naechste Einheit nicht mehr
SPEER = 24  # Bezugsgegner fuer den Ersatz der Gebaeuderate
RATEN = os.path.join(workspace.DATA, "angriff_raten.json")


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _gebaeude_raten(pfad=RATEN):
    try:
        with open(pfad, encoding="utf-8") as f:
            return {int(k): v for k, v in json.load(f).get("gebaeude", {}).items()}
    except (OSError, ValueError):
        return {}


@dataclasses.dataclass(frozen=True)
class Ziel:
    schluessel: tuple  # ("g", Gebaeude) oder ("e", Einheit)
    typ: int
    ort: tuple
    wert: float
    schuetzen: tuple  # Arten der feindlichen Schuetzen, die den Ort erreichen
    nah: tuple  # Arten der feindlichen Nahkaempfer bis raids.GEFAHR_NAH


def ziele(L, G, sp):
    """Alle sichtbaren feindlichen Gebaeude und Arbeiter mit Wert, mit den Schuetzen und Nahkaempfern, die sie decken."""
    fern, nah = [], []
    for e in L.values():
        if e.get("besitzer") in (0, sp) or e.get("leben", 1) <= 0:
            continue
        if e["typ"] in SW.FERNKAMPF:
            fern.append((e["typ"], (e["x"], e["y"])))
        elif e["typ"] in RA.NAH:
            nah.append((e["typ"], (e["x"], e["y"])))

    def deckung(p):
        return (
            tuple(sorted(t for t, q in fern if SW.in_gefahr(q, p, t))),
            tuple(sorted(t for t, q in nah if schach(p, q) <= RA.GEFAHR_NAH)),
        )

    aus = []
    for n, g in G.items():
        if g.get("besitzer") not in (0, sp) and g["typ"] in RA.WERT:
            p = (g["x"], g["y"])
            aus.append(Ziel(("g", n), g["typ"], p, float(RA.WERT[g["typ"]]), *deckung(p)))
    for n, e in L.items():
        if e.get("besitzer") not in (0, sp) and e["typ"] in RA.ARBEITER and e.get("leben", 1) > 0:
            p = (e["x"], e["y"])
            aus.append(Ziel(("e", n), e["typ"], p, float(RA.ARBEITER[e["typ"]]), *deckung(p)))
    return aus


class Wissen:
    """Was wir je Art wissen, mit Herkunft. lernen() nimmt das volle Leben der eigenen Einheiten aus dem Lagebild."""

    def __init__(self, tabelle=None, gebaeude=None, eichung=None):
        self._am_ziel = {}
        self.eichung = EI.laden() if eichung is None else eichung
        if tabelle is None:
            from selfaware.services import gefecht

            tabelle = gefecht.tabelle()
        self.schaden, self.leben_duell, self.fern = tabelle
        self.gebaeude = _gebaeude_raten() if gebaeude is None else gebaeude
        self.leben_lage = {}

    def lernen(self, L, sp):
        """Je Runde einmal: volles Leben der eigenen Arten; die Rechnung am Ziel beginnt neu, weil sich die Deckung bewegt."""
        self._am_ziel = {}
        for e in L.values():
            if e.get("besitzer") == sp and e.get("leben", 0) > self.leben_lage.get(e["typ"], 0):
                self.leben_lage[e["typ"]] = e["leben"]

    def leben(self, typ):
        if typ in self.leben_lage:
            return self.leben_lage[typ], "Lagebild"
        if typ in self.leben_duell:
            return self.leben_duell[typ], "Duell"
        return LEBEN_ERSATZ, "Ersatz"

    def dps(self, a, b, fern=False):
        zeile = self.fern.get(a) if fern and self.fern.get(a) else self.schaden.get(a)
        if not zeile:
            return DPS_ERSATZ, "Ersatz"
        if b in zeile:
            return zeile[b], "Duell"
        return sum(zeile.values()) / len(zeile), "Mittel der Duelle"

    def gebaeude_takte(self, typ, gtyp):
        """(Takte, bis das Gebaeude faellt oder brennt, Herkunft) oder (None, Grund), wenn diese Art es nicht zerstoert."""
        if typ == RA.SKLAVE:
            return FEUER_TAKTE, "gemessen 19.10. (Feuer)"
        art = EH.ARTEN.get(typ)
        if art is None or art.kampf != "nah" or not EH.darf(typ, "raid"):
            return None, "greift keine Gebaeude an"
        g = self.gebaeude.get(gtyp)
        if not g or not g.get("rate"):
            return None, "keine gemessene Rate fuer diese Gebaeudeart"
        rate, herkunft = g["rate"], "Partien (Assassine)"
        if typ != 73:
            rate *= self.dps(typ, SPEER)[0] / self.dps(73, SPEER)[0]
            herkunft = "Ersatz nach der Assassine"
        return g["leben_max"] / rate, herkunft

    def am_ziel(self, typ, z):
        """(Takte am Ziel, Erfolg zwischen 0 und 1). Erfolg 0 heisst: Diese Art richtet dort nichts aus."""
        k = (typ, z)
        if k not in self._am_ziel:
            self._am_ziel[k] = self._rechnen(typ, z)
        return self._am_ziel[k]

    def _rechnen(self, typ, z):
        takte = self.gebaeude_takte(typ, z.typ)[0] if z.schluessel[0] == "g" else ARBEITER_TAKTE
        if takte is None:
            return None, 0.0
        # B-182: gemessen in Partien - Takte am Ziel statt Ersatz, und nie mehr Erfolg als der gemessene Anteil je Zuweisung
        anteil, gemessen = self.eichung.get((typ, z.schluessel[0]), (None, None))
        if gemessen is not None:
            takte = gemessen
        fern = EH.ARTEN[typ].kampf == "fern"
        rein = sum(self.dps(s, typ, fern=True)[0] for s in z.schuetzen)
        if not fern:
            rein += sum(self.dps(m, typ)[0] for m in z.nah)
        erfolg = 1.0 if rein <= 0 else min(1.0, self.leben(typ)[0] / rein / max(takte, 1.0))
        return takte, erfolg if anteil is None else min(erfolg, anteil)

    def wert_je_takt(self, typ, ort, z, tempo=None):
        takte, erfolg = self.am_ziel(typ, z)
        if not erfolg:
            return 0.0, None
        dauer = schach(ort, z.ort) * (tempo or SW.takte_je_feld(typ, "trupp")) + takte
        return z.wert * erfolg / max(dauer, 1.0), dauer

    def kandidaten(self, typ, ziele_):
        """[(Ziel, Takte, Erfolg)] der Ziele, an denen diese Art etwas ausrichtet."""
        aus = []
        for z in ziele_:
            takte, erfolg = self.am_ziel(typ, z)
            if erfolg > 0:
                aus.append((z, takte, erfolg))
        return aus

    def tour(self, typ, start, kand, rest=None, horizont=HORIZONT):
        """(erwarteter Wert, [(Ziel, Anteil)]): Ziel fuer Ziel das mit dem meisten Wert je Takt, bis der Horizont um ist oder die Einheit wohl
        tot ist. rest: Anteil des Werts, der je Ziel noch offen ist. Anteil: Aussicht, dass gerade diese Einheit das Ziel erledigt."""
        rest = rest or {}
        tempo = SW.takte_je_feld(typ, "trupp")
        ort, t, lebt, wert, weg = start, 0.0, 1.0, 0.0, []
        offen = [k for k in kand if rest.get(k[0].schluessel, 1.0) >= ABGEDECKT]
        while offen and lebt > REST:
            best = None
            for i, (z, takte, erfolg) in enumerate(offen):
                dauer = schach(ort, z.ort) * tempo + takte
                q = z.wert * rest.get(z.schluessel, 1.0) * erfolg / max(dauer, 1.0)
                if best is None or q > best[0]:
                    best = (q, i, dauer)
            if t + best[2] > horizont:
                break
            z, _, erfolg = offen.pop(best[1])
            wert += lebt * z.wert * rest.get(z.schluessel, 1.0) * erfolg
            weg.append((z, lebt * erfolg))
            lebt *= erfolg
            t += best[2]
            ort = z.ort
        return wert, weg


def kaufen(
    wissen,
    kasse,
    feuer,
    preise,
    start,
    ziele_,
    bleibt=None,
    hoechstens=None,
    zielarten=None,
    erlaubt=None,
    vorhanden=None,
):
    """([(Typ, Anzahl)], Begruendung). Immer die Art mit dem meisten Wert je Gold, bis Gold, Leute am Feuer oder Ziele ausgehen.
    preise: {Typ: Gold} der Arten, die jetzt gekauft und auch gesteuert werden koennen. bleibt: so viele Leute bleiben je Art am Feuer.
    erlaubt(Typ, Ziel) -> bool: ob das Modul dieser Art das Ziel ueberhaupt angreift (raid.RaidEinsatz.greift_an).
    vorhanden: [(Typ, Ort)] eigener Einheiten, die ein Modul schon fuehrt (raid.RaidEinsatz.vorhanden)."""
    bleibt, hoechstens = bleibt or {}, hoechstens or {}
    zielarten = zielarten or {}

    # B-182: einer Art wird nur zugetraut, was ihr Modul angreift: die Zielart ("g" Gebaeude, "e" Einheiten) und, Reihe 5, die Ziele, die
    # das Modul nicht meidet
    def _kand(typ):
        return wissen.kandidaten(
            typ,
            [
                z
                for z in ziele_
                if z.schluessel[0] in zielarten.get(typ, "ge")
                and (erlaubt is None or erlaubt(typ, z))
            ],
        )

    kand = {typ: _kand(typ) for typ in preise}
    rest = {z.schluessel: 1.0 for z in ziele_}
    # B-182 Eichung: Was eigene Einheiten im Feld schon erledigen, zaehlt fuer keinen Kauf. Ohne das zaehlte jede Runde dieselben Ziele neu
    # (Reihen 1 bis 5: fuer die Sklaven je Partie 676 bis 12.935 Punkte erwartet, 17 bis 156 erreicht)
    for typ, ort in vorhanden or ():
        if typ not in kand:
            kand[typ] = _kand(typ)
        for z, anteil in wissen.tour(typ, ort, kand[typ], rest)[1]:
            rest[z.schluessel] *= 1.0 - anteil
    gekauft, erwartet = collections.Counter(), collections.defaultdict(float)
    while True:
        best = None
        for typ, preis in preise.items():
            if (
                preis > kasse
                or feuer - bleibt.get(typ, 0) < 1
                or gekauft[typ] >= hoechstens.get(typ, 10**6)
            ):
                continue
            wert, weg = wissen.tour(typ, start, kand[typ], rest)
            if wert > 0 and (best is None or wert / preis > best[0]):
                best = (wert / preis, typ, wert, weg, preis)
        if best is None:
            break
        _, typ, wert, weg, preis = best
        gekauft[typ] += 1
        erwartet[typ] += wert
        kasse -= preis
        feuer -= 1
        for z, anteil in weg:
            rest[z.schluessel] *= 1.0 - anteil
    text = [
        "WIRKUNG-KAUF: %d %s (Typ %d), erwartet %.1f Punkte, %.2f je Gold"
        % (n, EH.name(t), t, erwartet[t], erwartet[t] / (n * preise[t]))
        for t, n in sorted(gekauft.items())
    ]
    return sorted(gekauft.items()), text
