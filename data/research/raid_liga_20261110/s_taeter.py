# -*- coding: utf-8 -*-
"""B-182 (Daniel 10.11. 22:35: "belege wer wirklich trifft und was und wie viel"): ordnet jeden Lebensverlust gegnerischer
Einheiten und jeden Brand gegnerischer Gebaeude einem Taeter aus dem Lageprotokoll zu und misst, wie die eigenen Kampf-Einheiten
ihre Zeit verbringen. Nur Lageprotokoll, kein Spiel.

Zuordnung je Lebensverlust (Schnappschuss k-1 -> k). Die erste Klasse mit Kandidaten gewinnt, der Verlust wird zu gleichen Teilen
auf ihre Kandidaten verteilt:
  nah          eigene Einheit mit nahziel == Opfer, hoechstens 3 Felder (Schach)
  schuss       eigener Schuetze mit zielart 4 und zieleinheit == Opfer, Luftlinie <= Reichweite + 8
  neben        eigene Nahkampf-Einheit hoechstens 1 Feld (Schach) neben dem Opfer
  schuss_frei  eigener Schuetze ohne dieses Ziel, Luftlinie <= Reichweite
  fremd        Einheit eines dritten Spielers (nicht 0, nicht wir, nicht der Besitzer des Opfers), nahziel == Opfer oder Schuetze
               in Reichweite
  feuer        ein brennendes Gebaeude hoechstens 3 Felder (Schach) vom Opfer
  unbelegt     nichts davon
Tod: Die Nummer fehlt im naechsten Schnappschuss (das Protokoll fuehrt keine Toten) oder traegt dort eine andere Art oder einen
anderen Besitzer. Der letzte Lebenswert zaehlt dann als letzter Verlust, mit den Kandidaten aus k-1.
Brand: feuer eines gegnerischen Gebaeudes springt von 0 auf mehr. Eigener Sklave (Typ 71) hoechstens 5 Felder (Schach) vom
Gebaeudeort -> Sklave; sonst ein anderes brennendes Gebaeude hoechstens 12 Felder -> Ausbreitung; sonst unbelegt.
Gebaeude-Schaden: Lebensverlust eines gegnerischen Gebaeudes. Brennt es -> feuer; sonst eigene Nahkampf-Einheit hoechstens 4 Felder
(Schach) vom Gebaeudeort -> nah_gebaeude (das Lageprotokoll fuehrt bei eigenen Einheiten kein Gebaeudeziel); sonst unbelegt.
Zerstoert = Gebaeude fehlt im naechsten Schnappschuss; ohne vorherigen Schaden zaehlt es als ohne_schaden (Bau fertig, Abriss), nicht als
zerstoert.
Einsatzzeit je eigener Kampf-Einheit und Schnappschuss-Abstand: wirkt (in diesem Abstand Taeter von Schaden oder Brand),
laeuft (Ort aendert sich oder Laufziel != Ort), steht_mit_auftrag (zielart != 0), steht_ohne_auftrag; dazu der Ort: zuhause
(<= 40 Felder vom eigenen Lord beim ersten Schnappschuss), beim_feind (<= 50 Felder von einem gegnerischen Lord), dazwischen.
Die Grenzen (3, 8, 1, 5, 12, 40, 50 Felder) sind selbst gesetzt, nicht gemessen; die Reichweiten kommen aus services/spielwerte.py.

Ab 10.11. 23:07 (Tabelle "eigen" im Lageprotokoll, S114) gilt fuer jede eigene Einheit, die dort steht:
  schuss       nur, wenn ihr Schussziel aus dem Kern (schusseinheit) das Opfer ist - schuss_frei entfaellt fuer sie
  Gebaeude     nah_gebaeude_kern, wenn ihr angegriffenes Gebaeude (mauerx/mauery) hoechstens 3 Felder vom Gebaeudeort liegt
Ohne Tabelle (aeltere Protokolle) bleibt es bei den Naeherungen oben; die Klasse in der Ausgabe sagt, welche galt.

Aufruf: python s_taeter.py <lage.jsonl.gz> [<konsole.txt>]   (eigener Spieler 1; mit Mitschrift auch die Behauptungen der Module)
"""
import collections
import gzip
import json
import re
import sys

