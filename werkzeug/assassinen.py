# -*- coding: utf-8 -*-
"""Angriff mit Assassinen: in kleine Trupps aufteilen, moeglichst viele Gebaeude zerstoeren, ohne Verluste
(M16, Daniel 04.10.2026 21:54, 22:54, 23:13: "wirklich splitten und maximale Gebaeude kaputt machen, besonders auf
die Bogenschuetzen aufpassen").

Gelernt aus Partie 2 (23:12): ein grosser Trupp zerstoerte 11 Gebaeude, verlor aber 76 von 90 Assassinen - fast alle
nach Zielen 90-212 Felder tief im Feindgebiet und beim Rueckzug quer durch das Feindheer.

Je Runde (Lagebild + Gebaeudeliste aus EINEM Aufruf, siehe erstes_spiel.runde_lesen):
  - Mitglieder werden auf Trupps zu GROESSE verteilt (neue Anwerbungen fuellen den kleinsten Trupp auf).
  - Gefahr je Feind nach Art: Fernkaempfer (Bogen, Armbrust, Schleuder, Pferdebogen) FERN Felder, sonst NAH.
  - Jeder Trupp: Feind zu nah oder ein Mitglied verletzt -> ganzer Trupp zum NAECHSTEN sicheren Ort.
    Sonst ohne Ziel: Gebaeude mit bestem Wert / (Abstand + 20), hoechstens MAX_WEG Felder weg, Ziel und Weg frei von
    Gefahr, und nicht schon Ziel eines anderen Trupps. Alle Mitglieder des Trupps gebuendelt auf dieses Gebaeude.
Grenzen (offen): Reichweiten FERN/NAH sind Startwerte, nicht gemessen; Tuerme nicht beruecksichtigt.
"""
import math
from laden import befehl
from waechter import sicherster_ort
from bedrohung import fingerabdruck, bedarf as lage_bedarf, lagen_laden
import schussfeld
import sicht
import lordschutz
import json as _json
import os as _os

# 17.10. (Plan_Entdeckung.md, Daniel 10:10 "Gebaeude: Leben minus Schaden je Takt je Einheit"): Arbeit bis zerstoert in
# Assassinen-Takten je Gebaeudeart, gemessen in 11 Mitschriften (Median; daten/gebaeude_arbeit.json). Zeit = Arbeit / Zahl.
# Unbekannte Arten: der Median aller gemessenen Arten (benannt in der ZIELWAHL-Zeile als "Arbeit geschaetzt").
try:
    ARBEIT = {int(k): v["median"] for k, v in _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "daten",
                                                                          "gebaeude_arbeit.json"))).items()}
except (OSError, ValueError):
    ARBEIT = {}
ARBEIT_SONST = sorted(ARBEIT.values())[len(ARBEIT) // 2] if ARBEIT else 200
TEMPO = 14.6               # Takte je Feld, Assassine (L80, gemessen 17.10.)
# 17.10.: Lebensverlust des Ziels je Assassine und Takt im Nahkampf (daten/nahkampf_raten.json, gemessen), sonst 230
try:
    NAHKAMPF_RATE = {int(k): v for k, v in _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "daten",
                                                                      "nahkampf_raten.json")))["leben_je_takt"].items()}
except (OSError, ValueError, KeyError):
    NAHKAMPF_RATE = {}
# Wert einer feindlichen Einheit = Anwerbepreis in Gold (L63 gemessen: arab. Bogen 60, Sklave 5, Schleuder 12, Assassine 70,
# Pferdebogen 75, arab. Schwert 100, Feuerwerfer 125). Euro-Bogen 22 und Armbrust 23: UNGEMESSEN, wie arab. Bogen angesetzt.
EINHEIT_WERT = {70: 60, 71: 5, 72: 12, 73: 70, 74: 75, 75: 100, 76: 125, 22: 60, 23: 60}
EINHEIT_WERT_GEMESSEN = {70, 71, 72, 73, 74, 75, 76}

ASSASSINE = 73
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 55, 70, 71, 72, 73, 74, 75, 76}
FERNKAMPF = {22, 23, 70, 72, 74, 76}
WERT = {
    # Daniel 05.10. 19:05: Ausbildungslager, Steinbrueche, Haeuser usw. sind mehr wert als Apfelplantagen und, wenn
    # nicht allzu schwer bewacht, fast noch bessere Ziele. Kornspeicher-Bonus (04.10. 22:54). STARTWERTE, Rangfolge von Daniel.
    9: 100, 8: 100,                     # Kaserne, Soeldnerlager (Ausbildungslager)
    19: 100,                            # Kornspeicher
    # 17.10. (Daniel: "nie den unzerstoerbaren Abstellhaufen des Steinbruchs angreifen"): Steinhaufen Typ 21 (L8) raus -
    # in den 1017-Partien 89x Ziel, 6x "zerstoert" (vermutlich nur mit seinem Steinbruch)
    20: 80, 5: 70, 6: 60,               # Steinbruch, Eisenmine, Pechgrube
    11: 70, 12: 70, 13: 70, 14: 70, 15: 70,  # Waffenkammer und Waffenbauer
    24: 60, 25: 50, 35: 40,             # Ingenieurs-, Tunnelgraebergilde, Stall
    1: 60,                              # Huetten (Wohnraum = Arbeiter)
    # 19.10. (Daniel: "unten stehen Apfelfarmen und hinten ist keine Verteidigung - du nimmst die Farmen alle mit, dann ein paar
    # Holzfaeller, sneakst dich hinten in die Wirtschaft"): Nahrung und Holz der KI zuerst - Apfel 30 -> 70, Holzfaeller 50 -> 60
    4: 50, 3: 60,                       # Ochsenjoch, Holzfaeller
    22: 40, 18: 40, 17: 35, 34: 35, 33: 40, 30: 30, 36: 40, 37: 40, 38: 40,  # Wirtshaus, Brauerei, Baeckerei, Muehle, Milch, Weizen, Kirchen
    32: 70, 7: 30,                      # Apfelplantage, Jaegerhuette
    # 19.10. (Daniel: "auf dem Weg nimmt ein Assassine kein Markt mit, den ich als Mensch sofort mitgesnackt haette - die KI ist
    # ohne Markt komplett gelaehmt"): Markt hoechster Wert (vorher 20, unter der Apfelplantage) - der Zielwechsel unterwegs
    # (WECHSEL 1,5 x Wert je Weg) nimmt ihn dann mit; ab TEUER zwei Plaetze
    26: 150}
# Liga-Balance (liga_ai.json ranges): alle Bogen/Armbrust 40 Felder - eine Zahl fuer "in Schussweite" (Daniel 23:18: Schuetzen-
# Gefahr auf 40; live_6: Assassine starb bei Tick 8.527, naechster Bogenschuetze 26 Felder weg, gezaehlt wurde nur bis 16)
SCHUSSWEITE = 40
GROESSE, FERN, NAH, MAX_WEG = 1, SCHUSSWEITE, 8, 30   # 1: jeder Assassine einzeln, eigene Gruppe (Daniel 23:32; Modul reserviert Gruppen je Takt)

def lord_machbar(n, lord_leben, beschuss_je_tick, schaden=98.6, tod_alle=90, leben=12500, schritt=10, bis=6000):
    """12.10. 01:55: reicht ein Angriff von n Assassinen? Gemessen 1012d (lordkampf_messen.py): 98,6 Schaden je Assassine und
    Tick am Lord, der Lord toetet alle ~90 Ticks eine. Dazu Beschuss am Lord je Tick und Assassine (schussfeld, gemessene
    Saetze) - vorsichtig: jede Assassine bekommt ihn ganz (nicht auf die Gruppe verteilt). Gibt (machbar, Ticks, Ueberlebende)."""
    hp, lh, t = [leben] * max(0, n), float(lord_leben), 0
    while lh > 0 and hp and t < bis:
        t += schritt
        lh -= len(hp) * schaden * schritt
        hp = [h - beschuss_je_tick * schritt for h in hp if h - beschuss_je_tick * schritt > 0]
        if hp and t % tod_alle < schritt:
            hp.pop()
    return lh <= 0, t, len(hp)


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def feinde(L, sp):
    return [((e["x"], e["y"]), FERN if e["typ"] in FERNKAMPF else NAH)
            for e in L.values() if e["besitzer"] not in (0, sp) and e["typ"] in TRUPPE]

def gefaehrdet(p, fe, zuschlag=0):
    return any(schach(p, f) < r + zuschlag for f, r in fe)

