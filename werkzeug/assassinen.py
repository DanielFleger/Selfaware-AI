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

ASSASSINE = 73
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 55, 70, 71, 72, 73, 74, 75, 76}
FERNKAMPF = {22, 23, 70, 72, 74, 76}
WERT = {
    # Daniel 05.10. 19:05: Ausbildungslager, Steinbrueche, Haeuser usw. sind mehr wert als Apfelplantagen und, wenn
    # nicht allzu schwer bewacht, fast noch bessere Ziele. Kornspeicher-Bonus (04.10. 22:54). STARTWERTE, Rangfolge von Daniel.
    9: 100, 8: 100,                     # Kaserne, Soeldnerlager (Ausbildungslager)
    19: 100,                            # Kornspeicher
    20: 80, 21: 60, 5: 70, 6: 60,       # Steinbruch, Steinlager am Bruch, Eisenmine, Pechgrube
    11: 70, 12: 70, 13: 70, 14: 70, 15: 70,  # Waffenkammer und Waffenbauer
    24: 60, 25: 50, 35: 40,             # Ingenieurs-, Tunnelgraebergilde, Stall
    1: 60,                              # Huetten (Wohnraum = Arbeiter)
    4: 50, 3: 50,                       # Ochsenjoch, Holzfaeller
    22: 40, 18: 40, 17: 35, 34: 35, 33: 40, 30: 30, 36: 40, 37: 40, 38: 40,  # Wirtshaus, Brauerei, Baeckerei, Muehle, Milch, Weizen, Kirchen
    32: 30, 7: 30,                      # Apfelplantage, Jaegerhuette
    26: 20}