import selfaware.micro.tasks.raids as RA
import selfaware.services.spielwerte as SW
from selfaware.baukasten.einheiten import ARTEN
from selfaware.telemetry.lageprotokoll import eigen_lesen

ICH = 1
KAMPF = set(ARTEN) | {71, 72, 73, 74, 75}
ARTNAME = {t: a.name for t, a in ARTEN.items()}
ARTNAME.update({71: "Sklave", 72: "Schleuderer", 73: "Assassine", 74: "Berittener Bogenschuetze", 75: "Arabischer Schwertkaempfer"})


def tabelle(text, kopfzeile):
    z = text.split("\n")
    k = z[kopfzeile].split()
    aus = {}
    for r in z[kopfzeile + 1:]:
        w = r.split()
        if len(w) == len(k):
            d = dict(zip(k, w, strict=True))
            aus[d["nr"]] = {a: (int(b) if b.lstrip("-").isdigit() else b) for a, b in d.items()}
    return aus


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def ort(e):
    return (e["x"], e["y"])


def kandidaten(opfer_nr, o, E, brennt, eig=None):
    """Taeterklasse und Liste der Taeter (Nummer, Besitzer, Art) fuer einen Verlust der Einheit o (Stand k-1).
    eig: Tabelle "eigen" ({Nummer als Text: Felder}) - mit ihr zaehlt bei eigenen Schuetzen nur das Schussziel aus dem Kern."""
    eig = eig or {}
    p, besitzer = ort(o), o["besitzer"]
    nah, schuss, neben, frei, fremd = [], [], [], [], []
    for n, e in E.items():
        if e["besitzer"] in (0, besitzer):
            continue
        q, art = ort(e), e["typ"]
        r = SW.erfassen(art)
        if e["besitzer"] == ICH:
            ke = eig.get(n)
            if str(e.get("nahziel")) == opfer_nr and schach(p, q) <= 3:
                nah.append(n)
            elif ke is not None and r is not None:
                if str(ke["schusseinheit"]) == opfer_nr and SW.luftlinie2(p, q) <= (r + 8) ** 2:
                    schuss.append(n)
            elif r is not None and e["zielart"] == 4 and str(e["zieleinheit"]) == opfer_nr and SW.luftlinie2(p, q) <= (r + 8) ** 2:
                schuss.append(n)
            elif r is None and art in KAMPF and schach(p, q) <= 1:
                neben.append(n)
            elif r is not None and SW.luftlinie2(p, q) <= r * r:
                frei.append(n)
        elif str(e.get("nahziel")) == opfer_nr or (r is not None and SW.luftlinie2(p, q) <= r * r):
            fremd.append(n)
    for name, liste in (("nah", nah), ("schuss", schuss), ("neben", neben), ("schuss_frei", frei), ("fremd", fremd)):
        if liste:
            return name, liste
    if any(schach(p, g) <= 3 for g in brennt):
        return "feuer", []
    return "unbelegt", []


def gruppe_von(typ):
    """Lord ist Typ 55 (Lageprotokoll 10.11.: der Lord beider Spieler, 150.000 und 105.000 Leben); Arbeiter wie in der Reiterjagd."""
    if typ == 55:
        return "lord"
    if typ in RA.ARBEITER:
        return "arbeiter"
    return "soldat" if typ in KAMPF else "andere"


def lords(E):
    """Je Besitzer die Einheit mit dem meisten Leben (der Lord hat 75.000 und mehr, Arbeiter 2.500 bis 15.000)."""
    best = {}
    for e in E.values():
        if e["besitzer"] and (e["besitzer"] not in best or e["leben"] > best[e["besitzer"]]["leben"]):
            best[e["besitzer"]] = e
    return {b: ort(e) for b, e in best.items() if e["leben"] >= 50000}