def weg_sicher(von, nach, fe):
    n = max(1, int(schach(von, nach) // 4))
    return not any(gefaehrdet((von[0] + (nach[0] - von[0]) * i / n, von[1] + (nach[1] - von[1]) * i / n), fe)
                   for i in range(n + 1))

def naechster_sicherer(L, orte, von, fe, sp=1):
    gut = [o for o in orte if not gefaehrdet(o, fe, 4)]
    return min(gut, key=lambda o: schach(o, von)) if gut else sicherster_ort(L, orte, sp)

class Trupp:
    def __init__(self, nr):
        self.nr, self.mitglieder, self.ziel, self.ziel_typ, self.zurueck, self.daheim = nr, set(), None, None, False, set()
        self.bereit = None     # Bereitstellungsplatz, zu dem der Trupp gerade laeuft
        self.bereit_ziel = None  # das feindliche Gebaeude, vor dem er bereitsteht

class Angriffstrupp:
    def __init__(self, sp=1, mitglieder=(), rueckzug=(125, 155)):
        self.sp, self.rueckzug = sp, tuple(rueckzug)
        self.trupps, self.leben_max = [], {}
        self.bilanz = {"gebaeude": {}, "verluste": set()}
        self.aufnehmen(mitglieder)

    @property
    def mitglieder(self):
        return set().union(*[t.mitglieder for t in self.trupps]) if self.trupps else set()

    def aufnehmen(self, nummern):
        schon = self.mitglieder
        for n in nummern:
            if n in schon or n in self.bilanz["verluste"]:
                continue
            frei = [t for t in self.trupps if len(t.mitglieder) < GROESSE]
            if not frei:
                self.trupps.append(Trupp(len(self.trupps) + 1)); frei = [self.trupps[-1]]
            min(frei, key=lambda t: len(t.mitglieder)).mitglieder.add(n)
            schon.add(n)

    def schritt(self, L, G, sichere_orte=None):
        ereignis = []
        fe = feinde(L, self.sp)
        orte = list(sichere_orte or [self.rueckzug])
        belegt = {t.ziel for t in self.trupps if t.ziel is not None}
        for t in self.trupps:
            for n in list(t.mitglieder):
                if n not in L or L[n]["besitzer"] != self.sp:
                    self.bilanz["verluste"].add(n); t.mitglieder.discard(n); t.daheim.discard(n)
                    ereignis.append("VERLUST: Trupp %d Mitglied %d" % (t.nr, n))
            for n in t.mitglieder:
                self.leben_max[n] = max(self.leben_max.get(n, 0), L[n]["leben"])
            if t.ziel is not None and t.ziel not in G:
                self.bilanz["gebaeude"][t.ziel_typ] = self.bilanz["gebaeude"].get(t.ziel_typ, 0) + 1
                ereignis.append("Trupp %d: Gebaeude %d (Typ %d) zerstoert" % (t.nr, t.ziel, t.ziel_typ))
                belegt.discard(t.ziel); t.ziel = None
            aktiv = [n for n in t.mitglieder if n not in t.daheim]
            if not aktiv or (len(t.mitglieder) < GROESSE and t.ziel is None and t.bereit is None and not t.zurueck):
                continue      # Trupp waechst noch - ab 6 geht er los (Daniel 23:18)
            mitte = (sum(L[n]["x"] for n in aktiv) / len(aktiv), sum(L[n]["y"] for n in aktiv) / len(aktiv))
            # erst unter 60 % zurueck (Partie 6: jeder Kratzer schickte den Trupp heim, Schaden kam oft von Feinden
            # 17-29 Felder weg - Quelle offen, vermutlich Tuerme)
            verletzt = [n for n in aktiv if L[n]["leben"] < 0.6 * self.leben_max[n]]
            in_gefahr = any(gefaehrdet((L[n]["x"], L[n]["y"]), fe) for n in aktiv)
            if verletzt and not in_gefahr and not t.zurueck:
                # nur die Schwerverletzten heim, der Rest macht weiter
                ort = naechster_sicherer(L, orte, mitte, fe, self.sp)
                befehl({"halten": {"nr": verletzt, "x": ort[0], "y": ort[1]}}, 1.0, bis="HALTEN")
                t.daheim |= set(verletzt)
                ereignis.append("Trupp %d: %d unter 60 %% heim nach %s" % (t.nr, len(verletzt), tuple(ort)))
                aktiv = [n for n in aktiv if n not in t.daheim]
                if not aktiv:
                    continue
                verletzt = []
            if in_gefahr and not t.zurueck:
                # Kaempfen statt fliehen (Daniel 23:32): Fernkaempfer direkt daneben erledigen; gegen Nahkaempfer nur in
                # Ueberzahl (eigene Assassinen im Umkreis 6 mindestens doppelt so viele wie feindliche Nahkaempfer im Umkreis 8)
                fern_nah = sorted((schach(mitte, (e["x"], e["y"])), m) for m, e in L.items()
                                  if e["besitzer"] not in (0, self.sp) and e["typ"] in FERNKAMPF and schach(mitte, (e["x"], e["y"])) <= 6)
                nah_feinde = [m for m, e in L.items() if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE
                              and e["typ"] not in FERNKAMPF and schach(mitte, (e["x"], e["y"])) <= 8]
                freunde = sum(1 for e in L.values() if e["besitzer"] == self.sp and e["typ"] == ASSASSINE and schach(mitte, (e["x"], e["y"])) <= 6)
                ziel_einheit = fern_nah[0][1] if fern_nah else (min(nah_feinde, key=lambda m: schach(mitte, (L[m]["x"], L[m]["y"])))
                                                                 if nah_feinde and freunde >= 2 * len(nah_feinde) else None)
                if ziel_einheit is not None:
                    befehl({"angriff": {"einheiten": aktiv, "ziel": ziel_einheit}}, 1.0, bis="ANGRIFF")
                    belegt.discard(t.ziel); t.ziel = None
                    ereignis.append("Trupp %d kaempft gegen Einheit %d Typ %d (Freunde %d, Nahkaempfer %d)" % (
                        t.nr, ziel_einheit, L[ziel_einheit]["typ"], freunde, len(nah_feinde)))
                    continue
                # naechster Feind (Art, Abstand) - Messung der echten Reichweite (Daniel 23:22: einverstanden)
                feind_e = [(schach(mitte, (e["x"], e["y"])), e["typ"]) for e in L.values()
                           if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE]
                nf = min(feind_e) if feind_e else (999, 0)
                # weg vom Angreifer: 15 Felder in Gegenrichtung, wenn dort sicher - sonst naechster sicherer Ort
                fx, fy = min(((e["x"], e["y"]) for e in L.values() if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE),
                             key=lambda f: schach(mitte, f), default=(mitte[0], mitte[1]))
                dx, dy = mitte[0] - fx, mitte[1] - fy
                lang = max(abs(dx), abs(dy), 1)
                weg = (int(mitte[0] + 15 * dx / lang), int(mitte[1] + 15 * dy / lang))
                ort = weg if (0 < weg[0] < 400 and 0 < weg[1] < 400 and not gefaehrdet(weg, fe)) else naechster_sicherer(L, orte, mitte, fe, self.sp)
                ereignis.append("MESSUNG Trupp %d: naechster Feind Typ %d in %d Feldern, verletzt %d" % (t.nr, nf[1], nf[0], len(verletzt)))
                befehl({"halten": {"nr": list(t.mitglieder), "x": ort[0], "y": ort[1]}}, 1.0, bis="HALTEN")
                t.daheim |= set(verletzt); t.zurueck = True; t.bereit, t.bereit_ziel = None, None
                belegt.discard(t.ziel); t.ziel = None
                ereignis.append("Trupp %d zurueck nach %s (%s)" % (t.nr, tuple(ort), ("verletzt %s" % verletzt) if verletzt else "Feind nah"))
                continue
            if t.zurueck:
                if in_gefahr:
                    continue
                aktiv = [n for n in t.mitglieder if n not in t.daheim]
                if not aktiv:
                    continue
                befehl({"halten": {"los": aktiv}}, 1.0, bis="HALTEN")
                t.zurueck = False
            if t.ziel is None:
                # sofort das naechste Ziel (Daniel 23:14: nicht stehenbleiben) - Suchkreis stufenweise 30 / 45 / 60
                kand = []
                for weite in (MAX_WEG, 45, 60):
                    for n, g in G.items():
                        if g["besitzer"] in (0, self.sp) or g["typ"] not in WERT or n in belegt or not g.get("erreichbar", 1):
                            continue
                        ort = (g["x"], g["y"])
                        d = schach(mitte, ort)
                        if d > weite or gefaehrdet(ort, fe, 2) or not weg_sicher(mitte, ort, fe):
                            continue
                        kand.append((WERT[g["typ"]] / (d + 20.0), n, g, d))
                    if kand:
                        break
                if not kand:
                    # Bereitstellung (Daniel 23:18: ab 6 sofort nach vorne, nicht am Soeldnerlager warten): sicher bis
                    # 12 Felder vor das naechste ungeschuetzte, erreichbare feindliche Gebaeude laufen
                    if t.bereit is not None and schach(mitte, t.bereit) > 3:
                        continue
                    andere = [o.bereit_ziel for o in self.trupps if o is not t and o.bereit_ziel is not None]
                    ziele = sorted(((schach(mitte, (g["x"], g["y"])), (g["x"], g["y"])) for n, g in G.items()
                                    if g["besitzer"] not in (0, self.sp) and g["typ"] in WERT and g.get("erreichbar", 1)
                                    and n not in belegt and not gefaehrdet((g["x"], g["y"]), fe, 4)
                                    and all(schach((g["x"], g["y"]), a) > 10 for a in andere)))
                    for d, (gx, gy) in ziele:
                        f = max(0.0, (d - 12.0) / d) if d else 0.0
                        platz = (int(mitte[0] + (gx - mitte[0]) * f), int(mitte[1] + (gy - mitte[1]) * f))
                        if weg_sicher(mitte, platz, fe) and not gefaehrdet(platz, fe, 4):
                            befehl({"halten": {"nr": aktiv, "x": platz[0], "y": platz[1]}}, 1.0, bis="HALTEN")
                            t.bereit, t.bereit_ziel = platz, (gx, gy)
                            ereignis.append("Trupp %d (%d) rueckt vor nach %s (Ziel-Gebiet %s)" % (t.nr, len(aktiv), platz, (gx, gy)))
                            break
                    continue
                if t.bereit is not None:
                    befehl({"halten": {"los": aktiv}}, 1.0, bis="HALTEN")
                    t.bereit, t.bereit_ziel = None, None
                if kand:
                    w, n, g, d = max(kand)
                    befehl({"angriff": {"einheiten": aktiv, "gebaeude": n}}, 1.0, bis="ANGRIFF")
                    t.ziel, t.ziel_typ = n, g["typ"]; belegt.add(n)
                    ereignis.append("Trupp %d (%d) -> Gebaeude %d Typ %d bei (%d,%d), %d Felder" % (t.nr, len(aktiv), n, g["typ"], g["x"], g["y"], d))
        return ereignis

    def bericht(self):
        b = self.bilanz
        return "zerstoert %d Gebaeude %s, eigene Verluste %d, Trupps %d" % (
            sum(b["gebaeude"].values()), b["gebaeude"], len(b["verluste"]), len(self.trupps))


class Einzeln:
    """Jeder Assassine einzeln (Daniel 04.10. 23:35): Befehl auf das NAECHSTE erreichbare feindliche
    Wirtschaftsgebaeude; hoechstens JE_GEBAEUDE auf eines (Daniel 05.10. 00:00), sonst sofort das naechste.
    schritt() gibt (ereignisse, befehle) - alle Befehle einer Runde gehen gesammelt in EINEM Aufruf ans Spiel,
    das Modul setzt sie nacheinander ab.

    Gefahr (05.10., gemessen in Partie 9e: 21 von 25 Toten hatten KEIN Ziel und standen untaetig im Schussfeld,
    meist ~10 Bogenschuetzen 9-19 Felder weg; bei 223 Verletzungen stand der naechste Fernkaempfer meist 9-30 Felder weg):
      17.10.: "Reichweite"/"Gefahr" heisst jetzt sicht.py - sichtbar nur bei waehlbarem Feind <= 20 Feldern (Arbeiter
      verraten nicht), Beschuss nur mit freier Schusslinie, Verfolgung nur nach Haltung (L75-L80, Plan_Entdeckung.md).
      1. Ohne Ziel wartet ein Assassine dort, wo ihn keiner sieht und kein Trupp ihm nachlaeuft (sicht.sicher).
      2. Verletzt und beschiessbar, und der Beschuss bis zum Ende des Auftrags uebersteigt sein Leben: Rueckzug - ausser ein Fernkaempfer steht direkt daneben
         (bis ZUSCHLAGEN Felder) und hoechstens 1 Nahkaempfer im Umkreis 5: dann ihn angreifen (Daniel 04.10. 23:4x).
      3. Zielwahl: Gebaeude mit mehr als ZIEL_FERN_MAX Fernkaempfern im Umkreis ZIEL_FERN auslassen; wer unter
         SCHWACH Leben hat, nimmt nur Ziele ganz ohne Fernkaempfer bis SCHWACH_FERN.
    Die Zahlen sind STARTWERTE aus dieser Messung, nicht geeicht - jede Zielwahl schreibt ihre Gefahrenzahlen mit
    (ZIELWAHL-Zeilen), jede Verletzung und jeder Tod ihr Umfeld (MESSUNG-Zeilen), damit die naechste Partie sie eicht.
    Gegenprobe je Runde: laeuft ein Assassine nicht zu seinem Gebaeude (Laufziel im Lagebild weiter als ZIEL_NAH),
    bekommt er den Befehl neu - der Plan im Kopf zaehlt nicht, nur das Laufziel im Spiel."""
    JE_GEBAEUDE = 1          # 12.10. Daniel 00:41/00:44: EIN Assassine je Gebaeude reisst ein, bei teuren (Wert >= TEUER) zwei;
    LORD_TAKT_R = 3          # 12.10. gestaffelter Anlauf - 17.10. ERSETZT durch die Bereitstellung (BEREIT_R), bleibt fuer alte Pruefungen
    SCHUETZEN_MAX, SCHUETZEN_MAX_TEUER, SCHUETZEN_NOT = 1, 2, 3   # (01:54 nicht mehr in der Zielwahl)
    KOSTEN = 70              # Preis einer Assassine (L63, gemessen)
    VERWEILEN = 300          # 17.10. ERSETZT durch ARBEIT (gemessen) / Zahl - bleibt nur fuer alte Pruefungen stehen   # 12.10.: gute Tauschgeschaefte (Stellgroessen)
    WEGPUNKT_NAH = 3         # 12.10.: so nah am Wegpunkt gilt er als erreicht
    # 18.10. (Daniel: "der Assassine hat alle 1 Sekunde angehalten"; Probepartie: er erreichte jeden Wegpunkt, stand dort
    # (Zustand 1) bis zur naechsten Lenker-Runde): der naechste Wegpunkt geht hinaus, wenn er bis zur naechsten Runde ankommt -
    # Vorlauf = gemessene Rundenlaenge / TEMPO + VORLAUF_RESERVE Felder
    VORLAUF_RESERVE = 2
    VORLAUF_MAX = 8
    LOEWE = 45               # 18.10. (Daniel: Assassine von Loewen getoetet; UT_LIONSHWOLF, Besitzer 0) - Nahkampf-Gefahr
    BEUTE_R = 15             # 12.10.: Fernkaempfer am Boden in diesem Umkreis werden gejagt (Stellgroesse)
    # 17.10. (1017j, Daniel mit Bild: der erste Assassine jagte bei Tick 3.313 einen Feuerwerfer neben einem arab. Bogen,
    # Todesrisiko 47 %, "aussenrum gehen und unbeschaut die Gebaeude zerstoeren haette mehr gebracht"): gejagt wird nur,
    # wer kein Gebaeude-Ziel hat, solange es mehr lohnende Raid-Plaetze als Raider gibt gar nicht, und hoechstens BEUTE_RISIKO
    BEUTE_RISIKO = 0.10
    # Laufzeit-Typen mit begehbarem Dach (abgelesen VillageStudio/lib/aiv_typen.lua AIV_ZU_LAUFZEIT): Tuerme 74-78,
    # Torhaus gross 45 / klein 46, Steinbergfried 41. Andere Bergfried-Arten sind dort nicht aufgefuehrt (offen)
    ERHOEHT = {41, 45, 46, 74, 75, 76, 77, 78}
    HOCH_R = 4               # Umkreis um die Gebaeudemitte, der als "oben" gilt (groesster Turm/Torhaus ~6 Felder breit)
    LORD_ABSTAND = 6         # Beute neben ihrem Lord wird nicht gejagt (der Lord schlaegt Assassinen)
    TEUER = 100              # mehr nur, wenn unsere Assassinen dort angegriffen werden (+1 je angegriffenem) - vorher fest 6
    WECHSEL = 1.5            # 12.10. (Daniel 00:41 "sofort reagieren, auch mit Ziel, auf ein neu gebautes besseres Ziel")
    ZIEL_NAH = 8           # gemessen 05.10.: Gebaeudeangriff -> Laufziel 1-2 Felder neben dem Gebaeude
    NEU_NACH = 4           # Runden (je ~30 Ticks bei Tempo 1000), bis ein Befehl im Spiel sichtbar sein muss
    VOLL = 12500           # gemessen 05.10.: Leben eines frisch angeworbenen Assassinen
    SICHER_FERN, SICHER_NAH = SCHUSSWEITE, 10      # 17.10.: fuer Warten/Rueckzug ersetzt durch sicht.sicher (L75/L77)
    RUECKZUG_FERN = SCHUSSWEITE
    UEBERMACHT_R, FLUCHT_RUHE = 10, 2  # 4a (Daniel 22:16): Umkreis fuer "mehr Feinde als eigene", Runden ohne Verfolger bis zum Wiederangriff
                                       # (raidzuerst_4: mit 5 erst im Kontakt erkannt - Daniel 22:25 "er muss instant verstehen, wann das ist")
    FLUCHT_FREI = 15       # 4a: erst frei, wenn kein feindlicher Nahkaempfer naeher (raidzuerst_3: mit 10 hoerte er zu frueh auf)
    # 4a in Spielzeit (Daniel 23:01 "minimale Tickanzahlen"): gemessen gehen Assassinen ~1 Feld je 13-17 Ticks, echt
    # blockiert stand er 30+ Ticks (raidzuerst_4). Ohne Spielzeit (Pruefung) zaehlt eine Runde RUNDE_TICKS.
    BLOCK_TICKS, RUHE_TICKS, RUNDE_TICKS = 30, 30, 15
    # 4a (Daniel 22:37 "ja, beides"): Arbeiter, die Assassinen schlagen, zaehlen bei der Uebermacht mit. Gewicht = ihr Schaden
    # gegen Assassinen / Schaden eines Speertraegers (25), Liga-Balance meleeDamageVs "Arabian assassin": Holzfaeller 10,
    # Steinmetz 10, Schmied 10, Jaeger 5, Tunnelgraeber 20. Nur im Umkreis ARBEITER_R (sie schlagen nur, wer neben ihnen steht).
    # 12.10. 01:39: auf den Massstab von NAH_GEFAHR (Assassine = 1) umgerechnet - vorher Speertraeger = 1, Speertraeger ist
    # unter Ascension 0,2 Assassinen (powerLevel 4/20) -> alle Gewichte x 0,2
    ARBEITER_GEFAHR = {3: 0.08, 7: 0.08, 19: 0.08, 6: 0.04, 5: 0.16}
    ARBEITER_R = 3
    # Staerke gegen Assassinen in Assassinen-Einheiten = (Schaden gegen Assassine x Leben) / (Assassinen-Schaden gegen sie x 12.500),
    # alles Liga-Balance: Speer 25x12.500/(120x12.500)=0.21, Pike 30x80.000/(120x12.500)=1.6, Streitkolben 70x25.000/(120x12.500)
    # =1.17, Schwert/Ritter 150x40.000/(120x12.500)=4.0, arab. Schwert 125x32.000/(120x12.500)=2.67, Assassine 1.0.
    # Fernkaempfer 0.2 = STARTWERT (ihr Pfeilschaden laesst sich so nicht umrechnen); Lord 0 - die Verfolger nie zu unserem Lord.
    # Gemessen raidzuerst_6: der Waechter warf bei Tick 2.954 alle 13 Verteidiger (Bogen, Speer UND Lord) gegen einen
    # Verfolger bei (166,262), bei 3.416 noch 9 gegen den naechsten; am Ende 6 eigene tot, 0 Verfolger tot. Mit diesen Werten
    # zaehlen 7 Speer + 5 Bogen 2.5 - die Rechnung ist ein Startwert; die FLUCHT-Zeilen schreiben sie mit, damit nachgemessen wird.
    # GEMESSEN schlaegt GERECHNET (raidzuerst_6 und _7): 13 bzw. 11 Verteidiger (Bogen 22, Speer 24, Lord) toeteten in zwei
    # Laeufen 0 von 3 verfolgenden Assassinen und verloren 6 bzw. 3 Mann - vermutlich sehen sie die getarnten Assassinen gar
    # nicht. Darum Speer/Bogen/Armbrust/arab. Bogen/Schleuder/Pferdebogen 0, bis ein Lauf zeigt, dass sie einen toeten.
    # Pike/Streitkolben/Schwert/Ritter: gerechnet, nicht gemessen (wir haben keine).
    STAERKE = {24: 0.0, 25: 1.6, 26: 1.17, 27: 4.0, 28: 4.0, 75: 2.67, 73: 1.0, 22: 0.0, 23: 0.0, 70: 0.0, 72: 0.0, 74: 0.0, 55: 0.0}
    # 12.10. 01:37 (Daniel: "es macht keinen Sinn, vor den Sklaven wegzurennen"): Nahkampf-Gefahr je Feind in Assassinen-
    # Einheiten = powerLevel (abgelesen ascension_ai.json "units") / powerLevel der Assassine (20). Vorher zaehlte jeder
    # Nahkaempfer 1 - drei Sklaven (powerLevel 1, die Assassine trifft sie mit 450 statt 120) galten als Uebermacht.
    # Ihr Lord: 5 (gemessen 1012d: toetet alle ~90 Ticks eine Assassine). Unbekannte Typen: 1.
    NAH_GEFAHR = {24: 0.2, 25: 1.0, 26: 0.75, 27: 2.0, 28: 2.5, 71: 0.05, 73: 1.0, 75: 0.8, 55: 5.0,
                  45: 2.0}   # 18.10. Loewe: STARTWERT (1 Probe: Assassine 12.500 -> 2.900 im Kampf)
    VERFOLGER_AB = 0.2       # schwaechere Feinde (Sklaven) gelten nicht als Verfolger
    HEIM_R, HEIM_ABSTAND = 15, 25   # eigene Truppen bis HEIM_R um Lager/Bergfried; zu schwach -> Fluchtpunkt mind. HEIM_ABSTAND weg
    # T2 Im Kreis fuehren (Daniel 22:49): Ring mit Radius KREIS_R um eine Mitte KREIS_MITTE Felder in der ersten Fluchtrichtung,
    # mindestens KREIS_RAND vom Kartenrand (raidzuerst_9: geradeaus bis an den Rand, dort eingeholt). STARTWERTE.
    KREIS_R, KREIS_MITTE, KREIS_RAND = 20, 35, 40
    ZUSCHLAGEN = 3
    ZIEL_FERN, ZIEL_FERN_MAX = 20, 2
    SCHWACH, SCHWACH_FERN = 0.6, 25
    VORAUS_FERN, VORAUS_ANZAHL = 10, 3   # 17.10. ERSETZT (4b rechnet Beschuss x Restzeit gegen Leben) - Startwert aus 9f
    STAPEL_AB = 12         # Daniel 05.10. 00:30: "oben stehen noch so 30 Assassinen, die nichts machen" - ab so vielen
                           # Wartenden greifen ALLE gebuendelt einen erreichbaren Fernkaempfer am Boden an (perfekt stapeln)
    STAPEL_RUECKZUG = 0.3  # im Stapel erst unter 30 % Leben zurueck (Daniel: manchmal ist kein Rueckzug besser)
    # Lord-Trupp (Daniel 05.10. 00:52): nebenher immer wieder pruefen; freie Raid-Assassinen gebuendelt auf den Lord -
    # meist reichen 10, steht er allein sogar 5, bei Bogenschuetzen mehr, je nach Feindmenge noch viel mehr.
    # STARTWERTE aus dieser Regel: 5 allein, sonst 10 + 2 je Fernkaempfer + 1 je Nahkaempfer im Umkreis LORD_UMKREIS.
    LORD_ALLEIN, LORD_NORMAL, LORD_JE_FERN, LORD_JE_NAH, LORD_UMKREIS = 5, 10, 2, 1, 15
    LORD_PRUEFEN = 5       # alle 5 Runden (~150 Ticks bei Tempo 1000)
    LORD_WENIG_FEINDE = 5  # Daniel: "auf jeden Fall, wenn keine oder nur noch ein paar Einheiten im Spiel sind"
    # Daniel 05.10. 21:05: je gestapelter sie ankommen, desto wirksamer (Schaden stackt, der Lord trifft nur einen).
    # Wie viele noetig sind, steht nicht mehr als feste Zahl hier (bis 06.10.: sammeln ab 20, Angriff ab 40 - gemeinsam_1
    # griff mit 47-60 an, weil jeder Nachzuegler erst ankommen musste). Daniel 06.10.: nicht pauschal sammeln, die Lage
    # entscheidet, Zeit ist kritisch. Den Bedarf liefert bedrohung.bedarf aus gemessenen Lagen (oder vorlaeufig).
    LORD_SAMMEL_R = 8       # wer so nah am Treffpunkt steht, zaehlt als angekommen
    # Sammeln beginnt spaetestens bei 20 Lebenden, auch wenn der Bedarf hoeher ist: beim Raiden sterben laufend
    # Assassinen (bedarf_partie_1: Sammeln erst ab Bedarf 40 -> nie 40 gleichzeitig am Leben, 36 Verluste, kein
    # Lord-Angriff bis 28.747). Gemessen mit 20 (gemeinsam_1, Codex): Verluste 10-18, 3 Siege.
    LORD_SAMMELN_AB = 20
    LORD_SAMMEL_ABSTAND = SCHUSSWEITE + 5
    LORD_REST = 3          # weniger Ueberlebende aus dem Angriff -> vorbei, wieder raiden bis zum naechsten Bedarf
    # 17.10. Laptop, Partie 1017h (Lageprotokoll): 35x lief genau EIN Assassine los ("1 laufen los"), 38 von 93 Toten starben
    # am Lord mit 4+ Fernkaempfern im Umkreis 20 - die Rechnung lord_machbar gilt nur, wenn alle zugleich ankommen. Dazu standen
    # im Mittel ~6 Assassinen (= eine Lord-Gruppe) an unserer Burg still (Zustand 105, Laufziel = eigener Ort, 77 % aller
    # Stehzeit): der Angriffsbefehl auf einen Lord hinter Mauern wurde vermutlich ignoriert (nur Laufbefehl 17 sucht einen
    # Kletterweg, Wissensregister), im Lord-Trupp prueft niemand nach. Darum jetzt:
    #   Bereitstellung: jeder der Gruppe laeuft (Laufbefehl, sicherer Weg) zu einem Platz BEREIT_R Felder vom Lord, den kein
    #   waehlbarer Feind sieht (sicht.sicher); erst wenn n_bedarf dort stehen, greifen genau diese zugleich an.
    #   Angriff: wer weiter als ANLAUF_NAH vom Lord steht, bekommt einen LAUFbefehl auf den Lord (Kletterweg), erst daneben
    #   den Angriffsbefehl. Wer STEH_TICKS ohne Spielziel auf demselben Feld steht, faellt aus der Gruppe und raidet.
    BEREIT_R = (24, 28, 32)          # Felder vom Lord: ausserhalb der 20 Felder, in denen der Lord ihn sieht (L75)
    BEREIT_NAH = 3                   # so nah am Platz gilt er als bereit
    BEREIT_MAX = 3000                # Ticks fuer die Bereitstellung, dann Abbruch -> alle raiden
    BEREIT_NEU = 3                   # hoechstens so viele Laufbefehle zum Platz, dann raus aus der Gruppe
    # 17.10. (1017i, Lageprotokoll Tick 30.567-31.005): der Lord stand OBEN auf seinem Bergfried (Typ 41 daneben, Zustand 13);
    # mit 6 schaltete die Gruppe 4-5 Felder vor ihm auf den Angriffsbefehl um, der nicht klettert - Lord 30.000 unveraendert,
    # alle 5 tot. Beim 2. Angriff kam er herunter: -12.900 Leben. Darum Laufbefehl (Kletterweg) bis direkt neben ihn.
    ANLAUF_NAH = 1                   # naeher am Lord: Angriffsbefehl statt Laufbefehl
    STEH_TICKS = 200                 # ohne Spielziel auf demselben Feld -> Lenker-Zustand loesen
    BEREIT_PAUSE = 1000              # nach Abbruch/Ende eines Lord-Versuchs so viele Ticks nur raiden (STARTWERT)
    # Raiden geht vor (Daniel 17.10. "prio ist am Anfang raiden und auch waehrend des laufs spaeter"): eine Lord-Gruppe
    # bekommt nur, wer UEBER die lohnenden Raid-Plaetze hinaus da ist (Plaetze = freie Gebaeude ohne Beschuss am Ziel x
    # Assassinen je Gebaeude). Spaetestens LORD_SPAETESTENS Ticks nach dem Lord-Schutz darf der Lord trotzdem dran (STARTWERT).
    # 17.10. (Daniel: "wenn die gegnerische Wirtschaft brachliegt, kann man sich Zeit nehmen und erst die Wirtschaft
    # entmannen"): kein Zwang mehr - None = der Lord kommt nur mit dem Ueberschuss ueber die Raid-Plaetze dran
    LORD_SPAETESTENS = None
    FRONT_AB = 30                    # ohne Ziel weiter als so viele Felder vom naechsten Feindgebaeude -> nach vorn warten
    FRONT_R = (35, 45)               # Warteplaetze: Ring um den naechsten feindlichen Lord (STARTWERT)
    # 17.10. (1017k, Daniel: "wie kann man nicht sehen, dass da auch Fernkaempfer sind - er wurde gespottet und von ihnen
    # getoetet"): am Ankerfeld von Gebaeude 144 rechnete das Modell 0,0 Beschuss (das Gebaeude selbst versperrt die Linien),
    # auf seinen Randfeldern - wo die Assassine beim Angriff steht - im Mittel 19,9, hoechstens 37,6; 7 Schuetzen <= 16 Felder.
    # Und gemessen in 1017h-k (feuer_messen.py): echter Lebensverlust je Tick ~2-2,5x das Modell (6+ Schuetzen: 2,8 / 1,1).
    # Darum: Beschuss am Ziel = hoechster Wert der Randfelder; unbeobachtete Ziele (0) zuerst; beobachtete nur bis ZIEL_RISIKO;
    # Risiko x KALIB (STARTWERT aus dem Verhaeltnis echt/Modell, bis die Raten neu geeicht sind).
    # 18.10.: mit den Editor-Raten (L81) und der behobenen Nummer (L85) UEBERschaetzt das Modell den echten Verlust in 1017h-j
    # um das 2-4fache (6+ Schuetzen: Modell 8,4 / echt 2,8 je Takt; nahe Feuerwerfern 57-132 / 13-47) - es rechnet volles Feuer ab
    # dem ersten Takt, im Spiel vergehen 64-170 Takte bis zum ersten Treffer. Kein Aufschlag mehr; vorsichtig bleibt es so ohnehin
    KALIB = 1.0
    ANKUNFT_MIN = 0.3                    # 18.10.: so viel Leben je Assassine muss nach dem Anlauf am Lord uebrig sein (STARTWERT)
    SPERRE_ROUTE = 1500                  # 18.10.: so lange nimmt der Zielwechsel ein Ziel mit gefaehrlicher Route nicht wieder
    ZIEL_RISIKO = 0.05
    # 19.10. (Partie 1018p, alle 5 Tode Feind fuer Feind nachgesehen, treffer_genau.py): wer eine Assassine einmal gesehen hat,
    # schiesst bis ~300 Takte spaeter noch (Armbrust 49 sah 198 bei Tick 7.512, der Bolzen traf 7.750 - laengst ausser Sicht);
    # 265 stand 14 Runden in Sicht, 215 acht, 198 zwei - der Lenker reagierte nur auf Treffer. Neu: gesehen + Schuetze mit
    # Reichweite und Linie -> Auftrag ab, sofort ausser Sicht UND ausser Reichweite dieser Schuetzen, dort bis zum Vergessen
    ENTDECKT_TICKS = 400      # so lange gilt sie fuer jeden Schuetzen, der sie gesehen hat, als Ziel
    ENTDECKT_RAND = 4         # Felder ueber die Reichweite hinaus (Bolzen aus 42 Feldern, 1018p)
    GERADE_TEIL = 20          # lange Wege ohne Umweg trotzdem in Stuecken laufen (198 lief 222 Felder am Stueck)
    FLUCHT_MIN = 8            # 19.10. (1018s): Fluchtpunkte naeher als 8 Felder nur, wenn es weiter weg keinen gibt
    LOEWE_HEIM, LOEWE_GRUPPE, LOEWE_LEBEN = 25, 3, 9000      # 19.10. (1018t): Loewen am Heim gemeinsam erledigen
    RUHE_FELDER = 40          # 19.10.: so viele Felder ohne waehlbaren Feind = voller Ruhe-Bonus (x2)
    FERTIG_TAKTE = 120        # 19.10. (1018x): Restarbeit, die er beim Entdecktwerden noch fertig macht (Erkennen->Treffer 64-170, L81)
    ARBEITER_ZEIT = 120       # 19.10. (1018x, 203 verfolgte einen Arbeiter 500 Takte): so lange darf "mitnehmen" dauern
    SPAEHER_MAX, SPAEHER_R, SPAEHER_ANTEIL = 3, 16, 0.3    # 19.10. (1018w; 1018y: 20 floh vor 2 Sklaven in 13 Feldern - Daniel: "merkt zu spaet, dass er sie besiegen kann")
    # 19.10. (Daniel: "der Assassine geht auf die Kinder und Frauen am Haus - die sind literally nicht angreifbar, maximal auf
    # Arbeiter"): nur echte Arbeiter (Typen aus ablaufanalyse.EINHEIT) - Bauer, Holzfaeller, Jaeger, Steinmetz, Steinbruch-
    # arbeiter, Steinochse, Pechmann, Hofbauern, Apfelbauer, Milchbauer, Schmied, Gerber, Bergmann; NICHT 62-64 (Hausbewohner)
    ARBEITER_TYPEN = {1, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 21, 31}
    ARBEITER_MIT = 2          # 19.10. (Daniel: "nie gesagt aktiv jagen - mitnehmen, wenn er will; zu viel Traffic -> auf ein Minimum"): nur direkt am Weg
    ARBEITER_FREI = 30        # 19.10. (1018v): ... nur, wenn kein waehlbarer Feind naeher als so viele Felder steht
    ARBEITER_SCHWACH = 25     # 19.10. (Daniel): Gewicht schlagender Arbeiter fuer Geschwaechte - ein Holzfaeller (0,08) wiegt dann 2 > die Assassine selbst
    # 19.10. (Daniel: "weisst du, du verlierst den Assassinen eh, weil du Nahkaempfern, die schneller sind, nicht ausweichen
    # kannst - versteck dich, und wenn nicht ausweichbar, zerstoert er lieber noch moeglichst viel: Haeuser, Apfelplantagen,
    # Fern- oder Nahkaempfer, je nachdem wo er den meisten absoluten Wert hat"): LETZTER EINSATZ
    LETZT_R = 30              # Felder: Ziele fuer den letzten Einsatz
    NAH_SCHADEN = 60          # Leben je Takt je feindlichem Nahkaempfer <= 2 Felder (Schaetzung: 3 Loewen 9.200 in ~40 Takten)
    # Das Fluchtmodell rechnet jeden Schuetzen als Dauertreffer; 1018q kamen 34 von 44 Entdeckten ohne Treffer >= 1.000 davon
    # (Zielen ~140 Takte, bewegte Ziele) - fuer Gesunde zaehlt nur ein Viertel, wer ein Bolzen toetet, zaehlt voll
    LETZT_KALIB = 0.25
    # 19.10. (1018q: Einheiten heilen nie - in zwei Partien kein einziger Anstieg; 153 raidete mit 1.960 Leben, 86 mit 2.730,
    # beide starben am naechsten Treffer): unter EIN_TREFFER (ein Armbrustbolzen 6.000 + Rand) nur Ziele, die kein waehlbarer
    # Feind naeher als SICHT + RAND_SCHWACH Feinmass (32 Felder) sieht
    EIN_TREFFER = 6500
    RAND_SCHWACH = 96
    # 18.10. (Tode 1018n, tode_erklaeren.py: Zielwahl nahm 25/29/43 % Todesrisiko auf dem WEG zu unbeobachteten Zielen; das
    # Modell sah am Todesort 88-177 Beschuss je Takt): Risikogrenze auch fuer unbeobachtete Ziele; Schwache noch strenger
    ZIEL_RISIKO_WEG = 0.10
    ZIEL_RISIKO_SCHWACH = 0.02

    def __init__(self, sp=1, pruefe_begehbar=None, wegtest=None):
        self.sp = sp
        self.wegtest = wegtest                     # Funktion(nr, punkte) -> [bool] (Modulbefehl "wegtest", Wegfinder des Spiels)
        self.lordtrupp = {"lord": None, "mitglieder": set(), "seit": 0, "phase": None, "sammelpunkt": None}
        self.pruefe_begehbar = pruefe_begehbar     # Funktion(punkte) -> Menge begehbarer Punkte (Modulbefehl "begehbar")
        self._kand, self._begehbar = {}, set()
        self.mitglieder = set()
        self.ziel, self.ziel_typ, self.jagd, self.warte, self.befohlen = {}, {}, {}, {}, {}
        self.warte_seit = {}
        self.flucht = {}                     # 4a: n -> {seit, ruhig} - weicht einer Nahkampf-Uebermacht aus
        self.schlechte_orte = set()          # Warteplaetze, an die keiner hinlief (9g: Gebaeudemitten)
        self.stapel = {"ziel": None, "mitglieder": set()}
        self.leben, self.umfeld = {}, {}
        self.angriffe = []                   # je Alle-auf-den-Lord: Groesse, Weg, wer kam an, was hielt auf, Lord-Leben
        self.wellen_protokoll = None         # Datei fuer die S1-Messung je Runde (setzt erstes_spiel.py)
        self.gelaende = None                 # unveraenderte Kartenzeilen; einmal je Angriffsprotokoll geschrieben
        # Sichere Wege (12.10., Daniel 01:03/01:08: kuerzester Weg durch den toten Winkel statt geradeaus durch die Schuetzen):
        # n -> {"punkte": [Wegpunkte ohne Ziel], "gebaeude": Nr, "befohlen": Runde}; Gelaende-Gitter einmal je Partie
        self.route, self._frei, self.mit_wegen = {}, None, True
        self._gelaende_geschrieben = False
        # 17.10. Sicht (sicht.py): Haltung der feindlichen Trupps (L77) - Funktion(Gruppen) -> {Gruppe: 0/1/2}, setzt erstes_spiel
        self.lies_haltung, self._haltung, self._haltung_runde = None, {}, -99
        self._sicht = None
        self.runde, self.gemessen, self.ohne_ziel_zuletzt = 0, 0, None
        self.bilanz = {"gebaeude": {}, "verluste": set(), "neu_befohlen": 0, "rueckzug": 0, "zuschlagen": 0, "tote": 0}
        self.akte = {}                       # 19.10.: n -> {"erst": erste Verletzung, "treffer": Runden mit Treffern}
        self.entdeckt = {}                   # 19.10.: n -> {"schuetzen": {Nr}, "bis": Tick, "punkt": Ort, "seit": Tick}
        self.letzter = {}                    # 19.10.: n -> {"ziel": ("g"|"e", Nr), "seit": Tick} - letzter Einsatz
        # 17.10. (1017i nachgespielt: 299.038 Assassinen-Ticks ungesteuert = die ganze Stehzeit an unserer Burg): das Spiel
        # vergibt die Nummer einer toten Einheit neu; "verluste" sperrte die Nummer fuer immer, der neue Assassine stand bis
        # Partieende. Eine Nummer, die nach dem Tod einmal aus dem Lagebild verschwunden war, darf wieder aufgenommen werden.
        self._frei_nr = set()
        self.lagen = lagen_laden()           # gemessene Lagen (daten/lagen_belegt.json) fuer den Lord-Bedarf
        self.angriff_aus = False             # Trainingsstand: nur sammeln, nie angreifen (setzt erstes_spiel.py)
        self.lord_aus = False                # 18.10. (weg=feldzug, Daniel): Assassinen nur fuer die Wirtschaft, Lords toeten Streitkolben
        self.bedarf_zuletzt = None
        self.bedarf_grund, self.bedarf_fa = "", None
        self._raid_plaetze = None            # 17.10.: lohnende Raid-Plaetze der letzten Runde (Raiden geht vor)
        self._steht = {}                     # 17.10.: n -> (Feld, seit Tick) - Stillstand ohne Spielziel
        self._route_sperre = {}              # 18.10.: (n, Gebaeude) -> bis Tick (Route war gefaehrlich)

    def aufnehmen(self, nummern):
        self.mitglieder |= set(n for n in nummern if n not in self.bilanz["verluste"])

    # --- Hilfen ---------------------------------------------------------------------------------------------------
    def _feinde(self, L):
        fern, nah = [], []
        self._arbeiter = []                  # 4a: feindliche Arbeiter, die Assassinen schlagen (ARBEITER_GEFAHR)
        self._alle_arbeiter = []             # 19.10.: alle feindlichen Arbeiter (Beute unterwegs)
        for nr, e in L.items():
            if e["besitzer"] == 0 and e["typ"] == self.LOEWE:
                nah.append((nr, (e["x"], e["y"]), e["typ"]))      # 18.10.: Loewen greifen Assassinen an
                continue
            if e["besitzer"] in (0, self.sp):
                continue
            if e["typ"] not in TRUPPE:
                if e["typ"] in self.ARBEITER_GEFAHR:
                    self._arbeiter.append((nr, (e["x"], e["y"]), e["typ"]))
                if e["typ"] in self.ARBEITER_TYPEN:
                    self._alle_arbeiter.append((nr, (e["x"], e["y"]), e["typ"]))
                continue
            (fern if e["typ"] in FERNKAMPF else nah).append((nr, (e["x"], e["y"]), e["typ"]))
        return fern, nah

    def _bedrohung(self, ort, nah, schwach=False):
        """4a: Gewicht der Feinde um ihn - jeder Nahkaempfer im Umkreis UEBERMACHT_R zaehlt 1, jeder schlagende Arbeiter im
        Umkreis ARBEITER_R sein ARBEITER_GEFAHR-Gewicht; 19.10. (Daniel: "mit wenig Leben lieber den Holzfaellern
        ausweichen"): fuer Geschwaechte x ARBEITER_SCHWACH, so weicht er schon einem einzelnen Holzfaeller aus."""
        f = self.ARBEITER_SCHWACH if schwach else 1.0
        return sum(self.NAH_GEFAHR.get(t, 1.0) for _, p, t in nah if schach(ort, p) <= self.UEBERMACHT_R) + sum(
            f * self.ARBEITER_GEFAHR[t] for _, p, t in getattr(self, "_arbeiter", []) if schach(ort, p) <= self.ARBEITER_R)

    def _staerke(self, einheiten):
        """Staerke gegen Assassinen in Assassinen-Einheiten (STAERKE, aus der Liga-Balance)."""
        return sum(self.STAERKE.get(t, 1.0) for t in einheiten)

    @staticmethod
    def _naechster(ort, liste):
        return min(((schach(ort, p), nr, typ) for nr, p, typ in liste), default=(999, 0, 0))

    @staticmethod
    def _anzahl(ort, liste, r):
        return sum(1 for _, p, _ in liste if schach(ort, p) <= r)

    def _sicherer_ort(self, ort, orte, fern, nah, n=None):
        """17.10. (sicht.py statt fester Umkreise SICHER_FERN/SICHER_NAH): sicher = von keinem waehlbaren Feind gesehen (L75)
        und in keinem Verfolgungs-Radius (Haltung, L77). Zuerst der NAECHSTE sichere unter den kurzen Rueckzugspunkten
        (begehbar laut Modul), dann unter den eigenen Orten; gibt es keinen, der mit dem kleinsten Beschuss und dann dem
        groessten Sicht-Abstand. Gesperrte Orte nie."""
        s = self._sicht
        kurz = [p for p in self._kand.get(n, []) if p in self._begehbar and p not in self.schlechte_orte]
        orte = [o for o in orte if o not in self.schlechte_orte]
        if s is None:
            return max(kurz, key=lambda p: (self._naechster(p, fern)[0], -schach(ort, p))) if kurz else (orte[0] if orte else None)
        for liste in (kurz, orte):
            gut = [p for p in liste if s.sicher(p)]
            if gut:
                return min(gut, key=lambda p: schach(ort, p))
        alle = kurz + orte
        return min(alle, key=lambda p: (s.beschuss(p), -s.sicht_abstand(p), schach(ort, p))) if alle else None

    def _fluchtpunkt(self, ort, nah, n, L=None, nicht_bei=None, mitte=None):
        """4a: wohin vor einer Nahkampf-Uebermacht? Unter den begehbaren Punkten weg vom Feind (_weg_vom_feind, 15-25 Felder,
        geradeaus und 30 Grad seitlich) zuerst der mit den wenigsten Einheiten im Weg (Daniel 22:28: "Arbeiter koennen in
        den Weg kommen - dafuer muesste er wissen, wo diese Personen laufen"; _im_weg zaehlt Ort UND Laufziel jeder Einheit),
        dann der naechste an Heim (Lager/Bergfried = eigene Truppen, dort laufen die Verfolger in unsere Verteidigung).
        nicht_bei: Liste blockierter Fluchtpunkte dieser Flucht (er stand trotz Laufbefehl still) - Punkte dort auslassen,
        alle, sonst pendelt er zwischen zwei blockierten Richtungen.
        Ohne solchen Punkt: das naechste Heim selbst."""
        kurz = [p for p in self._kand.get(n, []) if p in self._begehbar and p not in self.schlechte_orte
                and all(schach(p, b) > 6 for b in (nicht_bei or []))]
        alle_heim = getattr(self, "_heim", [])
        # Daniel 22:37: nur nach Hause, wenn unsere Truppen dort die Verfolger schlagen koennen, sonst seitlich weg.
        # Gemessen raidzuerst_6: er zog 2-3 Assassinen bis an unsere Burg - 6 eigene Soldaten tot, kein Verfolger tot.
        # Verfolger im selben Umkreis zaehlen, in dem er weiter flieht (FLUCHT_FREI) - raidzuerst_8: mit 10 zaehlte ein
        # Verfolger 11 Felder hinter ihm als 0.0, "Heim ok", und er zog ihn doch wieder an die Burg
        verfolger = self._staerke(t for _, p, t in nah if schach(ort, p) <= self.FLUCHT_FREI)
        heim, self._heimgrund = [], []
        for h in alle_heim:
            eigene = 1.0 + self._staerke(e["typ"] for m, e in (L or {}).items()
                                         if m != n and e["besitzer"] == self.sp and e["typ"] in TRUPPE and schach((e["x"], e["y"]), h) <= self.HEIM_R)
            self._heimgrund.append("%s eigene %.1f gegen Verfolger %.1f" % (h, eigene, verfolger))
            if L is None or eigene >= verfolger:
                heim.append(h)
        if kurz:
            weg = (lambda q: self._im_weg(ort, q, L, n)) if L else (lambda q: 0)
            if heim:
                return min(kurz, key=lambda q: (weg(q), min(schach(q, h) for h in heim), -self._naechster(q, nah)[0]))
            if alle_heim and mitte:          # Heim zu schwach: IM KREIS um mitte (T2, Daniel 22:49), nie an unsere Burg
                # raidzuerst_9: geradeaus weg -> 4.000 Ticks bis an den Kartenrand, dort eingeholt. Daniel 22:49: "er fuehrt sie im
                # Kreis herum", waehrenddessen reissen die anderen ihre Wirtschaft ab. Bevorzugt Punkte auf dem Ring KREIS_R um mitte.
                # und nicht unter ihre Fernkaempfer (Pruefung 18: der Ring streifte bei (209,259) ihre Aussenmauer)
                fern = getattr(self, "_fern", [])
                return min(kurz, key=lambda q: (weg(q), self._an_feindburg(q), min(schach(q, h) for h in alle_heim) < self.HEIM_ABSTAND,
                                                self._sicht.beschuss(q) if self._sicht else self._anzahl(q, fern, self.RUECKZUG_FERN),
                                                abs(schach(q, mitte) - self.KREIS_R) // 4, -self._naechster(q, nah)[0]))
            if alle_heim:                    # Heim zu schwach: seitlich weg, die Verfolger NICHT an unsere Burg ziehen
                return min(kurz, key=lambda q: (weg(q), min(schach(q, h) for h in alle_heim) < self.HEIM_ABSTAND,
                                                -self._naechster(q, nah)[0]))
            return min(kurz, key=lambda q: (weg(q), -self._naechster(q, nah)[0]))
        return min(heim, key=lambda h: schach(ort, h)) if heim else None

    def _an_feindburg(self, q):
        """True, wenn q naeher als SCHUSSWEITE an einem feindlichen Lord (ihrer Burg) liegt."""
        return any(schach(q, b) < SCHUSSWEITE for b in getattr(self, "_feindburg", []))

    def _lord_sammelpunkt(self, lord, sichere_orte, fern):
        """Begehbarer Treffpunkt auf unserer Seite, ausser Schussweite von Lord und feindlichen Fernkaempfern.

        Die Richtung kommt vom naechsten bekannten sicheren Ort (Lager/Bergfried). Mehrere Ringe und Winkel sind die
        Gegenprobe gegen ein blockiertes Feld; wenn vor der Burg nichts sicher begehbar ist, faellt die Regel auf den
        naechsten bereits bekannten sicheren Ort zurueck statt einen Sonderfall mitten im Kampf zu erfinden.
        """
        heime = list(sichere_orte or [])
        heim = min(heime, key=lambda h: schach(h, lord)) if heime else (lord[0] - self.LORD_SAMMEL_ABSTAND, lord[1])
        vx, vy = heim[0] - lord[0], heim[1] - lord[1]
        norm = max(abs(vx), abs(vy), 1)
        ux, uy = vx / norm, vy / norm
        kandidaten = []
        for r in (self.LORD_SAMMEL_ABSTAND, self.LORD_SAMMEL_ABSTAND + 5, self.LORD_SAMMEL_ABSTAND + 10):
            for w in (0.0, 0.35, -0.35, 0.7, -0.7):
                rx = ux * math.cos(w) - uy * math.sin(w)
                ry = ux * math.sin(w) + uy * math.cos(w)
                q = (int(round(lord[0] + rx * r)), int(round(lord[1] + ry * r)))
                if 2 <= q[0] <= 397 and 2 <= q[1] <= 397 and schach(q, lord) > SCHUSSWEITE \
                        and all(schach(q, p) > SCHUSSWEITE for _, p, _ in fern):
                    kandidaten.append(q)
        if self.pruefe_begehbar and kandidaten:
            begehbar = self.pruefe_begehbar(kandidaten)
            kandidaten = [q for q in kandidaten if q in begehbar]
        if kandidaten:
            return min(kandidaten, key=lambda q: (schach(q, heim), schach(q, lord)))
        fallback = [q for q in heime if schach(q, lord) > SCHUSSWEITE
                    and all(schach(q, p) > SCHUSSWEITE for _, p, _ in fern)]
        return min(fallback, key=lambda q: schach(q, lord)) if fallback else None

    def _lord_bedarf(self, L, G, ereignis):
        """Bedarf fuer den Lord-Angriff in dieser Lage: (Zahl, Art, Gruppenleben). Meldet jede Aenderung einmal."""
        fa = fingerabdruck(L, G, self.sp)
        n, art, grund, gruppe_leben = lage_bedarf(fa, self.lagen)
        self.bedarf_grund, self.bedarf_fa = grund, fa      # fuer Sammelbeginn/Angriff (bedarf_partie_3: Grund fehlte dort)
        if (n, art) != self.bedarf_zuletzt:
            self.bedarf_zuletzt = (n, art)
            ereignis.append("LORD-BEDARF: %s %s - %s" % (n, "belegt" if art == "belegt" else "VORLAEUFIG", grund))
        return n, art, gruppe_leben

    @staticmethod
    def _lord_gruppe(L, angekommen, n, gruppe_leben):
        """Die kleinste ausreichende Gruppe aus den Angekommenen: die gesuendesten zuerst (so wurde gemessen), mindestens
        n, und zusammen mindestens so viel Leben wie die gemessene Gruppe. None, solange es nicht reicht."""
        reihe = sorted(angekommen, key=lambda k: (-L[k]["leben"], k))
        for k in range(n, len(reihe) + 1):
            gruppe = reihe[:k]
            if gruppe_leben is None or sum(L[g]["leben"] for g in gruppe) >= gruppe_leben:
                return gruppe
        return None

    @staticmethod
    def _im_weg(von, nach, L, ich):
        """Wie viele Einheiten (jeder Besitzer, auch Arbeiter) stehen auf der Strecke von -> nach (1 Feld breit) oder
        laufen gerade dorthin (Laufziel auf der Strecke)?"""
        k = max(schach(von, nach), 1)
        strecke = set()
        for i in range(1, k + 1):
            x = von[0] + (nach[0] - von[0]) * i / k
            y = von[1] + (nach[1] - von[1]) * i / k
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    strecke.add((int(round(x)) + dx, int(round(y)) + dy))
        n = 0
        for nr, e in L.items():
            if nr == ich or schach(von, (e["x"], e["y"])) > k + 2 and schach(von, (e.get("laufx", -99), e.get("laufy", -99))) > k + 2:
                continue
            if (e["x"], e["y"]) in strecke or (e.get("laufx"), e.get("laufy")) in strecke:
                n += 1
        return n

    def _weg_vom_feind(self, ort, fern, nah):
        """Kandidaten fuer einen KURZEN Rueckzug: 15/20/25 Felder weg vom Schwerpunkt der nahen Feinde, geradeaus und
        30 Grad links/rechts (Partie 9h: 210 Rueckzuege quer ueber die Karte nach Hause, 37 Assassinen starben im Laufen;
        Partie 2/5: kurz vom Angreifer weg war das Beste)."""
        # Nahkaempfer bis FLUCHT_FREI (15): solange einer so nah ist, flieht er (4a) - mit SICHER_NAH (10) gab es fuer einen
        # Verfolger 11-15 Felder hinter ihm keinen einzigen Fluchtpunkt, er blieb stehen (Pruefung 16)
        nahe = [p for _, p, _ in fern if schach(ort, p) <= self.RUECKZUG_FERN] + [p for _, p, _ in nah if schach(ort, p) <= max(self.SICHER_NAH, self.FLUCHT_FREI)]
        if not nahe:
            return []
        cx, cy = sum(p[0] for p in nahe) / len(nahe), sum(p[1] for p in nahe) / len(nahe)
        dx, dy = ort[0] - cx, ort[1] - cy
        lang = math.hypot(dx, dy) or 1.0
        dx, dy = dx / lang, dy / lang
        aus = []
        for k in (20, 15, 25):
            # 0 / 30 / 60 / 90 Grad: seitlich (60/90) braucht 4a, wenn die eigene Burg genau in Fluchtrichtung liegt und zu
            # schwach ist (Pruefung 16: alle Punkte geradeaus/30 Grad lagen 10-24 Felder vor der Burg)
            for w in (0.0, 0.52, -0.52, 1.05, -1.05, 1.57, -1.57):
                rx = dx * math.cos(w) - dy * math.sin(w)
                ry = dx * math.sin(w) + dy * math.cos(w)
                x, y = int(round(ort[0] + rx * k)), int(round(ort[1] + ry * k))
                if 2 <= x <= 397 and 2 <= y <= 397:
                    aus.append((x, y))
        return aus

    def umgebung(self, n, L, G, fern, nah):
        """Umfeld fuer die MESSUNG-Zeilen."""
        ort = (L[n]["x"], L[n]["y"])
        nf, nn = self._naechster(ort, fern), self._naechster(ort, nah)
        feind = min(nf, nn)
        gb = min(((schach(ort, (g["x"], g["y"])), g["typ"]) for g in G.values() if g["besitzer"] not in (0, self.sp)),
                 default=(999, 0))
        z = self.ziel.get(n)
        zd = schach(ort, (G[z]["x"], G[z]["y"])) if z in G else -1
        s = self._sicht
        return ("ort (%d,%d) zustand %d | naechster Feind Typ %d in %d | naechster Fernkaempfer Typ %d in %d | "
                "Fern<=%d: %d | Nah<=%d: %d | naechstes Feindgebaeude Typ %d in %d | Ziel %s in %d | "
                "Sicht-Abstand %s Feinmass, Beschuss %.2f, Verfolger %d" % (
                    ort[0], ort[1], L[n]["zustand"], feind[2], feind[0], nf[2], nf[0],
                    FERN, self._anzahl(ort, fern, FERN), NAH, self._anzahl(ort, nah, NAH), gb[1], gb[0], z, zd,
                    s.sicht_abstand(ort) if s else "-", s.beschuss(ort) if s else -1, len(s.verfolgt(ort)) if s else -1))

    def _lord_messen(self, L, G, ln, le, lp, fern, nah):
        """S1 (Plan_Lord.md): je Runde, was der Angriff tut - leben, Abstand zum Lord, wer greift den Lord an, wer etwas
        anderes (welcher Einheitentyp), wer hat kein Ziel. Protokoll nach self.wellen_protokoll, Kennzahlen in self.angriffe."""
        a = self.angriffe[-1]
        lebend = [n for n in a["truppe"] if n in self.mitglieder]
        abst = sorted(schach((L[n]["x"], L[n]["y"]), lp) for n in lebend) or [0]
        am_lord = [n for n in lebend if L[n]["zielart"] == 4 and L[n].get("zieleinheit") == ln and schach((L[n]["x"], L[n]["y"]), lp) <= 3]
        anderes = {}
        for n in lebend:
            z = L[n].get("zieleinheit")
            if L[n]["zielart"] == 4 and z and z != ln and z in L:
                anderes[L[z]["typ"]] = anderes.get(L[z]["typ"], 0) + 1
        ohne = sum(1 for n in lebend if L[n]["zielart"] == 0)
        # S2a: ohne Ziel in der Naehe des Lords = steht vor der Mauer (Daniel 21:47, Bild)
        stehen_nah = sum(1 for n in lebend if L[n]["zielart"] == 0 and schach((L[n]["x"], L[n]["y"]), lp) <= 15)
        a["stehen_nah_max"] = max(a.get("stehen_nah_max", 0), stehen_nah)
        a["lord_nachher"], a["verluste"] = le["leben"], len(a["truppe"]) - len(lebend)
        a["am_lord_max"] = max(a["am_lord_max"], len(am_lord))
        if am_lord and a["erreicht_runde"] is None:
            a["erreicht_runde"] = self.runde
        for t, k in anderes.items():
            a["anderes"][t] = max(a["anderes"].get(t, 0), k)
        if self.wellen_protokoll:
            import json
            # Daniel 06.10.: Nicht vorher festlegen, was Einfluss haben darf. Darum werden alle Menschen/Einheiten,
            # alle bestehenden Gebaeude und die ganze Geländekarte als Rohdaten bewahrt. "Gefahr" ist erst belegt,
            # wenn spaeter Schaden, Ablenkung, Sichtkontakt, Blockade oder Umweg damit zusammenfaellt.
            if self.gelaende is not None and not self._gelaende_geschrieben:
                with open(self.wellen_protokoll, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"art": "gelaende", "zeilen": list(self.gelaende)}) + chr(10))
                self._gelaende_geschrieben = True
            leben_alt = a.setdefault("leben_zuletzt", {})
            angreifer = [{"nr": n, "x": L[n]["x"], "y": L[n]["y"], "leben": L[n]["leben"],
                          "schaden": max(0, leben_alt.get(n, L[n]["leben"]) - L[n]["leben"]),
                          "zustand": L[n].get("zustand"), "zielart": L[n].get("zielart"),
                          "ziel": L[n].get("zieleinheit"), "nahangreifer": L[n].get("nahangreifer")} for n in lebend]
            leben_alt.update({n: L[n]["leben"] for n in lebend})
            alle_einheiten = [{"nr": n, "typ": e.get("typ"), "besitzer": e.get("besitzer"),
                               "x": e.get("x"), "y": e.get("y"), "leben": e.get("leben"),
                               "zustand": e.get("zustand"), "zielart": e.get("zielart"),
                               "ziel": e.get("zieleinheit"), "nahziel": e.get("nahziel"),   # +830: wen er schlaegt (06.10.)
                               "zielt_auf_angreifer": (e.get("zielart") == 4 and e.get("zieleinheit") in a["truppe"])
                                                      or e.get("nahziel") in a["truppe"]}
                              for n, e in sorted(L.items())]
            alle_gebaeude = [{"nr": n, "typ": g.get("typ"), "besitzer": g.get("besitzer"),
                              "x": g.get("x"), "y": g.get("y"), "leben": g.get("leben"),
                              "erreichbar": g.get("erreichbar")} for n, g in sorted(G.items())]
            with open(self.wellen_protokoll, "a", encoding="utf-8") as f:
                f.write(json.dumps({"art": "runde", "runde": self.runde, "angriff": len(self.angriffe), "lord_leben": le["leben"], "leben": len(lebend),
                                    "abst_min": abst[0], "abst_mitte": abst[len(abst) // 2], "am_lord": len(am_lord),
                                    "anderes": anderes, "ohne_ziel": ohne, "stehen_nah": stehen_nah, "fern_um_lord": self._anzahl(lp, fern, self.LORD_UMKREIS),
                                    "nah_um_lord": self._anzahl(lp, nah, self.LORD_UMKREIS), "angreifer": angreifer,
                                    "einheiten": alle_einheiten, "gebaeude": alle_gebaeude}) + chr(10))

    def _vergessen(self, n):
        self.ziel.pop(n, None); self.jagd.pop(n, None); self.warte.pop(n, None); self.warte_seit.pop(n, None)
        self.route.pop(n, None)

    def _lage(self, L, G):
        """17.10.: Sicht dieser Runde (sicht.Lage): wer uns sehen kann, wer schiessen kann, wer nachlaeuft. Die Haltung der
        feindlichen Trupps wird alle 10 Runden und fuer neue Trupps gelesen (lies_haltung, ein peek je Trupp)."""
        if self._sicht is not None and getattr(self, "_sicht_runde", None) == self.runde:
            return self._sicht
        if self.lies_haltung:
            gruppen = sorted({e.get("gruppe") for e in L.values() if e["besitzer"] not in (0, self.sp)
                              and e["typ"] in sicht.NAHKAMPF and e.get("gruppe")})
            neu = [g for g in gruppen if g not in self._haltung]
            # 18.10. (1017m: Assassinen-Teil 0,12 s je Runde statt 0,01-0,02 - die Nomaden werben laufend an, jeder neue Trupp
            # loeste jede Runde eine Abfrage im Spiel aus): nur alle 10 Runden; neue Trupps gelten bis dahin als Verteidigung (5)
            if self.runde - self._haltung_runde >= 10:
                try:
                    self._haltung.update(self.lies_haltung(gruppen) or {})
                    self._haltung_runde = self.runde
                except Exception:
                    pass
        # 17.10.: wer in den letzten 128 Takten sichtbar war, bleibt Ziel bis zu seiner naechsten Pruefrunde (L75)
        sb = getattr(self, "_sicht_bis", {})
        jetzt = getattr(self, "jetzt", self.runde * self.RUNDE_TICKS)
        self._sicht = sicht.Lage(L, G, self.sp, self._haltung if self.lies_haltung else None,
                                 noch_sichtbar={k for k, b in sb.items() if b > jetzt and k in L})
        for k in self.mitglieder:
            if k in L and self._sicht.sichtbar((L[k]["x"], L[k]["y"])):
                sb[k] = jetzt + self.ENTDECKT_TICKS      # 19.10.: 400 statt 128 (Bolzen bis ~300 Takte spaeter)
        self._sicht_bis = sb
        self._sicht_runde = self.runde
        return self._sicht

    def _arbeit(self, typ, zahl):
        """Takte bis zerstoert bei zahl Assassinen (gemessene Arbeit / Zahl)."""
        return ARBEIT.get(typ, ARBEIT_SONST) / max(1, zahl)

    def _gitter(self, L, G=None):
        """Gefahren-Gitter dieser Runde (schussfeld.py) mit der Sicht (17.10., sicht.py: sichtbar nur bei waehlbarem Feind
        <= 20 Feldern, Beschuss je Schuetze mit freier/versperrter Linie); einmal je Runde, Gelaende einmal je Partie."""
        if not self.mit_wegen or not self.gelaende:
            return None
        if getattr(self, "_gitter_runde", (None,))[0] == self.runde:
            return self._gitter_runde[1]
        g = schussfeld.Gitter(self.gelaende, schussfeld.schuetzen(L, self.sp), frei=self._frei, sicht=self._lage(L, G or {}))
        self._frei = g.frei
        self._gitter_runde = (self.runde, g)
        return g

    def _wege(self, L, G, angriffe, ereignis):
        """12.10.: neue Gebaeude-Angriffe ueber den sicheren Weg schicken. Gibt (direkte Angriffe, Laufbefehle {Ort: [n]})."""
        lauf, direkt = {}, []
        if not angriffe:
            return direkt, lauf
        g = self._gitter(L, G)
        if g is None:
            return list(angriffe), lauf
        for n, gn in angriffe:
            if n not in L or gn not in G:
                direkt.append((n, gn))
                continue
            start, ziel = (L[n]["x"], L[n]["y"]), (G[gn]["x"], G[gn]["y"])
            wp, bw, bg, _ = schussfeld.sicherer_weg(self.gelaende, L, self.sp, start, ziel, gitter=g)
            if len(wp) <= 1 and schach(start, ziel) > self.GERADE_TEIL:
                # 19.10. (1018p, Assassine 198 lief 222 Felder am Stueck an 4 Armbrustschuetzen vorbei): auch ohne Umweg in
                # Stuecken - dann prueft ROUTE GEFAEHRLICH jedes Stueck vor dem Betreten
                k = schach(start, ziel) // self.GERADE_TEIL + 1
                wp = [(start[0] + (ziel[0] - start[0]) * i // k, start[1] + (ziel[1] - start[1]) * i // k) for i in range(1, k)] + [ziel]
            if len(wp) > 1:
                self.route[n] = {"punkte": wp[:-1], "gebaeude": gn, "befohlen": self.runde}
                lauf.setdefault(wp[0], []).append(n)
                ereignis.append("WEG %d -> Gebaeude %d ueber %d Wegpunkte (Beschuss Weg %s statt gerade %s)" % (
                    n, gn, len(wp) - 1, bw, bg))
            else:
                direkt.append((n, gn))
        return direkt, lauf

    def _route_pflegen(self, L, G, angriffe, ereignis):
        """12.10.: Wegpunkt erreicht -> naechster; letzter erreicht -> Angriff aufs Gebaeude. Gibt Laufbefehle {Ort: [n]}."""
        lauf = {}
        for n, r in list(self.route.items()):
            if n not in L or n not in self.mitglieder or self.ziel.get(n) != r["gebaeude"] or r["gebaeude"] not in G                     or n in self.flucht or n in self.jagd:
                self.route.pop(n, None)
                continue
            ort = (L[n]["x"], L[n]["y"])
            while r["punkte"] and schach(ort, r["punkte"][0]) <= self._vorlauf():
                r["punkte"].pop(0)
            if not r["punkte"]:
                self.route.pop(n, None)
                angriffe.append((n, r["gebaeude"]))
                self.befohlen[n] = self.runde
                ereignis.append("WEG %d am Ziel angekommen -> Angriff auf Gebaeude %d" % (n, r["gebaeude"]))
                continue
            p = r["punkte"][0]
            if schach((L[n].get("laufx", -99), L[n].get("laufy", -99)), p) > self.WEGPUNKT_NAH and self.runde - r["befohlen"] >= 1:
                lauf.setdefault(p, []).append(n)
                r["befohlen"] = self.runde
        return lauf

    def _fliehen(self, n, ort, flieh):
        """4a: Flucht als echter Laufbefehl (Spielbefehl 17 wie ein Mensch-Klick, Modul angriff mit lauf). NICHT halten:
        abgelesen 05.10. (logik.lua halten/festhaltenTick) - halten setzt nur das Laufziel (setDestinationForUnit, der
        Nahkampf-Zustand bleibt) und laesst die Einheit los, sobald sie im Kampf ein Ziel hat (+924). So kam in
        raidzuerst_2 keiner aus dem Nahkampf heraus."""
        self.warte[n] = ort
        self.warte_seit[n] = self.runde
        flieh.setdefault(ort, []).append(n)

    def _warten(self, n, ort_sicher, halten):
        self.warte[n] = ort_sicher
        self.warte_seit[n] = self.runde
        halten.setdefault(ort_sicher, []).append(n)

    def _bereit_plaetze(self, lp):
        """17.10.: Bereitstellungsplaetze um den Lord - Ring BEREIT_R, alle 20 Grad, begehbar laut Modul. Zuerst die, die
        kein waehlbarer Feind sieht (sicht.sicher); gibt es keinen, die mit dem kleinsten Beschuss und groessten Sicht-Abstand."""
        ring = []
        for r in self.BEREIT_R:
            for k in range(18):
                w = k * math.pi / 9
                q = (int(round(lp[0] + r * math.cos(w))), int(round(lp[1] + r * math.sin(w))))
                if 2 <= q[0] <= 397 and 2 <= q[1] <= 397 and q not in ring:
                    ring.append(q)
        if self.pruefe_begehbar and ring:
            gut = self.pruefe_begehbar(ring)
            ring = [q for q in ring if q in gut]
        s = self._sicht
        sicher = [q for q in ring if s is None or s.sicher(q)]
        if sicher:
            return sicher
        return sorted(ring, key=lambda q: (s.beschuss(q), -s.sicht_abstand(q)))[:6]

    def _beschuss_angriff(self, gn, G, von=None):
        """17.10.: Beschuss je Takt dort, wo die Assassine beim Angriff steht - nicht das Ankerfeld (dort versperrt das Gebaeude
        selbst die Linien). von = Ort der Assassine: hoechster Wert der 3 Randfelder auf ihrer Anlaufseite. Ohne von: kleinster
        Wert aller Randfelder (gibt es eine unbeobachtete Seite?).
        18.10. (1017l: 1,1 s Rechenzeit je Runde, 16,9 von 23,6 s hier - jede Runde jedes Randfeld jedes Gebaeudes gegen jeden
        Schuetzen): erst pruefen, ob am Gebaeude ueberhaupt ein waehlbarer Feind sieht (sonst ueberall 0); Felder nur bei Bedarf
        rechnen und je Runde merken; ohne von beim ersten Feld mit 0 aufhoeren. Ergebnis gleich, nur schneller."""
        if getattr(self, "_ba_runde", None) != self.runde:
            self._ba_runde, self._ba, self._ba_feld = self.runde, {}, {}
        g = G[gn]
        b = sicht.GROESSE.get(g["typ"], 1) or 1
        if gn not in self._ba:
            mitte = (g["x"] + b // 2, g["y"] + b // 2)
            gesehen = self._sicht.sichtbar(mitte, rand=(b + 4) * 8 + 32)     # grosszuegig: lieber rechnen als falsch 0
            rand = [(x, y) for x in range(g["x"] - 1, g["x"] + b + 1) for y in range(g["y"] - 1, g["y"] + b + 1)
                    if not (g["x"] <= x < g["x"] + b and g["y"] <= y < g["y"] + b)]
            self._ba[gn] = (gesehen, rand)
        gesehen, rand = self._ba[gn]
        if not rand:
            return 0.0
        if not gesehen:
            # Ausnahme: eine eigene Einheit auf einem Randfeld, der noch Schuetzen zugeteilt sind (bleibt 128 Takte Ziel, L75)
            if not hasattr(self._sicht, '_besetzt'):
                self._sicht._besetzt = {p for nr_, p, t_ in self._sicht.eigene if self._sicht.feuer.get(nr_)}
            if not self._sicht._besetzt.intersection(rand):
                return 0.0

        def wert(q):
            if q not in self._ba_feld:
                self._ba_feld[q] = self._sicht.beschuss(q, self._sicht.RAND)
            return self._ba_feld[q]
        if von is None:
            m = None
            for q in rand:
                w = wert(q)
                if w <= 0:
                    return 0.0
                m = w if m is None else min(m, w)
            return m
        vx, vy = von[0], von[1]
        nah = sorted(rand, key=lambda q: (max(abs(q[0] - vx), abs(q[1] - vy)), q))[:3]
        return max(wert(q) for q in nah)

    def _anlauf_leben(self, von, lp, n):
        """18.10. (1017l: 5 Assassinen starben im Anlauf 10 Felder vor dem Lord - 13 Schleuderer, 6 Boegen, 1 Feuerwerfer im
        Umkreis 12; lord_machbar zaehlte nur Schuetzen mit Linie aufs Lordfeld, und der Bergfried sperrt viele): Leben, mit dem
        jede der n Assassinen am Lord ankommt = voll - (mittleres Gesamtfeuer entlang der Strecke von -> Lord x Laufzeit) / n."""
        d = schach(von, lp)
        if d <= 1 or n <= 0:
            return self.VOLL
        k = max(1, d // 3)
        punkte = [(von[0] + (lp[0] - von[0]) * i // k, von[1] + (lp[1] - von[1]) * i // k) for i in range(k + 1)]
        f = sum(self._sicht.feuer_gesamt(q) for q in punkte) / len(punkte)
        rest = int(self.VOLL - f * d * TEMPO * self.KALIB / n)
        # mindestens ANKUNFT_MIN Leben je Assassine am Lord, sonst gilt der Angriff als nicht machbar (Rechnung ist ein Modell)
        return rest if rest >= self.ANKUNFT_MIN * self.VOLL else 1

    def _anlauf_von(self, L, lp):
        """Ausgangspunkt fuer den Anlauf: Mitte der Bereiten, sonst ein Punkt BEREIT_R[1] Felder vom Lord Richtung unserer
        Assassinen."""
        lt = self.lordtrupp
        b = [k for k in lt.get("bereit", ()) if k in L]
        if b:
            return (sum(L[k]["x"] for k in b) // len(b), sum(L[k]["y"] for k in b) // len(b))
        m = [k for k in self.mitglieder if k in L]
        if not m:
            return lp
        mx, my = sum(L[k]["x"] for k in m) / len(m), sum(L[k]["y"] for k in m) / len(m)
        d = max(1.0, max(abs(mx - lp[0]), abs(my - lp[1])))
        r = self.BEREIT_R[1]
        return (int(round(lp[0] + (mx - lp[0]) * r / d)), int(round(lp[1] + (my - lp[1]) * r / d)))

    def _vorlauf(self):
        """18.10.: so nah (Felder) am Wegpunkt gilt er als 'gleich da' - der naechste Wegpunkt geht schon hinaus."""
        rt = getattr(self, "_runde_ticks", self.RUNDE_TICKS)
        # hoechstens VORLAUF_MAX: sonst ueberspraenge er bei langsamen Runden Wegpunkte, der sichere Weg wuerde zur Geraden
        return max(self.WEGPUNKT_NAH, min(self.VORLAUF_MAX, int(rt / TEMPO) + self.VORLAUF_RESERVE))

    def _im_lordangriff(self, n):
        """18.10. (Gegenpruefung): "Der Lord-Trupp bleibt dran" gilt nur im gemeinsamen Angriff, nicht in der Bereitstellung."""
        return n in self.lordtrupp["mitglieder"] and self.lordtrupp["phase"] in ("angriff", "sammeln")

    def _drohende(self, ort, nrs, L):
        """19.10.: die Schuetzen aus nrs (Einheitennummern), die ort jetzt erreichen: Reichweite + ENTDECKT_RAND, Linie frei."""
        s = self._sicht
        aus = []
        for k in nrs:
            e = L.get(k)
            if not e or e["besitzer"] in (0, self.sp) or e["typ"] not in sicht.REICHWEITE:
                continue
            p = (e["x"], e["y"])
            r = sicht.REICHWEITE[e["typ"]] + self.ENTDECKT_RAND
            if (p[0] - ort[0]) ** 2 + (p[1] - ort[1]) ** 2 > r * r:
                continue
            unter = s.gebaeude.get(p)
            if (unter and unter[1] in sicht.ERHOEHT) or s.linie_frei(p, unter[0] if unter else None, ort):
                aus.append(k)
        return aus

    def _ausser_reichweite(self, n, ort, nrs, L):
        """19.10. (Daniel: "statt ganz nach Hause einen besseren Platz - die sind auf Aussendienst und muessen so viel klatschen
        wie moeglich"): erst die Ringe bis 40 Felder (bis zu 24 Punkte beim Wegfinder geprueft), dann 50-75 Felder; erst wenn
        auch dort nichts erreichbar ist, None (dann Heim)."""
        for radien in ((6, 10, 14, 18, 24, 30, 40), (50, 60, 75)):
            q = self._ausser_reichweite_ringe(n, ort, nrs, L, radien)
            if q is not None:
                return q
        return None

    def _ausser_reichweite_ringe(self, n, ort, nrs, L, radien):
        """19.10.: naechster begehbarer Ort, den keiner der Schuetzen nrs erreicht, den kein waehlbarer Feind sieht und an dem
        kein Verfolger steht; gibt es keinen, der mit den wenigsten Schuetzen. Ringe in 16 Richtungen + Heim."""
        s = self._sicht
        kand = []
        for r in radien:
            for k in range(16):
                w = k * math.pi / 8
                q = (int(round(ort[0] + r * math.cos(w))), int(round(ort[1] + r * math.sin(w))))
                if 2 <= q[0] <= 397 and 2 <= q[1] <= 397 and q not in kand:
                    kand.append(q)
        kand += [h for h in getattr(self, "_heim", []) if h not in kand]
        gut = self.pruefe_begehbar(kand) if self.pruefe_begehbar else set(kand)
        kand = [q for q in kand if q in gut and q not in self.schlechte_orte
                and q not in self.entdeckt.get(n, {}).get("gesperrt", ())]
        if not kand:
            return None

        # 19.10. (1018q: 23 von 29 schweren Treffern kamen binnen 450 Takten NACH einer Entdeckung - der Fluchtweg blieb
        # 300 Takte in Reichweite, 178 starb ausser Sicht): Bewertung nach der Zeit in Reichweite AUF DEM WEG (alle 2 Felder,
        # Zahl der Schuetzen mit Linie), dann am Ziel, Sicht, Verfolger, Laenge - hinter Gebaeuden ist die Linie zu
        merk = {}

        def dro(q):                      # Zahl der Schuetzen, die q erreichen (je Aufruf gemerkt - Wege teilen Felder)
            if q not in merk:
                merk[q] = len(self._drohende(q, nrs, L))
            return merk[q]

        def weg(q):
            k = max(1, schach(ort, q) // 2)
            return sum(dro((ort[0] + (q[0] - ort[0]) * i // k, ort[1] + (q[1] - ort[1]) * i // k)) for i in range(1, k + 1))
        # Rechenzeit (1018n nachgespielt: 0,09 -> 0,23 s je Runde, wenn jeder Kandidat den ganzen Weg rechnet): den Weg nur
        # fuer die (hoechstens 24 naechsten) Punkte ausser Reichweite; gibt es keinen, die mit den wenigsten Schuetzen.
        # 19.10. (1018s: 3, 240, 283 bekamen Punkte 4-9 Felder weiter, ausser Reichweite nur der Schuetzen, die sie gesehen
        # hatten - die daneben sahen sie gleich wieder, sie pendelten im Feuer): zuerst Punkte ausser Sicht (mit Rand) und
        # mindestens FLUCHT_MIN Felder weit; Verfolger kosten wie 30 Wegstuecke in Reichweite
        def wert(q):
            return (weg(q) + (30 if s.verfolgt(q) else 0), s.sichtbar(q, s.RAND), schach(ort, q))
        frei = sorted((q for q in kand if dro(q) == 0 and not s.sichtbar(q, s.RAND) and schach(ort, q) >= self.FLUCHT_MIN),
                      key=lambda q: schach(ort, q))[:24]
        if not frei:
            frei = sorted((q for q in kand if dro(q) == 0), key=lambda q: schach(ort, q))[:24]
        if frei:
            kand = sorted(frei, key=wert)
        else:
            kand.sort(key=lambda q: (dro(q), s.sichtbar(q, s.RAND), bool(s.verfolgt(q)), schach(ort, q)))
        # 1018q (86 stand 3 Runden still: Fluchtpunkt laut Kartenabzug begehbar, im Spiel nicht erreichbar): die besten 8
        # beim Wegfinder des Spiels pruefen, der erste erreichbare gilt
        if self.wegtest:
            try:
                for a in (0, 8, 16):          # 19.10.: bis zu 24 Punkte, je 8 in einem Aufruf
                    teil = kand[a:a + 8]
                    if not teil:
                        break
                    for q, j in zip(teil, self.wegtest(n, teil)):
                        if j:
                            return q
                return None
            except Exception:
                pass
        return kand[0]

    def _nahe_schuetzen(self, ort, L, r=60):
        """19.10.: alle feindlichen Schuetzen bis r Felder - die Flucht meidet alle, nicht nur die, die ihn gesehen haben."""
        return {k for k, e in L.items() if e["besitzer"] not in (0, self.sp) and e["typ"] in sicht.REICHWEITE
                and schach(ort, (e["x"], e["y"])) <= r}

    def _entdeckt_pruefen(self, L, G, ereignis, flieh, jagen=None, angriffe=None):
        """19.10. (Daniel: "wenn 5 gestorben sind dann sofort stoppen und verhindern"; Partie 1018p): sichtbar (waehlbarer Feind
        <= 160 Feinmass, L75) UND ein Schuetze erreicht ihn mit freier Linie -> entdeckt: Auftrag ab, Laufbefehl ausser Sicht
        und ausser Reichweite aller Schuetzen, die ihn gesehen haben; dort bleiben, bis ENTDECKT_TICKS nach dem letzten Sehen
        um sind. Nicht im gemeinsamen Lord-Angriff, nicht auf der Flucht vor Nahkaempfern (4a)."""
        s = self._sicht
        if s is None:
            return
        for n in list(self.entdeckt):
            if n not in self.mitglieder or n not in L:
                del self.entdeckt[n]
        for n in sorted(self.mitglieder):
            if n not in L or self._im_lordangriff(n):
                continue
            ort = (L[n]["x"], L[n]["y"])
            e = self.entdeckt.get(n)
            # 19.10. (1018s: 132 floh vor Nahkaempfern sichtbar durch 7 Boegen - die Flucht 4a kennt keine Schuetzen; 1018r
            # 233/142 genauso): auf der Flucht nur, wenn Schuetzen ihn sehen - dann uebernimmt ENTDECKT (Verfolger zaehlen
            # in der Fluchtpunkt-Wahl)
            if n in self.flucht and e is None and not s.sichtbar(ort):
                continue
            if s.sichtbar(ort):
                sehen = [k for k, (p, r, erh, steht, art) in zip(s.schuetzen_nr, s.schuetzen)
                         if (p[0] - ort[0]) ** 2 + (p[1] - ort[1]) ** 2 <= (r + self.ENTDECKT_RAND) ** 2
                         and (erh or s.linie_frei(p, steht, ort))]
                if e is None and n in self.jagd and set(sehen) <= {self.jagd[n]}:
                    sehen = []                 # jagt den einzigen Schuetzen, der ihn erreicht (Beute, 3b): weiter jagen
                if e is None and sehen and self._spaeher_erledigen(n, ort, sehen, L, ereignis, jagen if jagen is not None else []):
                    continue                   # 19.10.: nur ein Sklave sieht ihn - erledigen statt fliehen
                if e is None and sehen and self._fertig_zuerst(n, ort, G, L, ereignis):
                    continue                   # 19.10.: fast kaputt - erst fertig abreissen
                if sehen:
                    if e is not None and e.get("ziel_ok") is not None:
                        e["ziel_ok"], e["punkt"] = None, None      # beim Aussendienst wieder gesehen: wieder raus
                    if e is None:
                        e = self.entdeckt[n] = {"schuetzen": set(), "seit": self.jetzt, "punkt": None}
                        self.flucht.pop(n, None)
                        self.bilanz["entdeckt"] = self.bilanz.get("entdeckt", 0) + 1
                        sp = min(((sicht.abstand_fein(ort, (x["x"], x["y"])), x["typ"], schach(ort, (x["x"], x["y"])))
                                  for x in L.values() if x["besitzer"] not in (0, self.sp) and x["typ"] in sicht.WAEHLBAR),
                                 default=(0, 0, 0))
                        ereignis.append("ENTDECKT %d bei %s (Auftrag: %s): Spaeher Typ %d in %d Feldern, %d Schuetzen mit Linie, "
                                        "Leben %d -> raus" % (n, ort, self._taetigkeit(n, G), sp[1], sp[2], len(sehen),
                                                              L[n]["leben"]))
                    e["schuetzen"].update(sehen)
                    e["bis"] = self.jetzt + self.ENTDECKT_TICKS
            if e is None:
                continue
            self.flucht.pop(n, None)
            if self.jetzt >= e["bis"]:
                del self.entdeckt[n]
                self.warte.pop(n, None); self.warte_seit.pop(n, None)
                ereignis.append("ENTDECKT vorbei %d: %d Takte nicht gesehen, Leben %d - raidet wieder" % (
                    n, self.ENTDECKT_TICKS, L[n]["leben"]))
                continue
            if e.get("ziel_ok") is not None and self.ziel.get(n) == e["ziel_ok"]:
                continue                       # Aussendienst: Ziel weit weg von den Schuetzen, die ihn gesehen haben
            if n in self.letzter:
                if self._drohende(ort, self._nahe_schuetzen(ort, L), L) or s.sichtbar(ort):
                    self._letzter_einsatz(n, L, G, "weiter", ereignis, angriffe or [], jagen if jagen is not None else [])
                    continue
                del self.letzter[n]            # die Gefahr ist weg: wieder normal fliehen/warten
            if n in self.ziel or n in self.jagd or n in self.route or n in self.stapel["mitglieder"]:
                if n in self.ziel:             # dasselbe Ziel nicht gleich wieder (wie nach ROUTE GEFAEHRLICH)
                    self._route_sperre[(n, self.ziel[n])] = self.jetzt + self.SPERRE_ROUTE
                self._vergessen(n)
                self.stapel["mitglieder"].discard(n)
                if jagen is not None:
                    jagen[:] = [j for j in jagen if j[0] != n]
            self._aus_bereit(n, "entdeckt, raus aus Sicht und Reichweite", ereignis)
            p = e.get("punkt")
            # neuer Punkt, wenn keiner da ist, der alte bedroht ist oder er seit BLOCK_TICKS nicht vorankommt
            if p is not None:
                if e.get("letzt") != ort:
                    e["letzt"], e["feld_seit"] = ort, self.jetzt
                d_jetzt, d_vor = schach(ort, p), e.get("abstand", 10 ** 6)
                e["abstand"] = d_jetzt
                # 19.10. (1018q: 86, 91, 205 liefen erst weg vom Punkt oder standen): naeher kommen MUSS er in jeder Runde
                if d_jetzt > 2 and (d_jetzt >= d_vor or self.jetzt - e.get("feld_seit", self.jetzt) >= max(
                        60, 2 * getattr(self, "_runde_ticks", self.RUNDE_TICKS))):
                    e.setdefault("gesperrt", []).append(p)
                    p = None
                elif self._drohende(p, e["schuetzen"] | self._nahe_schuetzen(p, L), L) or s.sichtbar(p, s.RAND):
                    p = None
            if p is None:
                p = self._ausser_reichweite(n, ort, e["schuetzen"] | self._nahe_schuetzen(ort, L), L)
                # 19.10. (Daniel): kostet der Fluchtweg mehr Leben, als er hat, kommt er nicht weg -> letzter Einsatz
                kalib = 1.0 if L[n]["leben"] < self.EIN_TREFFER else self.LETZT_KALIB
                if p is not None and kalib * self._fluchtschaden(ort, p, e["schuetzen"] | self._nahe_schuetzen(ort, L), L) >= L[n]["leben"]:
                    if self._letzter_einsatz(n, L, G, "Fluchtweg toedlich", ereignis, angriffe if angriffe is not None else [],
                                             jagen if jagen is not None else []):
                        continue
                if p is None:
                    # 19.10. (1018s, 283 blieb im Feuer stehen, weil kein Punkt passte): dann nach Hause, nie stehen bleiben
                    heim = getattr(self, "_heim", [])
                    p = min(heim, key=lambda h: schach(ort, h)) if heim else None
                    if p is None:
                        continue
                e["punkt"], e["letzt"], e["feld_seit"], e["abstand"] = p, ort, self.jetzt, schach(ort, p)
                self._fliehen(n, p, flieh)
                ereignis.append("ENTDECKT %d: laeuft nach %s (%d Felder; dort erreichen ihn %d der %d Schuetzen)" % (
                    n, p, schach(ort, p), len(self._drohende(p, e["schuetzen"], L)), len(e["schuetzen"])))
            elif schach((L[n]["laufx"], L[n]["laufy"]), p) > 2 and schach(ort, p) > 2:
                self._fliehen(n, p, flieh)       # laeuft nicht dorthin (z.B. vom Spiel umgelenkt): Befehl erneuern
            else:
                self.warte[n] = p

    def _fertig_zuerst(self, n, ort, G, L, ereignis):
        """19.10. (1018x, Daniel: "die Barracke nur bis kurz vor kaputt angegriffen, dann ist er nach hinten"): reisst er gerade
        ab (Zustand 107, Ziel daneben) und braucht das Gebaeude nur noch FERTIG_TAKTE (gemessene Arbeit x Restleben / hoechstes
        gesehenes Leben / Angreifer) - weniger, als die Schuetzen nach dem Erkennen bis zum ersten Treffer brauchen (L81) -,
        dann erst fertig abreissen, danach fliehen."""
        gn = self.ziel.get(n)
        g = G.get(gn)
        if g is None or L[n]["zustand"] != 107 or schach(ort, (g["x"], g["y"])) > self.ZIEL_NAH + 2:
            return False
        voll = max(getattr(self, "_gb_max", {}).get(gn, 0), g["leben"], 1)
        zahl = max(1, sum(1 for z in self.ziel.values() if z == gn))
        rest = ARBEIT.get(g["typ"], ARBEIT_SONST) * g["leben"] / float(voll) / zahl
        if rest > self.FERTIG_TAKTE:
            return False
        # 19.10. (1018y: ein Markt im Bau - sein Leben stieg 20 -> 60, die Restarbeit sank nie, "fertig zuerst" hielt 86 zehn
        # Runden im Feuer): je Gebaeude hoechstens FERTIG_TAKTE + 30 Takte, und nach 40 Takten muss das Leben gesunken sein
        fs = getattr(self, "_fertig_seit", {})
        self._fertig_seit = fs
        alt = fs.get(n)
        if alt is None or alt[0] != gn:
            fs[n] = alt = (gn, self.jetzt, g["leben"])
        dauer = self.jetzt - alt[1]
        if dauer > self.FERTIG_TAKTE + 30 or (dauer > 40 and g["leben"] >= alt[2]):
            return False
        ereignis.append("FERTIG ZUERST %d: entdeckt, aber Gebaeude %d (Typ %d) braucht nur noch ~%d Takte - erst abreissen" % (
            n, gn, g["typ"], rest))
        self._fertig.add(n)
        return True

    def _spaeher_erledigen(self, n, ort, sehen, L, ereignis, jagen):
        """19.10. (1018w: alle 6 Entdeckungen durch Sklaven, oft mit nur 1 Schuetzen in Reichweite - die Assassine floh und
        wartete, der Sklave blieb daneben; Daniel: "hier laeuft literally ein Assassine einem Sklaven weg", "hier pausieren sie
        ohne Grund"): sehen ihn nur Sklaven (hoechstens SPAEHER_MAX, der naechste bis SPAEHER_R Felder) und schaffen die
        Schuetzen mit Linie bis zu deren Tod (Weg + Toetungszeit) hoechstens SPAEHER_ANTEIL seines Lebens -> den naechsten
        Sklaven angreifen statt fliehen; danach sieht ihn niemand mehr."""
        if n in self.jagd and L.get(self.jagd[n], {}).get("typ") == 71:
            return True                        # ist schon dran
        sp = sorted((schach(ort, (e["x"], e["y"])), k, e) for k, e in L.items() if e["besitzer"] not in (0, self.sp)
                    and e["typ"] in sicht.WAEHLBAR and sicht.abstand_fein(ort, (e["x"], e["y"])) <= sicht.SICHT)
        if not sp or len(sp) > self.SPAEHER_MAX or any(e["typ"] != 71 for _, _, e in sp) or sp[0][0] > self.SPAEHER_R:
            return False
        zeit = sum(d * TEMPO + e["leben"] / float(NAHKAMPF_RATE.get(71, 230)) for d, _, e in sp)
        schaden = self._feuer_von(ort, set(sehen), L) * zeit
        if schaden > self.SPAEHER_ANTEIL * L[n]["leben"]:
            return False
        ziel = sp[0][1]
        self._vergessen(n)
        self.jagd[n] = ziel
        jagen.append((n, ziel))
        ereignis.append("SPAEHER WEG %d: nur Sklave %d (%d Felder) sieht ihn, %d Schuetzen mit Linie (~%d Schaden bis er tot ist) "
                        "-> erledigt ihn statt zu fliehen" % (n, ziel, sp[0][0], len(sehen), schaden))
        return True

    def _feuer_von(self, q, nrs, L):
        """19.10.: Leben je Takt an q von den Schuetzen nrs, die q erreichen (Linie frei)."""
        s = 0.0
        for k in self._drohende(q, nrs, L):
            e = L[k]
            s += sicht.dps(sicht.SCHUETZE_ART[e["typ"]], math.hypot(e["x"] - q[0], e["y"] - q[1]))
        return s

    def _fluchtschaden(self, ort, p, nrs, L):
        """19.10.: erwarteter Lebensverlust auf dem geraden Weg ort -> p (alle 2 Felder: Feuer x 2 x TEMPO)."""
        k = max(1, schach(ort, p) // 2)
        return sum(self._feuer_von((ort[0] + (p[0] - ort[0]) * i // k, ort[1] + (p[1] - ort[1]) * i // k), nrs, L)
                   for i in range(1, k + 1)) * 2 * TEMPO

    def _letzter_einsatz(self, n, L, G, grund, ereignis, angriffe, jagen):
        """19.10.: er kommt nicht mehr weg - in der Restzeit (Leben / eingehender Schaden je Takt) das Ziel mit dem hoechsten
        ABSOLUTEN Wert, das er noch schafft: Gebaeude (Weg + gemessene Arbeit) oder Einheit (Weg + Toetungszeit); Schuetzen,
        die ihn gerade treffen, zaehlen doppelt (ihr Tod verlaengert sein Leben). Schafft er keines, das mit dem besten
        Wert je Zeit."""
        ort = (L[n]["x"], L[n]["y"])
        nrs = self._nahe_schuetzen(ort, L)
        auf_ihn = set(self._drohende(ort, nrs, L))
        nah = sum(1 for e in L.values() if e["besitzer"] not in (0, self.sp) and e["typ"] in sicht.NAHKAMPF
                  and schach(ort, (e["x"], e["y"])) <= 2)
        nah += sum(1 for e in L.values() if e["besitzer"] == 0 and e["typ"] == self.LOEWE and schach(ort, (e["x"], e["y"])) <= 2)
        dps = self._feuer_von(ort, nrs, L) + nah * self.NAH_SCHADEN
        rest = L[n]["leben"] / max(dps, 1.0)
        kand = []
        for gn, g in G.items():
            if g["besitzer"] in (0, self.sp) or g["typ"] not in WERT:
                continue
            d = schach(ort, (g["x"], g["y"]))
            if d <= self.LETZT_R:
                kand.append((WERT[g["typ"]], d * TEMPO + ARBEIT.get(g["typ"], ARBEIT_SONST), ("g", gn)))
        for k, e in L.items():
            if e["besitzer"] in (0, self.sp) or e["typ"] not in TRUPPE or e["typ"] == 55:
                continue
            d = schach(ort, (e["x"], e["y"]))
            if d <= self.LETZT_R:
                w = EINHEIT_WERT.get(e["typ"], 30) * (2 if k in auf_ihn else 1)
                kand.append((w, d * TEMPO + e["leben"] / float(NAHKAMPF_RATE.get(e["typ"], 230)), ("e", k)))
        if not kand:
            return False
        schafft = [x for x in kand if x[1] <= rest]
        best = max(schafft, key=lambda x: (x[0], -x[1])) if schafft else max(kand, key=lambda x: x[0] / max(x[1], 1.0))
        art, nr = best[2]
        alt = self.letzter.get(n, {}).get("ziel")
        self.letzter[n] = {"ziel": best[2], "seit": self.letzter.get(n, {}).get("seit", self.jetzt)}
        if alt != best[2]:
            self._vergessen(n)
            if art == "g":
                self.ziel[n] = nr
                self.ziel_typ[nr] = G[nr]["typ"]
                angriffe.append((n, nr))
            else:
                self.jagd[n] = nr
                jagen.append((n, nr))
            ereignis.append("LETZTER EINSATZ %d (%s): Leben %d, Schaden %.0f je Takt -> noch ~%d Takte; Ziel %s %d (Typ %d, Wert %d, "
                            "braucht ~%d Takte%s)" % (n, grund, L[n]["leben"], dps, rest, "Gebaeude" if art == "g" else "Einheit",
                                                     nr, (G[nr] if art == "g" else L[nr])["typ"], best[0], best[1],
                                                     "" if schafft else ", schafft keines ganz"))
        return True

    def _aussendienst_frei(self, n, L):
        """19.10.: entdeckt, aber gerade weder sichtbar noch in Reichweite eines Schuetzen, der ihn sah oder nah ist."""
        ort = (L[n]["x"], L[n]["y"])
        e = self.entdeckt.get(n, {})
        return not self._sicht.sichtbar(ort, self._sicht.RAND) and not self._drohende(
            ort, e.get("schuetzen", set()) | self._nahe_schuetzen(ort, L), L)

    def _weit_von_gesehen(self, n, ort, ziel, L):
        """19.10.: Ziel und gerader Weg dorthin (alle 3 Felder) ausser Reichweite + Rand jedes Schuetzen, der ihn gesehen hat."""
        nrs = self.entdeckt.get(n, {}).get("schuetzen", set())
        k = max(1, schach(ort, ziel) // 3)
        return all(not self._drohende((ort[0] + (ziel[0] - ort[0]) * i // k, ort[1] + (ziel[1] - ort[1]) * i // k), nrs, L)
                   for i in range(0, k + 1))

    def _loewenjagd(self, L, jagen, ereignis):
        """19.10. (1018t: drei Loewen, je 12.000 Leben, lagerten am Soeldnerposten und toeteten zwei frisch angeworbene
        Assassinen): Loewen bis LOEWE_HEIM Felder von unseren sicheren Orten -> ab LOEWE_GRUPPE gesunden freien Assassinen
        gemeinsam auf den schwaechsten Loewen (einer nach dem anderen)."""
        heim = getattr(self, "_heim", [])
        loewen = [(e["leben"], k) for k, e in L.items() if e["typ"] == self.LOEWE and e["besitzer"] == 0
                  and any(schach((e["x"], e["y"]), h) <= self.LOEWE_HEIM for h in heim)]
        self._loewen_jaeger = set()
        if not loewen:
            return
        ziel = min(loewen)[1]
        lp = (L[ziel]["x"], L[ziel]["y"])
        frei = sorted((schach((L[n]["x"], L[n]["y"]), lp), n) for n in self.mitglieder
                      if n in L and L[n]["leben"] >= self.LOEWE_LEBEN and n not in self.entdeckt
                      and not self._im_lordangriff(n) and (n not in self.jagd or L.get(self.jagd[n], {}).get("typ") == self.LOEWE))
        gruppe = [n for d, n in frei[:self.LOEWE_GRUPPE + 1] if d <= 80]
        if len(gruppe) < self.LOEWE_GRUPPE:
            return
        for n in gruppe:
            self._loewen_jaeger.add(n)
            if self.jagd.get(n) != ziel:
                self._vergessen(n)
                self.flucht.pop(n, None)
                self.jagd[n] = ziel
                jagen.append((n, ziel))
        ereignis.append("LOEWENJAGD: %d Assassinen auf Loewe %d (Leben %d) bei %s, %d Loewen am Heim" % (
            len(gruppe), ziel, L[ziel]["leben"], lp, len(loewen)))

    def _taetigkeit(self, n, G):
        """19.10.: was der Lenker ihn zuletzt tun liess (fuer die Akte)."""
        lt = self.lordtrupp
        if n in self.flucht:
            return "Flucht"
        if n in lt["mitglieder"]:
            return "Lord-Trupp (%s)" % lt["phase"]
        if n in self.jagd:
            return "Jagd auf Einheit %s" % self.jagd[n]
        if n in self.ziel:
            gn = self.ziel[n]
            return "%sGebaeude %d (Typ %s)" % ("Route zu " if n in self.route else "", gn,
                                              G[gn]["typ"] if gn in G else self.ziel_typ.get(gn, "?"))
        if n in self.stapel["mitglieder"]:
            return "Stapel"
        if n in self.warte:
            return "wartet bei %s" % (self.warte[n],)
        return "ohne Auftrag"

    def _treffer_lage(self, n, L):
        """19.10.: wer ihn hier treffen konnte - Spaeher (naechster waehlbarer Feind; <= 160 Feinmass = sichtbar, L75),
        Schuetzen in Reichweite je Art mit freier Linie (Modell), die ihm vom Modell zugeteilten Schuetzen, Nahkaempfer <= 2,
        Loewen <= 4."""
        ort = (L[n]["x"], L[n]["y"])
        s = self._sicht
        spaeher, d_sp = None, 10 ** 9
        nah, loewe = [], []
        for e in L.values():
            p = (e["x"], e["y"])
            d = schach(ort, p)
            if e["besitzer"] == 0:
                if e["typ"] == 45 and d <= 4:
                    loewe.append(d)
                continue
            if e["besitzer"] == self.sp:
                continue
            if e["typ"] in sicht.WAEHLBAR:
                f = sicht.abstand_fein(ort, p)
                if f < d_sp:
                    spaeher, d_sp = (e["typ"], d), f
            if e["typ"] in sicht.NAHKAMPF and d <= 2:
                nah.append(e["typ"])
        teile = ["Spaeher %s" % ("Typ %d in %d Feldern (%d Feinmass, %s)" % (spaeher[0], spaeher[1], d_sp,
                                                                            "SICHTBAR" if d_sp <= sicht.SICHT else "nicht sichtbar")
                                 if spaeher else "keiner")]
        if s is not None:
            arten = {}
            for p, r, erh, steht, art in s.schuetzen:
                d2 = (p[0] - ort[0]) ** 2 + (p[1] - ort[1]) ** 2
                if d2 <= r * r:
                    a = arten.setdefault(art, [0, 0, 999])
                    a[0] += 1
                    if erh or s.linie_frei(p, steht, ort):
                        a[1] += 1
                    a[2] = min(a[2], schach(p, ort))
            teile.append("Schuetzen in Reichweite: %s" % (", ".join("%d %s (%d mit Linie, naechster %d)" % (a[0], k, a[1], a[2])
                                                                      for k, a in sorted(arten.items())) or "keine"))
            zu = s.feuer.get(n, ())
            teile.append("Modell teilt ihm zu: %s (%.1f je Takt)" % (
                ", ".join("%s in %.0f" % (k, d) for k, d in zu) or "niemand", sum(sicht.dps(k, d) for k, d in zu)))
        if nah:
            teile.append("Nahkaempfer <= 2: %s" % sorted(nah))
        if loewe:
            teile.append("Loewe in %d" % min(loewe))
        return " / ".join(teile)

    def _aus_bereit(self, n, grund, ereignis):
        """18.10.: wer in der Bereitstellung zurueckweicht, flieht oder ausweicht, verlaesst die Gruppe (sonst schickt ihn die
        Bereitstellung in der naechsten Runde wieder zum Platz) und wird fuer diese Bereitstellung gesperrt."""
        lt = self.lordtrupp
        if lt["phase"] == "bereit" and n in lt["mitglieder"]:
            lt["mitglieder"].discard(n)
            for k in ("platz", "weg", "neu", "befohlen"):
                lt.get(k, {}).pop(n, None)
            lt.setdefault("raus", set()).add(n)
            ereignis.append("LORD-BEREITSTELLUNG: %d raus (%s)" % (n, grund))

    def _front_platz(self, ort):
        """17.10.: verdeckter Warteplatz nah am Gegner - Ring FRONT_R um den naechsten feindlichen Lord, kein Beschuss, kein
        Verfolger (sicht.sicher), begehbar; der naechste zu ort. Einmal je Runde gerechnet."""
        if getattr(self, "_front_runde", None) != self.runde:
            self._front_runde, self._front = self.runde, []
            for b in getattr(self, "_feindburg", []):
                ring = []
                for r in self.FRONT_R:
                    for k in range(24):
                        w = k * math.pi / 12
                        q = (int(round(b[0] + r * math.cos(w))), int(round(b[1] + r * math.sin(w))))
                        if 2 <= q[0] <= 397 and 2 <= q[1] <= 397:
                            ring.append(q)
                # 18.10.: begehbare Ringpunkte je Lordposition merken - die Pruefung ist eine Abfrage im Spiel, das Gelaende
                # aendert sich nicht; nur die Sicherheit wird jede Runde neu gerechnet
                cache = self.__dict__.setdefault("_front_ring", {})
                if b not in cache:
                    if self.pruefe_begehbar and ring:
                        gut = self.pruefe_begehbar(ring)
                        ring = [q for q in ring if q in gut]
                    cache[b] = ring
                ring = cache[b]
                self._front += [q for q in ring if self._sicht is None or self._sicht.sicher(q)]
        return min(self._front, key=lambda q: schach(ort, q)) if self._front else None

    def _bereit_zuweisen(self, n, L, G, plaetze, ereignis):
        """17.10.: Platz fuer n = kleinstes Wegrisiko (Gefahren-Gitter, wie die Zielwahl), dann kuerzester Weg; Weg ueber
        den toten Winkel (schussfeld.sicherer_weg), sonst gerade."""
        ort = (L[n]["x"], L[n]["y"])
        g = self._gitter(L, G)
        rk = g.risiko_von(ort, TEMPO) if g is not None else {}
        def kosten(q):
            r = rk.get(g.zelle_von(q)) if g is not None else None
            return (r[0], r[1]) if r else (0, schach(ort, q))
        platz = min(plaetze, key=kosten)
        punkte = [platz]
        if g is not None:
            wp, bw, bg, _ = schussfeld.sicherer_weg(self.gelaende, L, self.sp, ort, platz, gitter=g)
            if len(wp) > 1:
                punkte = list(wp[:-1]) + [platz]
        self.lordtrupp.setdefault("platz", {})[n] = platz
        self.lordtrupp.setdefault("weg", {})[n] = punkte
        self.lordtrupp.setdefault("neu", {})[n] = 0
        self.lordtrupp.setdefault("befohlen", {})[n] = -99
        return platz

    # --- eine Runde -----------------------------------------------------------------------------------------------
    def schritt(self, L, G, sichere_orte=None, tick=None):
        ereignis, angriffe, jagen, halten, flieh = [], [], [], {}, {}
        self.runde += 1
        # 4a rechnet in TICKS, nicht in Runden (live_4, 23:05: ohne feste Wartezeiten dauert eine Runde 2-4 statt 13-20
        # Ticks - "2 Runden ohne Feldwechsel" war normales Gehen, er wechselte staendig die Richtung und wurde eingeholt).
        # Ohne Spielzeit (Pruefung ohne Spiel): RUNDE_TICKS je Runde.
        self.jetzt = tick if tick is not None else self.runde * self.RUNDE_TICKS
        if getattr(self, "_letzt_tick", None) is not None and self.jetzt > self._letzt_tick:
            rt = self.jetzt - self._letzt_tick
            self._runde_ticks = rt if not hasattr(self, "_runde_ticks") else 0.7 * self._runde_ticks + 0.3 * rt
        self._letzt_tick = self.jetzt
        self._heim = list(sichere_orte or [])          # 4a: Fluchtrichtung (Lager, Bergfried)
        # begehbare Warteplaetze: wo gerade eine eigene Nicht-Kampfeinheit steht, ist begehbarer Boden
        orte = list(sichere_orte or []) + sorted({(e["x"], e["y"]) for e in L.values()
                                                  if e["besitzer"] == self.sp and e["typ"] not in TRUPPE and e["typ"] != ASSASSINE})
        if self.pruefe_begehbar and orte:
            gut = self.pruefe_begehbar(orte)
            orte = [o for o in orte if o in gut] or orte
        fern, nah = self._feinde(L)
        self._lage(L, G)                     # 17.10.: Sicht dieser Runde (sicht.py) - vor allen Sicherheitsfragen
        self._fern = fern                    # 4a: Fluchtpunkte nicht unter feindliche Fernkaempfer
        # 4a: ihre Burg ist tabu (gewinn_1, Tick 4.312: Assassine 163 starb auf der Flucht an ihrer Aussenmauer, 13 Felder
        # neben ihrem Lord, 14 Fernkaempfer im Umkreis 40) - Fluchtpunkte und Kreismitte mind. SCHUSSWEITE von ihrem Lord
        self._feindburg = [(e["x"], e["y"]) for e in L.values() if e["typ"] == 55 and e["besitzer"] not in (0, self.sp)]
        # Rueckzugs-Kandidaten fuer alle, die Feinde nah haben - EIN Modulaufruf prueft, welche begehbar sind
        self._kand = {}
        for n in self.mitglieder:
            if n in L:
                c = self._weg_vom_feind((L[n]["x"], L[n]["y"]), fern, nah)
                if c:
                    self._kand[n] = c
        punkte = sorted({p for c in self._kand.values() for p in c})
        self._begehbar = (self.pruefe_begehbar(punkte) if self.pruefe_begehbar else set(punkte)) if punkte else set()
        # 0. Neu unter alter Nummer (17.10.): verschwunden gewesen und jetzt wieder eigener Assassine -> neuer Assassine
        for n in self.bilanz["verluste"]:
            if n not in L:
                self._frei_nr.add(n)
        neu_alt = sorted(n for n in self._frei_nr if n in L and L[n]["besitzer"] == self.sp and L[n]["typ"] == ASSASSINE)
        for n in neu_alt:
            self._frei_nr.discard(n); self.bilanz["verluste"].discard(n)
            self._vergessen(n); self.flucht.pop(n, None); self.leben.pop(n, None); self._steht.pop(n, None)
            self.akte.pop(n, None)
            self.mitglieder.add(n)
        if neu_alt:
            self.bilanz["alte_nummer"] = self.bilanz.get("alte_nummer", 0) + len(neu_alt)
            ereignis.append("NEU UNTER ALTER NUMMER: %s aufgenommen" % neu_alt)
        # 1. Verluste und Verletzungen messen
        for n in list(self.mitglieder):
            if n not in L or L[n]["besitzer"] != self.sp:
                # 19.10. (Daniel: "bei jedem verlorenen Assassinen genau notieren, warum er verletzt wurde und dann gestorben
                # ist"): Akte vor dem Vergessen - erste Verletzung, Zahl der Runden mit Treffern, letztes Umfeld, letzter Auftrag
                a = self.akte.pop(n, {})
                ereignis.append("TOD-AKTE %d: erste Verletzung: %s | Runden mit Treffern %d | Auftrag zuletzt: %s | Umfeld zuletzt: %s" % (
                    n, a.get("erst", "keine gemessen - in einer Runde von voll auf tot"), a.get("treffer", 0),
                    self._taetigkeit(n, G), self.umfeld.get(n, "unbekannt")))
                self.bilanz["verluste"].add(n); self.mitglieder.discard(n); self._vergessen(n); self.flucht.pop(n, None)
                self.bilanz["tote"] += 1
                self.lordtrupp["mitglieder"].discard(n)
                if n not in L:
                    self._frei_nr.add(n)
                ereignis.append("MESSUNG tot %d: zuletzt %s" % (n, self.umfeld.pop(n, "unbekannt")))
                self.leben.pop(n, None)
        # 17.10. (1017h: 304.000 Assassinen-Ticks Stillstand ohne Spielziel): seit wann steht er ohne Spielziel auf diesem Feld?
        for n in list(self._steht):
            if n not in self.mitglieder:
                del self._steht[n]
        # 18.10. (Gegenpruefung, 1017j: 18 von 36 "STILLSTAND geloest" trafen laufende Abrisse - beim Abreissen meldet das Spiel
        # zielart 0 und Laufziel = eigenes Feld): verliert sein Zielgebaeude Leben und steht er daneben, ist das Arbeit
        gb_leben = getattr(self, "_gb_leben", {})
        fort = {gn for gn, g in G.items() if gn in gb_leben and g["leben"] < gb_leben[gn]}
        self._gb_fort = {gn: self.jetzt for gn in fort} | {gn: tk for gn, tk in getattr(self, "_gb_fort", {}).items()
                                                           if gn in G and gn not in fort}
        self._gb_leben = {gn: g["leben"] for gn, g in G.items()}
        gm = getattr(self, "_gb_max", {})
        self._gb_max = {gn: max(gm.get(gn, 0), g["leben"]) for gn, g in G.items()}
        for n in self.mitglieder:
            f = (L[n]["x"], L[n]["y"])
            z = self.ziel.get(n)
            reisst = z in G and schach(f, (G[z]["x"], G[z]["y"])) <= self.ZIEL_NAH and \
                self.jetzt - self._gb_fort.get(z, -10 ** 9) < self.STEH_TICKS
            if L[n]["zielart"] != 0 or self._steht.get(n, (None,))[0] != f or reisst:
                self._steht[n] = (f, self.jetzt)
        verletzt = set()
        for n in self.mitglieder:
            u = self.umgebung(n, L, G, fern, nah)
            alt = self.leben.get(n)
            if alt is not None and L[n]["leben"] < alt:
                verletzt.add(n)
                ereignis.append("MESSUNG verletzt %d: leben %d -> %d | %s" % (n, alt, L[n]["leben"], u))
                a = self.akte.setdefault(n, {"treffer": 0})
                a["treffer"] += 1
                if "erst" not in a:
                    a["erst"] = "Tick %d bei (%d, %d), Leben %d -> %d, Auftrag: %s / %s" % (
                        self.jetzt, L[n]["x"], L[n]["y"], alt, L[n]["leben"], self._taetigkeit(n, G), self._treffer_lage(n, L))
                    ereignis.append("ERSTE VERLETZUNG %d: %s" % (n, a["erst"]))
            elif L[n]["leben"] >= self.VOLL:
                self.akte.pop(n, None)       # wieder voll geheilt: neue Akte beim naechsten Treffer
            self.leben[n], self.umfeld[n] = L[n]["leben"], u
        # 2. Erledigte Ziele, erledigte Jagd
        for n, z in list(self.ziel.items()):
            if z not in G:
                typ = self.ziel_typ.pop(z, None)
                if typ is not None:
                    self.bilanz["gebaeude"][typ] = self.bilanz["gebaeude"].get(typ, 0) + 1
                    ereignis.append("Gebaeude %d (Typ %d) zerstoert" % (z, typ))
                del self.ziel[n]
        for n, f in list(self.jagd.items()):
            seit = getattr(self, "_arb_seit", {}).get(n)
            if seit is not None and n in L and f in L and L[f]["typ"] not in TRUPPE and (
                    self.jetzt - seit > self.ARBEITER_ZEIT or schach((L[n]["x"], L[n]["y"]), (L[f]["x"], L[f]["y"])) > self.ARBEITER_MIT + 3):
                # 19.10. (1018x: 203 verfolgte einen weglaufenden Arbeiter 500 Takte, bis 11 Schuetzen ihn sahen): mitnehmen
                # heisst kurz - zu lang oder er laeuft weg -> lassen, das Ziel kommt in der Zielwahl wieder
                del self.jagd[n]
                self._arb_seit.pop(n, None)
                ereignis.append("ARBEITER %d laesst Arbeiter %d (laeuft weg oder dauert zu lange)" % (n, f))
                continue
            if f not in L or L[f]["besitzer"] in (0, self.sp):
                del self.jagd[n]
        # 3. Gegenprobe: laeuft er wirklich zu seinem Gebaeude?
        wirklich, abweichler = set(), 0
        for n, z in list(self.ziel.items()):
            if n in self.route:
                continue                   # 12.10. (Frage-Agent): laeuft zu einem Wegpunkt, nicht zum Gebaeude - kein Abweichler
            if schach((L[n]["laufx"], L[n]["laufy"]), (G[z]["x"], G[z]["y"])) <= self.ZIEL_NAH:
                wirklich.add(z)
            elif self.runde - self.befohlen.get(n, 0) >= self.NEU_NACH:
                abweichler += 1
                del self.ziel[n]
        # 3a. 17.10. (1017h): Stillstand - hat er im Lenker ein Ziel (Gebaeude, Route, Jagd, Stapel), steht aber STEH_TICKS ohne
        # Spielziel auf demselben Feld und will auch nirgends hin, wird der Lenker-Zustand geloest: er bekommt neu ein Ziel.
        # Routen-Laeufer waren von der Gegenprobe oben ausgenommen.
        stehen = []
        for n in sorted(self.mitglieder):
            f, seit = self._steht.get(n, (None, self.jetzt))
            if n in self.lordtrupp["mitglieder"] or self.jetzt - seit < self.STEH_TICKS:
                continue
            if schach((L[n].get("laufx", -99), L[n].get("laufy", -99)), f) > 1:
                continue
            if n in self.ziel or n in self.route or n in self.jagd or n in self.stapel["mitglieder"]:
                stehen.append("%d (%s, %d Ticks bei %s)" % (n, "Route" if n in self.route else "Gebaeude" if n in self.ziel else
                                                          "Jagd" if n in self.jagd else "Stapel", self.jetzt - seit, f))
                self._vergessen(n)
                self.stapel["mitglieder"].discard(n)
                self._steht[n] = (f, self.jetzt)
        if stehen:
            self.bilanz["stillstand"] = self.bilanz.get("stillstand", 0) + len(stehen)
            ereignis.append("STILLSTAND geloest: %s" % ", ".join(stehen))
        self.gemessen = len(wirklich)
        if abweichler:
            self.bilanz["neu_befohlen"] += abweichler
            ereignis.append("%d Assassinen liefen nicht zu ihrem Ziel - neu befohlen" % abweichler)
        # 3b. Beute (Daniel 12.10. 00:44 "erkennen, wenn Fernkaempfer sich auf dem Boden bewegen - im Nahkampf einfach zu
        # snacken"): ein Fernkaempfer am Boden (kein Turm/Torhaus im Umkreis 2), bei dem hoechstens ein Nahkaempfer steht,
        # wird von freien Assassinen im Umkreis BEUTE_R gejagt - auch statt eines Gebaeudes. GRENZE: Schuetzen auf Mauern
        # erkennt das nicht (Mauern stehen nicht in der Gebaeudeliste) - sie gelten als "am Boden"
        hoch = [(g["x"], g["y"]) for g in G.values() if g["besitzer"] not in (0, self.sp) and g["typ"] in self.ERHOEHT]
        beute = [(nr, p) for nr, p, typ in fern if all(schach(p, h) > self.HOCH_R for h in hoch)
                 and all(schach(p, b) > self.LORD_ABSTAND for b in self._feindburg) and self._anzahl(p, nah, 5) <= 1]
        # 18.10. (1018q/r: die meisten Entdeckungen durch Sklaven; 16 Assassinen standen "ohne Ziel, alle gefaehrlich" - Daniel:
        # "alle Einheiten sollten irgendwas Begruendetes machen"): ein Sklave allein (kein weiterer Nahkaempfer in 5) wird Beute,
        # wenn an seinem Ort kein Schuetze trifft (Risiko unten wie bei Fernkaempfern, Wert 5 + Spaeher weg)
        beute += [(k, (e["x"], e["y"])) for k, e in L.items() if e["typ"] == 71 and e["besitzer"] not in (0, self.sp)
                  and all(schach((e["x"], e["y"]), b) > self.LORD_ABSTAND for b in self._feindburg)
                  and self._anzahl((e["x"], e["y"]), nah, 5) <= 1 and self._sicht.beschuss((e["x"], e["y"]), self._sicht.RAND) <= 0]
        # 19.10. (Daniel: "sie beachten die Bauern nicht - die koennen gerne Bauern mitnehmen, aber Holzfaeller machen gut
        # Damage; das kann in Kauf genommen werden, aber mit wenig Leben lieber den Holzfaellern ausweichen"): feindliche Arbeiter
        # bis ARBEITER_MIT Felder, an deren Ort kein Schuetze trifft, nimmt jede Assassine unterwegs mit (auch mit Ziel);
        # schlagende Arbeiter (ARBEITER_GEFAHR) nur, wer gesund ist
        # 19.10. (1018v: 55 Arbeiter-Jagden in 300 Runden, drei Assassinen starben an derselben Stelle bei der Jagd auf einen
        # Bergmann - die KI schickt Verteidiger; dazu kostete jede Jagd die Wegrisiko-Rechnung, 0,7 s je Runde): nur Arbeiter
        # bis ARBEITER_MIT Felder, kein waehlbarer Feind bis ARBEITER_FREI Felder (Sicht-Abstand), je Arbeiter EIN Jaeger;
        # die Jagd ist kurz - ohne Gefahren-Gitter
        jaeger = set(self.jagd.values())
        alle_arb = getattr(self, "_alle_arbeiter", [])
        nahe = [(k, p, typ) for k, p, typ in alle_arb
                if any(schach(p, (L[m]["x"], L[m]["y"])) <= self.ARBEITER_MIT for m in self.mitglieder if m in L)] if alle_arb else []
        arbeiter_b = [(k, p) for k, p, typ in nahe if k not in jaeger
                      and all(schach(p, b) > self.LORD_ABSTAND for b in self._feindburg)
                      and self._sicht.sicht_abstand(p) > self.ARBEITER_FREI * 8]
        schlagend = {k for k, p, typ in alle_arb if typ in self.ARBEITER_GEFAHR}
        for n in sorted(self.mitglieder):
            if n in self.jagd or n in self.lordtrupp["mitglieder"] or n in self.stapel["mitglieder"] or n in self.flucht or n not in L \
                    or n in self.entdeckt:
                continue
            ort = (L[n]["x"], L[n]["y"])
            schwach_n = L[n]["leben"] < self.EIN_TREFFER
            mit = [b_ for b_ in arbeiter_b if schach(ort, b_[1]) <= self.ARBEITER_MIT and b_[0] not in jaeger
                   and not (schwach_n and b_[0] in schlagend)]
            if mit:
                ziel_a = min(mit, key=lambda b_: schach(ort, b_[1]))
                self.ziel.pop(n, None); self.route.pop(n, None); self.warte.pop(n, None)
                self.jagd[n] = ziel_a[0]
                self._arb_seit = getattr(self, "_arb_seit", {})
                self._arb_seit[n] = self.jetzt
                jaeger.add(ziel_a[0])
                jagen.append((n, ziel_a[0]))
                ereignis.append("ARBEITER %d nimmt Arbeiter %d (Typ %d) %d Felder neben dem Weg mit" % (
                    n, ziel_a[0], L[ziel_a[0]]["typ"], schach(ort, ziel_a[1])))
                continue
            if n in self.ziel or n in self.route or (self._raid_plaetze or 0) > len(self.ziel):
                continue                       # 17.10.: Raiden geht vor (Daniel)
            if schwach_n:
                continue                       # 19.10. (1018s, 262 jagte mit 1.460 Leben einen Sklaven und starb im Nahkampf)
            nah_b = [b_ for b_ in beute if schach(ort, b_[1]) <= self.BEUTE_R]
            # 17.10. (Partie 1017a: Assassine 195 jagte eine Armbrust neben 21 Schuetzen und starb in ~80 Takten): Risiko gegen
            # Ertrag wie bei Gebaeuden - Beschuss am Beuteort (nachgebaute Zielwahl der Schuetzen, sicht.py) x (Weg + gemessene
            # Toetungszeit = Leben / Nahkampf-Rate) gegen Wert der Einheit (Anwerbepreis L63) und Preis einer Assassine
            beste_b = None
            # 17.10. (Daniel: "manche gehen frontal auf Fernkaempfer"): Risiko auf dem WEG wie bei Gebaeuden (Gefahren-Gitter),
            # nicht nur am Beuteort
            g_b = self._gitter(L, G) if nah_b else None
            rk_b = g_b.risiko_von(ort, TEMPO) if g_b is not None else {}
            for b_ in nah_b:
                ziel_e = L.get(b_[0], {})
                t_toeten = ziel_e.get("leben", 10000) / float(NAHKAMPF_RATE.get(ziel_e.get("typ"), 230))
                t_weg = schach(ort, b_[1]) * TEMPO
                r_weg = rk_b.get(g_b.zelle_von(b_[1])) if g_b is not None else None
                risiko = (r_weg[0] + self._sicht.beschuss(b_[1], 16) * t_toeten) if r_weg else                     self._sicht.beschuss(b_[1], 16) * (t_toeten + t_weg)
                p_tod = min(1.0, risiko / max(1.0, float(L[n]["leben"])))
                saldo = EINHEIT_WERT.get(ziel_e.get("typ"), 30) * (1 - p_tod) - p_tod * self.KOSTEN
                if saldo > 0 and p_tod <= self.BEUTE_RISIKO and (beste_b is None or saldo / (t_toeten + t_weg) > beste_b[0]):
                    beste_b = (saldo / (t_toeten + t_weg), b_, p_tod, saldo, t_toeten)
            if beste_b:
                _, ziel_b, p_tod, saldo, t_toeten = beste_b
                self.ziel.pop(n, None); self.warte.pop(n, None)
                self.jagd[n] = ziel_b[0]
                jagen.append((n, ziel_b[0]))
                typ_b = L[ziel_b[0]]["typ"]
                ereignis.append("BEUTE %d jagt Fernkaempfer %d (Typ %d) am Boden (%d Felder): Saldo %.0f, Todesrisiko %.0f %%, "
                                "toeten %.0f Takte, Wert %s" % (n, ziel_b[0], typ_b, schach(ort, ziel_b[1]), saldo, 100 * p_tod,
                                                               t_toeten, "gemessen" if typ_b in EINHEIT_WERT_GEMESSEN else "geschaetzt"))
        self._fertig = set()                 # 19.10.: diese Runde "fertig zuerst" - 4/4b lassen sie in Ruhe
        self._entdeckt_pruefen(L, G, ereignis, flieh, jagen, angriffe)
        self._loewenjagd(L, jagen, ereignis)
        # 4. Verletzt im Schussfeld: Rueckzug oder zuschlagen
        for n in verletzt:
            if n in self.entdeckt or n in self._fertig:
                continue                   # 19.10.: laeuft schon ausser Sicht und Reichweite / reisst erst fertig ab
            ort = (L[n]["x"], L[n]["y"])
            nf = self._naechster(ort, fern)
            # 17.10. (L75/L78 statt RUECKZUG_FERN 40): nur wer gerade beschossen werden kann, zieht sich zurueck - und nur, wenn
            # der Beschuss bis zum Ende seines Gebaeude-Angriffs sein Leben ueberstiege (Risiko gegen Ertrag, Daniel 12.10. 01:49)
            b_ort = self._sicht.beschuss(ort)
            if b_ort <= 0:
                continue
            gz = self.ziel.get(n)
            if gz in G and n not in self.route and \
                    b_ort * self._arbeit(G[gz]["typ"], sum(1 for z in self.ziel.values() if z == gz)) < L[n]["leben"]:
                continue
            if self._im_lordangriff(n):
                continue                   # der Lord-Trupp bleibt dran (gebuendelt; Daniel: nur die letzten Lebenspunkte zaehlen)
            self._aus_bereit(n, "verletzt im Beschuss, Rueckzug", ereignis)
            if n in self.stapel["mitglieder"]:
                if L[n]["leben"] >= self.STAPEL_RUECKZUG * self.VOLL:
                    continue
                self.stapel["mitglieder"].discard(n)
            if nf[0] <= self.ZUSCHLAGEN and self._anzahl(ort, nah, 5) <= 1:
                if self.jagd.get(n) != nf[1]:
                    self.ziel.pop(n, None); self.warte.pop(n, None)
                    self.jagd[n] = nf[1]
                    jagen.append((n, nf[1]))
                    self.bilanz["zuschlagen"] += 1
                continue
            sicher = self._sicherer_ort(ort, orte, fern, nah, n)
            if sicher and self.warte.get(n) != sicher:
                self._vergessen(n)
                self._warten(n, sicher, halten)
                self.bilanz["rueckzug"] += 1
        # 4a. Uebermacht im Nahkampf (Daniel 05.10. 22:16: "der erste Assassine wurde leider weggeworfen und von ihren
        # Verteidigungs-Assassinen genommen (3 vs 1) - er haette lieber davor weggehen sollen, bis sie ihn nicht mehr
        # verfolgen, und dann weiter angreifen sollen, anstatt einfach zu sterben"). Gemessen in raidzuerst_1 (Tick 2.429):
        # drei feindliche Assassinen 2 Felder neben ihm, Leben 11.720 -> 920 in ~50 Ticks, kein Rueckzug - Regel 4 kennt
        # nur Fernkaempfer. Neu: mehr feindliche Nahkaempfer als eigene Assassinen im Umkreis UEBERMACHT_R -> kurz weg vom
        # Feind; kein neues Ziel, bis FLUCHT_RUHE Runden lang kein feindlicher Nahkaempfer im Umkreis SICHER_NAH stand.
        eigene_orte = [(L[m]["x"], L[m]["y"]) for m in self.mitglieder]
        for n in sorted(self.mitglieder):
            if self._im_lordangriff(n) or n in self.entdeckt or n in getattr(self, "_loewen_jaeger", ()):
                continue                   # 19.10.: wer entdeckt ist, flieht nach ENTDECKT (Schuetzen UND Verfolger); Loewenjaeger bleiben                   # der Lord-Angriff bleibt dran (Daniel 21:47)
            ort = (L[n]["x"], L[n]["y"])
            feinde = self._bedrohung(ort, nah, L[n]["leben"] < self.EIN_TREFFER)
            eigene = sum(1 for q in eigene_orte if schach(ort, q) <= self.UEBERMACHT_R)
            if n in self.flucht:
                verfolger = self._naechster(ort, [x for x in nah if self.NAH_GEFAHR.get(x[2], 1.0) >= self.VERFOLGER_AB])[0]
                if verfolger > self.FLUCHT_FREI:
                    frei = self.flucht[n].setdefault("frei_seit", self.jetzt)
                    if self.jetzt - frei >= self.RUHE_TICKS:
                        del self.flucht[n]
                        self.warte.pop(n, None); self.warte_seit.pop(n, None)
                        ereignis.append("AUSWEICHEN vorbei %d: %d Ticks kein Verfolger im Umkreis %d - greift wieder an (Leben %d)" % (
                            n, self.jetzt - frei, self.FLUCHT_FREI, L[n]["leben"]))
                    continue
                self.flucht[n].pop("frei_seit", None)
                # noch verfolgt: weiter weg, Richtung Heim (eigene Truppen) - auch mitten im Nahkampf. Gemessen raidzuerst_2:
                # ein einziger kurzer Rueckzug reichte nicht (unterwegs 2.481 und am Warteplatz 2.941 eingeholt).
                # Gemessen raidzuerst_3: ein NEUER Befehl in jeder Runde (neue Gruppe) liess ihn immer wieder kurz stehen -
                # 3 Felder in 60 Ticks, Leben 11.720 -> 3.020. Darum nur neu befehlen, wenn er NICHT schon zu seinem
                # Fluchtpunkt laeuft (steht, kaempft, anderes Laufziel) oder dort angekommen ist.
                o, lauf = self.warte.get(n), (L[n]["laufx"], L[n]["laufy"])
                laeuft_weg = o is not None and L[n]["zustand"] == 101 and schach(lauf, o) <= 2 and schach(ort, o) > 3
                # raidzuerst_4: Zustand "laeuft", Laufziel stimmt - und doch 30 Ticks auf demselben Feld (blockiert). Steht er
                # trotz Laufbefehl auf dem Feld der letzten Runde: sofort eine andere Richtung (Daniel: "durchklicken oder ausweichen")
                # raidzuerst_5: er laeuft ~1 Feld je 17 Ticks, eine Runde dauert 13-20 Ticks - EINE Runde auf demselben Feld ist
                # normales Gehen (sonst Zickzack: 1.150 Ticks fuer 45 Felder). Blockiert erst nach 2 Runden ohne Feldwechsel.
                f = self.flucht[n]
                if f.get("letzt") != ort or "feld_seit" not in f:
                    f["feld_seit"] = self.jetzt            # seit wann steht er auf diesem Feld (Spielzeit)
                f["letzt"] = ort
                # raidzuerst_9: am Kartenrand (160,43) kam er nicht weiter, Zustand 1 (steht) statt 101 - "blockiert" griff nicht,
                # er bekam immer wieder denselben unerreichbaren Punkt und wurde eingeholt. Blockiert = 2 Runden kein Feldwechsel,
                # solange er nicht am Fluchtpunkt ist - egal welcher Zustand.
                blockiert = o is not None and schach(ort, o) > 3 and self.jetzt - f["feld_seit"] >= self.BLOCK_TICKS
                if laeuft_weg and not blockiert:
                    ziel = None
                else:
                    if blockiert:
                        self.flucht[n].setdefault("gesperrt", []).append(o)
                    ziel = self._fluchtpunkt(ort, nah, n, L, nicht_bei=self.flucht[n].get("gesperrt"), mitte=self.flucht[n].get("mitte"))
                if ziel:
                    self._fliehen(n, ziel, flieh)
                ereignis.append("FLUCHT %d: ort %s zustand %d lauf %s Verfolger in %d Leben %d -> %s" % (
                    n, ort, L[n]["zustand"], lauf, verfolger, L[n]["leben"],
                    "laeuft weiter" if ziel is None and laeuft_weg else "%sneu nach %s (Heim: %s)" % (
                        "BLOCKIERT - " if blockiert else "", ziel, "; ".join(getattr(self, "_heimgrund", [])))))
                continue
            if feinde == 0 or feinde <= eigene:
                continue
            sicher = self._fluchtpunkt(ort, nah, n, L) or self._sicherer_ort(ort, orte, fern, nah, n)
            if not sicher:
                continue                       # kein Weg weg: weiterkaempfen
            self._vergessen(n)
            self.stapel["mitglieder"].discard(n)
            self._aus_bereit(n, "Flucht vor Nahkampf-Uebermacht", ereignis)
            self._fliehen(n, sicher, flieh)
            # Kreismitte (T2): KREIS_MITTE Felder in der ersten Fluchtrichtung, nicht naeher als KREIS_RAND am Kartenrand
            lang = max(schach(ort, sicher), 1)
            mitte = [ort[i] + (sicher[i] - ort[i]) * self.KREIS_MITTE / lang for i in (0, 1)]
            # der ganze Ring soll HEIM_ABSTAND von der Burg wegbleiben: Mitte notfalls von der naechsten Burg wegschieben
            # (Pruefung 18: Mitte 17 Felder neben dem Bergfried, halber Ring gesperrt, er driftete zur Burg)
            tabu = [(h, self.HEIM_ABSTAND + self.KREIS_R) for h in getattr(self, "_heim", [])]
            tabu += [(b, SCHUSSWEITE + self.KREIS_R) for b in getattr(self, "_feindburg", [])]
            for h, soll in tabu:
                d = max(abs(mitte[0] - h[0]), abs(mitte[1] - h[1]))
                if d < soll:
                    vx, vy = mitte[0] - h[0], mitte[1] - h[1]
                    if vx == 0 and vy == 0:
                        vx, vy = mitte[0] - ort[0] or 1, mitte[1] - ort[1]
                    f = soll / max(abs(vx), abs(vy))
                    mitte = [h[0] + vx * f, h[1] + vy * f]
            mitte = tuple(min(400 - self.KREIS_RAND, max(self.KREIS_RAND, int(round(v)))) for v in mitte)
            self.flucht[n] = {"seit": self.runde, "ruhig": 0, "letzt": ort, "mitte": mitte}
            self.bilanz["uebermacht"] = self.bilanz.get("uebermacht", 0) + 1
            ereignis.append("AUSWEICHEN %d: Bedrohung %.1f (Nahkaempfer im Umkreis %d, schlagende Arbeiter im Umkreis %d) gegen %d "
                            "eigene, Leben %d -> nach %s (Heim: %s)" % (n, feinde, self.UEBERMACHT_R, self.ARBEITER_R, eigene,
                                                                       L[n]["leben"], sicher, "; ".join(getattr(self, "_heimgrund", []))))
        # 4b. Ausweichen, bevor es weh tut: rueckt eine Gruppe Fernkaempfer heran, Ziel aufgeben
        for n in self.mitglieder:
            if n in verletzt or n in self.jagd or n in self.warte or n in self.stapel["mitglieder"] or self._im_lordangriff(n)                     or n in self._fertig:
                continue
            ort = (L[n]["x"], L[n]["y"])
            # 17.10. (statt VORAUS_FERN/VORAUS_ANZAHL: 3 Schuetzen im Umkreis 10): ausweichen, wenn er hier beschossen werden
            # kann und der Beschuss bis zum Ende seines Auftrags sein Leben ueberstiege; auf einer sicheren Route nicht (die
            # Route ist schon um die Gefahr gerechnet)
            if n in self.route:
                # 18.10. (Gegenpruefung, 1017k: die Route von 86 fuehrte ~2.400 Takte durch Zellen mit 18-19 Beschuss je Takt,
                # nie neu bewertet): liegt der Ort oder das Stueck bis zum naechsten Wegpunkt im Beschuss, Ziel aufgeben - die
                # Zielwahl rechnet in dieser Runde einen neuen Weg (oder nimmt ein anderes Ziel)
                punkte = self.route[n]["punkte"]
                stueck = [ort] + ([tuple(punkte[0])] if punkte else [])
                probe = []
                for a_, b_ in zip(stueck, stueck[1:]):
                    k_ = max(1, schach(a_, b_) // 2)
                    probe += [(a_[0] + (b_[0] - a_[0]) * i // k_, a_[1] + (b_[1] - a_[1]) * i // k_) for i in range(k_ + 1)]
                if any(self._sicht.beschuss(q, self._sicht.RAND) > 0 for q in (probe or [ort])):
                    ereignis.append("ROUTE GEFAEHRLICH %d bei %s: Ziel %s aufgegeben, neuer Weg" % (n, ort, self.ziel.get(n)))
                    # 18.10. (1017l: 86 pendelte 29 -> Route gefaehrlich -> anderes Ziel -> Zielwechsel zurueck auf 29, dreimal):
                    # der Zielwechsel prueft keinen Weg - dieses Ziel ist fuer ihn SPERRE_ROUTE Takte gesperrt
                    self._route_sperre[(n, self.ziel.get(n))] = self.jetzt + self.SPERRE_ROUTE
                    self._vergessen(n)
                continue
            b_ort = self._sicht.beschuss(ort)
            gz = self.ziel.get(n)
            rest = self._arbeit(G[gz]["typ"], sum(1 for z in self.ziel.values() if z == gz)) if gz in G else self.RUNDE_TICKS
            if b_ort > 0 and b_ort * rest >= L[n]["leben"]:
                sicher = self._sicherer_ort(ort, orte, fern, nah, n)
                if sicher:
                    self._vergessen(n)
                    self._aus_bereit(n, "Beschuss am Ort, ausgewichen", ereignis)
                    self._warten(n, sicher, halten)
                    self.bilanz["ausgewichen"] = self.bilanz.get("ausgewichen", 0) + 1
        # 4c. Gegenprobe Warten: laeuft er nach NEU_NACH Runden nicht zu seinem sicheren Ort, neu schicken (mit Messzeile)
        for n, o in list(self.warte.items()):
            if self.runde - self.warte_seit.get(n, self.runde) < self.NEU_NACH or n in halten.get(o, []) or n in self.flucht:
                continue
            ort, lauf = (L[n]["x"], L[n]["y"]), (L[n]["laufx"], L[n]["laufy"])
            if schach(ort, o) > 4 and schach(lauf, o) > 4:
                ereignis.append("MESSUNG warten klappt nicht %d: ort %s lauf %s Platz %s zustand %d zielart %d - Platz gesperrt" % (
                    n, ort, lauf, o, L[n]["zustand"], L[n]["zielart"]))
                self.schlechte_orte.add(o)
                neu_o = self._sicherer_ort(ort, orte, fern, nah, n)
                if neu_o:
                    self._warten(n, neu_o, halten)
                self.bilanz["warten_neu"] = self.bilanz.get("warten_neu", 0) + 1
        # 5a. GEMEINSAM AUF DEN LORD (Daniel 05.10. 23:51, 06.10.): sobald so viele leben, wie die Lage braucht, ausser
        # Schussweite sammeln; sobald die kleinste ausreichende Gruppe AM TREFFPUNKT steht, geht EIN Angriffsbefehl an genau
        # diese heraus - Nachzuegler werden nicht abgewartet, sie raiden weiter. Unter LORD_REST Ueberlebenden beginnt der
        # Ablauf wieder mit Raids.
        lord_befehl = None
        lord_lauf, lord_ziel = {}, []        # 17.10.: Laufbefehle {Ort: [n]} und Angriffsbefehle auf den Lord
        lt = self.lordtrupp
        lt["mitglieder"] = {n for n in lt["mitglieder"] if n in self.mitglieder}
        lords = [(n, e) for n, e in L.items() if e["typ"] == 55 and e["besitzer"] not in (0, self.sp)]
        if not lords:
            lt.update(mitglieder=set(), phase=None, sammelpunkt=None)
        else:
            # 17.10. (Partie 1017d: Anlauf auf einen Lord 227 Felder weit): der Lord, der dem Mittel unserer Assassinen am
            # naechsten steht; laeuft schon ein Anlauf, bleibt es sein Lord
            mx = sum(L[k]["x"] for k in self.mitglieder if k in L) / max(1, len(self.mitglieder))
            my = sum(L[k]["y"] for k in self.mitglieder if k in L) / max(1, len(self.mitglieder))
            # 18.10. (Gegenpruefung): ist der Lord der laufenden Bereitstellung bzw. des Angriffs weg (tot), Gruppe aufloesen -
            # sonst stuermte die Restgruppe ohne Bereitstellung den zweiten Lord, der Angriffsbefehl zielte auf die tote Nummer
            if lt["phase"] in ("bereit", "angriff") and lt.get("lord") not in {k for k, _ in lords}:
                if lt["phase"] == "angriff" and self.angriffe:
                    self.angriffe[-1]["lord_nachher"] = 0
                ereignis.append("LORD %s weg (tot?) - Lord-Trupp aufgeloest, %d raiden wieder" % (lt.get("lord"), len(lt["mitglieder"])))
                for k in list(lt["mitglieder"]):
                    self._vergessen(k)
                lt.update(mitglieder=set(), phase=None, lord=None, sammelpunkt=None, pause_bis=self.jetzt + self.BEREIT_PAUSE)
            fest = [x for x in lords if x[0] == lt.get("lord")] if lt["phase"] else []
            ln, le = fest[0] if fest else min(lords, key=lambda x: (schach((x[1]["x"], x[1]["y"]), (mx, my)), x[0]))
            lp = (le["x"], le["y"])
            n_bedarf, bedarf_art, gruppe_leben = self._lord_bedarf(L, G, ereignis)
            # 17.10. (1017c-e: vorlaeufiger Bedarf 40 = alle Lebenden, auch 211 Felder weit; Anlauf jedes Mal abgebrochen):
            # ohne gemessene Lage die kleinste Gruppe, mit der die Kampfrechnung (lord_machbar: 98,6 je Assassine und Takt,
            # der Lord toetet alle ~90 Takte eine, Feuer der Schuetzen am Lord verteilt) den Lord schafft. OFFEN: Verluste auf
            # dem Anmarsch rechnet sie nicht - jeder Angriff schreibt Groesse und Ausgang mit (Alle-auf-den-Lord im Bericht).
            if bedarf_art != "belegt":
                f_ges = self._sicht.feuer_gesamt(lp)
                von_a = self._anlauf_von(L, lp)
                n_r = next((k for k in range(5, len(self.mitglieder) + 1)
                            if lord_machbar(k, le["leben"], f_ges / k, leben=self._anlauf_leben(von_a, lp, k))[0]), None)
                if n_r is not None:
                    if (n_r, "gerechnet") != getattr(self, "_bedarf_rech", None):
                        self._bedarf_rech = (n_r, "gerechnet")
                        ereignis.append("LORD-BEDARF gerechnet: %d (statt %d %s) - Lord %d Leben, Feuer am Lord %.1f je Takt" % (
                            n_r, n_bedarf, bedarf_art, le["leben"], f_ges))
                    n_bedarf, bedarf_art, gruppe_leben = n_r, "gerechnet", None
            # 17.10. Laptop (1017h): Bereitstellung statt gestaffeltem Anlauf - die Gruppe zaehlt ganz (unterwegs + bereit)
            if lt["phase"] == "angriff" and len(lt["mitglieder"]) < self.LORD_REST:
                ereignis.append("GEMEINSAMER LORD-ANGRIFF vorbei: noch %d leben, Lord-Leben %d - wieder raiden bis %d" % (
                    len(lt["mitglieder"]), le["leben"], n_bedarf))
                for n in list(lt["mitglieder"]):
                    self._vergessen(n)
                lt.update(mitglieder=set(), phase=None, sammelpunkt=None, pause_bis=self.jetzt + self.BEREIT_PAUSE)
            pos = lambda k: (L[k]["x"], L[k]["y"])
            # 12.10. 01:55 (Daniel: "das wird beim besten Willen nicht reichen - besser die Assassinen fuers Raiden nutzen, wenn du
            # weisst, es reicht nicht wegen Lord-Leben UND vor allem der Fernkaempfer in Sichtweite"): Kampf vorher durchrechnen
            # 17.10.: am Lord ist sie sichtbar; alle Schuetzen mit freier Linie zum Lord verteilen ihr Feuer auf die Gruppe
            if lt["phase"] is None:
                n_l = len(self.mitglieder)
            elif lt["phase"] == "bereit":
                n_l = min(n_bedarf, len(self.mitglieder))
            else:
                n_l = len(lt["mitglieder"])
            satz_lord = self._sicht.feuer_gesamt(lp) / max(1, n_l)
            machbar, t_l, rest_l = lord_machbar(n_l, le["leben"], satz_lord,
                                                leben=self._anlauf_leben(self._anlauf_von(L, lp), lp, n_l))
            if lt["phase"] == "bereit" and not machbar:
                ereignis.append("LORD-BEREITSTELLUNG ABGEBROCHEN: reicht nicht mehr (Lord %d Leben, Beschuss am Lord %.1f je Tick) - alle raiden" % (
                    le["leben"], satz_lord))
                for k in list(lt["mitglieder"]):
                    self._vergessen(k)
                lt.update(mitglieder=set(), phase=None, pause_bis=self.jetzt + self.BEREIT_PAUSE)
            if lt["phase"] == "bereit" and self.jetzt - lt.get("seit_tick", self.jetzt) > self.BEREIT_MAX:
                ereignis.append("LORD-BEREITSTELLUNG ABGEBROCHEN: nach %d Ticks erst %d von %d bereit - alle raiden" % (
                    self.jetzt - lt["seit_tick"], len(lt.get("bereit", ())), n_bedarf))
                for k in list(lt["mitglieder"]):
                    self._vergessen(k)
                lt.update(mitglieder=set(), phase=None, pause_bis=self.jetzt + self.BEREIT_PAUSE)
            if not self.angriff_aus and lt["phase"] is None and len(self.mitglieder) >= n_bedarf and self.jetzt >= lordschutz.BIS \
                    and not machbar and self.runde % 20 == 0:
                ereignis.append("LORD-ANGRIFF NICHT MACHBAR mit %d: Lord %d Leben, Beschuss am Lord %.1f je Tick und Assassine -> raiden" % (
                    len(self.mitglieder), le["leben"], satz_lord))
            # Raiden geht vor (Daniel 17.10.): nur der Ueberschuss ueber die lohnenden Raid-Plaetze geht auf den Lord
            plaetze_r = self._raid_plaetze if self._raid_plaetze is not None else len(self.mitglieder)
            ueber = len(self.mitglieder) - plaetze_r
            spaet = self.LORD_SPAETESTENS is not None and self.jetzt >= lordschutz.BIS + self.LORD_SPAETESTENS
            if not self.angriff_aus and lt["phase"] is None and len(self.mitglieder) >= n_bedarf and self.jetzt >= lordschutz.BIS \
                    and machbar and ueber < n_bedarf and not spaet and self.runde % 20 == 0:
                ereignis.append("LORD WARTET: Raiden geht vor - %d Assassinen, %d lohnende Raid-Plaetze (Lord-Gruppe %d erst ab Ueberschuss)" % (
                    len(self.mitglieder), plaetze_r, n_bedarf))
            if not self.angriff_aus and not self.lord_aus and lt["phase"] is None and len(self.mitglieder) >= n_bedarf \
                    and self.jetzt >= lordschutz.BIS and machbar and (ueber >= n_bedarf or spaet) and self.jetzt >= lt.get("pause_bis", 0):
                plaetze = self._bereit_plaetze(lp)
                if plaetze:
                    # zuerst, wer kein Raid-Ziel hat, dann die naechsten am Lord (1017d: nie die weitesten)
                    gruppe = sorted((k for k in self.mitglieder if k not in self.flucht),
                                    key=lambda k: (k in self.ziel or k in self.jagd, schach(pos(k), lp), -L[k]["leben"], k))[:n_bedarf]
                    lt.update(mitglieder=set(gruppe), warte=set(), lord=ln, phase="bereit", seit=self.runde, seit_tick=self.jetzt,
                              sammelpunkt=None, platz={}, weg={}, neu={}, befohlen={}, bereit=set(), plaetze=plaetze, raus=set())
                    for k in gruppe:
                        self._vergessen(k)
                        self.stapel["mitglieder"].discard(k)
                        self.flucht.pop(k, None)
                        self._bereit_zuweisen(k, L, G, plaetze, ereignis)
                    ereignis.append("LORD-BEREITSTELLUNG: %d Assassinen zu %d verdeckten Plaetzen %s Felder vom Lord %d, Wege %d-%d Felder (Bedarf %d %s; %s; %d Raid-Plaetze)" % (
                        len(gruppe), len(set(lt["platz"].values())), "/".join(map(str, self.BEREIT_R)), ln,
                        min(schach(pos(k), lt["platz"][k]) for k in gruppe), max(schach(pos(k), lt["platz"][k]) for k in gruppe),
                        n_bedarf, bedarf_art, "spaetestens" if spaet and ueber < n_bedarf else "Ueberschuss %d" % ueber, plaetze_r))
            if lt["phase"] == "bereit":
                # Tote ersetzen (1017f: sonst Abbruch beim ersten Toten) - zuerst Freie ohne Raid-Ziel, dann die naechsten
                frei_k = sorted((k for k in self.mitglieder if k not in lt["mitglieder"] and k not in lt.get("raus", ())
                                 and k not in self.flucht),
                                key=lambda k: (k in self.ziel or k in self.jagd, schach(pos(k), lp), -L[k]["leben"], k))
                while frei_k and len(lt["mitglieder"]) < n_bedarf:
                    k = frei_k.pop(0)
                    self._vergessen(k); self.stapel["mitglieder"].discard(k); self.flucht.pop(k, None)
                    lt["mitglieder"].add(k)
                    self._bereit_zuweisen(k, L, G, lt["plaetze"], ereignis)
                    ereignis.append("LORD-BEREITSTELLUNG: %d rueckt nach (Platz %s)" % (k, lt["platz"][k]))
                bereit = set()
                for k in sorted(lt["mitglieder"]):
                    platz = lt["platz"].get(k)
                    if platz is None:
                        platz = self._bereit_zuweisen(k, L, G, lt["plaetze"], ereignis)
                    if schach(pos(k), platz) <= self.BEREIT_NAH:
                        # 18.10. (Gegenpruefung): der Platz wurde nur beim Start geprueft - wird er unsicher (Schuetzen ruecken
                        # nach) oder verliert der Wartende dort Leben, Platz streichen und einen neuen nehmen
                        if k in verletzt or not self._sicht.sicher(platz):
                            lt["plaetze"] = [q for q in lt["plaetze"] if q != platz]
                            if not lt["plaetze"]:
                                lt["plaetze"] = [q for q in self._bereit_plaetze(lp) if q != platz]
                            if lt["plaetze"]:
                                neu_p = self._bereit_zuweisen(k, L, G, lt["plaetze"], ereignis)
                                ereignis.append("LORD-BEREITSTELLUNG: Platz %s unsicher - %d nach %s" % (platz, k, neu_p))
                            else:
                                self._aus_bereit(k, "kein sicherer Platz mehr", ereignis)
                            continue
                        bereit.add(k)
                        continue
                    weg = lt["weg"][k]
                    while len(weg) > 1 and schach(pos(k), weg[0]) <= self._vorlauf():
                        weg.pop(0)
                        lt["neu"][k] = 0           # 18.10.: Wegpunkt erreicht = er laeuft; nur Befehle ohne Fortschritt zaehlen
                    lauf = (L[k].get("laufx", -99), L[k].get("laufy", -99))
                    # 18.10.: blockiert = steht STEH_TICKS ohne Spielziel auf demselben Feld, auch wenn das Laufziel noch stimmt
                    f_s, seit_s = self._steht.get(k, (None, self.jetzt))
                    blockiert = f_s == pos(k) and self.jetzt - seit_s >= self.STEH_TICKS
                    # 18.10.: im Spiel zeigt das Laufziel beim Gehen nur 1 Feld voraus (1017j, Assassine 336) - "Laufziel = eigenes
                    # Feld" heisst also nicht "steht". Gezaehlt werden nur Befehle ohne Fortschritt seit dem letzten Befehl
                    if schach(pos(k), lt.setdefault("ort_bef", {}).get(k, pos(k))) > 1:
                        lt["neu"][k] = 0
                    if (schach(lauf, weg[0]) > 2 or blockiert) and self.runde - lt["befohlen"].get(k, -99) >= 2:
                        if lt["neu"].get(k, 0) >= self.BEREIT_NEU and (schach(lauf, pos(k)) <= 1 or blockiert):
                            ereignis.append("LORD-BEREITSTELLUNG: %d laeuft nach %d Befehlen nicht los (Feld %s, Zustand %d) - raus, raidet" % (
                                k, lt["neu"][k], pos(k), L[k]["zustand"]))
                            self._aus_bereit(k, "laeuft nicht los", ereignis)
                            continue
                        lt["neu"][k] = lt["neu"].get(k, 0) + 1
                        lt["befohlen"][k] = self.runde
                        lt["ort_bef"][k] = pos(k)
                        lord_lauf.setdefault(weg[0], []).append(k)
                lt["bereit"] = bereit
                if len(bereit) >= n_bedarf and lord_machbar(len(bereit), le["leben"], self._sicht.feuer_gesamt(lp) / len(bereit),
                                                            leben=self._anlauf_leben(self._anlauf_von(L, lp), lp, len(bereit)))[0]:
                    alle = sorted(bereit)
                    for k in lt["mitglieder"] - bereit:
                        self._vergessen(k)            # wer noch unterwegs ist, raidet weiter
                    lt.update(mitglieder=set(alle), phase="angriff", seit=self.runde, angriff_tick=self.jetzt)
                    for k in alle:
                        if schach(pos(k), lp) > self.ANLAUF_NAH:
                            lord_lauf.setdefault(lp, []).append(k)
                        else:
                            lord_ziel.append(k)
                    self.bilanz["lordtrupps"] = self.bilanz.get("lordtrupps", 0) + 1
                    wege = sorted(schach(pos(k), lp) for k in alle)
                    self.angriffe.append({"runde": self.runde, "groesse": len(alle), "lord_vorher": le["leben"], "lord_nachher": le["leben"],
                                          "fern": self._anzahl(lp, fern, self.LORD_UMKREIS), "nah": self._anzahl(lp, nah, self.LORD_UMKREIS),
                                          "weg_min": wege[0], "weg_max": wege[-1], "am_lord_max": 0, "erreicht_runde": None,
                                          "anderes": {}, "truppe": set(alle), "verluste": 0,
                                          "bedarf": n_bedarf, "bedarf_art": bedarf_art, "bedarf_grund": self.bedarf_grund,
                                          "fingerabdruck": self.bedarf_fa})
                    ereignis.append("GEMEINSAM-AUF-LORD: %d Assassinen bereit, greifen zugleich an (Wege %d-%d Felder, Bereitstellung %d Ticks; Lord %d Leben, Fern %d / Nah %d um ihn)" % (
                        len(alle), wege[0], wege[-1], self.jetzt - lt["seit_tick"], le["leben"],
                        self._anzahl(lp, fern, self.LORD_UMKREIS), self._anzahl(lp, nah, self.LORD_UMKREIS)))
                elif self.runde % 10 == 0:
                    ereignis.append("LORD-BEREITSTELLUNG: %d/%d bereit, %d in der Gruppe (seit %d Ticks)" % (
                        len(bereit), n_bedarf, len(lt["mitglieder"]), self.jetzt - lt["seit_tick"]))
            elif self.angriff_aus and lt["phase"] is None and len(self.mitglieder) >= min(n_bedarf, self.LORD_SAMMELN_AB):
                punkt = self._lord_sammelpunkt(lp, sichere_orte, fern)
                if punkt is not None:
                    alle = sorted(self.mitglieder)
                    for n in alle:
                        self._vergessen(n)
                        self._warten(n, punkt, halten)
                    self.stapel["mitglieder"], self.stapel["ziel"] = set(), None
                    lt.update(mitglieder=set(alle), seit=self.runde, lord=ln, phase="sammeln", sammelpunkt=punkt)
                    ereignis.append("LORD-SAMMELN: %d Assassinen nach %s (ausser Schussweite), Angriff ab %d am Treffpunkt (%s: %s)" % (
                        len(alle), punkt, n_bedarf, bedarf_art, self.bedarf_grund))
            elif lt["phase"] == "sammeln":
                # Neue Anwerbungen gehoeren sofort dazu. Bereits Laufende nicht jede Runde neu befehlen: jeder neue
                # Befehl ist ein kurzer Halt. Die bestehende Warten-Gegenprobe schickt nur bei Stillstand erneut.
                neu = self.mitglieder - lt["mitglieder"]
                lt["mitglieder"] |= self.mitglieder
                punkt = lt["sammelpunkt"]
                for n in sorted(neu):
                    self._vergessen(n)
                    self._warten(n, punkt, halten)
                angekommen = {n for n in lt["mitglieder"] if schach((L[n]["x"], L[n]["y"]), punkt) <= self.LORD_SAMMEL_R}
                gruppe = None if self.angriff_aus else self._lord_gruppe(L, angekommen, n_bedarf, gruppe_leben)
                if gruppe:
                    alle = sorted(gruppe)
                    for n in lt["mitglieder"]:
                        self._vergessen(n)           # wer nicht in der Gruppe ist, raidet ab jetzt wieder
                    lt["mitglieder"] = set(alle)
                    lt["phase"], lt["seit"] = "angriff", self.runde
                    lord_befehl = {"angriff": {"einheiten": alle, "ziel": ln}}
                    self.bilanz["lordtrupps"] = self.bilanz.get("lordtrupps", 0) + 1
                    wege = sorted(schach((L[n]["x"], L[n]["y"]), lp) for n in alle)
                    self.angriffe.append({"runde": self.runde, "groesse": len(alle), "lord_vorher": le["leben"], "lord_nachher": le["leben"],
                                          "fern": self._anzahl(lp, fern, self.LORD_UMKREIS), "nah": self._anzahl(lp, nah, self.LORD_UMKREIS),
                                          "weg_min": wege[0], "weg_max": wege[-1], "am_lord_max": 0, "erreicht_runde": None,
                                          "anderes": {}, "truppe": set(alle), "verluste": 0,
                                          "bedarf": n_bedarf, "bedarf_art": bedarf_art, "bedarf_grund": self.bedarf_grund,
                                          "fingerabdruck": self.bedarf_fa})
                    ereignis.append("GEMEINSAM-AUF-LORD: %d Assassinen zusammen von %s (Bedarf %d %s, %d Nachzuegler raiden weiter; Leben %d, Fern %d / Nah %d um ihn, Weg %d-%d) | %s | Fingerabdruck %s" % (
                        len(alle), punkt, n_bedarf, bedarf_art, len(self.mitglieder) - len(alle), le["leben"],
                        self._anzahl(lp, fern, self.LORD_UMKREIS), self._anzahl(lp, nah, self.LORD_UMKREIS), wege[0], wege[-1],
                        self.bedarf_grund, self.bedarf_fa))
                elif neu or self.runde % 10 == 0:
                    ereignis.append("LORD-SAMMELN: %d/%d da, %d lebend (Angriff ab %d am Treffpunkt, %s)" % (
                        len(angekommen), len(lt["mitglieder"]), len(self.mitglieder), n_bedarf, bedarf_art))
            elif lt["phase"] == "angriff" and lt["mitglieder"]:
                # S2a (Daniel 21:46: "jeder Tick, wo sie rumstehen, ist eine Sekunde mehr, wo der Gegner rekrutieren und auf
                # unsere schiessen kann"): wer nicht den Lord angreift, bekommt den Befehl JEDE Runde neu.
                # 17.10. (1017h): weiter weg -> Laufbefehl auf den Lord (Kletterweg), erst daneben der Angriffsbefehl;
                # wer STEH_TICKS ohne Spielziel steht, faellt aus der Gruppe (sonst stand er an unserer Burg bis Partieende)
                for k in sorted(lt["mitglieder"]):
                    if L[k]["zielart"] == 4 and L[k].get("zieleinheit") == ln:
                        continue
                    f, seit = self._steht.get(k, (None, self.jetzt))
                    will_nirgends = schach((L[k].get("laufx", -99), L[k].get("laufy", -99)), pos(k)) <= 1
                    if f == pos(k) and will_nirgends and self.jetzt - seit >= self.STEH_TICKS                             and self.jetzt - lt.get("angriff_tick", 0) >= self.STEH_TICKS:
                        ereignis.append("LORD-ANGRIFF: %d steht %d Ticks ohne Spielziel bei %s (Zustand %d, Lord %d Felder) - raus, raidet" % (
                            k, self.jetzt - seit, pos(k), L[k]["zustand"], schach(pos(k), lp)))
                        lt["mitglieder"].discard(k)
                        self._vergessen(k)
                        continue
                    # 18.10. (Gegenpruefung): 2-3 Felder vor dem Lord ging weder Lauf- noch Angriffsbefehl hinaus. Jetzt: wer
                    # hoechstens 3 Felder vor ihm nicht mehr laeuft, bekommt den Angriffsbefehl; wer weiter weg steht und
                    # nicht laeuft oder ein anderes Laufziel hat, einen neuen Laufbefehl auf den Lord (Kletterweg)
                    d_l = schach(pos(k), lp)
                    lauf_k = (L[k].get("laufx", -99), L[k].get("laufy", -99))
                    steht_k = schach(lauf_k, pos(k)) <= 1 or (f == pos(k) and self.jetzt - seit >= self.BLOCK_TICKS)
                    if d_l <= self.ANLAUF_NAH or (d_l <= 3 and steht_k):
                        lord_ziel.append(k)
                    elif schach(lauf_k, lp) > 3 or steht_k:
                        lord_lauf.setdefault(lp, []).append(k)
                lt["seit"] = self.runde
            if lt["phase"] == "angriff" and lt["mitglieder"] and self.angriffe:
                self._lord_messen(L, G, ln, le, lp, fern, nah)
        # 5. Ziele verteilen (Gefahr am Gebaeude beachten); wer keins bekommt, wartet ausser Reichweite
        zahl = {}
        for z in self.ziel.values():
            zahl[z] = zahl.get(z, 0) + 1
        kand = []
        for gn, g in G.items():
            if g["besitzer"] in (0, self.sp) or g["typ"] not in WERT:
                continue
            p = (g["x"], g["y"])
            # 18.10.: Abstaende zu den Fernkaempfern einmal je Gebaeude, dann vier Zaehlungen (vorher vier Durchlaeufe)
            df = [max(abs(p[0] - q[0]), abs(p[1] - q[1])) for _, q, _ in fern]
            kand.append((gn, p, g["typ"], g.get("erreichbar", 1), sum(1 for d in df if d <= 10),
                         sum(1 for d in df if d <= self.ZIEL_FERN), sum(1 for d in df if d <= 30),
                         sum(1 for d in df if d <= self.SCHWACH_FERN), self._anzahl(p, nah, self.UEBERMACHT_R)))
        # 12.10. 01:47 Gute Tauschgeschaefte (Daniel: "warum hast du ueberhaupt einen Assassinen verloren - nur gute Trades
        # eingehen oder schlauer angreifen"; 1012i: 8 Tote an Holzfaellerhuetten mit 4 Schuetzen im Umkreis 30): ein Gebaeude
        # ist nur Ziel, wenn hoechstens SCHUETZEN_MAX feindliche Schuetzen es mit ihrer Reichweite (schussfeld.REICHWEITE)
        # erreichen - teure (WERT >= TEUER) bis SCHUETZEN_MAX_TEUER. Stellgroessen, keine Messung.
        sch_liste = schussfeld.schuetzen(L, self.sp)
        gedeckt = {k[0]: schussfeld.gefahr_am(k[1], sch_liste) for k in kand}
        guter_tausch = lambda k: True     # 01:54: ersetzt durch Risiko gegen Ertrag in der Zielwahl
        # Platz je Gebaeude nach Lage (Daniel 00:44): 1, teuer 2, +1 je dort angegriffenem eigenen Assassinen
        angegriffen = {}
        for n_a, g_a in self.ziel.items():
            if n_a in L and L[n_a].get("nahangreifer"):
                angegriffen[g_a] = angegriffen.get(g_a, 0) + 1
        platz = lambda k: (2 if WERT.get(k[2], 10) >= self.TEUER else self.JE_GEBAEUDE) + angegriffen.get(k[0], 0)
        # 17.10. Raiden geht vor: lohnende Raid-Plaetze = erreichbare Gebaeude ohne Beschuss am Ziel x Plaetze je Gebaeude.
        # Gilt in der NAECHSTEN Runde fuer die Frage, ob ein Ueberschuss fuer den Lord da ist.
        # 18.10.: gerechnet wird erst nach der Zielwahl (unten) und nur, wenn alle ein Ziel bekamen - sonst gilt ohnehin die
        # Zahl der vergebenen Ziele (spaet im Spiel kostete diese Zaehlung die Haelfte der Rechenzeit)
        # Zielwechsel: wer ein Gebaeude angreift, wechselt sofort, wenn ein freies, erreichbares Gebaeude mindestens WECHSEL-mal
        # mehr Wert je Weg bringt (z.B. ein neu gebautes in der Naehe)
        wert = lambda ort, k: WERT.get(k[2], 10) / ((schach(ort, k[1]) + 20.0) * (1 + k[5]))
        for n, gn in list(self.ziel.items()):
            if n not in L or gn not in G:
                continue
            ort = (L[n]["x"], L[n]["y"])
            jetzt = next((k for k in kand if k[0] == gn), None)
            # 17.10. (1017k nachgespielt: Zielwechsel sprang immer wieder auf Gebaeude 29, auf dessen Weg 86 an Feuerwerfern starb):
            # gewechselt wird nur auf ein Ziel, das an der Anlaufseite nicht staerker beobachtet ist als das jetzige
            b_jetzt = self._beschuss_angriff(gn, G, ort)
            besser = [k for k in kand if k[3] and k[0] != gn and zahl.get(k[0], 0) < platz(k) and k[5] <= self.ZIEL_FERN_MAX
                      and guter_tausch(k) and self._beschuss_angriff(k[0], G, ort) <= b_jetzt
                      and self._route_sperre.get((n, k[0]), -1) < self.jetzt]
            if jetzt and besser:
                b_k = max(besser, key=lambda k: wert(ort, k))
                if wert(ort, b_k) >= self.WECHSEL * wert(ort, jetzt):
                    # direkt auf das bessere Gebaeude setzen (00:44: nur Loeschen liess die normale Zielwahl ein anderes
                    # Gebaeude nehmen - Assassine 183 pendelte 89 -> 30, 110 -> 30)
                    self.ziel[n] = b_k[0]
                    self.ziel_typ[b_k[0]] = b_k[2]
                    zahl[gn] = max(0, zahl.get(gn, 1) - 1)
                    zahl[b_k[0]] = zahl.get(b_k[0], 0) + 1
                    self.befohlen[n] = self.runde
                    angriffe.append((n, b_k[0]))
                    ereignis.append("ZIELWECHSEL %d: %d -> besseres Gebaeude %d (Wert je Weg x%.1f)" % (
                        n, gn, b_k[0], wert(ort, b_k) / max(wert(ort, jetzt), 1e-9)))
        gruende = {"keins erreichbar": 0, "alle voll": 0, "alle gefaehrlich": 0}
        ohne = 0
        for n in sorted(self.mitglieder):
            if n in self.ziel or n in self.jagd or n in self.stapel["mitglieder"] or n in self.lordtrupp["mitglieder"] \
                    or (n in self.entdeckt and not self._aussendienst_frei(n, L)) \
                    or (n in self.warte and n in verletzt) or n in self.flucht:
                continue
            ort = (L[n]["x"], L[n]["y"])
            schwach = L[n]["leben"] < self.SCHWACH * self.VOLL
            erreichbar = [k for k in kand if k[3]]
            frei = [k for k in erreichbar if zahl.get(k[0], 0) < platz(k)]
            # 12.10. 01:54 RISIKO GEGEN ERTRAG statt fester Schwellen (Daniel 01:49 "warum wieder ein fixer Umkreis? frei entscheiden
            # und Risk/Reward abwaegen", 01:52 "ALLE Einheiten muessen wirklich aktiv raiden"): je Ziel kleinster erwarteter Schaden
            # auf dem Weg (Dijkstra ueber die GEMESSENE Gefahrenkarte schussfeld.SCHADEN_SATZ: Entdeckung + Deckung) plus Schaden
            # beim Angriff -> Todeswahrscheinlichkeit; Saldo = Wert x Ueberleben - Tod x Preis; das beste Saldo je Zeit.
            g_r = self._gitter(L, G)
            rk = g_r.risiko_von(ort, TEMPO) if g_r is not None else {}
            beste, beste_bew = None, None     # 17.10.: unbeobachtete Ziele zuerst, beobachtete nur bis ZIEL_RISIKO
            # 18.10.: Grenzen fuer den ganzen Auftrag (Weg + Angriff) - schwach = unter SCHWACH x volles Leben (Regel war
            # berechnet, aber nicht angewendet: Assassine 163 zog mit 120 Leben los, 17 mit 3.100)
            grenze = self.ZIEL_RISIKO_SCHWACH if schwach else self.ZIEL_RISIKO_WEG
            grenze_bew = min(self.ZIEL_RISIKO, grenze)
            for k in frei:
                if k[8] > zahl.get(k[0], 0) + 1:
                    continue                   # 4a: nicht dorthin, wo mehr Nahkampf-Wachen stehen als wir Angreifer haetten
                if self._route_sperre.get((n, k[0]), -1) >= self.jetzt:
                    continue                   # 18.10. (1018n, Assassine 17): nach ROUTE GEFAEHRLICH nicht gleich dasselbe Ziel
                if n in self.entdeckt and not self._weit_von_gesehen(n, ort, k[1], L):
                    continue                   # 19.10.: Aussendienst - Weg und Ziel ausser Reichweite der Schuetzen, die ihn sahen
                b_ziel = self._beschuss_angriff(k[0], G, ort)
                if L[n]["leben"] < self.EIN_TREFFER and (b_ziel > 0 or self._sicht.sicht_abstand(k[1]) < sicht.SICHT + self.RAND_SCHWACH):
                    continue                   # 19.10.: ein Bolzen toetet ihn - nur Ziele weit ab von jedem Spaeher
                # 17.10.: Zeit am Ziel = gemessene Arbeit / Zahl der Angreifer (statt VERWEILEN 300 ungemessen); Beschuss am
                # Ziel aus der Sicht (sichtbar nur bei waehlbarem Feind <= 20 Feldern, Schusslinie) statt Schadenssatz L73
                verweilen = self._arbeit(k[2], zahl.get(k[0], 0) + 1)
                if g_r is not None:
                    c = g_r.zelle_von(k[1])
                    r_weg, felder = rk.get(c, (1e9, 999))
                    risiko = (r_weg + b_ziel * verweilen) * self.KALIB
                else:
                    felder = schach(ort, k[1])
                    risiko = b_ziel * (verweilen + felder * TEMPO) * self.KALIB
                p_tod = min(1.0, risiko / max(1.0, float(L[n]["leben"])))
                saldo = WERT.get(k[2], 10) * (1 - p_tod) - p_tod * self.KOSTEN
                # 19.10. (Daniel: zwei Fronten, "hinten ist keine Verteidigung"): Ruhe-Bonus bis x2 fuer Ziele weit weg von jedem
                # waehlbaren Feind (Sicht-Abstand in Feldern / RUHE_FELDER) - dort wird er nicht entdeckt, verliert keine Zeit
                ruhe = 1.0 + min(self._sicht.sicht_abstand(k[1]) / 8.0, self.RUHE_FELDER) / self.RUHE_FELDER
                je_zeit = ruhe * saldo / (felder * TEMPO + verweilen)
                if saldo <= 0:
                    continue
                if b_ziel <= 0:
                    if p_tod <= grenze and (beste is None or je_zeit > beste[0]):
                        beste = (je_zeit, k, p_tod, saldo)
                elif p_tod <= grenze_bew and (beste_bew is None or je_zeit > beste_bew[0]):
                    beste_bew = (je_zeit, k, p_tod, saldo)
            beste = beste or beste_bew
            if beste:
                _, k_b, p_tod, saldo = beste
                gn, p, typ, _, f10, f20, f30, _, _ = k_b
                if n in self.entdeckt:
                    self.entdeckt[n]["ziel_ok"] = gn
                    ereignis.append("AUSSENDIENST %d: entdeckt, aber ausser Reichweite - raidet Gebaeude %d weit weg von den "
                                    "%d Schuetzen, die ihn sahen" % (n, gn, len(self.entdeckt[n]["schuetzen"])))
                self.ziel[n] = gn
                self.ziel_typ[gn] = typ
                zahl[gn] = zahl.get(gn, 0) + 1
                self.befohlen[n] = self.runde
                self.warte.pop(n, None); self.warte_seit.pop(n, None)
                angriffe.append((n, gn))
                ereignis.append("ZIELWAHL %d -> %d Typ %d in %d: Saldo %.0f, Todesrisiko %.0f %%, Fern<=30 %d, Leben %d, "
                                "Beschuss am Ziel %.2f/Takt, Arbeit %s %d Takte" % (
                    n, gn, typ, schach(ort, p), saldo, 100 * p_tod, f30, L[n]["leben"], self._beschuss_angriff(gn, G, ort),
                    "gemessen" if typ in ARBEIT else "geschaetzt", ARBEIT.get(typ, ARBEIT_SONST)))
                continue
            ohne += 1
            gruende["keins erreichbar" if not erreichbar else "alle voll" if not frei else "alle gefaehrlich"] += 1
            # 17.10.: warten nur dort, wo ihn kein waehlbarer Feind sieht und kein Trupp ihm nachlaeuft (sicht.sicher) - statt
            # 40 Felder von jedem Schuetzen; so warten sie nah am Feind und sind schnell wieder am naechsten Ziel
            if not self._sicht.sicher(ort):
                sicher_ort = self._sicherer_ort(ort, orte, fern, nah, n)
                if sicher_ort and self.warte.get(n) != sicher_ort:
                    self._warten(n, sicher_ort, halten)
            elif n not in self.warte and min((schach(ort, k[1]) for k in kand), default=0) > self.FRONT_AB:
                # 17.10. (Daniel, Bild: "es wird am Ausbildungslager gesammelt anstatt nah an der KI"): an unserer Burg ist es
                # immer sicher - wer ohne Ziel weit weg steht, wartet verdeckt nah am Gegner (Ring um den naechsten Lord)
                front = self._front_platz(ort)
                if front:
                    self._warten(n, front, halten)
        # 6. Stapel: viele Wartende -> alle gebuendelt auf EINEN erreichbaren Fernkaempfer am Boden, dann den naechsten
        stapel_befehl = None
        stp = self.stapel
        stp["mitglieder"] = {n for n in stp["mitglieder"] if n in self.mitglieder}
        ziel_lebt = stp["ziel"] in L and L[stp["ziel"]]["besitzer"] not in (0, self.sp)
        wartende = [n for n in self.mitglieder if n not in self.ziel and n not in self.jagd and n not in stp["mitglieder"]
                    and n not in self.lordtrupp["mitglieder"] and n not in self.flucht and L[n]["leben"] >= self.SCHWACH * self.VOLL]
        if stp["mitglieder"] or len(wartende) >= self.STAPEL_AB:
            if not stp["mitglieder"]:
                stp["mitglieder"] = set(wartende)
                for n in wartende:
                    self.warte.pop(n, None)
                    self.warte_seit.pop(n, None)
            if not ziel_lebt:
                # 9h: der naechste Schuetze stand inmitten von 17 weiteren - jetzt nur Schuetzen, um die hoechstens
                # (Stapelgroesse - 4) / 2 weitere Fernkaempfer im Umkreis 10 stehen; davon der einsamste, dann der naechste
                mx = sum(L[n]["x"] for n in stp["mitglieder"]) / len(stp["mitglieder"])
                my = sum(L[n]["y"] for n in stp["mitglieder"]) / len(stp["mitglieder"])
                erreichbar = []
                for f in fern:
                    if L[f[0]].get("erreichbar", -1) != 1:
                        continue
                    um = self._anzahl(f[1], fern, 10) - 1
                    if len(stp["mitglieder"]) >= 2 * um + 4:
                        erreichbar.append((um, schach((mx, my), f[1]), f))
                if erreichbar:
                    um, d, (f, _, typ) = min(erreichbar)
                    stp["ziel"] = f
                    stapel_befehl = {"angriff": {"einheiten": sorted(stp["mitglieder"]), "ziel": f}}
                    self.bilanz["stapel_ziele"] = self.bilanz.get("stapel_ziele", 0) + 1
                    ereignis.append("STAPEL: %d Assassinen gebuendelt auf Fernkaempfer %d (Typ %d, %d Felder vom Stapel, Fern<=10 dort %d)" % (
                        len(stp["mitglieder"]), f, typ, d, self._anzahl((L[f]["x"], L[f]["y"]), fern, 10)))
                else:
                    ereignis.append("STAPEL aufgeloest: kein erreichbarer Fernkaempfer, den %d schlagen koennen (zurueck ins Warten)" % len(stp["mitglieder"]))
                    stp["mitglieder"], stp["ziel"] = set(), None
        # 18.10. (Gegenpruefung): die Zaehlung oben nahm jedes Gebaeude mit irgendeiner unbeobachteten Seite - die Zielwahl
        # nimmt aber nur die Anlaufseite, ohne Wachen, mit Wegrisiko. Bleibt jemand ohne Ziel, sind alle annehmbaren Plaetze
        # besetzt: dann zaehlen nur die vergebenen (sonst sperrte die Zahl Jagd und Lord, waehrend Assassinen standen)
        if ohne > 0:
            self._raid_plaetze = len(self.ziel)
        elif self.lord_aus:
            # 19.10. (1018v nachgespielt: 14,5 von 30 s hier - jedes Gebaeude, jedes Randfeld): ohne Lord-Angriff zaehlt nur noch
            # "mehr Raid-Plaetze als vergebene Ziele?" (Beute-Schranke) - zaehlen, bis das feststeht
            self._raid_plaetze, grenze = 0, len(self.ziel) + 1
            for k in kand:
                if k[3] and self._beschuss_angriff(k[0], G) <= 0:
                    self._raid_plaetze += platz(k)
                    if self._raid_plaetze >= grenze:
                        break
        else:
            self._raid_plaetze = sum(platz(k) for k in kand if k[3] and self._beschuss_angriff(k[0], G) <= 0)
        if ohne != self.ohne_ziel_zuletzt:
            self.ohne_ziel_zuletzt = ohne
            ereignis.append("%d Assassinen ohne Ziel (%s)" % (ohne, ", ".join("%s %d" % kv for kv in gruende.items() if kv[1])))
        # 6. Sichere Wege (12.10.): laufende Routen weiterfuehren, neue Gebaeude-Angriffe ueber den toten Winkel schicken
        am_ziel = []
        lauf_weg = self._route_pflegen(L, G, am_ziel, ereignis)
        direkt, lauf_neu = self._wege(L, G, angriffe, ereignis)
        for o, ns in lauf_neu.items():
            lauf_weg.setdefault(o, []).extend(ns)
        befehle = [{"angriff": {"einheiten": [n], "gebaeude": gn}} for n, gn in direkt + am_ziel]
        befehle += [{"angriff": {"einheiten": ns, "lauf": [o[0], o[1]]}} for o, ns in lauf_weg.items()]
        befehle += [{"angriff": {"einheiten": [n], "ziel": f}} for n, f in jagen]
        befehle += [{"halten": {"nr": ns, "x": o[0], "y": o[1]}} for o, ns in halten.items()]
        # 19.10. (1018u: der Fluchtbefehl fuer 207 lief ~100 Ticks spaeter - hinter 5-15 Routinebefehlen in der Schlange des
        # Moduls): Flucht mit Vorrang, logik.lua stellt sie vorn an
        befehle += [{"angriff": {"einheiten": ns, "lauf": [o[0], o[1]], "vorrang": True}} for o, ns in flieh.items()]   # 4a: echter Laufbefehl
        if stapel_befehl:
            befehle.append(stapel_befehl)
        if lord_befehl:
            befehle.append(lord_befehl)
        befehle += [{"angriff": {"einheiten": ns, "lauf": [o[0], o[1]]}} for o, ns in lord_lauf.items()]   # 17.10.: Kletterweg
        if lord_ziel:
            befehle.append({"angriff": {"einheiten": sorted(lord_ziel), "ziel": self.lordtrupp.get("lord")}})
        # 17.10. (Daniel: "manche Assassinen stehen rum ohne Grund"): alle 50 Runden, wer STEH_TICKS ohne Spielziel steht und warum
        if self.runde % 50 == 0:
            st_alle = [n for n in self.mitglieder if self.jetzt - self._steht.get(n, (None, self.jetzt))[1] >= self.STEH_TICKS]
            if st_alle:
                grund = {}
                for n in st_alle:
                    g_ = ("Lord-Trupp" if n in self.lordtrupp["mitglieder"] else "Flucht" if n in self.flucht else
                          "Warten" if n in self.warte else "Ziel" if n in self.ziel or n in self.jagd else "ohne Ziel")
                    grund[g_] = grund.get(g_, 0) + 1
                ereignis.append("STEHEN: %d von %d Assassinen seit >= %d Ticks ohne Spielziel (%s)" % (
                    len(st_alle), len(self.mitglieder), self.STEH_TICKS, ", ".join("%s %d" % kv for kv in sorted(grund.items()))))
        if angriffe:
            ereignis.append("%d Assassinen auf %d Gebaeude verteilt (im Spiel gemessen: %d Gebaeude gleichzeitig angelaufen)" % (
                len(angriffe), len(set(g for _, g in angriffe)), self.gemessen))
        if jagen:
            ereignis.append("%d Assassinen greifen Fernkaempfer direkt daneben an" % len(jagen))
        if halten:
            ereignis.append("%d Assassinen warten/ziehen sich zurueck ausser Reichweite" % sum(len(v) for v in halten.values()))
        return ereignis, befehle

    def bericht(self):
        b = self.bilanz
        return ("zerstoert %d Gebaeude %s, eigene Verluste %d, im Spiel gleichzeitig angelaufen zuletzt %d, neu befohlen %d, "
                "Rueckzuege %d, ausgewichen %d, Fernkaempfer angegriffen %d, Warten neu geschickt %d, Stapel-Ziele %d, "
                "gesperrte Warteplaetze %d" % (
                    sum(b["gebaeude"].values()), b["gebaeude"], b.get("tote", len(b["verluste"])), self.gemessen, b["neu_befohlen"],
                    b["rueckzug"], b.get("ausgewichen", 0), b["zuschlagen"], b.get("warten_neu", 0),
                    b.get("stapel_ziele", 0), len(self.schlechte_orte)) + ", Lord-Trupps %d" % b.get("lordtrupps", 0)
                + ", Uebermacht ausgewichen %d" % b.get("uebermacht", 0)
                + ", Alle-auf-den-Lord [%s]" % "; ".join(
                    "Runde %d: %d Assassinen, Weg %d-%d, Fern %d / Nah %d am Lord, am Lord hoechstens %d (zuerst Runde %s), "
                    "abgelenkt durch Typ %s, ohne Ziel nah am Lord hoechstens %s, Lord %d -> %d, Verluste %d" % (
                        a["runde"], a["groesse"], a["weg_min"], a["weg_max"], a["fern"], a["nah"], a["am_lord_max"], a["erreicht_runde"],
                        a["anderes"] or "-", a.get("stehen_nah_max", 0), a["lord_vorher"], a["lord_nachher"], a["verluste"]) for a in self.angriffe))