# Liga-Balance (liga_ai.json ranges): alle Bogen/Armbrust 40 Felder - eine Zahl fuer "in Schussweite" (Daniel 23:18: Schuetzen-
# Gefahr auf 40; live_6: Assassine starb bei Tick 8.527, naechster Bogenschuetze 26 Felder weg, gezaehlt wurde nur bis 16)
SCHUSSWEITE = 40
GROESSE, FERN, NAH, MAX_WEG = 1, SCHUSSWEITE, 8, 30   # 1: jeder Assassine einzeln, eigene Gruppe (Daniel 23:32; Modul reserviert Gruppen je Takt)

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
      1. Ohne Ziel wartet ein Assassine ausser Reichweite (eigener Ort ohne Fernkaempfer bis SICHER_FERN).
      2. Verletzt und Fernkaempfer bis RUECKZUG_FERN: Rueckzug - ausser ein Fernkaempfer steht direkt daneben
         (bis ZUSCHLAGEN Felder) und hoechstens 1 Nahkaempfer im Umkreis 5: dann ihn angreifen (Daniel 04.10. 23:4x).
      3. Zielwahl: Gebaeude mit mehr als ZIEL_FERN_MAX Fernkaempfern im Umkreis ZIEL_FERN auslassen; wer unter
         SCHWACH Leben hat, nimmt nur Ziele ganz ohne Fernkaempfer bis SCHWACH_FERN.
    Die Zahlen sind STARTWERTE aus dieser Messung, nicht geeicht - jede Zielwahl schreibt ihre Gefahrenzahlen mit
    (ZIELWAHL-Zeilen), jede Verletzung und jeder Tod ihr Umfeld (MESSUNG-Zeilen), damit die naechste Partie sie eicht.
    Gegenprobe je Runde: laeuft ein Assassine nicht zu seinem Gebaeude (Laufziel im Lagebild weiter als ZIEL_NAH),
    bekommt er den Befehl neu - der Plan im Kopf zaehlt nicht, nur das Laufziel im Spiel."""
    JE_GEBAEUDE = 1          # 12.10. Daniel 00:41/00:44: EIN Assassine je Gebaeude reisst ein, bei teuren (Wert >= TEUER) zwei;
    SCHUETZEN_MAX, SCHUETZEN_MAX_TEUER = 1, 2   # 12.10.: gute Tauschgeschaefte (Stellgroessen)
    WEGPUNKT_NAH = 3         # 12.10.: so nah am Wegpunkt gilt er als erreicht
    BEUTE_R = 15             # 12.10.: Fernkaempfer am Boden in diesem Umkreis werden gejagt (Stellgroesse)
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
    SICHER_FERN, SICHER_NAH = SCHUSSWEITE, 10
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
    NAH_GEFAHR = {24: 0.2, 25: 1.0, 26: 0.75, 27: 2.0, 28: 2.5, 71: 0.05, 73: 1.0, 75: 0.8, 55: 5.0}
    VERFOLGER_AB = 0.2       # schwaechere Feinde (Sklaven) gelten nicht als Verfolger
    HEIM_R, HEIM_ABSTAND = 15, 25   # eigene Truppen bis HEIM_R um Lager/Bergfried; zu schwach -> Fluchtpunkt mind. HEIM_ABSTAND weg
    # T2 Im Kreis fuehren (Daniel 22:49): Ring mit Radius KREIS_R um eine Mitte KREIS_MITTE Felder in der ersten Fluchtrichtung,
    # mindestens KREIS_RAND vom Kartenrand (raidzuerst_9: geradeaus bis an den Rand, dort eingeholt). STARTWERTE.
    KREIS_R, KREIS_MITTE, KREIS_RAND = 20, 35, 40
    ZUSCHLAGEN = 3
    ZIEL_FERN, ZIEL_FERN_MAX = 20, 2
    SCHWACH, SCHWACH_FERN = 0.6, 25
    VORAUS_FERN, VORAUS_ANZAHL = 10, 3   # Startwert aus Partie 9f: Tote standen 2-9 Felder neben ~7 Bogenschuetzen
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
        self.runde, self.gemessen, self.ohne_ziel_zuletzt = 0, 0, None
        self.bilanz = {"gebaeude": {}, "verluste": set(), "neu_befohlen": 0, "rueckzug": 0, "zuschlagen": 0}
        self.lagen = lagen_laden()           # gemessene Lagen (daten/lagen_belegt.json) fuer den Lord-Bedarf
        self.angriff_aus = False             # Trainingsstand: nur sammeln, nie angreifen (setzt erstes_spiel.py)
        self.bedarf_zuletzt = None
        self.bedarf_grund, self.bedarf_fa = "", None

    def aufnehmen(self, nummern):
        self.mitglieder |= set(n for n in nummern if n not in self.bilanz["verluste"])

    # --- Hilfen ---------------------------------------------------------------------------------------------------
    def _feinde(self, L):
        fern, nah = [], []
        self._arbeiter = []                  # 4a: feindliche Arbeiter, die Assassinen schlagen (ARBEITER_GEFAHR)
        for nr, e in L.items():
            if e["besitzer"] in (0, self.sp):
                continue
            if e["typ"] not in TRUPPE:
                if e["typ"] in self.ARBEITER_GEFAHR:
                    self._arbeiter.append((nr, (e["x"], e["y"]), e["typ"]))
                continue
            (fern if e["typ"] in FERNKAMPF else nah).append((nr, (e["x"], e["y"]), e["typ"]))
        return fern, nah

    def _bedrohung(self, ort, nah):
        """4a: Gewicht der Feinde um ihn - jeder Nahkaempfer im Umkreis UEBERMACHT_R zaehlt 1, jeder schlagende Arbeiter im
        Umkreis ARBEITER_R sein ARBEITER_GEFAHR-Gewicht."""
        return sum(self.NAH_GEFAHR.get(t, 1.0) for _, p, t in nah if schach(ort, p) <= self.UEBERMACHT_R) + sum(
            self.ARBEITER_GEFAHR[t] for _, p, t in getattr(self, "_arbeiter", []) if schach(ort, p) <= self.ARBEITER_R)

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
        """Zuerst KURZ weg vom Feind (begehbar laut Modul, der Punkt mit dem groessten Abstand zum naechsten Fernkaempfer);
        nur wenn das nicht geht: naechster begehbarer eigener Ort ohne Fernkaempfer bis SICHER_FERN und Nahkaempfer bis
        SICHER_NAH, sonst der Ort mit dem groessten Abstand zum naechsten Feind. Gesperrte Orte nie."""
        kurz = [p for p in self._kand.get(n, []) if p in self._begehbar and p not in self.schlechte_orte]
        if kurz:
            return max(kurz, key=lambda p: (self._naechster(p, fern)[0], -schach(ort, p)))
        orte = [o for o in orte if o not in self.schlechte_orte]
        gut = [o for o in orte if self._naechster(o, fern)[0] > self.SICHER_FERN and self._naechster(o, nah)[0] > self.SICHER_NAH]
        if gut:
            return min(gut, key=lambda o: schach(ort, o))
        return max(orte, key=lambda o: min(self._naechster(o, fern)[0], self._naechster(o, nah)[0])) if orte else None

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
                                                self._anzahl(q, fern, self.RUECKZUG_FERN),
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
        return ("ort (%d,%d) zustand %d | naechster Feind Typ %d in %d | naechster Fernkaempfer Typ %d in %d | "
                "Fern<=%d: %d | Nah<=%d: %d | naechstes Feindgebaeude Typ %d in %d | Ziel %s in %d" % (
                    ort[0], ort[1], L[n]["zustand"], feind[2], feind[0], nf[2], nf[0],
                    FERN, self._anzahl(ort, fern, FERN), NAH, self._anzahl(ort, nah, NAH), gb[1], gb[0], z, zd))

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

    def _gitter(self, L):
        """Gefahren-Gitter dieser Runde (schussfeld.py); das Gelaende-Gitter wird nur einmal gerechnet."""
        if not self.mit_wegen or not self.gelaende:
            return None
        g = schussfeld.Gitter(self.gelaende, schussfeld.schuetzen(L, self.sp), frei=self._frei)
        self._frei = g.frei
        return g

    def _wege(self, L, G, angriffe, ereignis):
        """12.10.: neue Gebaeude-Angriffe ueber den sicheren Weg schicken. Gibt (direkte Angriffe, Laufbefehle {Ort: [n]})."""
        lauf, direkt = {}, []
        if not angriffe:
            return direkt, lauf
        g = self._gitter(L)
        if g is None:
            return list(angriffe), lauf
        for n, gn in angriffe:
            if n not in L or gn not in G:
                direkt.append((n, gn))
                continue
            start, ziel = (L[n]["x"], L[n]["y"]), (G[gn]["x"], G[gn]["y"])
            wp, bw, bg, _ = schussfeld.sicherer_weg(self.gelaende, L, self.sp, start, ziel, gitter=g)
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
            while r["punkte"] and schach(ort, r["punkte"][0]) <= self.WEGPUNKT_NAH:
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

    # --- eine Runde -----------------------------------------------------------------------------------------------
    def schritt(self, L, G, sichere_orte=None, tick=None):
        ereignis, angriffe, jagen, halten, flieh = [], [], [], {}, {}
        self.runde += 1
        # 4a rechnet in TICKS, nicht in Runden (live_4, 23:05: ohne feste Wartezeiten dauert eine Runde 2-4 statt 13-20
        # Ticks - "2 Runden ohne Feldwechsel" war normales Gehen, er wechselte staendig die Richtung und wurde eingeholt).
        # Ohne Spielzeit (Pruefung ohne Spiel): RUNDE_TICKS je Runde.
        self.jetzt = tick if tick is not None else self.runde * self.RUNDE_TICKS
        self._heim = list(sichere_orte or [])          # 4a: Fluchtrichtung (Lager, Bergfried)
        # begehbare Warteplaetze: wo gerade eine eigene Nicht-Kampfeinheit steht, ist begehbarer Boden
        orte = list(sichere_orte or []) + sorted({(e["x"], e["y"]) for e in L.values()
                                                  if e["besitzer"] == self.sp and e["typ"] not in TRUPPE and e["typ"] != ASSASSINE})
        if self.pruefe_begehbar and orte:
            gut = self.pruefe_begehbar(orte)
            orte = [o for o in orte if o in gut] or orte
        fern, nah = self._feinde(L)
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
        # 1. Verluste und Verletzungen messen
        for n in list(self.mitglieder):
            if n not in L or L[n]["besitzer"] != self.sp:
                self.bilanz["verluste"].add(n); self.mitglieder.discard(n); self._vergessen(n); self.flucht.pop(n, None)
                ereignis.append("MESSUNG tot %d: zuletzt %s" % (n, self.umfeld.pop(n, "unbekannt")))
                self.leben.pop(n, None)
        verletzt = set()
        for n in self.mitglieder:
            u = self.umgebung(n, L, G, fern, nah)
            alt = self.leben.get(n)
            if alt is not None and L[n]["leben"] < alt:
                verletzt.add(n)
                ereignis.append("MESSUNG verletzt %d: leben %d -> %d | %s" % (n, alt, L[n]["leben"], u))
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
        for n in sorted(self.mitglieder):
            if n in self.jagd or n in self.lordtrupp["mitglieder"] or n in self.stapel["mitglieder"] or n in self.flucht or n not in L:
                continue
            ort = (L[n]["x"], L[n]["y"])
            nah_b = [b_ for b_ in beute if schach(ort, b_[1]) <= self.BEUTE_R]
            if nah_b:
                ziel_b = min(nah_b, key=lambda b_: schach(ort, b_[1]))
                self.ziel.pop(n, None); self.warte.pop(n, None)
                self.jagd[n] = ziel_b[0]
                jagen.append((n, ziel_b[0]))
                ereignis.append("BEUTE %d jagt Fernkaempfer %d am Boden (%d Felder)" % (n, ziel_b[0], schach(ort, ziel_b[1])))
        # 4. Verletzt im Schussfeld: Rueckzug oder zuschlagen
        for n in verletzt:
            ort = (L[n]["x"], L[n]["y"])
            nf = self._naechster(ort, fern)
            if nf[0] > self.RUECKZUG_FERN:
                continue
            if n in self.lordtrupp["mitglieder"]:
                continue                   # der Lord-Trupp bleibt dran (gebuendelt; Daniel: nur die letzten Lebenspunkte zaehlen)
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
            if n in self.lordtrupp["mitglieder"]:
                continue                   # der Lord-Angriff bleibt dran (Daniel 21:47)
            ort = (L[n]["x"], L[n]["y"])
            feinde = self._bedrohung(ort, nah)
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
            if n in verletzt or n in self.jagd or n in self.warte or n in self.stapel["mitglieder"] or n in self.lordtrupp["mitglieder"]:
                continue
            ort = (L[n]["x"], L[n]["y"])
            if self._anzahl(ort, fern, self.VORAUS_FERN) >= self.VORAUS_ANZAHL:
                sicher = self._sicherer_ort(ort, orte, fern, nah, n)
                if sicher:
                    self._vergessen(n)
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
        lt = self.lordtrupp
        lt["mitglieder"] = {n for n in lt["mitglieder"] if n in self.mitglieder}
        lords = [(n, e) for n, e in L.items() if e["typ"] == 55 and e["besitzer"] not in (0, self.sp)]
        if not lords:
            lt.update(mitglieder=set(), phase=None, sammelpunkt=None)
        else:
            ln, le = lords[0]
            lp = (le["x"], le["y"])
            n_bedarf, bedarf_art, gruppe_leben = self._lord_bedarf(L, G, ereignis)
            if lt["mitglieder"] and len(lt["mitglieder"]) < self.LORD_REST:
                ereignis.append("GEMEINSAMER LORD-ANGRIFF vorbei: noch %d leben, Lord-Leben %d - wieder raiden bis %d" % (
                    len(lt["mitglieder"]), le["leben"], n_bedarf))
                for n in list(lt["mitglieder"]):
                    self._vergessen(n)
                lt.update(mitglieder=set(), phase=None, sammelpunkt=None)
            if lt["phase"] is None and len(self.mitglieder) >= min(n_bedarf, self.LORD_SAMMELN_AB):
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
                # unsere schiessen kann"): wer nicht den Lord angreift, bekommt den Befehl JEDE Runde neu (vorher erst nach NEU_NACH)
                abseits = [n for n in lt["mitglieder"] if not (L[n]["zielart"] == 4 and L[n].get("zieleinheit") == ln)]
                if abseits:
                    lord_befehl = {"angriff": {"einheiten": sorted(abseits), "ziel": ln}}
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
            kand.append((gn, p, g["typ"], g.get("erreichbar", 1), self._anzahl(p, fern, 10),
                         self._anzahl(p, fern, self.ZIEL_FERN), self._anzahl(p, fern, 30), self._anzahl(p, fern, self.SCHWACH_FERN),
                         self._anzahl(p, nah, self.UEBERMACHT_R)))
        # 12.10. 01:47 Gute Tauschgeschaefte (Daniel: "warum hast du ueberhaupt einen Assassinen verloren - nur gute Trades
        # eingehen oder schlauer angreifen"; 1012i: 8 Tote an Holzfaellerhuetten mit 4 Schuetzen im Umkreis 30): ein Gebaeude
        # ist nur Ziel, wenn hoechstens SCHUETZEN_MAX feindliche Schuetzen es mit ihrer Reichweite (schussfeld.REICHWEITE)
        # erreichen - teure (WERT >= TEUER) bis SCHUETZEN_MAX_TEUER. Stellgroessen, keine Messung.
        sch_liste = schussfeld.schuetzen(L, self.sp)
        gedeckt = {k[0]: schussfeld.gefahr_am(k[1], sch_liste) for k in kand}
        guter_tausch = lambda k: gedeckt.get(k[0], 0) <= (self.SCHUETZEN_MAX_TEUER if WERT.get(k[2], 10) >= self.TEUER
                                                            else self.SCHUETZEN_MAX)
        # Platz je Gebaeude nach Lage (Daniel 00:44): 1, teuer 2, +1 je dort angegriffenem eigenen Assassinen
        angegriffen = {}
        for n_a, g_a in self.ziel.items():
            if n_a in L and L[n_a].get("nahangreifer"):
                angegriffen[g_a] = angegriffen.get(g_a, 0) + 1
        platz = lambda k: (2 if WERT.get(k[2], 10) >= self.TEUER else self.JE_GEBAEUDE) + angegriffen.get(k[0], 0)
        # Zielwechsel: wer ein Gebaeude angreift, wechselt sofort, wenn ein freies, erreichbares Gebaeude mindestens WECHSEL-mal
        # mehr Wert je Weg bringt (z.B. ein neu gebautes in der Naehe)
        wert = lambda ort, k: WERT.get(k[2], 10) / ((schach(ort, k[1]) + 20.0) * (1 + k[5]))
        for n, gn in list(self.ziel.items()):
            if n not in L or gn not in G:
                continue
            ort = (L[n]["x"], L[n]["y"])
            jetzt = next((k for k in kand if k[0] == gn), None)
            besser = [k for k in kand if k[3] and k[0] != gn and zahl.get(k[0], 0) < platz(k) and k[5] <= self.ZIEL_FERN_MAX
                      and guter_tausch(k)]
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
                    or (n in self.warte and n in verletzt) or n in self.flucht:
                continue
            ort = (L[n]["x"], L[n]["y"])
            schwach = L[n]["leben"] < self.SCHWACH * self.VOLL
            erreichbar = [k for k in kand if k[3]]
            frei = [k for k in erreichbar if zahl.get(k[0], 0) < platz(k)]
            sicher = [k for k in frei if (k[7] == 0 if schwach else k[5] <= self.ZIEL_FERN_MAX)
                      and k[8] <= zahl.get(k[0], 0) + 1 and guter_tausch(k)]   # 4a: nicht dorthin, wo mehr Nahkampf-Wachen stehen als wir Angreifer haetten
            if sicher:
                # Wert je Weg, abgeschwaecht durch Fernkaempfer am Ziel (Daniel 19:05: wertvoll UND nicht allzu schwer bewacht)
                gn, p, typ, _, f10, f20, f30, _, _ = max(sicher, key=lambda k: WERT.get(k[2], 10) / ((schach(ort, k[1]) + 20.0) * (1 + k[5])))
                self.ziel[n] = gn
                self.ziel_typ[gn] = typ
                zahl[gn] = zahl.get(gn, 0) + 1
                self.befohlen[n] = self.runde
                self.warte.pop(n, None); self.warte_seit.pop(n, None)
                angriffe.append((n, gn))
                ereignis.append("ZIELWAHL %d -> %d Typ %d in %d: Fern<=10 %d, <=20 %d, <=30 %d, Leben %d" % (
                    n, gn, typ, schach(ort, p), f10, f20, f30, L[n]["leben"]))
                continue
            ohne += 1
            gruende["keins erreichbar" if not erreichbar else "alle voll" if not frei else "alle gefaehrlich"] += 1
            nf, nn = self._naechster(ort, fern)[0], self._naechster(ort, nah)[0]
            if nf <= self.SICHER_FERN or nn <= self.SICHER_NAH:
                sicher_ort = self._sicherer_ort(ort, orte, fern, nah, n)
                if sicher_ort and self.warte.get(n) != sicher_ort:
                    self._warten(n, sicher_ort, halten)
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
        befehle += [{"angriff": {"einheiten": ns, "lauf": [o[0], o[1]]}} for o, ns in flieh.items()]   # 4a: echter Laufbefehl
        if stapel_befehl:
            befehle.append(stapel_befehl)
        if lord_befehl:
            befehle.append(lord_befehl)
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
                    sum(b["gebaeude"].values()), b["gebaeude"], len(b["verluste"]), self.gemessen, b["neu_befohlen"],
                    b["rueckzug"], b.get("ausgewichen", 0), b["zuschlagen"], b.get("warten_neu", 0),
                    b.get("stapel_ziele", 0), len(self.schlechte_orte)) + ", Lord-Trupps %d" % b.get("lordtrupps", 0)
                + ", Uebermacht ausgewichen %d" % b.get("uebermacht", 0)
                + ", Alle-auf-den-Lord [%s]" % "; ".join(
                    "Runde %d: %d Assassinen, Weg %d-%d, Fern %d / Nah %d am Lord, am Lord hoechstens %d (zuerst Runde %s), "
                    "abgelenkt durch Typ %s, ohne Ziel nah am Lord hoechstens %s, Lord %d -> %d, Verluste %d" % (
                        a["runde"], a["groesse"], a["weg_min"], a["weg_max"], a["fern"], a["nah"], a["am_lord_max"], a["erreicht_runde"],
                        a["anderes"] or "-", a.get("stehen_nah_max", 0), a["lord_vorher"], a["lord_nachher"], a["verluste"]) for a in self.angriffe))

