# -*- coding: utf-8 -*-
"""Gefechtsbewertung: lohnt sich ein Gegenangriff? (Daniel 19.10.2026, Partie 1019b: "die lassen sich einfach angreifen ohne
Grund und koennen noch nicht evaluieren, wann ein Counter sich lohnt - jede Sekunde Zoegerung bei so einer Entscheidung
kostet wertvolle Leben"; "die Staerkewerte je Einheit vorher im Editor messen").

Grundlage: Duelle im Karteneditor (editor_messen.py duell, daten/editor_duell_*.jsonl) - je Paar Einheitenart X gegen Y:
Schaden je Takt, den X an Y macht, solange beide kaempfen (Nahkampf auf Beruehrung, Schuetzen schiessen aus Reichweite),
volles Leben je Art. Daraus SCHADEN[x][y] (beide Richtungen jedes Duells, Mittel ueber Wiederholungen).

simuliere(): Gefecht in Schritten von SCHRITT Takten - jede Einheit nimmt das naechste lebende Ziel der Gegenseite,
Nahkaempfer laufen hin (TEMPO Takte je Feld) und schlagen auf Beruehrung (<= 1 Feld), Schuetzen schiessen bis zu ihrer
Reichweite (sicht.REICHWEITE) und laufen sonst naeher; der Schaden einer Einheit geht ganz an ihr Ziel. Feindliche
Schuetzen, die nicht zur angreifenden Gruppe gehoeren, aber in Reichweite des Kampfplatzes stehen, schiessen mit (sie
laufen nicht). Ende: eine Seite tot oder BIS Takte.

bewerte(): Angriff lohnt, wenn die feindliche Gruppe faellt und von unserem eingesetzten Leben mindestens BEHALTEN bleibt.
Alles Weitere entscheidet der Waechter (waechter.py).
"""
import glob
import io
import json
import math
import os

HIER = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HIER, "..", "daten")
FERN_REICH = {22: 44, 23: 44, 70: 44, 74: 44, 72: 17, 76: 11}
SCHRITT = 10              # Takte je Simulationsschritt
TEMPO = 15.0              # Takte je Feld (L68: 16 fuer die meisten, Assassine 14,6 - L80)
BIS = 1500                # laengstens so viele Takte rechnen
BEHALTEN = 0.4            # Anteil unseres eingesetzten Lebens, der nach dem Sieg mindestens bleiben muss (Stellgroesse)
LORD = 55
LORD_LEBEN = 150000       # 1018o: "Lord 26 mit 149750 Leben" (voll; Mitschrift LORD EINDEUTIG)
LORD_PROBEN = 5           # Lord-Werte aus Partien erst ab so vielen Proben (lord_messen.py)
# Lauftempo, Takte je Feld (L80, Median aus 11 Mitschriften, 17.10.); fehlt eine Art, ist ihr Tempo unbekannt (None)
TEMPO_ART = {22: 11.5, 71: 12.0, 70: 12.2, 24: 13.5, 73: 14.6, 72: 15.0, 55: 19.0, 75: 19.5, 23: 21.0, 76: 21.5,
             25: 24.0}

_TABELLE = None


def raten(r):
    """19.10. (Auswertung der ersten Duell-Reihe): Schaden je Takt beider Richtungen aus der Zeitreihe eines Duells.
    - Wer nie getroffen hat, liefert KEINEN Wert (None): der Gegenbefehl an Spieler 2 wird quittiert, wirkt aber nicht - ein
      feindlicher Nahkaempfer, den unser Schuetze aus 3 Feldern beschiesst, bleibt stehen (sonst 0 statt seines Schadens).
    - Endet der Schaden binnen 30 Takten nach dem ersten Treffer (ein Pfeil toetet den Sklaven), zaehlt die Zeit ab
      Kampfbeginn (Zielen gehoert dazu) - sonst Teilen durch ~0 Takte (6.000 je Takt)."""
    reihe = r["reihe"]
    ende = reihe[-1][0]
    abst = [z[3] for z in reihe if z[3] is not None]
    # aus der Ferne = die beiden kamen sich nie naeher als beim Setzen (3 Felder); sonst Nahkampf
    aus = {"fern": bool(abst) and min(abst) >= 3}
    for name, i, voll in (("a_an_d", 2, r.get("leben_d")), ("d_an_a", 1, r.get("leben_a"))):
        erst = next((z[0] for z in reihe if voll and z[i] < voll), None)
        if erst is None:
            aus[name] = None
            continue
        verlust = voll - reihe[-1][i]
        dauer = ende - erst if ende - erst >= 30 else ende
        aus[name] = verlust / float(max(1, dauer))
    return aus