def auswerten(pfad):
    schaden = collections.Counter()      # (klasse, taeter_art, opfer_gruppe) -> Lebenspunkte
    tote = collections.Counter()         # (klasse, taeter_art, opfer_art) -> Anzahl (geteilt)
    braende = collections.Counter()      # (ursache, taeter_art) -> Anzahl
    geb_schaden = collections.Counter()  # (ursache, taeter_art) -> Lebenspunkte
    zerstoert = collections.Counter()    # letzte Ursache -> Anzahl
    zeit = collections.Counter()         # (art, zustand, ortsklasse) -> Takte
    je_einheit = collections.defaultdict(lambda: collections.Counter())  # nr -> (zustand) -> Takte (eigene Kampf-Einheiten)
    vE = vG = vd = None
    vt = None
    heim = feinde = None
    letzte_geb_ursache = {}
    verschwunden, wieder_da, tote_n = {}, collections.Counter(), 0   # Gegenprobe: taucht ein "Toter" mit gleicher Nummer, Art und Besitzer wieder auf?
    for zeile in gzip.open(pfad, "rt", encoding="utf-8"):
        d = json.loads(zeile)
        t = d["t"]
        E = tabelle(d["einheiten"], 1)
        G = tabelle(d["gebaeude"], 0)
        if heim is None:
            L = lords(E)
            if ICH in L:
                heim = L[ICH]
                feinde = [q for b, q in L.items() if b != ICH]
        for n, e in E.items():
            v = verschwunden.get(n)
            if v and v[1] == e["typ"] and v[2] == e["besitzer"]:
                wieder_da["bis 500 Takte" if t - v[0] <= 500 else "spaeter"] += 1
            if v:
                verschwunden.pop(n)
        if vE is not None and heim is not None:
            dt = t - vt
            brennt_v = [ort(g) for g in vG.values() if g.get("feuer", 0) > 0]
            veig = {str(k): v for k, v in eigen_lesen(vd).items()}
            taeter_jetzt = collections.Counter()
            # 1. Gegnerische Einheiten: Verlust und Tod
            for n, o in vE.items():
                if o["besitzer"] in (0, ICH):
                    continue
                e = E.get(n)
                if e is not None and (e["besitzer"] != o["besitzer"] or e["typ"] != o["typ"]):
                    continue    # Artwechsel derselben Nummer: ein Bauer nimmt Arbeit an oder wird angeworben (1 -> 3, 1 -> 72 ...), kein Tod
                if e is not None:
                    verlust, tot = o["leben"] - e["leben"], False
                else:
                    verlust, tot = o["leben"], True
                    verschwunden[n] = (t, o["typ"], o["besitzer"])
                    tote_n += 1
                if verlust <= 0:
                    continue
                klasse, wer = kandidaten(n, o, vE, brennt_v, veig)
                gruppe = gruppe_von(o["typ"])
                if wer:
                    for w in wer:
                        art = vE[w]["typ"] if vE[w]["besitzer"] == ICH else "fremd"
                        schaden[(klasse, art, gruppe)] += verlust / len(wer)
                        if tot:
                            tote[(klasse, art, gruppe, o["typ"])] += 1 / len(wer)
                        if vE[w]["besitzer"] == ICH:
                            taeter_jetzt[w] += 1
                else:
                    schaden[(klasse, "-", gruppe)] += verlust
                    if tot:
                        tote[(klasse, "-", gruppe, o["typ"])] += 1
            # 2. Gegnerische Gebaeude: Brand, Schaden, Zerstoerung
            for n, g in vG.items():
                if g["besitzer"] in (0, ICH):
                    continue
                h = G.get(n)
                p = ort(g)
                if h is not None and h["besitzer"] == g["besitzer"] and h["typ"] == g["typ"]:
                    if g.get("feuer", 0) == 0 and h.get("feuer", 0) > 0:
                        sk = [w for w, e in vE.items() if e["besitzer"] == ICH and e["typ"] == 71 and schach(ort(e), p) <= 5]
                        if sk:
                            braende[("sklave", 71)] += 1
                            for w in sk:
                                taeter_jetzt[w] += 1
                        elif any(schach(p, q) <= 12 for q in brennt_v if q != p):
                            braende[("ausbreitung", "-")] += 1
                        else:
                            braende[("unbelegt", "-")] += 1
                    verlust = g["leben"] - h["leben"]
                    if verlust > 0:
                        brennt_g = g.get("feuer", 0) > 0 or h.get("feuer", 0) > 0
                        # 10.11. 22:50: zielgebaeude ist im Lageprotokoll bei eigenen Einheiten immer 0 (gemessen an
                        # lage_20261110_104030), darum die Naehe: eigene Nahkampf-Einheit hoechstens 4 Felder am Gebaeudeort
                        kern_wer = [w for w, ke in veig.items() if (ke["mauerx"], ke["mauery"]) != (0, 0)
                                    and schach((ke["mauerx"], ke["mauery"]), p) <= 3 and w in vE and schach(ort(vE[w]), p) <= 8]
                        wer = [] if brennt_g else [w for w, e in vE.items() if e["besitzer"] == ICH and e["typ"] in KAMPF
                                                   and SW.erfassen(e["typ"]) is None and schach(ort(e), p) <= 4]
                        if kern_wer and not brennt_g:
                            for w in kern_wer:
                                geb_schaden[("nah_gebaeude_kern", vE[w]["typ"])] += verlust / len(kern_wer)
                                taeter_jetzt[w] += 1
                            letzte_geb_ursache[n] = "nah_gebaeude_kern"
                        elif wer and not veig:
                            for w in wer:
                                geb_schaden[("nah_gebaeude", vE[w]["typ"])] += verlust / len(wer)
                                taeter_jetzt[w] += 1
                            letzte_geb_ursache[n] = "nah_gebaeude"
                        elif brennt_g:
                            geb_schaden[("feuer", "-")] += verlust
                            letzte_geb_ursache[n] = "feuer"
                        else:
                            geb_schaden[("unbelegt", "-")] += verlust
                            letzte_geb_ursache[n] = letzte_geb_ursache.get(n, "unbelegt")
                else:
                    zerstoert[letzte_geb_ursache.get(n, "feuer" if g.get("feuer", 0) > 0 else "ohne_schaden")] += 1
            # 3. Einsatzzeit der eigenen Kampf-Einheiten
            for n, e in vE.items():
                if e["besitzer"] != ICH or e["typ"] not in KAMPF:
                    continue
                f = E.get(n)
                q = ort(e)
                ziel_e = vE.get(str(e["zieleinheit"])) if e["zielart"] == 4 else None
                nah_e = vE.get(str(e.get("nahziel")))
                r_e = SW.erfassen(e["typ"])
                if taeter_jetzt.get(n):
                    zustand = "wirkt"
                elif nah_e is not None and nah_e["besitzer"] not in (0, ICH) and schach(ort(nah_e), q) <= 3:
                    zustand = "kaempft"
                elif (ziel_e is not None and ziel_e["besitzer"] not in (0, ICH) and r_e is not None
                      and SW.luftlinie2(ort(ziel_e), q) <= r_e * r_e):
                    zustand = "kaempft"
                elif e["typ"] == 71 and any(g["besitzer"] not in (0, ICH) and schach(ort(g), q) <= 3 for g in vG.values()):
                    zustand = "am_gebaeude"
                elif (f is not None and ort(f) != q) or (e["laufx"], e["laufy"]) != q:
                    zustand = "laeuft"
                elif e["zielart"] != 0:
                    zustand = "steht_mit_auftrag"
                else:
                    zustand = "steht_ohne_auftrag"
                wo = "zuhause" if schach(q, heim) <= 40 else ("beim_feind" if any(schach(q, x) <= 50 for x in feinde) else "dazwischen")
                zeit[(e["typ"], zustand, wo)] += dt
                je_einheit[(n, e["typ"])][zustand] += dt
        vE, vG, vt, vd = E, G, t, d
    return {"schaden": schaden, "tote": tote, "braende": braende, "geb_schaden": geb_schaden, "zerstoert": zerstoert, "zeit": zeit,
            "ende": vt, "heim": heim, "feinde": feinde, "wieder_da": wieder_da, "verschwunden_n": tote_n}


