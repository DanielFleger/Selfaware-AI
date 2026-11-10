# -*- coding: utf-8 -*-
"""B-182 Obergrenze fuer eigene Kaempfer (Daniel 10.11. 23:16: "unsere ki soll maximal 20 einheiten haben insgesamt ich will
sehen ob sie sich dran haelt").

Gezaehlt wird live aus dem Kern: jede lebende eigene Einheit einer Kampfart (baukasten/einheiten.py ARTEN), ohne Lord.
Arbeiter, Bauern und Tiere zaehlen nicht. Jeder Werbebefehl des Lenkers geht durch game/ucp/laden.befehl; ist dort eine
Obergrenze gesetzt und erreicht, geht er nicht ans Spiel und wird je Art gezaehlt.

Ein Geworbener steht erst einige Takte spaeter in der Kerntabelle. Bis dahin zaehlt er als "unterwegs" mit, damit zwei
Werbungen kurz hintereinander die Grenze nicht gemeinsam ueberschreiten. Erscheint er nicht (kein Gold, kein Bauer), verfaellt
er nach UNTERWEGS_TAKTE Takten.
"""
import collections

from selfaware.baukasten.einheiten import ARTEN

LORD = 55
KAEMPFER = frozenset(t for t in ARTEN if t != LORD)
UNTERWEGS_TAKTE = 50      # selbst gesetzt: so lange zaehlt eine Werbung, die der Kern noch nicht zeigt


def kaempfer(welt, sp):
    """Nummern der lebenden eigenen Kaempfer im Weltbild des Kerns (ohne Lord)."""
    return sorted(n for n, e in welt.einheiten.items()
                  if e.get("besitzer") == sp and e.get("typ") in KAEMPFER and e.get("leben", 1) > 0)


class Obergrenze:
    def __init__(self, grenze, kern, sp=1):
        """grenze: hoechste Zahl eigener Kaempfer; kern: Leser mit lesen() -> Weltbild (kern_leitung.Leitung)."""
        self.grenze, self.kern, self.sp = int(grenze), kern, sp
        self.erlaubt_n = 0
        self.abgelehnt = collections.Counter()
        self.hoechst = 0               # die meisten Kaempfer, die der Kern je zeigte
        self._unterwegs = []           # Kern-Takte der Werbungen, die der Kern noch nicht zeigt
        self._basis = None             # Kaempferzahl bei der ersten noch offenen Werbung

    def zahl(self):
        """Kaempfer laut Kern plus Werbungen, die er noch nicht zeigt. Liest der Kern nicht, gilt die Grenze als erreicht."""
        try:
            w = self.kern.lesen()
        except Exception:
            return self.grenze
        n = len(kaempfer(w, self.sp))
        self.hoechst = max(self.hoechst, n)
        self._unterwegs = [t for t in self._unterwegs if w.tick - t < UNTERWEGS_TAKTE]
        if not self._unterwegs or n >= (self._basis or 0) + len(self._unterwegs):
            self._unterwegs, self._basis = [], None
            return n
        return max(n, self._basis + len(self._unterwegs))

    def erlaubt(self, typ):
        """True, wenn eine Einheit der Art typ jetzt geworben werden darf; merkt sie dann als unterwegs."""
        if typ not in KAEMPFER:
            return True
        n = self.zahl()
        if n >= self.grenze:
            self.abgelehnt[typ] += 1
            return False
        try:
            tick = self.kern.lesen().tick
        except Exception:
            tick = 0
        if self._basis is None:
            self._basis = n
        self._unterwegs.append(tick)
        self.erlaubt_n += 1
        return True

    def stand(self):
        return "Grenze %d, erlaubt %d, abgelehnt %d %s, hoechstens %d gesehen" % (
            self.grenze, self.erlaubt_n, sum(self.abgelehnt.values()), dict(self.abgelehnt), self.hoechst)
