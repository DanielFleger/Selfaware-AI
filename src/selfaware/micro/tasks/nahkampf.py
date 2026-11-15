# -*- coding: utf-8 -*-
"""Nahkaempfer (B-181). Daniel 10.11.2026: "ein Modul fuer Nahkaempfer und die hat eben das Submodul Raid ganz einfach fuer jede Einheit.
Alles was wir wissen wird da reingefeeded und default agieren sie einfach wie es am Anfang Assassinen gemacht haben - nach Wirkung.
schlaues pathing. maximaler effekt".

NahkampfRaid fuehrt jede Einheit einzeln: Ziel nach Wirkung (baukasten/wirkung.py: Wert mal Erfolg je Takt, ein Ziel je Einheit), Weg mit
der wenigsten Gefahr (services/schussfeld.sicherer_weg, wie die Assassinen), am Ende der Angriff. Faellt das Ziel weg oder wird es zu
gefaehrlich, kommt das naechste. Dazu gehoeren die fuer den Raid bestellten Einheiten und seit 13.11.2026 alle, denen die Rollen-Rechnung
(micro/rollen.py, zuteilen) die Rolle Raid gibt - Daniel 23:07: "Ich persoenlich sehe in dem fall keinen grund nicht zu raiden".

B-182 (Plan_Wegfuehrung.md; Daniel 11.11. 00:48 auf die Frage, ob als Naechstes der Nahkampf-Raid umzieht: "Ja, Nahkampf-Raid"):
Mit der gemeinsamen Wegfuehrung (self.weg, setzt der Raid-Einsatz) waehlt das Modul nur noch das Ziel; Weg und Befehle kommen jede
Runde neu von der Wegfuehrung. Meldet sie "gefahr" oder "kein_weg", nimmt diese Einheit fuer raids.SPERRE_RUNDEN ein anderes Ziel;
ein Erfolg zaehlt nur, wenn sie das Ziel am Ziel angriff ("greift_an"). Am Ziel greift sie auch unter Beschuss an: Daniel 11.11.
19:40 auf die Frage "Darf der Nahkampf-Raid Ziele unter Beschuss angreifen?": "Gerne freigeben" (baukasten/raid.TROTZ_GEFAHR).
"""

import collections

import selfaware.services.schussfeld as schussfeld
from selfaware.baukasten import wirkung as WK
from selfaware.baukasten import zielvergabe as ZV
from selfaware.execution import kampfschutz
from selfaware.micro.tasks import raids as RA
from selfaware.micro.unit_log import Action, building, unit

# Nahkampf-Arten ohne eigenes Raid-Modul: Sklaven fuehrt der Brandtrupp, Assassinen ihr eigenes Modul, der Lord verteidigt nur
KANN = frozenset({24, 25, 26, 27, 28, 75})
AM_ZIEL = 4  # Felder: so nah gilt die Einheit als am Ziel (wie der Brandtrupp)
AM_WEGPUNKT = 3  # Felder: dann kommt der naechste Wegpunkt
# S151 (Daniel 14.11.2026 23:48 "Ja, einbauen"): was ein Zielwechsel kostet - gemessen 23:47 in den Takt-Mitschriften der Partien 20-22:
# ein Feldwechsel einer laufenden Einheit dauert ohne Befehl dazwischen im Mittel 9,5 Takte (n=8879), mit einem neuen Laufbefehl 15,9 (n=224)
WECHSEL_TAKTE = 15.9 - 9.5
# S161: so nah muss ein Arbeiter stehen, damit eine Einheit ihn mitnimmt - der Wert der Assassinen (assassinen.Einzeln.ARBEITER_MIT)
from selfaware.micro.tasks.assassinen import Einzeln as _AS_Einzeln  # noqa: E402

ARBEITER_MIT = _AS_Einzeln.ARBEITER_MIT


def _name(schluessel):
    return "Gebaeude" if schluessel[0] == "g" else "Arbeiter"