def tabelle(dateien=None):
    """(SCHADEN {x: {y: je Takt}}, LEBEN {x: voll}, FERN {x: {y: je Takt}}) fuer die Gefechtsrechnung.
    B-273 (Daniel 27.10. 20:15 "verknuepfe das mit den Augenwerten, egal welche Balance"): stehen Spielwerte aus dem
    laufenden Spiel bereit (spielwerte_einlesen, Balance-Gegenprobe balance_pruefen), kommt ALLES aus ihnen - jede Art gegen
    jede Art, Nahkampf und Geschosse (kaufrechnung.schadenstabelle). Sonst (oder mit dateien) die alten Duell-Messungen."""
    global _TABELLE
    if dateien is None and SPIELWERTE is not None:
        if _TABELLE is None:
            _TABELLE = _aus_spielwerten(SPIELWERTE)
        return _TABELLE
    return tabelle_duelle(dateien)


# B-273: Schadenswerte aus dem Spiel (Auge, spielwerte.py) - je Partie frisch gelesen; die Duelle nur noch zur Gegenprobe
SPIELWERTE = None          # dict wie kaufrechnung.spielwerte_laden, gesetzt von spielwerte_einlesen
QUELLE = "Duell-Messungen (keine Spielwerte geladen)"
VERWORFEN = None           # Grund, wenn die Balance-Gegenprobe die Spielwerte verworfen hat
_DUELLE = None
_HOECHST = {}              # typ -> hoechstes beobachtetes Leben (Balance-Gegenprobe)


def _aus_spielwerten(sw):
    """(SCHADEN, LEBEN, FERN) aus den Spielwerten. Arten, die nicht schlagen koennen (melee_damage 0), bekommen 0 statt des
    Zeilenmittels - sonst raechnete dps() fuer sie einen erfundenen Wert."""
    import kaufrechnung as KR
    schaden, fern, leben, _kalib = KR.schadenstabelle(sw, duelle=tabelle_duelle())
    md = sw["tabellen"]["einheit.melee_damage"]["werte"]
    for a, zeile in schaden.items():
        for z in leben:
            if z not in zeile and a < len(md) and z < len(md[a]):
                zeile[z] = float(md[a][z])
    return schaden, leben, fern


