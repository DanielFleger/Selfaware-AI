# -*- coding: utf-8 -*-
"""Lernkreis (Daniel 06.10. 23:13: "das End-End-Ziel ... es geht darum, dass die KI selbst lernt, nicht wir fuer sie";
23:12: "es waere schoen, wenn solche Punkte dir auch auffallen wuerden nach jedem Run").

Die KI spielt, misst und entscheidet selbst, welcher Versuch als naechstes kommt:
  1. Strategie = Wert je Knopf (KNOEPFE). Erster Lauf: Grundstrategie; danach immer von der BESTEN bisherigen Strategie
     aus genau EIN Knopf anders - nie eine Kombination, die schon gespielt wurde (Daniel 21:59: keine gleichen Laeufe).
  2. Lauf: erstes_spiel.py bis zum Ziel (10 Streitkolbenkaempfer) oder bis_tick.
  3. Nachschau aus dem Lageprotokoll (jede Runde): Ticks mit vollem Wohnraum, mit >= 4 untaetigen Bauern, ohne Holz,
     mit liegendem Gold (>= 100) bei fehlendem Holz; erste Holz- und Steinlieferung; Abbruchgrund.
  4. Note (kleiner = besser): Tick des 10. Kaempfers; sonst bis_tick + fehlendes Gold / Zuwachs der letzten 2.000 Ticks
     (geschaetzte Restzeit, im Ergebnis als "geschaetzt" markiert); Fruehabbruch = 30.000.
  5. Wahl des naechsten Knopfs: Gewicht 1 fuer jeden Knopf, +3 fuer Knoepfe, die zum groessten Verlust der Nachschau
     passen (VERLUST_KNOEPFE); Wert des Knopfs zufaellig unter den noch nicht gespielten.
  6. Alles in daten/lernen.jsonl (je Lauf: Strategie, Note, Nachschau, Datei) und daten/lernen_wissen.json (je Knopfwert:
     beobachtete Notenaenderung gegen die Ausgangsstrategie).
Aufruf: python lernen.py laeufe=5 [bis_tick=14000] [start=grund|bester]
"""
import json
import os
import random
import re
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
sys.path.insert(0, HIER)

