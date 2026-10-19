# -*- coding: utf-8 -*-
"""Jeder tote Assassine mit klarer Erklaerung (Daniel 18.10.2026: "warum sind die Assassinen gestorben? ich will fuer jeden
eine klare Erklaerung und was man haette besser machen koennen").

Quellen je Tod (nichts geschaetzt, was in den Daten steht):
  - Mitschrift (Konsole): was der Lenker mit IHM vorhatte - letzte Meldungen mit seiner Nummer (ZIELWAHL, WEG, BEUTE,
    ROUTE GEFAEHRLICH, AUSWEICHEN, FLUCHT, LORD-..., STILLSTAND) und die MESSUNG-Zeilen
  - Lageprotokoll: die letzten Runden vor dem Tod - Leben, Zustand, Ort, Laufziel; Feinde je Art im Umkreis (Fernkaempfer in
    ihrer Reichweite, Nahkaempfer <= 3 Felder, Loewen <= 4, Feuerwerfer <= 11); sichtbar = waehlbarer Feind <= 20 Felder
    (L75/L81); Lebensverlust je Takt
Ursache nach Regeln (Reihenfolge = Vorrang): Lord-Angriff, Loewe, Nahkampf, Feuerwerfer, Beschuss (sichtbar), unklar.
Was besser waere: je Ursache die Regel aus den Editor-Messungen (L81-L84) bzw. den Funden.

Aufruf: uv run python -m selfaware.tools.analysis.tode_erklaeren <konsole.txt> <lage.jsonl.gz> [ausgabe.md]
"""
import collections
import io
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.telemetry.lageprotokoll as LP
import selfaware.services.sicht as SI

FERN = {22: ("Bogen", 40), 23: ("Armbrust", 40), 70: ("arab. Bogen", 40), 72: ("Schleuder", 17), 74: ("Pferdebogen", 40),
        76: ("Feuerwerfer", 11)}
NAHKAMPF = {24: "Speer", 25: "Pike", 26: "Streitkolben", 27: "Schwert", 28: "Ritter", 55: "Lord", 71: "Sklave",
            73: "Assassine", 75: "arab. Schwert"}
WAEHLBAR = {5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 39, 40, 41, 55, 58, 59, 60, 61, 70, 71, 72, 73, 74, 75, 76, 77}
LOEWE = 45


