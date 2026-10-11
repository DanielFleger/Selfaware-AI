# -*- coding: utf-8 -*-
"""Stillstand-Waechter fuer den Lenker (SAI 11.10., Daniel 17:22 "warum faellt dir nicht auf, dass das Vorratslager voll
ist? eigentlich sollte das direkt auffallen"; 22:37 "ja mach weiter" zu: Waechter in den Lenker, Lagerteil anbauen, wenn
ein Arbeiter mit Ware in der Hand wartet und kein Teil frei ist).

Anlass (gemessen 17:20-17:27): alle 4 Lagerteile Holz (je Teil EINE Ware), der Getreidebauer stand ab Tick 7.341 still
(Zustand 9, Ladung 0 - fertiger Weizen am Feld), Muehle/Baeckerei 15.000 Ticks leer. Ein angebautes Teil -> nach ~100 Ticks
lieferte er. Die Wirtschaft (wirtschaft.py, Lager erweitern) zaehlte nur Holz als "unterwegs" - Weizen, Mehl, Stein,
Eisen, Pech, Hopfen in der Hand eines wartenden Arbeiters sah sie nicht.

Je Runde:
  - jede eigene Einheit mit Arbeitsplatz: steht sie am selben Fleck, wie lange schon;
  - MELDEN: Lagertraeger MIT Ware ab MELDEN_AB Ticks einmal je Fleck, mit Zustand, Ladung und leeren Lagerteilen;
  - HANDELN: ab HANDELN_AB Ticks mit Ladung > 0 und keinem leeren Lagerteil -> Lagerteil anbauen (einmal je Fleck,
    nicht solange ein Lagerbau offen ist, nicht bei lager_stopp = Endphase "Lager waechst nicht mehr" - dann nur melden).
Die Speicherabfrage der Lagerteile (+0x184 Menge) laeuft nur, wenn ein Fall eintritt - nicht jede Runde."""

MELDEN_AB = 1500        # wie im Messaufbau (arbeitsgang_nahrung.py); fand 17:27 sofort die ersetzten Bauern
HANDELN_AB = 300        # im WARTEZUSTAND mit Ware in der Hand; Fehlalarm kostet nur ein Lagerteil (0 Holz, Ascension und Liga)
# Wartezustand "will abliefern, Lager fasst nichts": Holzfaeller 7 (abgelesen UpdateWoodcutter 0x0054C710, Wissensstand),
# Getreidebauer 9 (gemessen 11.10.: Zustand 9 mit Ladung 0 - der Weizen bleibt am Feld -, erst nach dem Anbau Zustand 10
# mit Ladung 2; Live-Probe 22:49: Zustand 9, Ladung 0, alle 4 Teile Holz). Im Wartezustand zaehlt darum NICHT die Ladung. Andere Lagertraeger (Steinochse 9,
# Pechmann 10, Muehle 15, Bergmann 31) erst ab MELDEN_AB: Mueller stehen beim Mahlen ~680 Ticks MIT Ware still (Lauf 17:32).
WARTEZUSTAND = {3: 7, 11: 9}
LAGERTRAEGER = (3, 9, 10, 11, 15, 31)
LAGER = 10


class Stillstand:
    def __init__(self, sp, teil_menge, baue_lager, lager_offen=lambda: False):
        """teil_menge(nr) -> Menge im Lagerteil nr (Speicher +0x184); baue_lager() -> Ort oder None;
        lager_offen() -> True, solange ein Lagerbau im Auftragsbuch offen ist."""
        self.sp, self.teil_menge, self.baue_lager, self.lager_offen = sp, teil_menge, baue_lager, lager_offen
        self.ort = {}               # nr -> (ort, seit_tick, gemeldet, gehandelt)
        self.faelle = []

    def leere_teile(self, G):
        teile = [n for n, g in G.items() if g["besitzer"] == self.sp and g["typ"] == LAGER]
        return sum(1 for n in teile if self.teil_menge(n) == 0), len(teile)

    def schritt(self, t, L, G, lager_stopp=False):
        ev, frei = [], None
        for n, e in L.items():
            if e.get("besitzer") != self.sp or not e.get("arbeitsplatz"):
                continue
            ort = (e["x"], e["y"])
            alt = self.ort.get(n)
            if not alt or alt[0] != ort:
                self.ort[n] = (ort, t, False, False)
                continue
            _, seit, gemeldet, gehandelt = alt
            dauer = t - seit
            wartet = WARTEZUSTAND.get(e["typ"]) == e.get("zustand")
            mit_ware = e["typ"] in LAGERTRAEGER and (e.get("ladung", 0) > 0 or wartet)
            ab = HANDELN_AB if wartet else MELDEN_AB
            # Melden nur MIT Ware: die Lenker-Probe 22:46 meldete 58 Zeilen, fast alle normales Warten ohne Ware (Leute am
            # Lagerfeuer Typ 1, Ochsen beim Beladen 9, Holzfaeller 3, Steinmetze 7) - das verdeckt den echten Fall
            if mit_ware and ((dauer >= MELDEN_AB and not gemeldet) or (dauer >= ab and not gehandelt)):
                if frei is None:
                    frei = self.leere_teile(G)
                fall = {"t": t, "nr": n, "typ": e["typ"], "ort": ort, "seit": seit, "zustand": e.get("zustand"),
                        "ladung": e.get("ladung", 0), "arbeitsplatz": e.get("arbeitsplatz"),
                        "lagerteile_leer": frei[0], "lagerteile": frei[1]}
                tat = ""
                if mit_ware and dauer >= ab and not gehandelt:
                    gehandelt = True
                    if frei[0] == 0:
                        if lager_stopp:
                            tat = " -> Lager voll, aber Endphase (lager_stopp): kein Anbau"
                        elif self.lager_offen():
                            tat = " -> Lager voll, Lagerbau schon offen"
                        else:
                            o = self.baue_lager()
                            tat = " -> Lager voll: Lagerteil angebaut bei %s" % (o,)
                            frei = (frei[0], frei[1])      # Anbau zaehlt erst, wenn er steht
                            fall["anbau"] = o
                if dauer >= MELDEN_AB:
                    gemeldet = True
                self.ort[n] = (ort, seit, gemeldet, gehandelt)
                self.faelle.append(fall)
                ev.append("STILLSTAND Einheit %d (Typ %d, Arbeitsplatz %s) seit Tick %d bei %s, Zustand %s, Ladung %d, "
                          "Lagerteile leer %d von %d%s" % (n, e["typ"], e.get("arbeitsplatz"), seit, ort, e.get("zustand"),
                                                          e.get("ladung", 0), frei[0], frei[1], tat))
        for n in [n for n in self.ort if n not in L]:
            del self.ort[n]
        return ev