KNOEPFE = {
    "umzug": ["frueh", "nachb", "nein"],
    "holzfaeller_vorab": [0, 4, 8, 14],
    "holz_spam": [0, 10, 20, 30],
    "holzfaeller_je_baum": [1, 2, 4],
    "holzfaeller_max": [20, 30, 45, 70],
    "steinbruch_zuerst": ["ja", "nein"],
    "stein_parallel": ["ja", "nein"],
    "joch_nach_stein": ["ja", "nein"],
    "huetten_voraus": ["ja", "nein"],
    "holz_kaufen": ["ja", "nein"],
    "je_arbeiter": ["ja", "nein"],
    "vollbeschaeftigung": ["ja", "nein"],
    "entscheider": ["regeln", "kausal"],
    "b_versatz": ["reif", 0, 300, 600],
    "steuer_ende": ["nein", "ja"],   # "wohnraum" (Lauf 23) gestrichen: Hoechststeuer ab Tick 1.650 -> Beliebtheit 30, Arbeiter weg, Ziel verfehlt
    "kasse": ["nein", "steuer", "steuer_essen"],     # Daniel 07.10. 00:17/00:20
    "bevoelkerung_ziel": [70, 80, 90, 60, 50, 0],     # Reihenfolge = Testfolge (naechste nimmt den ersten ungespielten)
    "kasse_grenze": [0],   # Daniel 01:39: "Steuern nicht bei 20 oder irgendeiner Nummer halten" - Kasse immer -40 bis zum Ende
    "penner": [2, 20, 12],
    "abriss": ["ja", "nein"],      # Daniel 01:51: direkt anwerben statt abreissen
    "einzelkauf": ["nein", "ja"],   # fehlende Waffen einzeln (Daniel 01:35)
    "aufloesen": ["nein", "ja", "ende"],   # ja = nach Bedarf als Arbeiter, ende = als Rekruten im Endspiel (Daniel 01:44)   # Daniel 01:29: Start-Soldaten zu Bauern
    "schub": ["nein", "ja"],      # erste 5 Kaempfer waehrend der Kasse (07.10.)
    "kasse_stufe": [11],     # Daniel 01:04: nicht testen - gerechnet bringen 9/7 insgesamt nicht mehr Gold, nur langsamer     # Wachstums-Holzfaeller ab so vielen Wartenden (Daniel 00:54: Platz fuer Penner lassen)   # 0 = immer -40 ab Kasse-Start (Daniel 00:51: "erst gehen nur die im Pennergraben")     # Lauf 26: Beliebtheit 0 -> 50 auf 4 Leute, kein Kaempfer; Beliebtheit ist ein Vorrat
    "steuer_runter": [95, 90, 85, 80],
    "stein_max": ["nein", "ja"],
}
# Aufgabe s25 (Daniel 07.10. 23:34: 25 Streitkolbenkaempfer, "niemals unter 50 Beliebtheit", kuerzeste Zeit; Rat 23:50 in
# Plan_Streitkolben.md): eigene Ergebnisdatei, Ausgang = Lauf 69 mit Haushalt statt Kasse -40
S25 = {
    "datei": "lernen_s25.jsonl", "wissen": "lernen_s25_wissen.json", "ziel": 25, "bis_tick": 40000,
    "fest": ["leere_ki=ja", "minuten=60", "streitkolben=25", "weg=bilanz", "experiment=ja", "regel50=ja"],
    "knoepfe": {
        "kasse": ["haushalt"],
        "schub": ["nein"],
        "bevoelkerung_ziel": [70, 90, 110, 50],
        "gute_dinge": [0, 4, 8, 16],
        "haushalt_rand": [650, 400, 900],
        "wachstum_boden": [9500, 9000, 10000],
        "rationen": ["doppelt", "normal"],
        "nahrung_ausbau": ["ja", "nein", "kasse"],     # Lauf s25/1: Nahrung fehlte fuer doppelte Rationen
    },
    "grund": {"abriss": "nein", "aufloesen": "ende", "b_versatz": 600, "bevoelkerung_ziel": 70, "einzelkauf": "nein",
              "entscheider": "kausal", "holz_kaufen": "ja", "holz_spam": 20, "holzfaeller_je_baum": 4, "holzfaeller_max": 30,
              "holzfaeller_vorab": 4, "huetten_voraus": "nein", "je_arbeiter": "ja", "joch_nach_stein": "ja",
              "kasse": "haushalt", "kasse_grenze": 0, "kasse_stufe": 11, "penner": 20, "schub": "nein", "stein_max": "nein",
              "stein_parallel": "ja", "steinbruch_zuerst": "nein", "steuer_ende": "ja", "steuer_runter": 90, "umzug": "frueh",
              "v14": "ja", "vollbeschaeftigung": "ja",
              "gute_dinge": 0, "haushalt_rand": 650, "wachstum_boden": 9500, "rationen": "doppelt", "nahrung_ausbau": "nein"},
    "hinweise": ["nahrung_ausbau", "bevoelkerung_ziel", "gute_dinge", "haushalt_rand", "wachstum_boden", "rationen", "penner"],
}
ZIEL = 10
GRUND = {"v14": "ja", "umzug": "frueh", "holzfaeller_vorab": 4, "holz_spam": 20, "holzfaeller_je_baum": 4, "holzfaeller_max": 30,
         "steinbruch_zuerst": "nein", "stein_parallel": "ja", "joch_nach_stein": "ja", "huetten_voraus": "ja",
         "holz_kaufen": "ja", "je_arbeiter": "ja", "vollbeschaeftigung": "nein", "entscheider": "regeln", "b_versatz": "reif",
         "steuer_ende": "nein", "steuer_runter": 95, "stein_max": "nein",
         "kasse": "nein", "bevoelkerung_ziel": 0, "kasse_grenze": 50, "penner": 2, "kasse_stufe": 11, "schub": "nein", "aufloesen": "nein", "einzelkauf": "nein", "abriss": "ja"}