class NahkampfRaid:
    def __init__(self, sp, gelaende=None, wissen=None):
        self.sp, self.gelaende = sp, gelaende
        self.wissen = wissen if wissen is not None else WK.Wissen()
        self.erwartet = collections.Counter()  # bestellte, noch nicht angekommene Einheiten je Art
        self.bekannt = None  # eigene Einheit -> Art, wie zuletzt gesehen; None bis zur ersten Runde
        self.mitglieder = set()
        self.ziel = {}  # Einheit -> Schluessel des Ziels
        self.wegpunkte = {}  # Einheit -> offene Wegpunkte (nur ohne Wegfuehrung)
        self.befohlen = {}  # Einheit -> (Befehl, Runde) (nur ohne Wegfuehrung)
        self.weg = (
            None  # B-182: gemeinsame Wegfuehrung (micro/wegfuehrung.py), setzt der Raid-Einsatz
        )
        self.gesperrt = {}  # (Einheit, Ziel) -> Runde: nach "gefahr"/"kein_weg" waehlt diese Einheit das Ziel so lange nicht
        self.dazu = False  # Daniel 15.11.2026 22:29: letzte Zielwahl stellte die Einheit zu einem schon besetzten Ziel
        self.greift = {}  # Einheit -> Ziel, das sie zuletzt am Ziel angriff (Status "greift_an" der Wegfuehrung)
        self.runde = 0
        self.zerstoert = self.getoetet = 0
        self.absicht = {}  # B-182 Logbuch je Einheit: Einheit -> (Aktion, Ziel, Grund, Werte) dieser Runde
        self.lord = None  # S162: gegnerischer Lord, auf den alle gehen - setzt der Lenker, sobald die Assassinen ihn angreifen
        self.wehrt = {}  # S150: Einheit -> (gegnerischer Soldat, schlaegt zurueck?) - die Entscheidung steht einmal in der Mitschrift

    def bestellt(self, typ, anzahl):
        """Der Lenker meldet, was er fuer den Raid bestellt hat: Diese Arten nimmt das Modul auf, sobald sie da sind."""
        if typ in KANN:
            self.erwartet[typ] += anzahl

    def zuteilen(self, dazu, weg):
        """Rollen-Rechnung (micro/rollen.py): dazu raiden ab jetzt, weg gehen an die Verteidigung (Ziel und Wegfuehrung frei)."""
        dazu, weg = {n for n in dazu}, {n for n in weg}
        for n in sorted(weg & self.mitglieder):
            self._freigeben(n)
        self.mitglieder = (self.mitglieder - weg) | dazu

    def _aufnehmen(self, L):
        eigene = {
            n: e for n, e in L.items() if e.get("besitzer") == self.sp and e.get("leben", 1) > 0
        }
        if self.bekannt is None:
            self.bekannt = {n: e["typ"] for n, e in eigene.items()}
            return
        # Reihe 2b (10.11.): Angeworben wird aus einem Bauern, die Nummer bleibt, nur die Art wechselt (Bauer 565 wurde Typ 75)
        for n in sorted(eigene):
            typ = eigene[n]["typ"]
            if typ in KANN and self.bekannt.get(n) != typ and self.erwartet[typ] > 0:
                self.erwartet[typ] -= 1
                self.mitglieder.add(n)
        self.bekannt = {n: e["typ"] for n, e in eigene.items()}
        self.mitglieder &= {n for n, e in eigene.items() if e["typ"] in KANN}

    def _senden(self, n, b, befehl):
        alt = self.befohlen.get(n)
        if alt is None or alt[0] != b or self.runde - alt[1] >= RA.NEU_ALLE:
            befehl(b, 1.0, bis="ANGRIFF")
            self.befohlen[n] = (b, self.runde)

    def _werte(self, n, e, ziele, belegt, laenge=None):
        """[(Wert je Takt, Felder, Ziel)] der erlaubten Ziele. B-182 S150 (Daniel 14.11.2026 23:29 "Niemals nach luftlinie warum
        auch?"): mit Wegfuehrung zaehlt die Laenge ihres sicheren Wegs (laenge = Wegfuehrung.weglaenge), ein Ziel ohne Weg faellt
        heraus; ohne Wegfuehrung die Schachdistanz."""
        ort = (e["x"], e["y"])
        aus = []
        for z in ziele.values():
            if z.schluessel in belegt or self.gesperrt.get((n, z.schluessel), -1) > self.runde:
                continue
            # S161 (Daniel 15.11.2026 01:32: alle wie die Assassinen): einen Arbeiter nur mitnehmen, wenn er direkt am Weg steht - wie
            # die Assassinen (Daniel 19.10.: "nie gesagt aktiv jagen - mitnehmen, wenn er will"), nicht quer ueber die Karte jagen
            if z.schluessel[0] == "e" and WK.schach(ort, z.ort) > ARBEITER_MIT:
                continue
            felder = laenge(z.ort) if laenge is not None else WK.schach(ort, z.ort)
            if felder is None:
                continue
            wert, dauer = self.wissen.wert_je_takt(e["typ"], ort, z, felder=felder)
            aus.append((wert, felder, z, dauer))
        return aus

    @staticmethod
    def _nach_wechsel(wert, dauer):
        """Wert je Takt eines neuen Ziels, wenn die Einheit dafuer wechselt: Wert x Erfolg / (Takte + WECHSEL_TAKTE)."""
        return 0.0 if not wert or not dauer else wert * dauer / (dauer + WECHSEL_TAKTE)

    def _laenge(self, e, L, G, raster):
        """Weglaengen von dieser Einheit aus (Wegfuehrung.weglaenge); raster: {Klasse: Gitter} dieser Runde, einmal gebaut."""
        if self.weg is None or G is None:
            return None
        klasse = e["typ"] == 73
        if klasse not in raster:
            raster[klasse] = self.weg.raster(L, G, e["typ"])
        return self.weg.weglaenge(raster[klasse], (e["x"], e["y"]))

    def _waehlen(self, n, e, ziele, belegt, L, G=None, laenge=None):
        """Bestes Ziel nach Wert je Takt, die freien zuerst. Daniel 15.11.2026 22:29 (baukasten/zielvergabe.py): bringt kein freies
        Ziel Wert, stellt sich die Einheit zu einem, das schon ein anderer Nahkaempfer angreift, statt zu warten."""
        ort = (e["x"], e["y"])
        werte = self._werte(
            n, e, ziele, (), laenge if laenge is not None else self._laenge(e, L, G, {})
        )

        def wahl(liste):
            best = max(liste, key=lambda x: x[0])
            return best if best[2] is not None and best[0] > 0 else None

        best, self.dazu = ZV.waehle(werte, lambda w: w[2].schluessel not in belegt, wahl)
        if best is None:
            return None
        z = best[2]
        weg = []
        if self.gelaende and self.weg is None:  # mit Wegfuehrung plant sie den Weg, jede Runde neu
            weg = list(schussfeld.sicherer_weg(self.gelaende, L, self.sp, ort, z.ort)[0])
        self.ziel[n], self.wegpunkte[n] = (
            z.schluessel,
            weg[:-1],
        )  # der letzte Wegpunkt ist das Ziel selbst, dort kommt der Angriff
        return z

    def _am_ziel_gewesen(self, n, alt):
        """Griff diese Einheit ihr Ziel zuletzt am Ziel an? Mit Wegfuehrung deren Status, sonst der letzte eigene Befehl."""
        if self.weg is not None:
            # B-182 (Partie 12.11. 00:05, Fehlerwache F4): nur ein Angriff der letzten raids.ABSCHUSS_RUNDEN Runden zaehlt
            g = self.greift.get(n)
            return g is not None and g[0] == alt and self.runde - g[1] <= RA.ABSCHUSS_RUNDEN
        return n in self.befohlen and bool(
            self.befohlen[n][0].get("angriff", {}).keys() & {"gebaeude", "ziel"}
        )

    def _freigeben(self, n):
        self.ziel.pop(n, None)
        self.wegpunkte.pop(n, None)
        self.greift.pop(n, None)
        if self.weg is not None:
            self.weg.loslassen(n)

    @staticmethod
    def _bekaempft(e, ziele):
        """Schluessel des gegnerischen Arbeiters, gegen den die Einheit gerade kaempft (Kernzustand 106, Gegner in nahziel, sonst
        zieleinheit), wenn er unter den Zielen des Raids ist - sonst None. Ein Kampf gegen Soldaten zaehlt nicht."""
        if e.get("zustand") != kampfschutz.KAMPF_EINHEIT:
            return None
        for g in (e.get("nahziel"), e.get("zieleinheit")):
            if g and ("e", g) in ziele:
                return ("e", g)
        return None

    @staticmethod
    def _soldat_gegner(e, L, sp):
        """Nummer des gegnerischen Nahkaempfers (raids.NAH), gegen den die Einheit gerade kaempft (Kernzustand 106, nahziel), sonst None."""
        if e.get("zustand") != kampfschutz.KAMPF_EINHEIT:
            return None
        g = L.get(e.get("nahziel") or 0)
        if (
            g is None
            or g.get("besitzer") in (0, sp)
            or g.get("leben", 1) <= 0
            or g.get("typ") not in RA.NAH
        ):
            return None
        return e["nahziel"]

    def _zurueckschlagen(self, e, g, z, felder):
        """S150 (Daniel 23:34 "Ja, mit einbauen"): (Wert je Takt beim Weitergehen, beim Zurueckschlagen, Angaben) gegen den Soldaten g
        auf dem Weg zu z. Gemessen 10.-14.11. (94 Lageprotokolle): ein gegnerischer Soldat folgte einem weitergehenden eigenen
        Kaempfer 1 von 18 Mal - Weitergehen kostet darum nichts ausser dem Weg. Zurueckschlagen kostet die Zeit, bis er tot ist, und
        Leben (Duelltabelle), und bringt nur etwas, wenn er das Ziel deckt (innerhalb raids.GEFAHR_NAH): dann ohne ihn am Ziel."""
        if felder is None:
            return 0.0, 0.0, {}
        typ, gtyp = e["typ"], g["typ"]
        tempo = WK.SW.takte_je_feld(typ, "trupp")
        dps_wir, h_wir = self.wissen.dps(typ, gtyp)
        dps_er, h_er = self.wissen.dps(gtyp, typ)
        t_tot = g.get("leben", 0) / max(dps_wir, 1e-9)
        nah = list(z.nah)
        deckt = WK.schach((g["x"], g["y"]), z.ort) <= RA.GEFAHR_NAH and gtyp in nah
        if deckt:
            nah.remove(gtyp)
        takte_w, erfolg_w = self.wissen.rechnen_mit(typ, z, leben=e.get("leben"))
        takte_k, erfolg_k = self.wissen.rechnen_mit(
            typ, z, leben=e.get("leben", 0) - dps_er * t_tot, nah=nah
        )
        if takte_w is None:
            return 0.0, 0.0, {}
        weg_takte = felder * tempo
        w = z.wert * erfolg_w / max(weg_takte + takte_w, 1.0)
        k = z.wert * erfolg_k / max(t_tot + weg_takte + takte_k, 1.0)
        return w, k, {"t_tot": round(t_tot), "deckt": deckt, "dps": "%s/%s" % (h_wir, h_er)}

    def schritt(self, L, G, befehl):
        self.runde += 1
        self.absicht = {}
        self._aufnehmen(L)
        # B-182: Ziele toter Teilnehmer gelten nicht mehr als belegt (sie sperrten das Ziel fuer die anderen und fuer den Kauf)
        for n in [n for n in self.ziel if n not in self.mitglieder]:
            self._freigeben(n)
        if not self.mitglieder:
            return []
        self.wissen.lernen(L, self.sp)
        ziele = {z.schluessel: z for z in WK.ziele(L, G, self.sp)}
        aus = []
        raster = {}  # S150: ein Gitter je Runde (und je Klasse) fuer alle Einheiten des Raids
        for n in sorted(self.mitglieder):
            e = L[n]
            ort = (e["x"], e["y"])
            alt = self.ziel.get(n)
            grund = "keeps_target"
            if self.lord is not None and self.lord in L and self.weg is not None:
                # S162 (Daniel 15.11.2026 01:50 "ich will den gegnerischen lord so schnell und erbarmungslos wie moeglich killen"):
                # greifen die Assassinen den Lord an, gehen alle Raid-Nahkaempfer mit - ohne Ruecksicht (trotz_gefahr), ueber die
                # Wegfuehrung (ihr Weg ist der mit der wenigsten Gefahr) und den Kern
                if alt != ("e", self.lord):
                    self._freigeben(n)
                    self.ziel[n] = ("e", self.lord)
                    aus.append(
                        "NAHKAMPF-RAID: %d (Typ %d) geht mit auf den Lord %d"
                        % (n, e["typ"], self.lord)
                    )
                self.weg.fuehre(n, "einheit", self.lord, "nahkampfraid")
                self.absicht[n] = (Action.ATTACK_UNIT, unit(self.lord), "lord_push", {})
                continue
            # B-182 (Partie 16 vom 14.11.2026, S142; Daniel 22:31 "Ja, Raid ändern"): Speertraeger 332 jagte seit Takt 1894 Arbeiter 307,
            # kaempfte unterwegs gegen den Holzfaeller 365 - und der naechste Laufbefehl zu 307 holte ihn 10 Takte aus dem Kampf.
            # Kaempft die Einheit schon gegen einen gegnerischen Arbeiter, wird er ihr Ziel; die Wegfuehrung gibt am Ziel den Angriff,
            # den der Kampfschutz zurueckhaelt (sie kaempft genau gegen ihn) - kein Laufbefehl
            # S154 (Daniel 15.11.2026 00:04/00:07: kein Soldat, der ohne Grund gegen einen Holzfaeller kaempft und sich aufhalten
            # laesst; "sie braucht noch weitere laufbefehle um durchzuspammen"): der Arbeiter, gegen den sie kaempft, wird nicht mehr
            # einfach ihr Ziel - die Wertrechnung entscheidet (mit der gemessenen Zeit, bis er faellt). Ist er ihr Ziel, zaehlt der Angriff;
            # sonst geht in dieser Runde ein neuer Laufbefehl hinaus (die Wegfuehrung vergisst den alten und schickt ihn noch einmal)
            kampf = self._bekaempft(e, ziele)
            if kampf is not None and kampf == alt:
                self.greift[n] = (
                    alt,
                    self.runde,
                )  # sie greift ihr Ziel an: der Taeter steht in den Daten (nahziel)
            durchspammen = kampf is not None and kampf != alt
            kampf = kampf if kampf == alt else None
            st = self.weg.status(n) if self.weg is not None and alt is not None else None
            if st == "greift_an":
                self.greift[n] = (alt, self.runde)
            elif st in ("gefahr", "kein_weg"):
                # B-182 (Plan_Wegfuehrung.md): kein sicherer Standplatz oder kein Weg - diese Einheit nimmt ein anderes Ziel
                self.gesperrt[(n, alt)] = self.runde + RA.SPERRE_RUNDEN
                aus.append(
                    "NAHKAMPF-RAID: %d (Typ %d) gibt %s %d auf (%s)"
                    % (n, e["typ"], _name(alt), alt[1], st)
                )
                self._freigeben(n)
                alt = None
            # "ziel_weg": die Wegfuehrung sieht unter der Nummer etwas anderes (Art, Besitzer) - das alte Ziel ist weg
            weg_ist = alt is not None and (alt not in ziele or st == "ziel_weg")
            # ein Arbeiter, gegen den sie schon kaempft, bleibt ihr Ziel, auch wenn die Rechnung dort keinen Erfolg erwartet
            if alt is not None and (
                weg_ist or (alt != kampf and not self.wissen.am_ziel(e["typ"], ziele[alt])[1])
            ):
                if weg_ist and self._am_ziel_gewesen(n, alt):
                    if alt[0] == "g":
                        self.zerstoert += 1
                    else:
                        self.getoetet += 1
                    # B-182: jeder Erfolg in die Mitschrift, die Eichung misst daran die Takte vom Ziel bis zum Erfolg
                    aus.append(
                        "NAHKAMPF-RAID: %d (Typ %d) hat %s %d erledigt"
                        % (n, e["typ"], _name(alt), alt[1])
                    )
                elif weg_ist and self.weg is not None:
                    aus.append(
                        "NAHKAMPF-RAID: %s %d ist weg, %d war nicht am Ziel - kein eigener Erfolg"
                        % (_name(alt), alt[1], n)
                    )
                self._freigeben(n)
                alt = None
            laenge = self._laenge(e, L, G, raster) if self.weg is not None else None
            if alt is not None and kampf is None and laenge is not None:
                # S150: jede Runde das Ziel mit dem hoechsten Wert je Takt von hier aus, ueber den sicheren Weg - ein neues Ziel auf dem
                # Weg oder dahinter gewinnt, wenn es mehr Wert je Takt bringt (keine Huerde: Daniel 23:32 "kein komischer wert bitte")
                werte = self._werte(
                    n, e, ziele, {v for m, v in self.ziel.items() if m != n}, laenge
                )
                jetzt = next((w for w in werte if w[2].schluessel == alt), None)
                # ein anderes Ziel zaehlt mit der Zeit, die der Wechsel kostet (WECHSEL_TAKTE, gemessen)
                andere = [
                    (self._nach_wechsel(w[0], w[3]),) + w[1:]
                    for w in werte
                    if w[2].schluessel != alt
                ]
                best = max(andere, default=None, key=lambda w: w[0])
                if best is not None and best[0] > 0 and (jetzt is None or best[0] > jetzt[0]):
                    aus.append(
                        "NAHKAMPF-RAID: %d (Typ %d) wechselt von %s %d zu %s %d (Typ %d) bei %s - %.4f statt %s Wert je Takt "
                        "(mit %.1f Takten fuer den Wechsel), %d statt %s Felder auf dem sicheren Weg"
                        % (
                            n,
                            e["typ"],
                            _name(alt),
                            alt[1],
                            _name(best[2].schluessel),
                            best[2].schluessel[1],
                            best[2].typ,
                            best[2].ort,
                            best[0],
                            "%.4f" % jetzt[0] if jetzt else "kein Weg",
                            WECHSEL_TAKTE,
                            best[1],
                            jetzt[1] if jetzt else "-",
                        )
                    )
                    self._freigeben(n)
                    self.ziel[n], self.wegpunkte[n] = best[2].schluessel, []
                    alt, grund = best[2].schluessel, "better_value_on_path"
            gegner = self._soldat_gegner(e, L, self.sp) if kampf is None else None
            if gegner is not None and alt is not None and alt in ziele and self.weg is not None:
                w, k, info = self._zurueckschlagen(
                    e, L[gegner], ziele[alt], laenge(ziele[alt].ort) if laenge else None
                )
                if self.wehrt.get(n) != (gegner, k > w):
                    self.wehrt[n] = (gegner, k > w)
                    aus.append(
                        "NAHKAMPF-RAID: %d (Typ %d) kaempft gegen Soldat %d (Typ %d): %s - weiter zu %s %d %.4f, zurueckschlagen "
                        "%.4f Wert je Takt (%s Takte bis er faellt, deckt das Ziel: %s, Schaden aus %s)"
                        % (
                            n,
                            e["typ"],
                            gegner,
                            L[gegner]["typ"],
                            "schlaegt zurueck" if k > w else "geht weiter",
                            _name(alt),
                            alt[1],
                            w,
                            k,
                            info.get("t_tot"),
                            "ja" if info.get("deckt") else "nein",
                            info.get("dps"),
                        )
                    )
                if k > w:
                    self.absicht[n] = (
                        Action.ATTACK_UNIT,
                        unit(gegner),
                        "defender_worth_it",
                        {"typ": L[gegner]["typ"]},
                    )
                    self.weg.fuehre(n, "einheit", gegner, "nahkampfraid")
                    continue
            if alt is None:
                belegt = set(self.ziel.values())
                z = self._waehlen(n, e, ziele, belegt, L, G, laenge)
                if z is None:
                    self.absicht[n] = (
                        Action.WAIT_SAFE_TARGET,
                        None,
                        "no_target_with_value",
                        {"targets": len(ziele)},
                    )
                    continue
                grund = "best_value_per_tick"
                aus.append(
                    "NAHKAMPF-RAID: %d (Typ %d) -> %s %d (Typ %d) bei %s, %d Wegpunkte, %s Felder%s"
                    % (
                        n,
                        e["typ"],
                        _name(z.schluessel),
                        z.schluessel[1],
                        z.typ,
                        z.ort,
                        len(self.wegpunkte[n]),
                        (
                            "%s auf dem sicheren Weg, %d Luftlinie"
                            % (laenge(z.ort), WK.schach(ort, z.ort))
                        )
                        if laenge is not None
                        else WK.schach(ort, z.ort),
                        (", Weg ueber die Wegfuehrung" if self.weg is not None else "")
                        + (", dazu (schon besetzt, kein freies)" if self.dazu else ""),
                    )
                )
            art, nr = self.ziel[n]
            z_n = ziele.get(self.ziel[n])
            self.absicht[n] = (
                Action.ATTACK_BUILDING if art == "g" else Action.ATTACK_UNIT,
                building(nr) if art == "g" else unit(nr),
                grund,
                {"typ": z_n.typ} if z_n is not None else {},
            )
            if self.weg is not None:
                # B-182: Weg und Befehle jede Runde neu von der Wegfuehrung - unterwegs um neue Gefahr herum, am Ziel der Angriff
                if durchspammen and self.ziel.get(n) != self._bekaempft(e, ziele):
                    if self.weg.kern_fuehrt(n):
                        # S155: der Kern wiederholt ihren Laufbefehl jeden Takt, solange sie gegen einen anderen als ihr Ziel kaempft
                        aus.append(
                            "NAHKAMPF-RAID: %d (Typ %d) kaempft gegen Arbeiter %d - der Kern wiederholt den Laufbefehl zu %s %d"
                            % (n, e["typ"], self._bekaempft(e, ziele)[1], _name(self.ziel[n]), nr)
                        )
                    else:
                        self.weg.loslassen(
                            n
                        )  # S154 ohne Kern: der Laufbefehl geht in dieser Runde wieder hinaus
                        aus.append(
                            "NAHKAMPF-RAID: %d (Typ %d) haengt im Kampf gegen Arbeiter %d fest - Laufbefehl neu zu %s %d"
                            % (n, e["typ"], self._bekaempft(e, ziele)[1], _name(self.ziel[n]), nr)
                        )
                self.weg.fuehre(n, "gebaeude" if art == "g" else "einheit", nr, "nahkampfraid")
                continue
            weg = self.wegpunkte.get(n, [])
            while weg and WK.schach(ort, weg[0]) <= AM_WEGPUNKT:
                weg.pop(0)
            if weg:
                b = {"angriff": {"einheiten": [n], "lauf": [weg[0][0], weg[0][1]]}}
            elif art == "g":
                b = {"angriff": {"einheiten": [n], "gebaeude": nr}}
            else:
                b = {"angriff": {"einheiten": [n], "ziel": nr}}
            self._senden(n, b, befehl)
        return aus

    def bericht(self):
        return "Nahkampf-Raid: %d Einheiten, %d Gebaeude zerstoert, %d Arbeiter getoetet" % (
            len(self.mitglieder),
            self.zerstoert,
            self.getoetet,
        )