def ch(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def meldungen(konsole):
    """{nr: [(tick, text)]} - jede Meldung, die eine Assassinen-Nummer als Handelnden nennt."""
    m = collections.defaultdict(list)
    muster = re.compile(r"(ERSTE VERLETZUNG|TOD-AKTE|ZIELWAHL|ZIELWECHSEL|WEG|BEUTE|ROUTE GEFAEHRLICH|AUSWEICHEN|FLUCHT|STILLSTAND geloest|"
                        r"LORD-BEREITSTELLUNG|LORD-ANGRIFF|MESSUNG verletzt|MESSUNG tot) ([0-9]+)")
    for z in io.open(konsole, encoding="utf-8", errors="replace"):
        t = re.match(r"^ *([0-9]+) \|", z)
        if not t:
            continue
        tick = int(t.group(1))
        z = re.sub(r"^ *[0-9]+ \|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\| ", "", z)   # Spalten der Rundenzeile weg
        for teil in z.split("; "):
            for mm in muster.finditer(teil):
                m[int(mm.group(2))].append((tick, teil.strip()[:230]))
            for gm in re.finditer(r"GEMEINSAM-AUF-LORD[^;]*", teil):
                m[-1].append((tick, gm.group(0)[:200]))
    return m


def lage_am(ort, n, L, G):
    """19.10.: wer konnte ihn an ort treffen - Spaeher, Schuetzen in Reichweite (mit Linie laut Modell), Modell-Zuteilung,
    Nahkaempfer <= 2, Loewen <= 4, Feuerwerfer <= 11. Gibt (Text, Werte)."""
    try:
        s = SI.Lage(L, G, 1)
    except Exception:
        s = None
    feinde = [e for e in L.values() if e["besitzer"] not in (0, 1)]
    sp = min(((SI.abstand_fein(ort, (e["x"], e["y"])), e["typ"], ch(ort, (e["x"], e["y"]))) for e in feinde
              if e["typ"] in WAEHLBAR), default=None)
    arten, mit_linie = collections.Counter(), collections.Counter()
    if s is not None:
        for p, r, erh, steht, art in s.schuetzen:
            if (p[0] - ort[0]) ** 2 + (p[1] - ort[1]) ** 2 <= r * r:
                arten[art] += 1
                if erh or s.linie_frei(p, steht, ort):
                    mit_linie[art] += 1
    zu = s.feuer.get(n, []) if s is not None else []
    modell = s.beschuss(ort, nr=n) if s is not None else -1
    nah = sorted((ch(ort, (e["x"], e["y"])), NAHKAMPF[e["typ"]]) for e in feinde if e["typ"] in NAHKAMPF
                 and ch(ort, (e["x"], e["y"])) <= 2)
    loewe = [ch(ort, (e["x"], e["y"])) for e in L.values() if e["besitzer"] == 0 and e["typ"] == LOEWE
             and ch(ort, (e["x"], e["y"])) <= 4]
    fw = [ch(ort, (e["x"], e["y"])) for e in feinde if e["typ"] == 76 and ch(ort, (e["x"], e["y"])) <= 11]
    teile = ["Spaeher " + ("%s in %d Feldern (%d Feinmass, %s)" % (SPAEHER.get(sp[1], "Typ %d" % sp[1]), sp[2], sp[0],
                                                                    "sichtbar" if sp[0] <= SI.SICHT else "NICHT sichtbar")
                           if sp else "keiner"),
             "Schuetzen in Reichweite: " + (", ".join("%d %s (%d mit Linie)" % (k, a, mit_linie[a]) for a, k in arten.most_common())
                                           or "keine"),
             "Modell: %s (%.0f je Takt)" % (", ".join("%s in %.0f" % z for z in zu) or "niemand zielt auf ihn", modell)]
    if nah:
        teile.append("Nahkampf <= 2: %s" % ", ".join("%s in %d" % (b, a) for a, b in nah))
    if loewe:
        teile.append("Loewe in %d" % min(loewe))
    if fw:
        teile.append("Feuerwerfer in %d" % min(fw))
    return "; ".join(teile), {"sichtbar": bool(sp and sp[0] <= SI.SICHT), "spaeher": sp, "schuetzen": sum(mit_linie.values()),
                              "modell": modell, "nah": nah, "loewe": loewe, "fw": fw}


SPAEHER = {22: "Bogen", 23: "Armbrust", 24: "Speer", 25: "Pike", 26: "Streitkolben", 27: "Schwert", 28: "Ritter", 29: "Tunnelgraeber",
           30: "Leiter", 37: "Moench", 55: "Lord", 70: "arab. Bogen", 71: "Sklave", 72: "Schleuder", 73: "Assassine",
           74: "Pferdebogen", 75: "arab. Schwert", 76: "Feuerwerfer", 5: "Ingenieur"}


def auswerten(konsole, lage):
    mel = meldungen(konsole)
    verlauf = collections.defaultdict(list)       # nr -> [(t, ort, leben, zustand, lauf)] des jetzigen Lebens
    akte = {}                                     # nr -> erste Verletzung dieses Lebens
    tode = []
    vorher = None
    for t, st, E, G in LP.runden(lage):
        L = {d["nr"]: d for d in E}
        Gd = {g["nr"]: g for g in G}
        if vorher:
            tv, Lv, Gv = vorher
            for n, d in Lv.items():
                if d["besitzer"] == 1 and d["typ"] == 73:
                    neu = L.get(n)
                    if neu is None or neu["besitzer"] != 1 or neu["typ"] != 73:
                        tode.append((tv, t, n, d, Lv, Gv, list(verlauf.pop(n, [])), akte.pop(n, None)))
        for n, d in L.items():
            if d["besitzer"] == 1 and d["typ"] == 73:
                v = verlauf[n]
                if v and d["leben"] < v[-1][2] and n not in akte and vorher:
                    # erster Treffer dieses Lebens: Lage davor (wo er stand, als geschossen wurde) und danach
                    tv, Lv, Gv = vorher
                    o_v = v[-1][1]
                    text_v, w_v = lage_am(o_v, n, Lv, Gv)
                    text_n, w_n = lage_am((d["x"], d["y"]), n, L, Gd)
                    akte[n] = {"t": t, "tv": tv, "ort_v": o_v, "ort": (d["x"], d["y"]), "leben": (v[-1][2], d["leben"]),
                               "zustand": d["zustand"], "text_v": text_v, "text_n": text_n, "w_v": w_v, "w_n": w_n}
                elif v and d["leben"] >= 12500 and n in akte:
                    del akte[n]                   # wieder voll geheilt
                v.append((t, (d["x"], d["y"]), d["leben"], d["zustand"], (d["laufx"], d["laufy"])))
        vorher = (t, L, Gd)
    berichte = []
    for tv, t, n, d, Lv, Gv, leben_v, ak in tode:
        ort = (d["x"], d["y"])
        try:
            modell = SI.Lage(Lv, Gv, 1).beschuss(ort, nr=n)
        except Exception as fehler:
            modell = -1
            print('Modell-Fehler bei', n, repr(fehler)[:200])
        feinde = [e for e in Lv.values() if e["besitzer"] not in (0, 1)]
        fern = sorted((ch(ort, (e["x"], e["y"])), FERN[e["typ"]][0]) for e in feinde if e["typ"] in FERN
                      and ch(ort, (e["x"], e["y"])) <= FERN[e["typ"]][1])
        fw = [x for x in fern if x[1] == "Feuerwerfer"]
        nah = sorted((ch(ort, (e["x"], e["y"])), NAHKAMPF[e["typ"]]) for e in feinde if e["typ"] in NAHKAMPF and ch(ort, (e["x"], e["y"])) <= 3)
        loewe = [ch(ort, (e["x"], e["y"])) for e in Lv.values() if e["besitzer"] == 0 and e["typ"] == LOEWE and ch(ort, (e["x"], e["y"])) <= 4]
        sicht = min((ch(ort, (e["x"], e["y"])) for e in feinde if e["typ"] in WAEHLBAR), default=999)
        # 19.10.: ganzes Leben (Nummern werden neu vergeben - nur Meldungen seit Beginn DIESES Lebens)
        start = leben_v[0][0] if leben_v else 0
        if ak:
            v = [x for x in leben_v if x[0] >= ak["tv"]]
        else:
            v = leben_v[-2:]
        leben_vorher = v[0][2] if v else 12500
        dauer = (tv - v[0][0]) if len(v) > 1 else 0
        rate = (leben_vorher - d["leben"]) / dauer if dauer else 0
        eig = [x for x in mel.get(n, []) if start <= x[0] <= t]
        erst = reaktion = besser_erst = None
        if ak:
            erst = ("Tick %d -> %d: Leben %d -> %d. VORHER bei %s: %s. NACHHER bei %s: %s" % (
                ak["tv"], ak["t"], ak["leben"][0], ak["leben"][1], ak["ort_v"], ak["text_v"], ak["ort"], ak["text_n"]))
            reakt = [x for x in eig if ak["tv"] <= x[0] <= t and x[1].startswith((
                "FLUCHT", "AUSWEICHEN", "ROUTE GEFAEHRLICH", "ZIELWECHSEL", "ZIELWAHL", "BEUTE", "LORD", "WEG", "STILLSTAND"))]
            treffer = sum(1 for a, b in zip(v, v[1:]) if b[2] < a[2])
            reaktion = "%d Runden mit Treffern in %d Takten; Leben %s; Lenker: %s" % (
                treffer, tv - ak["tv"], " -> ".join(str(x[2]) for x in v[:12]) + (" ..." if len(v) > 12 else ""),
                " / ".join("%d: %s" % (a, b[:160]) for a, b in reakt[:6]) or "KEINE Reaktion (kein Rueckzug, kein Ausweichen)")
            w = ak["w_v"]
            if w["nah"]:
                besser_erst = "Nahkaempfer %s neben ihm - nicht neben Nahkaempfer laufen/stehen (Verfolger-Radius, L77)." % w["nah"][:2]
            elif w["loewe"]:
                besser_erst = "Loewe %d Felder daneben - Loewen weitraeumig meiden." % min(w["loewe"])
            elif w["sichtbar"] and w["schuetzen"]:
                besser_erst = ("Er stand in Sicht (%s) von %d Schuetzen mit Linie - Weg/Angriffsfeld muss mehr als 20 Felder von "
                               "jedem waehlbaren Feind bleiben." % (ak["text_v"].split("; ")[0], w["schuetzen"]))
                if w["modell"] <= 0:
                    besser_erst += " Das Modell sah dort 0 Beschuss - Modellfehler (Zuteilung)."
            elif w["schuetzen"]:
                besser_erst = ("Laut Sichtregel (L75) unsichtbar und trotzdem beschossen - die Regel erklaert diesen Treffer nicht "
                               "(klebrige Sicht aus den letzten 128 Takten? Spaeher auf Mauer/Turm?). Pruefen im Editor.")
            elif w["fw"]:
                besser_erst = "Feuerwerfer in %d Feldern - mehr als 11 Felder Abstand." % min(w["fw"])
            else:
                besser_erst = "Treffer ohne Schuetzen in Reichweite - Einzelfall ansehen."
            if not any(x[1].startswith(("FLUCHT", "AUSWEICHEN", "ROUTE GEFAEHRLICH")) for x in reakt):
                besser_erst += " Nach dem ersten Treffer haette er sofort aus Sicht und Reichweite muessen."
        letzte = [x for x in eig if not x[1].startswith(("MESSUNG", "STILLSTAND"))][-3:]
        zielwahl = [x for x in eig if x[1].startswith("ZIELWAHL")][-1:]
        risiko = None
        if zielwahl:
            m_r = re.search(r"Todesrisiko ([0-9]+) %, .*?Leben ([0-9]+)", zielwahl[0][1])
            if m_r:
                risiko = (int(m_r.group(1)), int(m_r.group(2)))
        lord = any("LORD" in x[1] for x in eig[-6:]) or any(abs(x[0] - tv) < 800 and str(n) in x[1] for x in mel.get(-1, []))
        taetig = {101: "lief", 106: "kaempfte (Einheit)", 107: "riss ein Gebaeude ab", 1: "stand", 105: "stand (Gruppe)"}.get(d["zustand"], "Zustand %d" % d["zustand"])
        stand = st_text = ""
        if lord:
            ursache = "Lord-Angriff"
            besser = ("Lord-Gruppe zu klein fuer das Feuer auf dem Anlauf - lord_machbar mit Anlauf (L87) haette sie erst ab genug "
                      "Leuten losgeschickt; sonst raiden.")
        elif loewe:
            ursache = "Loewe %d Felder daneben" % min(loewe)
            besser = "Loewen wie Nahkaempfer meiden (seit 18.10. im Lenker): Route/Ziel nicht neben Loewen, frueh ausweichen."
        elif nah and nah[0][0] <= 2:
            ursache = "Nahkampf gegen %s (%d Felder)" % (", ".join(sorted({x[1] for x in nah})), nah[0][0])
            besser = ("Nahkaempfer-Uebermacht frueher erkennen und ausweichen (Regel 4a); Ziele mit Wachen meiden; nicht stehen "
                      "bleiben, wo Trupps in Angriffshaltung bis 25 Felder verfolgen (L77).")
        elif fw:
            ursache = "Feuerwerfer %d Felder (Brand ~37 je Takt, L81)" % fw[0][0]
            besser = "Feuerwerfer haben 11 Felder Reichweite: Weg und Angriffsfeld mehr als 11 Felder von jedem Feuerwerfer."
        elif fern and sicht <= 20:
            arten = collections.Counter(x[1] for x in fern)
            ursache = "Beschuss: sichtbar (waehlbarer Feind %d Felder), %d Schuetzen in Reichweite (%s)" % (
                sicht, len(fern), ", ".join("%d %s" % (k, a) for a, k in arten.most_common()))
            besser = ("Angriffsfeld/Weg mehr als 20 Felder von jedem waehlbaren Feind (L83) - dann schiesst niemand; "
                      "wenn doch entdeckt: sofort raus, Erkennen -> Treffer dauert 64-170 Takte (L81).")
        elif fern:
            ursache = "Beschuss ohne sichtbaren Spaeher <= 20 (%d Schuetzen in Reichweite) - vermutlich noch sichtbar aus " \
                      "den letzten 128 Takten (L75)" % len(fern)
            besser = "Nach dem Entdecktwerden 128 Takte weg von allen Schuetzen bleiben, nicht nur aus der Sicht gehen."
        else:
            ursache = "unklar (keine Schuetzen in Reichweite, kein Nahkampf <= 2, kein Loewe)"
            besser = "Einzelfall ansehen (Bild/Lageprotokoll)."
        zusatz = []
        if risiko and risiko[0] >= 10:
            zusatz.append("Zielwahl nahm %d %% Todesrisiko in Kauf (Leben %d) - auch fuer unbeobachtete Ziele eine Risikogrenze "
                          "auf dem WEG (fehlte)" % risiko)
        if risiko and risiko[1] < 0.3 * 12500:
            zusatz.append("mit nur %d Leben weiter raiden - wer schwach ist, nur Ziele ohne jedes Wegrisiko oder zurueckziehen "
                          "(Regel SCHWACH wurde nicht angewendet)" % risiko[1])
        if modell == 0 and (fern or nah):
            zusatz.append("das Modell sah am Todesort 0 Beschuss - Gefahr nicht erkannt")
        if zusatz:
            besser = besser + " Zusaetzlich: " + "; ".join(zusatz) + "."
        berichte.append({"nr": n, "modell": modell, "tick": tv, "ort": ort, "taetig": taetig, "leben_vorher": leben_vorher, "dauer": dauer,
                         "rate": rate, "ursache": ursache, "besser": besser, "lenker": letzte, "sicht": sicht,
                         "fern": len(fern), "nah": nah[:3], "erst": erst, "reaktion": reaktion, "besser_erst": besser_erst})
    return berichte


def main():
    konsole, lage = sys.argv[1], sys.argv[2]
    aus = sys.argv[3] if len(sys.argv) > 3 else None
    b = auswerten(konsole, lage)
    zeilen = ["# Tote Assassinen - %s" % os.path.basename(konsole), "",
              "%d Tote. Ursachen: %s" % (len(b), ", ".join("%s %d" % kv for kv in collections.Counter(
                  x["ursache"].split(" ")[0].split(":")[0] for x in b).most_common())), ""]
    for x in b:
        zeilen.append("## Assassine %d - Tick %d bei %s" % (x["nr"], x["tick"], x["ort"]))
        zeilen.append("- **Tat zuletzt:** %s; Leben %d -> tot in %d Takten (%.0f je Takt)" % (x["taetig"], x["leben_vorher"], x["dauer"], x["rate"]))
        if x["erst"]:
            zeilen.append("- **Erster Treffer:** %s" % x["erst"])
            zeilen.append("- **Was beim ersten Treffer falsch war:** %s" % x["besser_erst"])
            zeilen.append("- **Danach:** %s" % x["reaktion"])
        else:
            zeilen.append("- **Erster Treffer:** keiner gemessen - in einer Runde von voll auf tot")
        zeilen.append("- **Lenker vorher:** %s" % (" / ".join("%d: %s" % m for m in x["lenker"]) or "keine Meldung"))
        zeilen.append("- **Ursache:** %s (Modell am Ort: %s je Takt)" % (x["ursache"], "%.1f" % x["modell"] if x["modell"] >= 0 else "-"))
        zeilen.append("- **Besser:** %s" % x["besser"])
        zeilen.append("")
    txt = "\n".join(zeilen)
    if aus:
        io.open(aus, "w", encoding="utf-8").write(txt)
        print("->", os.path.abspath(aus))
    print(txt[:6000])


if __name__ == "__main__":
    main()