FEST = ["leere_ki=ja", "minuten=60", "streitkolben=10", "weg=bilanz", "experiment=ja"]
TEMPO = 100      # 07.10. 00:31: 1000 getestet (Daniel 00:27) - der Lenker braucht dann 1,2 s je Runde, alle 8 Laeufe brachen ab;
                 # das Tempo bestimmt, wie oft der Lenker hinsieht (bei 100 alle ~11 Ticks). Je Lauf gespeichert.
# 23:26 (Daniel: Ochse vor Steinbruch, Lager nicht umgezogen - in der v5-Bauweise galten die alten Regeln): EIN Weg.
# v14 ist fest; der Kreis aendert nur Werte, keine Bauweisen ("zwei Wege zum selben Ziel sind immer ein Fehler")
HINWEISE = ["aufloesen", "schub", "bevoelkerung_ziel", "penner", "kasse", "steuer_ende", "steuer_runter", "stein_max", "b_versatz"]   # 07.10.: Steuern, dritter Steinbruch     # Daniel 23:30: "Seasoning passiert immer noch zu spaet ... jede Wartezeit der Apfelbauern ist unproduktiv"
# welche Knoepfe zu welchem gemessenen Verlust gehoeren (Vorwissen; die Wirkung misst der Kreis selbst)
VERLUST_KNOEPFE = {
    "wohnraum_voll": ["entscheider", "huetten_voraus", "holz_kaufen"],
    "bauern_untaetig": ["entscheider", "vollbeschaeftigung", "holz_kaufen", "holz_spam", "holzfaeller_je_baum", "je_arbeiter"],
    "gold_liegt_holz_fehlt": ["holz_kaufen", "holz_spam"],
    "ohne_holz": ["holz_spam", "holzfaeller_vorab", "holzfaeller_je_baum", "holzfaeller_max", "umzug"],
    "apfel_warten": ["b_versatz"],
    "holz_liegt_bauern_warten": ["entscheider", "vollbeschaeftigung", "holzfaeller_je_baum"],
    "stein_spaet": ["steinbruch_zuerst", "stein_parallel", "joch_nach_stein", "umzug"],
}


def nachschau(lage):
    """Verluste und Marken aus dem Lageprotokoll (jede Runde)."""
    from lageprotokoll import runden
    m = {"wohnraum_voll": 0, "bauern_untaetig": 0, "ohne_holz": 0, "gold_liegt_holz_fehlt": 0,
         "erstes_holz_geliefert": None, "erster_stein": None, "ticks": 0, "apfel_warten": 0, "holz_liegt_bauern_warten": 0}
    vor, lad_vor = None, {}
    for t, st, E, G in runden(lage):
        if vor is not None:
            dt = t - vor
            m["ticks"] += dt
            if st.get("leute", 0) >= st.get("platz", 0):
                m["wohnraum_voll"] += dt
            if st.get("feuer", 0) >= 4:
                m["bauern_untaetig"] += dt
            if st.get("holz", 0) >= 5 and st.get("feuer", 0) >= 2:
                m["holz_liegt_bauern_warten"] += dt      # Widerspruch: Holz da UND Bauern untaetig (Daniel 23:41)
            if st.get("holz", 0) < 5:
                m["ohne_holz"] += dt
                if st.get("gold", 0) >= 100:
                    m["gold_liegt_holz_fehlt"] += dt
        if vor is not None:
            # Apfelbauer ohne reifen Baum = Zustand 1 (Wissensstand selectClosestTree); Bauer-Ticks, auf "je Bauer" umgerechnet
            bauern = [e for e in E if e["besitzer"] == 1 and e["typ"] == 13]
            if bauern:
                m["apfel_warten"] += (t - vor) * sum(1 for e in bauern if e["zustand"] == 1) / float(len(bauern))
        lad = {e["nr"]: e.get("ladung", 0) for e in E if e["besitzer"] == 1 and e["typ"] == 3}
        if m["erstes_holz_geliefert"] is None and any(lad_vor.get(n, 0) > l for n, l in lad.items()):
            m["erstes_holz_geliefert"] = t
        lad_vor = lad
        if m["erster_stein"] is None and st.get("stein", 0) > 0:
            m["erster_stein"] = t
        vor = t
    return m