def spielwerte_einlesen():
    """Spielwerte aus dem laufenden Spiel lesen (spielwerte.py, Speicher) und als daten/spielwerte_<stempel>.json sichern;
    geht das nicht, die juengste gesicherte live-Datei (dann prueft balance_pruefen, ob sie zur laufenden Balance passt).
    Gibt eine Meldung zurueck."""
    global SPIELWERTE, QUELLE, _TABELLE, VERWORFEN
    import time
    try:
        import spielwerte as SW
        q, lies = SW.quelle_live()
        w = SW.lesen(lies)
        sch = SW.schuss(lies)
        w.update(SW.abgeleitet(w, sch, SW.hacken(lies)))
        sw = {"erstellt": time.strftime("%Y-%m-%d %H:%M:%S"), "quelle": q, "tabellen": w, "schuss": sch,
              "aufzaehlungen": {"UT": {str(k): v for k, v in SW.UT.items()}}}
        pfad = os.path.join(D, time.strftime("spielwerte_%Y%m%d_%H%M%S.json"))
        json.dump(sw, io.open(pfad, "w", encoding="utf-8"), ensure_ascii=False)
        sw["_pfad"] = pfad
        QUELLE = "live aus dem laufenden Spiel (%s)" % os.path.basename(pfad)
    except Exception as ex:
        import kaufrechnung as KR
        sw = KR.spielwerte_laden()
        if sw is None:
            return "SPIELWERTE: nicht lesbar (%s) und keine Datei - Gefechtsrechnung mit Duell-Messungen" % ex
        QUELLE = "Datei %s (live nicht lesbar: %s)" % (os.path.basename(sw.get("_pfad", "?")), ex)
    SPIELWERTE, _TABELLE, VERWORFEN = sw, None, None
    _HOECHST.clear()
    return "SPIELWERTE: Gefechtsrechnung aus %s" % QUELLE


def balance_pruefen(L):
    """Gegenprobe gegen das Sichtbare: hat eine Einheit mehr Leben, als die Spielwerte als volles Leben nennen, gehoeren die
    Werte zu einer anderen Balance - dann verwerfen (Duell-Messungen). Der Lord ist ausgenommen: sein Leben haengt am
    einzelnen Lord (Daniel 27.10. 20:16; Feld maxHealthRatingLord, gemessen 300.000 beim Gegner gegen 150.000 bei uns in
    derselben Partie), nicht an der Balance - die Rechnung nimmt sein Leben aus dem Lagebild. Meldung nur beim Verwerfen."""
    global SPIELWERTE, _TABELLE, VERWORFEN
    if SPIELWERTE is None:
        return None
    hp = SPIELWERTE["tabellen"]["einheit.base_hp"]["werte"]
    for e in L.values():
        t = e.get("typ", -1)
        if t == LORD or not 0 <= t < len(hp) or hp[t] <= 0:
            continue
        _HOECHST[t] = max(_HOECHST.get(t, 0), e.get("leben", 0))
        if _HOECHST[t] > hp[t]:
            VERWORFEN = "Art %d mit %d Leben, Spielwerte nennen %d als volles Leben (%s)" % (t, _HOECHST[t], hp[t], QUELLE)
            SPIELWERTE, _TABELLE = None, None
            return "SPIELWERTE VERWORFEN: %s - Gefechtsrechnung mit Duell-Messungen" % VERWORFEN
    return None