def kaeufe(konsole):
    """Stueck, erwartete Punkte und Gold je Art aus den WIRKUNG-KAUF-Zeilen (Gold = Punkte / Punkte je Gold)."""
    text = open(konsole, encoding="utf-8", errors="replace").read()
    k = collections.defaultdict(lambda: [0, 0.0, 0.0])
    for n, art, pkt, jg in re.findall(r"WIRKUNG-KAUF: (\d+) [^,(;|]*\(Typ (\d+)\), erwartet ([\d.]+) Punkte, ([\d.]+) je Gold", text):
        z = k[int(art)]
        z[0] += int(n)
        z[1] += float(pkt)
        z[2] += float(pkt) / float(jg) if float(jg) > 0 else 0.0
    return dict(k)


def behauptungen(konsole):
    """Was die Module selbst als Erfolg schrieben."""
    text = open(konsole, encoding="utf-8", errors="replace").read()
    return {
        "Reiterjagd 'erledigt'": len(re.findall(r"REITERJAGD: Reiter \d+ hat Arbeiter \d+ erledigt", text)),
        "Brandtrupp 'angezuendet'": len(re.findall(r"BRANDTRUPP: Sklave \d+ hat Gebaeude \d+ \(Typ \d+\) angezuendet", text)),
        "Nahkampf-Raid 'erledigt'": len(re.findall(r"NAHKAMPF-RAID: \d+ \(Typ \d+\) hat \w+ \d+ erledigt", text)),
    }


