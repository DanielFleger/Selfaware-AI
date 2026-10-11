# -*- coding: utf-8 -*-
"""Gemessene Ertragsmodelle der Nahrungsquellen unter Ascension-Balance (SAI 11.10., Instanz 4, Pruefstand gegen eine
Ratte mit leerer KI). Jede Zahl mit ihrer Quelle; nichts hier ist geschaetzt - was offen ist, steht als OFFEN dabei.

Grundlage (Wissensregister L58-L60, Handbuch "Arbeitsgang-Messung"):
  - Laufen 16 Ticks je Feld (Schachabstand), gerade wie schraeg (143 Teilstrecken, Lauf 22:40).
  - Aepfel in der GRUPPE: Umlauf ~ 830 + 26 * Abstand Huette-Kornspeicher, 4,46 Aepfel je Gang (3 Plantagen 13/20/51 Felder,
    je <= 5 %, Lauf 22:40); erste Aepfel ~1.500 Ticks nach dem Bau. EINZELN: 2,2 je 1.000 (Lauf 22:44, Ursache OFFEN).
  - Milch: 6 Kaese je Umlauf; Umlauf 2.126 bei 21 Feldern Hof-Kornspeicher -> 1.454 + 32 * Abstand (1 Lauf, 17:32).
  - Jaeger: 9 Fleisch je Umlauf; Umlauf 5.633 bei 93 Feldern Huette-Kornspeicher -> 2.657 + 32 * Abstand (1 Lauf, 17:32).
    Herde endlich? OFFEN.
  - Brot: 1 Weizen -> 1 Mehl -> 8 Brot; Getreidefarm 2 Weizen je ~1.500 Ticks bei ~30 Feldern zum Lager (Bauer ~85 %
    Laufen; Umlauf 1.508 bei Schachabstand 31 -> 516 + 32 * Abstand); Baeckerei 8 Brot je Backgang, mit 3 nahen Baeckereien ~10 Brot/1.000 (Lauf 22:57);
    erstes Brot ~9.500 Ticks nach dem Bau. Weizen bei kurzem Abstand (Wachstum als Grenze?) OFFEN.
Die Zahlen gelten fuer die gemessene Balance; unter einer anderen Balance muessen sie neu gemessen werden."""

LAUF_JE_FELD = 16

# je Quelle: Ware, Ladung je Gang, feste Zeit je Umlauf, Ticks je Feld Abstand (hin und zurueck), erste Lieferung nach
# dem Bau, Arbeiter, fruchtbare Felder, Messung
QUELLEN = {
    "apfel_gruppe": dict(ware="apfel", ladung=4.46, fest=830, je_feld=26, erste=1500, arbeiter=1, boden=100,
                         quelle="Lauf 22:40 (3 Plantagen)"),
    "milch": dict(ware="kaese", ladung=6.0, fest=1454, je_feld=2 * LAUF_JE_FELD, erste=5000, arbeiter=1, boden=100,
                  quelle="Lauf 17:32 (1 Hof)"),
    "jaeger": dict(ware="fleisch", ladung=9.0, fest=2657, je_feld=2 * LAUF_JE_FELD, erste=5000, arbeiter=1, boden=0,
                   quelle="Lauf 17:32 (1 Jaeger, Herde 93 Felder vom Kornspeicher)"),
    "weizen": dict(ware="weizen", ladung=2.0, fest=516, je_feld=2 * LAUF_JE_FELD, erste=5900, arbeiter=1, boden=81,
                   quelle="Lauf 17:32 und 22:57 (je 1 Farm, ~30 Felder vom Lager)"),
}
APFEL_EINZELN_JE_1000 = 2.2          # Lauf 22:44: eine Plantage allein am selben Platz
BROT_JE_MEHL = 8                     # Lauf 22:57: 20 Weizen = 13 Backgaenge + 4 Mehl im Lager
BROT_ERSTE = 9500                    # Lauf 22:57: erstes Brot bei Tick 9.453 (alles beim Start gebaut)
BAECKEREI_JE_1000 = 10.0 / 3         # Lauf 22:57: 3 nahe Baeckereien zusammen ~10 Brot je 1.000 (weizenbegrenzt - Untergrenze)
MUEHLE_ARBEITER, BAECKEREI_ARBEITER = 3, 1


def je_1000(quelle, abstand):
    """Ertrag je 1.000 Ticks im Dauerbetrieb bei gegebenem Abstand (Felder) zur Ablage."""
    q = QUELLEN[quelle]
    return 1000.0 * q["ladung"] / (q["fest"] + q["je_feld"] * abstand)


def brotkette(abstand_farm_lager, farmen=1):
    """Brot je 1.000 Ticks einer Kette aus `farmen` Getreidefarmen; Baeckereien so viele, wie der Weizen traegt.
    Gibt (brot_je_1000, baeckereien, arbeiter)."""
    weizen = farmen * je_1000("weizen", abstand_farm_lager)
    brot = weizen * BROT_JE_MEHL
    baeckereien = max(1, int(round(brot / BAECKEREI_JE_1000 + 0.49)))
    arbeiter = farmen + MUEHLE_ARBEITER + baeckereien
    return brot, baeckereien, arbeiter


if __name__ == "__main__":
    # Gegenprobe gegen die Messungen selbst (Abweichung muss klein sein, sonst ist das Modell falsch abgeschrieben)
    for name, ab, ist in (("apfel_gruppe", 13, 4.0), ("apfel_gruppe", 51, 2.0), ("milch", 21, 2.82), ("jaeger", 93, 1.60),
                          ("weizen", 31, 1.33)):
        print("%-13s Abstand %3d: Modell %.2f, gemessen %.2f" % (name, ab, je_1000(name, ab), ist))
    print("Brotkette 30 Felder: %.1f Brot/1.000 mit %d Baeckereien, %d Arbeiter (gemessen ~10 mit 3)" % brotkette(30))
