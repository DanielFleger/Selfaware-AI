"""P5 (B-157): Einheitenbefehle eines Auftraggebers ueber den Befehlsweg des Kerns statt ueber logik.lua.

Plan: docs/plans/Plan_Befehlsweg.md. Zuerst nur die Assassinen; der Schalter steht standardmaessig aus (kernweg=ja beim
Start des Lenkers). Uebersetzt werden die Befehle, die der Lenker sonst an das Modul schickt. Was der Kern nicht kann
(zum Beispiel "halten"), geht ans Modul; die betroffenen Einheiten gibt der Kern vorher frei, damit nie zwei Stellen
dieselbe Einheit fuehren. Den Fortgang (angenommen, abgesetzt, wirkt; E7) meldet der Kern im Ergebnisfeld des Rings.
"""

import collections

from selfaware.game import kern_leitung as KL

ASSASSINEN = 1
VORSTOSS = 2
BRANDTRUPP = 3
# Eine Flucht, die nach so vielen Takten nicht abgesetzt ist, ist ueberholt: die naechste Lenker-Runde entscheidet neu.
# Vorlaeufiger Wert, nicht gemessen (Messung M3 im Plan).
FLUCHT_FRIST = 60
UNTERWEGS = {KL.OFFEN, KL.ERG_ANGENOMMEN, KL.ERG_ABGESETZT, KL.ERG_GEPARKT}
ART_NAMEN = {KL.LAUF: "laufen", KL.ANGRIFF_EINHEIT: "einheit", KL.ANGRIFF_GEBAEUDE: "gebaeude"}


def uebersetze(befehl):
    """Lenker-Befehl -> (Einheiten, Art, a, b, Vorrang) oder None, wenn der Kern ihn nicht ausfuehren kann."""
    c = befehl.get("angriff")
    if not isinstance(c, dict) or not c.get("einheiten"):
        return None
    einheiten = list(c["einheiten"])
    if "lauf" in c:
        vorrang = KL.VORRANG_FLUCHT if c.get("vorrang") else KL.VORRANG_LAUFEN
        return einheiten, KL.LAUF, int(c["lauf"][0]), int(c["lauf"][1]), vorrang
    if "ziel" in c:
        return einheiten, KL.ANGRIFF_EINHEIT, int(c["ziel"]), 0, KL.VORRANG_ANGRIFF
    if "gebaeude" in c:
        return einheiten, KL.ANGRIFF_GEBAEUDE, int(c["gebaeude"]), 0, KL.VORRANG_ANGRIFF
    return None


def einheiten_von(befehl):
    """Einheiten eines Befehls, der beim Modul bleibt."""
    c = befehl.get("halten") or befehl.get("angriff") or {}
    return c.get("nr") or c.get("einheiten") or []


class Kernweg:
    """Legt die Befehle eines Auftraggebers in den Auftragsring und verfolgt ihren Fortgang."""

    def __init__(self, leitung, auftraggeber=ASSASSINEN):
        self.leitung = leitung
        self.auftraggeber = auftraggeber
        self.uebergeben = set()
        self.offen = {}
        self.stand = collections.Counter()

    def _uebergeben(self, einheiten):
        for nr in einheiten:
            if nr not in self.uebergeben:
                self.leitung.auftrag(KL.UEBERNEHMEN, nr, self.auftraggeber)
                self.uebergeben.add(nr)

    def _freigeben(self, einheiten):
        for nr in einheiten:
            if nr in self.uebergeben:
                self.leitung.auftrag(KL.FREIGEBEN, nr)
                self.uebergeben.discard(nr)

    def _einreihen(self, einheiten, art, a, b, vorrang, tick):
        frist = tick + FLUCHT_FRIST if vorrang == KL.VORRANG_FLUCHT else 0
        self._uebergeben(einheiten)
        for nr in einheiten:
            ring = self.leitung.auftrag(art, nr, a, b, vorrang, frist, self.auftraggeber)
            self.offen[ring] = art

    def ausweichen(self, einheiten, ziel, trupp=1):
        """B-174: Die Einheiten laufen als ein Trupp im Zickzack nach ziel; ein neues Ziel geht ohne Bruch weiter. False, wenn
        der Ring voll ist: Dann bleibt der Befehl beim Modul."""
        try:
            self._uebergeben(einheiten)
            for nr in einheiten:
                self.leitung.auftrag(
                    KL.AUSWEICHEN, nr, int(ziel[0]), int(ziel[1]), trupp, 0, self.auftraggeber
                )
        except RuntimeError:
            self.stand["ring voll"] += 1
            return False
        return True

    def freigeben(self, einheiten):
        """Gibt die Einheiten zurueck, bevor das Modul sie fuehrt: Ihr Zickzack endet, nie fuehren zwei Stellen dieselbe Einheit."""
        try:
            self._freigeben(einheiten)
        except RuntimeError:
            self.stand["ring voll"] += 1

    def senden(self, liste):
        """Legt alle uebersetzbaren Befehle in den Ring und gibt zurueck, was ans Modul gehen muss. Ist der Ring voll
        (der Kern arbeitet nicht), geht der Befehl ebenfalls ans Modul."""
        tick = self.leitung.takt()
        rest = []
        for befehl in liste:
            u = uebersetze(befehl)
            beim_modul = u is None
            try:
                if beim_modul:
                    self._freigeben(einheiten_von(befehl))
                else:
                    self._einreihen(*u, tick)
            except RuntimeError:
                self.stand["ring voll"] += 1
                beim_modul = True
            if beim_modul:
                rest.append(befehl)
        self.fortgang()
        return rest

    def aufraeumen(self, lebend):
        """Gibt tote oder nicht mehr gefuehrte Einheiten frei."""
        try:
            self._freigeben(sorted(self.uebergeben - set(lebend)))
        except RuntimeError:
            self.stand["ring voll"] += 1

    def fortgang(self):
        """Liest die Ergebnisse offener Auftraege; endgueltige werden gezaehlt und vergessen."""
        for ring in list(self.offen):
            if not self.leitung.lesbar(ring):
                self.stand["nicht mehr lesbar"] += 1
                del self.offen[ring]
                continue
            e = self.leitung.ergebnis(ring)
            if e is None or e in UNTERWEGS:
                continue
            name = KL.ERGEBNIS_NAMEN.get(e, str(e))
            self.stand[f"{name}/{ART_NAMEN[self.offen.pop(ring)]}"] += 1
        return self.stand

    def bericht(self):
        self.fortgang()
        teile = ", ".join(f"{k} {v}" for k, v in sorted(self.stand.items()))
        return f"KERNWEG: {len(self.uebergeben)} Einheiten, {len(self.offen)} unterwegs; {teile or 'noch nichts'}"


def oeffnen(spiel_ordner, auftraggeber=ASSASSINEN):
    """Kernweg zum laufenden Spiel oder None, wenn der Kern (passender Aufbau) nicht bereit ist. Eine Namensdatei
    ohne laufendes Spiel ergaebe einen leeren Speicher; das erkennt lesen() am ungueltigen Kopf."""
    try:
        leitung = KL.Leitung(spiel_ordner)
        return Kernweg(leitung, auftraggeber) if leitung.lesen() else None
    except (OSError, ValueError, KL.FalscherAufbau):
        return None