def widersprueche(text):
    """Daniel 23:42: "das Problem ist eher, warum es nicht von dir gesehen wird". Allgemeiner Grundsatz statt Einzelfaelle:
    jede ausgegebene Ressource muss etwas bewirken. Zaehlt im Laufprotokoll: eigene Bauten, die binnen 1.000 Ticks wieder
    abgerissen werden; immer wieder scheiternde Befehle (ABGELEHNT/GESCHEITERT/"gesendet: None")."""
    gebaut = {}
    w = {"bau_wieder_abgerissen": 0, "fehlversuche": 0}
    for zeile in text.splitlines():
        t = re.match(r"\s*(\d+) \|", zeile)
        tick = int(t.group(1)) if t else None
        for nr in re.findall(r"BAU BESTAETIGT \S+ Nr (\d+)", zeile):
            gebaut[nr] = tick
        for nr in re.findall(r"BAU UNERREICHBAR \S+ Nr (\d+)", zeile):
            if tick is not None and gebaut.get(nr) is not None and tick - gebaut[nr] <= 1000:
                w["bau_wieder_abgerissen"] += 1
        w["fehlversuche"] += len(re.findall(r"BAU ABGELEHNT|BAU GESCHEITERT|gesendet: None", zeile))
    return w


def note_aus(text, bis_tick):
    r = re.search(r"KAEMPFER %d bei Tick (\d+)" % ZIEL, text) or re.search(r"ZIEL %d Streitkolbenkaempfer erreicht bei Tick (\d+)" % ZIEL, text)
    if r:
        return int(r.group(1)), "erreicht"
    rb = re.search(r"REGELBRUCH bei Tick (\d+): [^\n]*", text)
    if rb:
        # Aufgabe s25: ein gueltiger, aber verlorener Lauf - der Kreis soll daraus lernen (nicht "ungueltig")
        return 30000, "Regel verletzt: " + rb.group(0)
    if re.search(r"ABBRUCH - Testbedingung weg", text):
        # 07.10.: Lauf 24/27 - Spielansicht von aussen geaendert; Lauf 27 wurde hochgerechnet und galt als beste (8.562)
        return 30000, "ungueltig: Testbedingung weg (Spielansicht von aussen geaendert)"
    if re.search(r"FRUEHABBRUCH|ABBRUCH - Spiel angehalten|Traceback", text):
        return 30000, "abgebrochen"
    bil = [(int(t), int(h), int(b)) for t, h, b in re.findall(r"^\s*(\d+) \|.*BILANZ .*= (\d+) \| Bedarf (\d+)", text, re.M)]
    if not bil:
        return 30000, "keine Bilanz"
    t1, h1, b1 = bil[-1]
    if b1 - h1 <= 0:
        # Lauf 26: Gold reichte, aber nur noch 4 Leute (Beliebtheit 0) - keine Kaempfer; hochrechnen waere Unsinn
        return 30000, "nicht erreicht (Gold reicht bei Tick %d, Ziel trotzdem verfehlt)" % t1
    frueh = [x for x in bil if x[0] <= t1 - 2000] or bil[:1]
    t0, h0, _ = frueh[-1]
    rate = max(1.0, (h1 - h0) * 1000.0 / max(1, t1 - t0))
    return int(t1 + 1000.0 * max(0, b1 - h1) / rate), "geschaetzt (fehlt %d, Zuwachs %.0f je 1.000)" % (b1 - h1, rate)


