"""P5 (B-157): Einheitenbefehle eines Auftraggebers ueber den Befehlsweg des Kerns statt ueber logik.lua.

Plan: docs/plans/Plan_Befehlsweg.md. Zuerst nur die Assassinen; der Schalter steht standardmaessig aus (kernweg=ja beim
Start des Lenkers). Uebersetzt werden die Befehle, die der Lenker sonst an das Modul schickt. Was der Kern nicht kann
(zum Beispiel "halten"), geht ans Modul; die betroffenen Einheiten gibt der Kern vorher frei, damit nie zwei Stellen
dieselbe Einheit fuehren. Den Fortgang (angenommen, abgesetzt, wirkt; E7) meldet der Kern im Ergebnisfeld des Rings.
"""

import collections

from selfaware.execution import kampfschutz
from selfaware.game import kern_leitung as KL

ASSASSINEN = 1
VORSTOSS = 2
BRANDTRUPP = 3
RAID = 4  # S155: der Nahkampf-Raid (Wegfuehrung KERN_ZWECKE)
# Eine Flucht, die nach so vielen Takten nicht abgesetzt ist, ist ueberholt: die naechste Lenker-Runde entscheidet neu.
# Vorlaeufiger Wert, nicht gemessen (Messung M3 im Plan).
FLUCHT_FRIST = 60
UNTERWEGS = {KL.OFFEN, KL.ERG_ANGENOMMEN, KL.ERG_ABGESETZT, KL.ERG_GEPARKT}
ART_NAMEN = {
    KL.LAUF: "laufen",
    KL.LAUF_DURCHSETZEN: "laufen_durch",
    KL.ANGRIFF_EINHEIT: "einheit",
    KL.ANGRIFF_GEBAEUDE: "gebaeude",
}


def uebersetze(befehl):
    """Lenker-Befehl -> (Einheiten, Art, a, b, Vorrang) oder None, wenn der Kern ihn nicht ausfuehren kann."""
    c = befehl.get("angriff")
    if not isinstance(c, dict) or not c.get("einheiten"):
        return None
    einheiten = list(c["einheiten"])
    if "lauf" in c:
        vorrang = KL.VORRANG_FLUCHT if c.get("vorrang") else KL.VORRANG_LAUFEN
        # S155: "durchsetzen" - der Kern wiederholt den Laufbefehl, solange die Einheit gegen einen anderen als den erlaubten Gegner kaempft
        art = KL.LAUF_DURCHSETZEN if c.get("durchsetzen") else KL.LAUF
        return einheiten, art, int(c["lauf"][0]), int(c["lauf"][1]), vorrang
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
        self.erlaubt = {}  # S155: Einheit -> Gegner, gegen den der Kampf gewollt ist (zuletzt an den Kern gegeben)
        self.version = None  # S159: Kern-Version beim Oeffnen (oeffnen setzt sie)
        # B-182 Kettenpruefung je Befehl (micro/chain_audit.ChainAudit): sieht jeden Ringauftrag und sein Ergebnis; setzt der Lenker
        self.beobachter = None

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
                self.erlaubt.pop(nr, None)

    def _einreihen(self, einheiten, art, a, b, vorrang, tick):
        frist = tick + FLUCHT_FRIST if vorrang == KL.VORRANG_FLUCHT else 0
        self._uebergeben(einheiten)
        for nr in einheiten:
            ring = self.leitung.auftrag(art, nr, a, b, vorrang, frist, self.auftraggeber)
            self.offen[ring] = art
            if self.beobachter is not None:
                self.beobachter.from_ring(ring, nr, art, a, b, tick)

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

    def erlauben(self, nr, gegner):
        """S155: Gegen diesen Gegner (Einheitennummer, 0 = keiner) setzt der Kern den Laufbefehl der Einheit nicht durch - der Kampf gegen
        ihn ist gewollt, er ist ihr Ziel. Geht nur bei einer Aenderung in den Ring. False, wenn der Ring voll ist."""
        gegner = int(gegner or 0)
        if self.erlaubt.get(nr, 0) == gegner:
            return True
        try:
            self._uebergeben([nr])
            self.leitung.auftrag(KL.GEGNER_ERLAUBT, nr, gegner, 0, 0, 0, self.auftraggeber)
        except RuntimeError:
            self.stand["ring voll"] += 1
            return False
        self.erlaubt[nr] = gegner
        return True

    @property
    def kann_ketten(self):
        """S159: Kennt der Kern die Wegpunktkette (Version ab KL.KETTE_AB)?"""
        return (self.version or 0) >= KL.KETTE_AB

    def kette(self, nr, punkte, danach=None):
        """S159: haengt an den eben gesendeten Laufauftrag der Einheit die weiteren Wegpunkte und zuletzt den Angriff (("einheit" oder
        "gebaeude", Nummer)) - der Kern gibt den naechsten Schritt im Takt, in dem die Einheit ankommt. False, wenn der Ring voll ist."""
        try:
            for p in punkte:
                self.leitung.auftrag(KL.WEGPUNKT, nr, int(p[0]), int(p[1]), 0, 0, self.auftraggeber)
            if danach is not None:
                art = KL.DANACH_EINHEIT if danach[0] == "einheit" else KL.DANACH_GEBAEUDE
                self.leitung.auftrag(art, nr, int(danach[1]), 0, 0, 0, self.auftraggeber)
        except RuntimeError:
            self.stand["ring voll"] += 1
            return False
        self.stand["ketten"] += 1
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
        # B-182 S118: nicht noch einmal an eine Einheit, die schon kaempft
        liste, meld = kampfschutz.liste(liste)
        for m in meld:
            print(m, flush=True)
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
            if self.beobachter is not None:
                self.beobachter.ring_result(ring, name)
        return self.stand

    def bericht(self):
        self.fortgang()
        teile = ", ".join(f"{k} {v}" for k, v in sorted(self.stand.items()))
        return f"KERNWEG: {len(self.uebergeben)} Einheiten, {len(self.offen)} unterwegs; {teile or 'noch nichts'}"


def oeffnen(spiel_ordner, auftraggeber=ASSASSINEN, mindestens=0):
    """Kernweg zum laufenden Spiel oder None, wenn der Kern (passender Aufbau, Version ab mindestens) nicht bereit ist. Eine Namensdatei
    ohne laufendes Spiel ergaebe einen leeren Speicher; das erkennt lesen() am ungueltigen Kopf."""
    try:
        leitung = KL.Leitung(spiel_ordner)
        w = leitung.lesen()
        if not w or w.kern < mindestens:
            return None
        k = Kernweg(leitung, auftraggeber)
        k.version = w.kern
        return k
    except (OSError, ValueError, KL.FalscherAufbau):
        return None