def tabelle_duelle(dateien=None):
    """(SCHADEN {x: {y: je Takt}}, LEBEN {x: voll}, FERN {x: {y: je Takt}}) aus allen Duell-Messungen. 19.10.: Schuetzen
    machen aus der Ferne mehr Schaden als im Nahkampf (Bogen gegen Speer ~24 statt ~10) - FERN haelt die Werte der
    Duelle, in denen sie aus 3 Feldern schossen, SCHADEN die aus dem Nahkampf (fuer Nahkaempfer nur SCHADEN)."""
    global _DUELLE
    if _DUELLE is not None and dateien is None:
        return _DUELLE
    dateien = dateien or sorted(glob.glob(os.path.join(D, "editor_duell_*.jsonl")))
    summen, leben, fsum = {}, {}, {}
    for f in dateien:
        for z in io.open(f, encoding="utf-8"):
            r = json.loads(z)
            a, d = r["a_typ"], r["d_typ"]
            if r.get("leben_a"):
                leben[a] = max(leben.get(a, 0), r["leben_a"])
            if r.get("leben_d"):
                leben[d] = max(leben.get(d, 0), r["leben_d"])
            rt = raten(r) if r.get("reihe") else {"a_an_d": r["schaden_a_an_d_je_takt"], "d_an_a": r["schaden_d_an_a_je_takt"]}
            for x, y, w in ((a, d, rt["a_an_d"]), (d, a, rt["d_an_a"])):
                if w is None:
                    continue
                ziel = fsum if (rt.get("fern") and x in FERN_REICH) else summen
                s = ziel.setdefault(x, {}).setdefault(y, [0.0, 0])
                s[0] += w
                s[1] += 1
    schaden = {x: {y: s / n for y, (s, n) in ys.items()} for x, ys in summen.items()}
    fern = {x: {y: s / n for y, (s, n) in ys.items()} for x, ys in fsum.items()}
    # 19.10. 18:15: der Lord fehlt in den Editor-Duellen - seine Werte kommen aus echten Partien (lord_messen.py,
    # daten/lord_kampfwerte.json); vorher Ersatzwert 20 je Takt -> die Lordwache hielt 2 Assassinen fuer toedlich (1018o)
    lw = os.path.join(D, "lord_kampfwerte.json")
    if os.path.exists(lw):
        k = json.load(io.open(lw, encoding="utf-8"))
        for y, v in k.get("lord_an", {}).items():
            if v["proben"] >= LORD_PROBEN:
                schaden.setdefault(LORD, {})[int(y)] = v["je_takt"]
        for x, v in k.get("an_lord", {}).items():
            if v["proben"] >= LORD_PROBEN:
                schaden.setdefault(int(x), {})[LORD] = v["je_takt"]
        # 18:45: Arten ohne reine Probe aus gemischten Gruppen (kleinste Quadrate, lord_messen.gemischt)
        for x, v in k.get("an_lord_gemischt", {}).items():
            if LORD not in schaden.get(int(x), {}) and v["proben"] >= LORD_PROBEN and v["je_takt"] > 0:
                schaden.setdefault(int(x), {})[LORD] = v["je_takt"]
        leben.setdefault(LORD, LORD_LEBEN)
    # B-207 (22.10.): Nahkaempfer am Lord im Sandkasten gemessen (lord_nahkampf_messen.py, daten/lord_nahkampf.jsonl) - Median
    # je Art ab LORD_PROBEN Messungen; ersetzt den Ersatzwert (Mittel der Zeile)
    ln = os.path.join(D, "lord_nahkampf.jsonl")
    if os.path.exists(ln):
        je = {}
        for z in open(ln, encoding="utf-8"):
            try:
                r = json.loads(z)
            except ValueError:
                continue
            if r.get("je_takt"):
                je.setdefault(int(r["typ"]), []).append(r["je_takt"])
        for x, werte in je.items():
            if len(werte) >= LORD_PROBEN:
                schaden.setdefault(x, {})[LORD] = sorted(werte)[len(werte) // 2]
    _DUELLE = (schaden, leben, fern)
    return _DUELLE


def gemessen(x, y, d=1):
    """19.10.: ist der Schaden von Art x an Art y gemessen (Duell oder Partie) - oder nur Ersatz (Mittel/20)?"""
    tb = tabelle()
    if d > 1 and len(tb) > 2 and y in tb[2].get(x, {}):
        return True
    return y in tb[0].get(x, {})


def dps(x, y, schaden, fern=None, d=1):
    """Schaden je Takt von Art x an Art y; Schuetzen ueber 1 Feld aus der Fern-Tabelle (wenn gemessen); fehlt das Paar,
    Mittel von x ueber alle gemessenen Ziele, sonst 20."""
    if fern and d > 1 and fern.get(x):
        zeile = fern[x]
        return zeile[y] if y in zeile else sum(zeile.values()) / len(zeile)
    zeile = schaden.get(x)
    if not zeile:
        return 20.0
    if y in zeile:
        return zeile[y]
    return sum(zeile.values()) / len(zeile)


ABLENK_R = 2              # B-273: Nahkampf-Suchfeld des Spiels (Auge AU18: 5x5 um die Einheit) - wer dort einen anderen Feind hat
                          # und nicht am Lord steht, schlaegt erst diesen (gemessen 27.10.: 18 von ~30 am Lord schlugen andere)


def simuliere(wir, sie, schaden=None, bis=BIS, rest_aus=None, fokus=None, fern=None, protokoll=None):
    """wir/sie: Listen von dict(typ, leben, x, y, steht=False). Gibt (wir_leben_rest, sie_leben_rest, takte, sieg) -
    sieg = True, wenn alle von "sie" tot sind und von "wir" noch jemand lebt.
    protokoll (Liste): B-273 - Ereignisse (takt, art, seite, typ, nah): "kampf" (erste Beruehrung unserer mit einer
    Feindeinheit; nah = Nahkampf), "beschuss" (erster Schaden einer feindlichen Art an uns), "tot", "lord_faellt"."""
    if schaden is None:
        tb = tabelle()
        schaden, fern = tb[0], (tb[2] if len(tb) > 2 else None)      # B-241: fern kommt sonst vom Aufrufer (kaufrechnung)
    seiten = [[dict(e) for e in wir], [dict(e) for e in sie]]
    for s in seiten:
        for e in s:
            e["x"], e["y"] = float(e["x"]), float(e["y"])
    t = 0
    beruehrt, beschiesst = set(), set()
    while t < bis:
        lebend = [[e for e in s if e["leben"] > 0] for s in seiten]
        if not lebend[0] or not lebend[1]:
            break
        treffer = [{}, {}]
        for i in (0, 1):
            gegner = lebend[1 - i]
            # B-207 Lord-Wettlauf: fokus = Index in "sie" - solange er lebt, schlagen alle von "wir" nur auf ihn
            f_ziel = seiten[1][fokus] if (fokus is not None and i == 0 and seiten[1][fokus]["leben"] > 0) else None
            for e in lebend[i]:
                naechst = min(gegner, key=lambda g: max(abs(g["x"] - e["x"]), abs(g["y"] - e["y"])))
                z = f_ziel or naechst
                reich = FERN_REICH.get(e["typ"], 1)
                # B-273 Ablenkung: ein Nahkaempfer ausserhalb ABLENK_R vom Lord mit einem anderen Feind in ABLENK_R schlaegt diesen
                if f_ziel is not None and reich == 1 and naechst is not f_ziel:
                    d_n = max(abs(naechst["x"] - e["x"]), abs(naechst["y"] - e["y"]))
                    if d_n <= ABLENK_R and max(abs(f_ziel["x"] - e["x"]), abs(f_ziel["y"] - e["y"])) > ABLENK_R:
                        z = naechst
                d = max(abs(z["x"] - e["x"]), abs(z["y"] - e["y"]))
                if d <= reich:
                    treffer[1 - i][id(z)] = treffer[1 - i].get(id(z), 0.0) + dps(e["typ"], z["typ"], schaden, fern, d) * SCHRITT
                    if protokoll is not None and i == 0 and (id(z), reich == 1) not in beruehrt:
                        beruehrt.add((id(z), reich == 1))
                        protokoll.append((t, "kampf", "sie", z["typ"], reich == 1))
                    elif protokoll is not None and i == 1 and e["typ"] not in beschiesst:
                        beschiesst.add(e["typ"])
                        protokoll.append((t, "beschuss", "sie", e["typ"], reich == 1))
                elif not e.get("steht"):
                    schritt = min(d - reich, SCHRITT / TEMPO)
                    e["x"] += (z["x"] - e["x"]) / d * schritt
                    e["y"] += (z["y"] - e["y"]) / d * schritt
        for i in (0, 1):
            for e in lebend[i]:
                e["leben"] -= treffer[i].get(id(e), 0.0)
                if protokoll is not None and e["leben"] <= 0:
                    protokoll.append((t + SCHRITT, "tot", "wir" if i == 0 else "sie", e["typ"], None))
        t += SCHRITT
        if fokus is not None and seiten[1][fokus]["leben"] <= 0:
            if protokoll is not None:
                protokoll.append((t, "lord_faellt", "sie", LORD, None))
            break
    rest = [sum(max(0.0, e["leben"]) for e in s) for s in seiten]
    if fokus is not None:
        return rest[0], max(0.0, seiten[1][fokus]["leben"]), t, seiten[1][fokus]["leben"] <= 0 and rest[0] > 0
    if rest_aus is not None:                 # 19.10.: Rest je Einheit von "wir" (lebt der Lord?) - zuweisung.py
        rest_aus.extend(max(0.0, e["leben"]) for e in seiten[0])
    return rest[0], rest[1], t, rest[1] <= 0 and rest[0] > 0


def bewerte(wir, sie, schaden=None, bis=BIS):
    """(lohnt, Text): Gegenangriff lohnt, wenn die Gruppe faellt und mindestens BEHALTEN unseres Lebens bleibt.
    bis: Rechengrenze in Takten (B-140: grosse Schlachten brauchen laenger als BIS - sonst "offen")."""
    if not wir or not sie:
        return False, "keine Gegner" if wir else "keine Verteidiger"
    voll = sum(e["leben"] for e in wir)
    r_wir, r_sie, t, sieg = simuliere(wir, sie, schaden, bis=bis)
    anteil = r_wir / float(max(1, voll))
    lohnt = sieg and anteil >= BEHALTEN
    return lohnt, "%d eigene (%d Leben) gegen %d (%d Leben): %s nach %d Takten, uns bleiben %.0f %%" % (
        len(wir), voll, len(sie), sum(e["leben"] for e in sie), "Sieg" if sieg else "Niederlage" if r_wir <= 0 else "offen",
        t, 100 * anteil)


LETZTES_RENNEN = None     # B-273: Zahlen des letzten lord_rennen (Tagebuch)


def art_name(typ):
    """Spielname mit Codename und Nummer aus den Spielwerten ('Streitkolbenkaempfer (E_MACE 26)'), sonst 'Art 26'."""
    sw = SPIELWERTE or {}
    n = ((sw.get("namen") or {}).get("einheit") or {}).get(str(typ))
    code = ((sw.get("aufzaehlungen") or {}).get("UT") or {}).get(str(typ))
    if n or code:
        return "%s (%s %d)" % ((n or code).split(" (")[0], code or "?", typ)
    return "Art %d" % typ


def erklaerung(r, lohnt, bis):
    """B-273 (Daniel 27.10. 20:25): Lord-Wettlauf in Worten - wen die Truppe auf dem Weg wann bekaempft, wer wann faellt, und
    warum sie vorgeht oder wartet; dazu, wann sie abbrechen sollte (dieselbe Frist misst das Tagebuch)."""
    v = r.get("verlauf") or []
    kampf, tote_sie, tote_wir, beschuss = {}, {}, [], []
    for t, art, seite, typ, nah in v:
        if art == "kampf" and typ != LORD and nah:
            kampf.setdefault(typ, [t, 0])[1] += 1
        elif art == "beschuss":
            beschuss.append((t, typ, nah))
        elif art == "tot" and seite == "sie":
            tote_sie[typ] = tote_sie.get(typ, 0) + 1
        elif art == "tot" and seite == "wir":
            tote_wir.append(t)
    nah_lord = next((t for t, art, _s, typ, nah in v if art == "kampf" and typ == LORD and nah), None)
    fern_lord = next((t for t, art, _s, typ, nah in v if art == "kampf" and typ == LORD and not nah), None)
    teile = []
    if beschuss:
        teile.append("uns treffen " + ", ".join("%s ab Takt %d%s" % (art_name(typ), t0, "" if not nah else " (Nahkampf)")
                                               for t0, typ, nah in beschuss[:8]))
    if kampf:
        teile.append("unsere Nahkaempfer bleiben unterwegs haengen an " + ", ".join(
            "%dx %s ab Takt %d" % (n, art_name(typ), t0) for typ, (t0, n) in sorted(kampf.items(), key=lambda kv: kv[1][0])))
    teile.append(("Nahkampf am Lord ab Takt %d" % nah_lord) if nah_lord is not None else "unsere Nahkaempfer erreichen den Lord nicht")
    if fern_lord is not None:
        teile.append("unsere Schuetzen treffen den Lord ab Takt %d" % fern_lord)
    gefaellt = ", ".join("%dx %s" % (n, art_name(typ)) for typ, n in sorted(tote_sie.items()) if typ != LORD)
    if gefaellt:
        teile.append("faellen " + gefaellt)
    if tote_wir:
        teile.append("eigene Verluste %d (erster Takt %d, letzter %d)" % (len(tote_wir), tote_wir[0], tote_wir[-1]))
    if lohnt:
        grund = "VOR: Lord faellt nach %d Takten, uns bleiben %.0f %% (mindestens %.0f %% verlangt)" % (
            r["takte"], 100 * r["rest_anteil"], 100 * RENNEN_REST)
    elif r["faellt"]:
        grund = "WARTEN: Lord faellt zwar nach %d Takten, aber uns blieben nur %.0f %% (unter %.0f %%)" % (
            r["takte"], 100 * r["rest_anteil"], 100 * RENNEN_REST)
    else:
        grund = "WARTEN: Lord lebt nach %d Takten noch (%d Leben)" % (bis, r["lord_rest"])
    if lohnt:
        teile.append("Abbruch, wenn der Lord nach %d Takten noch lebt oder unter %.0f %% unserer Leben bleiben" % (
            max(2 * r["takte"], 1500), 100 * RENNEN_REST))
    return "; ".join([grund] + teile)
RENNEN_REST = 0.1         # B-207: so viel unseres Lebens muss bleiben, wenn der Lord faellt (Startwert, UNGEMESSEN)


def lord_rennen(wir, sie, lord_i, schaden=None, bis=BIS):
    """B-207 (Daniel 22.10. 18:58: "warum sollten sie gegen alle kaempfen? Sie sollen gegen so wenige wie moeglich kaempfen -
    so kannst du mit 10 gegen 500 gewinnen, du musst ja nur den Lord killen"): (lohnt, Text) - alle von "wir" schlagen nur auf
    sie[lord_i], die Verteidiger auf uns; lohnt, wenn der Lord faellt, solange noch RENNEN_REST unseres Lebens lebt."""
    if not wir:
        return False, "keine eigenen"
    voll = sum(e["leben"] for e in wir)
    global LETZTES_RENNEN
    prot = []
    r_wir, r_lord, t, gefallen = simuliere(wir, sie, schaden, bis=bis, fokus=lord_i, protokoll=prot)
    anteil = r_wir / float(max(1, voll))
    lohnt = gefallen and anteil >= RENNEN_REST
    # B-273: die Zahlen dieser Vorhersage fuer das Tagebuch (tagebuch.lord_angriff stellt sie spaeter neben das Ergebnis) und
    # die ehrliche Erklaerung (Daniel 27.10. 20:25: wen sie wann angreifen, warum vor oder zurueck)
    LETZTES_RENNEN = {"takte": t, "faellt": bool(gefallen), "rest_anteil": round(anteil, 3), "wir": len(wir),
                      "verteidiger": len(sie) - 1, "lord_leben": sie[lord_i]["leben"], "lord_rest": round(r_lord),
                      "verlauf": prot[:60]}
    LETZTES_RENNEN["erklaerung"] = erklaerung(LETZTES_RENNEN, lohnt, bis)
    return lohnt, "Lord-Wettlauf %d eigene (%d Leben) gegen Lord + %d Verteidiger: Lord %s nach %d Takten, uns bleiben %.0f %%" % (
        len(wir), voll, len(sie) - 1, "faellt" if gefallen else "lebt (%d)" % r_lord, t, 100 * anteil)