def lauf(strategie, bis_tick, nr, horizont=None):
    stempel = time.strftime("%Y%m%d_%H%M%S")
    aus = os.path.join(D, "lernen_lauf_%s_%d.txt" % (stempel, nr))
    args = [sys.executable, os.path.join(HIER, "erstes_spiel.py")] + FEST + ["tempo=%d" % TEMPO, "bis_tick=%d" % bis_tick] + \
        ["%s=%s" % kv for kv in sorted(strategie.items())] + (["ziel_tick=%d" % horizont] if horizont else [])
    env = dict(os.environ, SHC_INSTANZ="1")
    with open(aus, "w", encoding="utf-8") as f:
        subprocess.run(args, stdout=f, stderr=subprocess.STDOUT, env=env, cwd=HIER, timeout=3600)
    text = open(aus, encoding="utf-8", errors="replace").read()
    note, art = note_aus(text, bis_tick)
    lp = re.search(r"Lageprotokoll \(jede Runde komplett\): (.+?\.jsonl\.gz)", text)   # Pfad hat Leerzeichen (Lauf 1: Nachschau leer)
    ns = nachschau(lp.group(1)) if lp and os.path.exists(lp.group(1)) else {}
    ns.update(widersprueche(text))
    abbruch = re.search(r"FRUEHABBRUCH bei Tick \d+: [^\n]*", text)
    return {"nr": nr, "zeit": stempel, "strategie": strategie, "note": note, "art": art, "nachschau": ns,
            "abbruch": abbruch.group(0) if abbruch else None, "datei": os.path.basename(aus)}


def schluessel(s):
    # fehlende Knoepfe (aeltere Laeufe kannten sie nicht) zaehlen mit ihrem Grundwert - sonst haelt der Kreis eine schon
    # gespielte Strategie fuer neu (23:21: Lauf 3 wiederholte Lauf 2, weil "vollbeschaeftigung" fehlte)
    return json.dumps(dict(GRUND, **s), sort_keys=True)


