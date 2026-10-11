# -*- coding: utf-8 -*-
"""Arbeitsgang der Nahrungsarbeiter messen (SAI 11.10., Daniel 17:12: "schlauer testen - per Tick per Entfernung, dann
weisst du, wie viel mehr Ertrag es pro Feld Naehe gibt; damit kann man auch eine maximal effektive, kompakte Burg
berechnen"; 17:15: geht es nicht auf, fehlt etwas - z.B. Abwandern/Verschwinden oder Getoetetwerden).

Wie arbeitsgang_messen.py (Schmied/Gerber, 06.10.), nur fuer Nahrung: Pruefstand gegen eine Ratte mit leerer KI, Gold
gesetzt, Baukosten 0 (Rueckweg im finally). Je ein Bau auf vorher per Wegtest erreichbarem Platz: Kornspeicher, Apfelhof,
Milchviehhof, Getreidefarm, Muehle, Baeckerei, Jaegerhuette an der Herde, Huetten. Rationen "keine" (nichts gegessen).
Mitgeschrieben im Spiel (einheitwacht, alle 2 Ticks): Ort jedes Nahrungsarbeiters; dazu alle 100 Ticks der Bestand.
Auswertung danach mit arbeitsgang_auswerten.py: Ticks je Feld (gerade/schraeg), Haltezeiten je Ort (= Arbeitszeit am
Gebaeude), Gaenge. Daraus je Gebaeude: Ertrag(d) = Ladung / (Arbeitszeit + 2 * d * Ticks je Feld).
VORHER festgelegt (Widerlegung): Die Formel muss die lange Messung (daten/nahrung_messung_ascension_lauf5_20000.json,
Aepfel 2,43 bei Weg 12, Kaese 2,80 bei 19, Fleisch 1,80 bei 91, Brot 3,00) auf 20 % treffen; sonst fehlt ein Faktor
(Abwandern, Tod, Warten auf Rohstoff, volles Lager) - dann die Spuren der Arbeiter auf genau das durchsehen.
Aufruf: SHC_INSTANZ=4 python arbeitsgang_nahrung.py [ticks=20000] [tempo=300]"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
import erstes_spiel as E
import wegkarte as W
from laden import befehl, peek, TICK
from streitkolben_messen import setze, warte_ticks, GOLD
from wege_abstand import kosten_nullen, kosten_zurueck
from arbeitsgang_messen import log_ab
from nahrung_messen import wegtest
from farmen_mischen import lies_karte
from waechter import schach
from bauen import vorrat

D = os.path.join(HIER, "..", "daten")
SP = 1
# Arbeiter-Typen: im Lagebild 11.10. 17:05 ueber das Feld 'arbeitsplatz' den Gebaeuden zugeordnet
ARBEITER = {13: "Apfelbauer", 14: "Milchbauer", 11: "Getreidebauer", 15: "Mueller", 16: "Baecker", 6: "Jaeger"}
WAREN = ("apfel", "kaese", "fleisch", "brot", "weizen", "mehl")


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    dauer, tempo = int(arg.get("ticks", 20000)), int(arg.get("tempo", 300))
    # art=apfel (Daniel 22:37 "ja mach weiter"): nur Kornspeicher + Apfelplantagen in gestaffelter Entfernung - die Formel
    # verfehlte Aepfel um 28 %, weil der Bauer ~22 Felder zu seinen Baeumen lief. Vorher festgelegt: stehen die Baeume bei
    # allen Plantagen im eigenen 10x10-Feld, war der lange Baumweg ein Sonderfall.
    art = arg.get("art", "alle")
    abstaende = [int(x) for x in arg.get("abstaende", "10,30,50").split(",")]
    E.LEERE_KI = True
    E.GEGNER_ERWARTET = ""
    E.LIGA_GEFECHT = dict(E.LIGA_GEFECHT, ki=1)
    E.gefecht_starten(tempo)
    setze(GOLD, 20000)
    kosten_vorher = kosten_nullen()
    # 11.10. 17:28: ein Absturz im finally liess die Baukosten auf 0 - die Sicherung liegt jetzt auch als Datei
    json.dump({str(a): v for a, v in kosten_vorher.items()}, open(os.path.join(D, "kosten_sicherung_i%s.json" % os.environ.get("SHC_INSTANZ", "1")), "w"))
    erg = {"gebaeude": {}, "bestand": [], "arbeiter": {}}
    try:
        info = json.load(open(os.path.join(D, "start_M19.json"), encoding="utf-8"))
        K, F = tuple(info["bergfried_eingang"]), tuple(info["feind_bergfried"]["2"]["eingang"])
        eigen = lambda p: schach(p, K) < schach(p, F)
        karte = lambda n: [p for p in lies_karte(os.path.join(D, "start_M19_platz_%s.txt" % n)) if eigen(p)]
        teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == 10]
        lager = (teile[0]["x"], teile[0]["y"]) if teile else K
        fr = sorted(karte("apfel"), key=lambda p: schach(p, lager))
        # art=brot (Daniel 22:53: "Brot ist effektiver bei weniger Farmplatz und je naeher die Farm am Vorratslager"):
        # Kornspeicher am Bergfried, damit die Getreidefarm den fruchtbaren Platz am naechsten zum Lager bekommt
        ks = E.baue_schnell(19, fr[0][0], fr[0][1], 12) if fr and art != "brot" else E.baue_schnell(19, K[0], K[1], 15)
        erg["gebaeude"]["kornspeicher"] = ks
        warte_ticks(60)
        belegt = [ks] if ks else []
        # Daniel 17:22 "warum faellt dir nicht auf, dass das Vorratslager voll ist?": Lauf 17:20 - alle 4 Lagerteile Holz
        # (je Teil EINE Ware, je 48), der Getreidebauer stand ab Tick 7.341 still (Zustand 9, Ladung 0 -
        # der fertige Weizen bleibt am Feld), Muehle und Baeckerei hatten nichts. Gegenprobe 17:27: ein Lagerteil angebaut -> nach ~100 Ticks
        # liefert er, Mehl entsteht. Darum zuerst anbauen und das Lager sperren (Muehle/Baeckerei mauerten es ein).
        erg["gebaeude"]["lager_anbau"] = E.baue_schnell(10, lager[0], lager[1], 12)
        warte_ticks(30)
        belegt += [(t["x"], t["y"]) for t in teile] + [p for p in [erg["gebaeude"]["lager_anbau"]] if p]
        fr = sorted(fr, key=lambda p: schach(p, lager if art == "brot" else (ks or lager)))
        if art == "brot":
            frei = [p for p in fr if all(schach(p, q) >= 10 for q in belegt)][:40]
            erg["gebaeude"]["getreide"] = next((o for o in (E.baue_schnell(30, p[0], p[1], 4) for p in wegtest(frei)) if o), None)
            if erg["gebaeude"]["getreide"]:
                belegt.append(erg["gebaeude"]["getreide"])
        if art == "apfel":
            for i, ab in enumerate(abstaende):
                kand = sorted([p for p in fr if all(schach(p, q) >= 14 for q in belegt)],
                              key=lambda p: abs(schach(p, ks or lager) - ab))[:24]
                ort = next((o for o in (E.baue_schnell(32, p[0], p[1], 2) for p in wegtest(kand)) if o), None)
                erg["gebaeude"]["apfel%d" % i] = ort
                if ort:
                    belegt.append(ort)
        for name, typ in (() if art in ("apfel", "brot") else (("apfel", 32), ("milch", 33), ("getreide", 30))):
            frei = [p for p in fr if all(schach(p, q) >= 12 for q in belegt)][:40]
            ort = next((o for o in (E.baue_schnell(typ, p[0], p[1], 4) for p in wegtest(frei)) if o), None)
            erg["gebaeude"][name] = ort
            if ort:
                belegt.append(ort)
        hu = sorted(karte("huette"), key=lambda p: schach(p, lager))
        for name, typ in (() if art == "apfel" else (("muehle", 34), ("baeckerei", 17), ("baeckerei2", 17), ("baeckerei3", 17))
                          if art == "brot" else (("muehle", 34), ("baeckerei", 17))):
            frei = [p for p in hu if all(schach(p, q) >= 6 for q in belegt)][:40]
            ort = next((o for o in (E.baue_schnell(typ, p[0], p[1], 2) for p in wegtest(frei)) if o), None)
            erg["gebaeude"][name] = ort
            if ort:
                belegt.append(ort)
        L = E.runde_lesen()[1]
        rehe = [(e["x"], e["y"]) for e in L.values() if e["typ"] == 44 and eigen((e["x"], e["y"])) and schach((e["x"], e["y"]), K) <= 70]
        herde = max(rehe, key=lambda p: sum(1 for q in rehe if schach(p, q) <= 15)) if rehe else None
        erg["gebaeude"]["jaeger"] = E.baue_schnell(7, herde[0], herde[1], 12) if herde and art not in ("apfel", "brot") else None
        for i in range(4):
            erg["gebaeude"]["huette%d" % i] = E.baue_schnell(1, K[0] - 7, K[1] - 2, 25)
        befehl({"spielbefehl": {"nr": 35, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")     # Rationen keine
        # Lauf 17:17: ohne Bestechung fiel die Beliebtheit auf 23, Apfel-/Milchbauer, Baecker und 3 Mueller wanderten ab
        # (EW "WEG" bei 3.132 / 3.506 / 9.893-10.043, alle 50 Ticks einer). Steuerstufe 0 = Bestechung haelt sie.
        befehl({"spielbefehl": {"nr": 34, "werte": [0]}}, 1.0, bis="SPIELBEFEHL")
        print("gebaut:", erg["gebaeude"], flush=True)
        nummern = {}
        for _ in range(80):
            L = E.runde_lesen()[1]
            nummern = {n: e["typ"] for n, e in L.items() if e["besitzer"] == SP and e["typ"] in ARBEITER}
            if (art == "brot" and {11, 15, 16} <= set(nummern.values())) \
                    or (art == "apfel" and len(nummern) >= sum(1 for n in erg["gebaeude"] if n.startswith("apfel") and erg["gebaeude"][n]))                     or (art not in ("apfel", "brot") and len(set(nummern.values())) >= 6):
                break
            warte_ticks(25)
        erg["arbeiter"] = {str(n): ARBEITER[t] for n, t in nummern.items()}
        print("Arbeiter:", erg["arbeiter"], flush=True)
        erg["ew"], erg["stillstand"], erg["lagerteile"], erg["angriffe"], erg["tiere_nah"] = [], [], [], [], []
        erg["ladungen"], letzte_ladung = [], {}

        def ew_ernten():
            # log_ab liest nur ab der LETZTEN Scharf-Marke - vor jedem Neu-Scharfschalten einsammeln
            erg["ew"] += [z.split("INFO|", 1)[-1] for z in log_ab("EINHEITWACHT: scharf")
                          if " EW " in z or "EW Orte" in z or "EW Tick" in z]
        befehl({"einheitwacht": {"nr": sorted(nummern), "alle": 2}}, 1.0, bis="EINHEITWACHT")
        cx, cy = (ks or lager)
        k = W.holen(max(cx - 80, 0), max(cy - 80, 0), min(cx + 80, 399), min(cy + 80, 399))
        erg["wegkarte_fenster"] = [k["x0"], k["y0"], k["x1"], k["y1"]]
        t0 = peek(TICK)[0]
        still = {}                      # Nummer -> (Ort, seit Tick, gemeldet)
        while peek(TICK)[0] - t0 < dauer:
            kanal.belege()
            v = vorrat(SP)
            st, L, G = E.runde_lesen()
            t = peek(TICK)[0] - t0
            erg["bestand"].append(dict({w: v.get(w, 0) for w in WAREN}, t=t, beliebt=st.get("beliebt"), leute=st.get("leute")))
            # 11.10. 17:20: Apfel-/Milchbauer werden bei Tick 3.132/3.506 durch NEUE Einheiten ersetzt -> dem
            # Arbeitsplatz folgen: neue Nahrungsarbeiter sofort mitbeobachten
            neu = {n: e["typ"] for n, e in L.items() if e["besitzer"] == SP and e["typ"] in ARBEITER and n not in nummern}
            if neu:
                ew_ernten()
                nummern.update(neu)
                erg["arbeiter"].update({str(n): "%s (ab Tick %d, Arbeitsplatz %s)" % (ARBEITER[ty], t, L[n].get("arbeitsplatz"))
                                        for n, ty in neu.items()})
                befehl({"einheitwacht": {"nr": sorted(nummern), "alle": 2}}, 1.0, bis="EINHEITWACHT")
                print("Tick %d: neue Arbeiter beobachtet %s" % (t, neu), flush=True)
            # Ladung/Zustand je Arbeiter bei jeder Aenderung (Mehl je Backgang, Weizen je Mahlgang - 22:53)
            for n in nummern:
                e = L.get(n)
                if e and letzte_ladung.get(n) != (e.get("zustand"), e.get("ladung")):
                    letzte_ladung[n] = (e.get("zustand"), e.get("ladung"))
                    erg["ladungen"].append((t, n, e["typ"], e.get("zustand"), e.get("ladung"), (e["x"], e["y"])))
            # Raubtiere und Angriffe (Daniel 17:15 "getoetet werden"; Apfel-/Milchbauer verschwinden in jedem Lauf bei Tick
            # 3.132/3.506): jedes Tier (Typ 44/45) bis 8 Felder an einem beobachteten Arbeiter und jeder Angreifer wird notiert
            for n in nummern:
                e = L.get(n)
                if not e:
                    continue
                if e.get("nahangreifer"):
                    erg["angriffe"].append({"t": t, "nr": n, "ort": (e["x"], e["y"]), "angreifer": e.get("nahangreifer"),
                                            "leben": e.get("leben")})
                for m, x in L.items():
                    if x["typ"] in (44, 45) and schach((x["x"], x["y"]), (e["x"], e["y"])) <= 8:
                        erg["tiere_nah"].append({"t": t, "nr": n, "tier": m, "typ": x["typ"],
                                                 "abstand": schach((x["x"], x["y"]), (e["x"], e["y"]))})
            # Stillstand-Waechter (Daniel 17:22 "sollte direkt auffallen"): wer 1.500 Ticks am selben Fleck steht, wird
            # sofort gemeldet - mit Zustand, Ladung und freien Lagerteilen, damit die Ursache gleich daneben steht
            for n in nummern:
                e = L.get(n)
                if not e:
                    continue
                ort = (e["x"], e["y"])
                vorher_ort = still.get(n)
                if not vorher_ort or vorher_ort[0] != ort:
                    still[n] = (ort, t, False)
                elif t - vorher_ort[1] >= 1500 and not vorher_ort[2]:
                    teile_jetzt = [peek(0xF98520 + 0x14 + int(g) * 0x32C + 0x184, 1)[0] for g, x in G.items()
                                   if x["besitzer"] == SP and x["typ"] == 10]
                    s = {"nr": n, "wer": ARBEITER.get(e["typ"]), "seit": vorher_ort[1], "t": t, "ort": ort, "zustand": e.get("zustand"),
                         "ladung": e.get("ladung"), "lagerteile_frei": sum(1 for c in teile_jetzt if c == 0),
                         "lagerteile": len(teile_jetzt)}
                    erg["stillstand"].append(s)
                    still[n] = (ort, vorher_ort[1], True)
                    print("STILLSTAND:", s, flush=True)
            if t // 500 != (erg["lagerteile"][-1][0] // 500 if erg["lagerteile"] else -1):
                erg["lagerteile"].append((t, [(int(g), peek(0xF98520 + 0x14 + int(g) * 0x32C + 0x184, 2))
                                              for g, x in G.items() if x["besitzer"] == SP and x["typ"] == 10]))
            if st.get("beliebt", 10000) < 5000:
                erg["ungueltig"] = "Beliebtheit %s unter 50 bei Tick %d - Abwanderung verfaelscht die Messung" % (
                    st.get("beliebt"), peek(TICK)[0] - t0)
                print("ABBRUCH:", erg["ungueltig"], flush=True)
                break
            warte_ticks(int(arg.get("stich", 100)))
        befehl({"einheitwacht": False}, 1.0, bis="EINHEITWACHT")
        ew_ernten()
        print("EW-Zeilen:", len(erg["ew"]), "| Stillstaende:", len(erg["stillstand"]), flush=True)
    finally:
        # Reihenfolge (Absturz 17:28 verlor 20.000 Ticks Daten): erst sichern, dann zuruecksetzen - jeder Schritt fuer sich
        pfad = os.path.join(D, "arbeitsgang_nahrung_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        try:
            kosten_zurueck(kosten_vorher)
        finally:
            befehl({"pause": True}, 0.5)
        import shutil
        try:
            shutil.copy(os.path.join(kanal.ABZUG, "wegkarte.txt"), pfad.replace(".json", "_wegkarte.txt"))
        except OSError:
            pass
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