def bericht(r, konsole=None):
    aus = ["Lageprotokoll bis Takt %d, eigener Lord bei %s, Gegner-Lords bei %s" % (r["ende"], r["heim"], r["feinde"])]
    aus.append("Gegenprobe Tod: %d gegnerische Einheiten verschwanden, mit gleicher Nummer, Art und Besitzer wieder da: %s"
               % (r["verschwunden_n"], dict(r["wieder_da"]) or "keine"))
    aus.append(chr(10) + "TOTE gegnerische Einheiten nach Taeter (Klasse, Taeter-Art, Opfer-Gruppe, Opfer-Typ): Anzahl")
    for (k, a, g, o), v in sorted(r["tote"].items(), key=lambda x: -x[1]):
        aus.append("  %-12s %-28s %-9s Typ %-3s %6.1f" % (k, ARTNAME.get(a, a), g, o, v))
    je = collections.Counter()
    for (k, a, _g, _o), v in r["tote"].items():
        je[ARTNAME.get(a, a) if k in ("nah", "schuss", "neben", "schuss_frei") else k] += v
    aus.append("  zusammen je Taeter: " + ", ".join("%s %.1f" % kv for kv in je.most_common()))
    aus.append("  %-12s %-28s %-9s %6.1f" % (k, ARTNAME.get(a, a), g, v))
    aus.append("\nSCHADEN an gegnerischen Einheiten (Lebenspunkte) nach Taeter")
    for (k, a, g), v in sorted(r["schaden"].items(), key=lambda x: -x[1]):
        aus.append("  %-12s %-28s %-9s %9.0f" % (k, ARTNAME.get(a, a), g, v))
    aus.append("\nBRAENDE gegnerischer Gebaeude: " + ", ".join("%s %d" % (k[0], v) for k, v in r["braende"].most_common()))
    aus.append("GEBAEUDE-SCHADEN (Lebenspunkte): " + ", ".join("%s %s %.0f" % (k[0], ARTNAME.get(k[1], k[1]), v) for k, v in r["geb_schaden"].most_common()))
    aus.append("ZERSTOERTE gegnerische Gebaeude nach letzter Ursache: " + ", ".join("%s %d" % kv for kv in r["zerstoert"].most_common()))
    aus.append("\nEINSATZZEIT eigener Kampf-Einheiten (Einheiten-Takte, Anteil je Art)")
    arten = sorted({a for a, _z, _w in r["zeit"]})
    for a in arten:
        ges = sum(v for (b, _z, _w), v in r["zeit"].items() if b == a)
        teile = collections.Counter()
        for (b, z, w), v in r["zeit"].items():
            if b == a:
                teile["%s/%s" % (z, w)] += v
        aus.append("  %-28s %8d Takte: " % (ARTNAME.get(a, a), ges) + ", ".join("%s %.0f %%" % (k, 100 * v / ges) for k, v in teile.most_common(6)))
    if konsole:
        aus.append("GEKAUFT nach Wirkung (Art: Stueck, erwartete Punkte, Gold): " + "; ".join(
            "%s %d, %.0f, %.0f" % (ARTNAME.get(art, art), *v) for art, v in sorted(kaeufe(konsole).items())))
        aus.append("\nBEHAUPTET von den Modulen: " + ", ".join("%s %d" % kv for kv in behauptungen(konsole).items()))
    return "\n".join(aus)


if __name__ == "__main__":
    r = auswerten(sys.argv[1])
    print(bericht(r, sys.argv[2] if len(sys.argv) > 2 else None))