def naechste(beste, gespielt, ns):
    """23:24: nicht wuerfeln. Die Verluste der besten Strategie der Groesse nach; je Verlust seine Knoepfe in Rangfolge;
    der erste Knopf mit einem noch nicht gespielten Wert gewinnt (logische Konsequenz aus der Nachschau). Erst wenn alle
    passenden Knoepfe durch sind, zufaellig."""
    beste = dict(GRUND, **beste)            # aeltere Laeufe kennen neue Knoepfe nicht -> Grundwert
    # Hinweise von Daniel zuerst (Vorwissen eines Experten): Knopf, auf den er gezeigt hat, vor der eigenen Rangfolge
    for k in HINWEISE:
        for w in KNOEPFE[k]:
            if w != beste[k]:
                s = dict(beste, **{k: w})
                if schluessel(s) not in gespielt:
                    return s, k
    if ns:
        anteil = {v: ns.get(v, 0) / float(max(1, ns.get("ticks", 1))) for v in VERLUST_KNOEPFE}
        for verlust in sorted(anteil, key=anteil.get, reverse=True):
            if anteil[verlust] <= 0.1:
                break
            for k in VERLUST_KNOEPFE[verlust]:
                for w in KNOEPFE[k]:
                    if w != beste[k]:
                        s = dict(beste, **{k: w})
                        if schluessel(s) not in gespielt:
                            return s, k
    gewicht = {k: 1.0 for k in KNOEPFE}
    for _ in range(200):
        k = random.choices(list(gewicht), weights=list(gewicht.values()))[0]
        werte = [w for w in KNOEPFE[k] if w != beste[k]]
        random.shuffle(werte)
        for w in werte:
            s = dict(beste, **{k: w})
            if schluessel(s) not in gespielt:
                return s, k
    return None, None


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    global TEMPO, KNOEPFE, GRUND, FEST, HINWEISE, ZIEL
    datei, wissen_datei = "lernen.jsonl", "lernen_wissen.json"
    if arg.get("aufgabe") == "s25":
        KNOEPFE = dict(KNOEPFE)
        for k, werte in S25["knoepfe"].items():
            KNOEPFE[k] = werte
        GRUND, FEST, HINWEISE, ZIEL = dict(S25["grund"]), list(S25["fest"]), list(S25["hinweise"]), S25["ziel"]
        datei, wissen_datei = S25["datei"], S25["wissen"]
        arg.setdefault("bis_tick", str(S25["bis_tick"]))
    laeufe, bis_tick = int(arg.get("laeufe", 5)), int(arg.get("bis_tick", 14000))
    TEMPO = int(arg.get("tempo", TEMPO))
    pfad = os.path.join(D, datei)
    alle = [json.loads(z) for z in open(pfad, encoding="utf-8")] if os.path.exists(pfad) else []
    for r in alle:
        r["strategie"] = dict(GRUND, **r["strategie"])     # aeltere Laeufe: neue Knoepfe mit Grundwert (KeyError 23:21)
    alle_roh = alle
    alle = [r for r in alle if not r.get("ungueltig")]       # Fehler im Lenker - daraus wird nichts gelernt
    gespielt = {schluessel(r["strategie"]) for r in alle}
    gueltig = [r for r in alle if r["strategie"].get("v14", "ja") == "ja"]     # nur Laeufe auf dem einen Weg zaehlen
    # 07.10.: der letzte Kontrolllauf setzt den Massstab - aeltere Laeufe liefen mit anderem Code (Lauf 11 alt 10.543,
    # dieselbe Strategie im Kontrolllauf 18 mit neuem Code 11.502). Neustart ohne kontrolle=ja vergleicht ab dort.
    k_idx = [i for i, r in enumerate(gueltig) if r.get("geaendert") == "kontrolle"]
    if k_idx:
        # 07.10. 01:20: auch der Kontrolllauf nimmt die beste Strategie seit dem letzten Massstab - vorher die beste aller
        # Zeiten (Lauf 38, 9.395, Gluecksfall mit altem Code) statt Lauf 54 (9.796); Kontrolle 56 lief so mit Grenze 50
        gueltig = gueltig[k_idx[-1]:]
    beste = min(gueltig, key=lambda r: r["note"]) if gueltig else None
    kontrolle = arg.get("kontrolle") == "ja"
    # 07.10.: Nummer aus ALLEN Laeufen (vorher len(alle) ohne ungueltige -> 8 bis 11 doppelt vergeben)
    nr_neu = max([x.get("nr", 0) for x in alle_roh] + [0]) + 1
    for i in range(laeufe):
        if kontrolle and beste is not None:
            # Code hat sich seit der Bestzeit geaendert -> beste Strategie einmal neu messen (keine Wiederholung im Sinne
            # gleicher Laeufe: anderer Code), danach wird gegen diesen Kontrolllauf verglichen
            s, knopf, kontrolle = dict(beste["strategie"]), "kontrolle", False
            # setze=knopf:wert,... (Daniel 00:34 "Lauf mit 60-70 Bevoelkerung so schnell wie moeglich"): der Kontrolllauf
            # nimmt diese Werte gleich mit und wird damit der neue Massstab
            for kv in filter(None, arg.get("setze", "").split(",")):
                k_s, w_s = kv.split(":", 1)
                s[k_s] = type(KNOEPFE[k_s][-1])(w_s) if not isinstance(KNOEPFE[k_s][-1], str) else w_s
            horizont = beste["note"]
            beste = None
        elif beste is None:
            s, knopf = dict(GRUND), None
        else:
            s, knopf = naechste(beste["strategie"], gespielt, beste.get("nachschau"))
            if s is None:
                print("Alle Nachbarn der besten Strategie gespielt - Ende", flush=True)
                break
        print("LERNEN Lauf %d: %s%s" % (nr_neu, "Grundstrategie" if knopf is None else "Kontrolllauf der besten Strategie mit neuem Code"
              if knopf == "kontrolle" else "%s = %s (statt %s)" % (knopf, s[knopf], beste["strategie"][knopf]),
              "" if beste is None else ", beste Note bisher %d" % beste["note"]), flush=True)
        if knopf != "kontrolle":
            horizont = beste["note"] if beste else None
        # 07.10.: Rechenzeitraum des Kausalmodells = gemessenes Ende der besten Strategie, nicht das Wunschziel 9.400
        # (Lauf 18: Holzfaeller ab ~6.000 liefern erst nach 9.400 -> "Holz ueberfluessig", das Spiel lief aber bis 11.502)
        if horizont and horizont >= 30000:
            horizont = None                      # abgebrochen - kein gemessenes Ende
        r = lauf(s, bis_tick, nr_neu, horizont)
        r["horizont"] = horizont
        r["tempo"] = TEMPO
        nr_neu += 1
        r["geaendert"] = knopf
        r["vergleich"] = None if beste is None else {"gegen": beste["nr"], "note_vorher": beste["note"], "differenz": r["note"] - beste["note"]}
        if r["art"].startswith("ungueltig"):
            r["ungueltig"] = r["art"]                # von aussen gestoert - daraus wird nichts gelernt, darf wieder gespielt werden
        else:
            alle.append(r)
            gespielt.add(schluessel(s))
        alle_roh.append(r)
        with open(pfad, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("LERNEN Ergebnis Lauf %d: Note %d (%s)%s | Nachschau %s" % (
            r["nr"], r["note"], r["art"], "" if r["vergleich"] is None else ", %+d gegen Lauf %d" % (r["vergleich"]["differenz"], beste["nr"]),
            {k: v for k, v in r["nachschau"].items() if v}), flush=True)
        ns_r = r.get("nachschau", {})
        w_r = []
        if ns_r.get("bau_wieder_abgerissen"):
            w_r.append("%d eigene Bauten binnen 1.000 Ticks wieder abgerissen" % ns_r["bau_wieder_abgerissen"])
        if ns_r.get("fehlversuche", 0) > 20:
            w_r.append("%d gescheiterte/abgelehnte Befehle (Schleife?)" % ns_r["fehlversuche"])
        if ns_r.get("holz_liegt_bauern_warten", 0) > 0.1 * max(1, ns_r.get("ticks", 1)):
            w_r.append("Holz lag %d Ticks, waehrend >= 2 Bauern warteten" % ns_r["holz_liegt_bauern_warten"])
        if w_r:
            print("LERNEN WIDERSPRUCH Lauf %d: %s" % (r["nr"], "; ".join(w_r)), flush=True)
        if not r.get("ungueltig") and (beste is None or r["note"] < beste["note"]):
            beste = r
            print("LERNEN neue beste Strategie (Lauf %d)" % r["nr"], flush=True)
        # Wissen: je Knopfwert die beobachteten Differenzen
        wissen = {}
        for x in alle:
            if x.get("geaendert") and x.get("geaendert") != "kontrolle" and x.get("vergleich"):
                k = "%s=%s" % (x["geaendert"], x["strategie"][x["geaendert"]])
                wissen.setdefault(k, []).append(x["vergleich"]["differenz"])
        json.dump({"beste": beste, "wirkung_je_knopfwert": wissen}, open(os.path.join(D, wissen_datei), "w", encoding="utf-8"),
                  indent=1, ensure_ascii=False)
    print("LERNEN fertig: beste Note %s (Lauf %s, %s)" % (beste["note"], beste["nr"], beste["strategie"]), flush=True)


if __name__ == "__main__":
    main()
