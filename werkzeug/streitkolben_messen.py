# -*- coding: utf-8 -*-
"""Recherche fuer die Streitkolben-Challenge (Daniel 06.10. 19:45/19:49): was kostet und liefert jedes Glied der Kette?
Messpartie, KEIN Benchmark - Gold und Waren werden direkt gesetzt, damit nur die Gebaeude gemessen werden.

Gemessen (vorher festgelegt, Plan_Streitkolben.md):
  1. Markt: Stueck und Gold je Kauf/Verkauf fuer Keule (21) und Leder (23)
  2. Kaserne: was ein Streitkolbenkaempfer (Typ 26) abzieht - Gold, Keule, Leder, Bauer am Feuer
  3. Abriss: was eine abgerissene Schmiede zurueckgibt
  4. Produktion je Zeit: Kuehe (Milchviehhof), Leder je Kuh (Gerberei), Keulen je Eisen (Schmiede)
Ergebnis: daten/streitkolben_messung_<zeit>.json + Zeilen im Log.
Aufruf: python werkzeug/streitkolben_messen.py [ticks=6000] [tempo=300]
"""
import json
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as kanal
import erstes_spiel as E
from bauen import vorrat
from laden import befehl, peek, TICK

D = os.path.join(HIER, "..", "daten")
SP = 1
KEULE, LEDER, GOLD, HOLZ, STEIN, EISEN = 21, 23, 15, 2, 4, 6
MILCH, GERBER, SCHMIEDE, WAFFENLAGER, KASERNE, LAGER, MARKT, HUETTE = 33, 16, 13, 11, 9, 10, 26, 1


def setze(art, menge):
    befehl({"ware": {"typ": art, "menge": menge}}, 1.0, bis="WARE")


def bestand():
    v = vorrat(SP)
    st = E.runde_lesen()[0]
    return {"t": st.get("t"), "gold": v.get("gold"), "keule": v.get("keule"), "leder": v.get("leder"), "eisen": v.get("eisen"),
            "holz": v.get("holz"), "stein": v.get("stein"), "feuer": st.get("feuer"), "kaempfer": st.get("T26", 0),
            "einheiten": {k: v2 for k, v2 in st.items() if re.match(r"T\d+$", k)}}


def differenz(a, b):
    return {k: b[k] - a[k] for k in ("gold", "keule", "leder", "eisen", "holz", "stein", "feuer", "kaempfer") if a.get(k) is not None and b.get(k) is not None}


def warte_ticks(n):
    t0 = peek(TICK)[0]
    while peek(TICK)[0] - t0 < n:
        time.sleep(0.05)


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    dauer, tempo = int(arg.get("ticks", 6000)), int(arg.get("tempo", 300))
    plan = json.load(open(os.path.join(D, "eroeffnung_plan_M19.json"), encoding="utf-8"))
    lx, ly = plan["lager"]
    # Messpartie 4: Schmiede ~55 Felder vom Lager am Bergfried -> ~4.100 Ticks je Eisen. Darum alles direkt an dieses Lager
    # (Daniel: Kaserne naeher zum Vorratslager, minimale Laufwege).
    teile0 = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == LAGER]
    if teile0:
        lx, ly = teile0[0]["x"], teile0[0]["y"]
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    erg = {"ablauf": [], "proben": []}
    # Nur Gold ist eine reine Zahl. Stein/Holz/Eisen/Waffen liegen in Lagern: ein gesetzter Zaehler wird vom Spiel neu
    # gezaehlt (Messpartie 2: Stein 0 -> 300 gesetzt, kurz darauf 0) - darum fehlte Kaserne (12 Stein), Schmiede (8),
    # Gerberei (3), Daniel 19:54: "du brauchst gewisse Gueter, siehe Balance". Waren werden echt am Markt gekauft.
    setze(GOLD, 20000)
    # Bauen nah am Lager (Daniel: Kaserne naeher zum Vorratslager, minimale Laufwege)
    orte = {}
    # Messpartie 1 (19:51): nach 5 Ticks war das vorige Gebaeude noch nicht eingetragen - die Platzsuche gab Schmiede,
    # Gerberei und Huette denselben Platz (90, 276); Milchviehhoefe (10x10) fanden im Umkreis 25 keinen Platz.
    # Darum: nach jedem Bau warten, bis das Gebaeude in der Liste steht; grosse Hoefe weiter weg suchen.
    # Messpartie 5: alles direkt ans Lager gebaut -> kein Platz zum Anbauen, Eisenkauf und Abriss-Rueckgabe scheiterten
    # (jedes Teil nur eine Warenart, 48). Darum ZUERST zwei Lagerbloecke anbauen, dann den Rest drumherum.
    for typ, r in ((LAGER, 8), (LAGER, 10), (MARKT, 20), (WAFFENLAGER, 10), ("kaufen", 0), (KASERNE, 12), (SCHMIEDE, 12), (GERBER, 12),
                   (MILCH, 45), (MILCH, 45), (HUETTE, 20), (HUETTE, 20), (HUETTE, 20), (SCHMIEDE, 20)):
        if typ == "kaufen":                       # nach dem Markt: Stein und Holz echt kaufen
            for art, lose in ((STEIN, 10), (HOLZ, 10)):
                for _ in range(lose):
                    befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
            warte_ticks(10)
            orte["gekauft"] = [bestand()]
            continue
        vorher = sum(1 for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == typ)
        o = E.baue_schnell(typ, lx, ly, r)
        for _ in range(40):
            warte_ticks(3)
            if sum(1 for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == typ) > vorher:
                break
        else:
            o = ("nicht gebaut", o)
        orte.setdefault(typ, []).append(o)
    erg["ablauf"].append({"gebaut": {str(k): v for k, v in orte.items()}, "t": peek(TICK)[0]})
    print("gebaut:", orte, flush=True)
    warte_ticks(200)                                   # Gebaeude fertig, Arbeiter unterwegs
    G = E.runde_lesen()[2]
    eigen = {n: g for n, g in G.items() if g["besitzer"] == SP}
    kaserne = [n for n, g in eigen.items() if g["typ"] == KASERNE]
    # Schmiede auf Keulen stellen: Spielbefehl 33 ClickSetBuildingProductionType (Gebaeude, Art, UID) ->
    # SetBuildingProductionType setzt producedItemType, wenn die UID passt (dekomp_produktionstyp*.c). Art 21 = Keule.
    for n, g in eigen.items():
        if g["typ"] == SCHMIEDE:
            befehl({"spielbefehl": {"nr": 33, "werte": [n, KEULE, g.get("uid", 0)]}}, 1.0, bis="SPIELBEFEHL")
            erg["ablauf"].append({"schmiede_auf_keule": [n, g.get("uid")]})
    schmieden = [n for n, g in eigen.items() if g["typ"] == SCHMIEDE]
    # 1. Markt
    for name, art in (("keule", KEULE), ("leder", LEDER)):
        a = bestand()
        befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
        warte_ticks(3)
        b = bestand()
        befehl({"spielbefehl": {"nr": 38, "werte": [1, art]}}, 1.0, bis="SPIELBEFEHL")
        warte_ticks(3)
        c = bestand()
        erg["ablauf"].append({"markt": name, "kauf": differenz(a, b), "verkauf": differenz(b, c)})
        print("MARKT %s: Kauf %s | Verkauf %s" % (name, differenz(a, b), differenz(b, c)), flush=True)
    # 2. Kaserne: ein Kaempfer mit gesetzter Keule und Leder
    for art in (KEULE, LEDER):                     # Waffen liegen im Waffenlager: echt kaufen statt setzen
        befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(5)
    a = bestand()
    if kaserne:
        befehl({"werbe": {"typ": 26, "gebaeude": kaserne[0]}}, 1.0, bis="WERBE")
        warte_ticks(30)
    b = bestand()
    erg["ablauf"].append({"kaserne": kaserne, "werben": differenz(a, b)})
    print("KASERNE: ein Streitkolbenkaempfer zieht ab %s" % differenz(a, b), flush=True)
    # 3. Abriss der zweiten Schmiede
    if len(schmieden) >= 2:
        a = bestand()
        # Spielbefehl 29 {nr, rueckgabe in Prozent, uid}: Rueckgabe = Kosten * Prozent / 100, ohne Zustand-Anteil
        # (daten/dekomp_abriss_rueckgabe.c). Der Abriss-Knopf traegt 50 ein (0x00438ad9) - das Modul nimmt jetzt 50 als
        # Standard. Mit 0 und 1 kam 4-mal nichts zurueck. Daniel 20:06: "die Haelfte, egal in welchem Zustand".
        befehl({"abreissen": {"nr": schmieden[-1]}}, 0.8, bis="ABREISSEN")
        warte_ticks(150)      # Messpartie 3: nach 10 Ticks noch nichts
        b = bestand()
        erg["ablauf"].append({"abriss_schmiede": differenz(a, b)})
        print("ABRISS Schmiede: %s" % differenz(a, b), flush=True)
    # 4. Produktion: Eisen fuer die Schmiede, Keule/Leder auf 0, dann laufen lassen und mitschreiben
    # Jedes Lagerteil fasst nur eine Warenart (Messung 19:58, Tipp Daniel); die 4 Startteile waren mit Holz und Stein
    # belegt, Eisen fand keinen Platz. Darum vorher einen Lagerblock anbauen (kostet nichts).
    teile = [g for g in E.runde_lesen()[2].values() if g["besitzer"] == SP and g["typ"] == LAGER]
    if teile:
        erg["ablauf"].append({"lager_anbau": E.baue_schnell(LAGER, teile[0]["x"], teile[0]["y"], 8)})
        warte_ticks(40)
    vor_eisen = bestand()
    for _ in range(4):                              # Eisen fuer die Schmiede echt kaufen (Los zu 270 Gold)
        befehl({"spielbefehl": {"nr": 38, "werte": [0, EISEN]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(5)
    erg["ablauf"].append({"eisenkauf": differenz(vor_eisen, bestand())})
    print("EISENKAUF 4 Lose: %s" % erg["ablauf"][-1]["eisenkauf"], flush=True)
    t0 = peek(TICK)[0]
    while peek(TICK)[0] - t0 < dauer:
        p = bestand()
        erg["proben"].append(p)
        time.sleep(0.3)
    letzte = erg["proben"][-1]
    print("PRODUKTION in %d Ticks: Keulen %s (Eisen 20 -> %s), Leder %s; Einheiten %s" % (
        letzte["t"] - t0, letzte["keule"], letzte["eisen"], letzte["leder"], letzte["einheiten"]), flush=True)
    befehl({"pause": True}, 0.5)
    pfad = os.path.join(D, "streitkolben_messung_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1)
    print("Daten:", pfad)


EISENMINE, KORNSPEICHER = 5, 19


def eigene(typ=None):
    G = E.runde_lesen()[2]
    return {n: g for n, g in G.items() if g["besitzer"] == SP and (typ is None or g["typ"] == typ)}


def baue_und_warte(typ, x, y, r, protokoll, name):
    """Bauen und warten, bis das Gebaeude in der Liste steht (Messpartie 1: sonst bekommen zwei Bauten denselben Platz)."""
    vorher = set(eigene(typ))
    ort = E.baue_schnell(typ, x, y, r)
    neu = []
    for _ in range(40):
        warte_ticks(3)
        neu = [n for n in eigene(typ) if n not in vorher]
        if neu:
            break
    g = eigene(typ).get(neu[0]) if neu else None
    eintrag = {"name": name, "typ": typ, "gesucht": [x, y, r], "ort": ort, "nr": neu[0] if neu else None,
               "x": g["x"] if g else None, "y": g["y"] if g else None, "uid": g.get("uid") if g else None, "t": peek(TICK)[0]}
    protokoll.append(eintrag)
    print("GEBAUT %s: %s" % (name, eintrag), flush=True)
    return eintrag


def baue_plan_und_warte(typ, x, y, richtung, protokoll, name):
    """Einen vom Wegplaner bestimmten 4x4-Bau exakt mit seiner Eingangsrichtung setzen."""
    mapper = {WAFFENLAGER: 81, SCHMIEDE: 83, GERBER: 85}[typ]
    vorher = set(eigene(typ))
    befehl({"baue": {"mapper": mapper, "x": x, "y": y, "groesse": 4, "richtung": richtung}}, 0.8, bis="BAUE")
    neu = []
    for _ in range(50):
        warte_ticks(3)
        neu = [n for n in eigene(typ) if n not in vorher]
        if neu:
            break
    g = eigene(typ).get(neu[0]) if neu else None
    eintrag = {"name": name, "typ": typ, "gesucht": [x, y, 0], "richtung": richtung,
               "ort": [x, y] if g else None, "nr": neu[0] if neu else None,
               "x": g["x"] if g else None, "y": g["y"] if g else None,
               "uid": g.get("uid") if g else None, "t": peek(TICK)[0]}
    protokoll.append(eintrag)
    print("GEBAUT %s NACH WEGPLAN: %s" % (name, eintrag), flush=True)
    if not g:
        raise SystemExit("ABBRUCH: Wegplan-Bau %s wurde nicht gesetzt" % name)
    return eintrag


def gebaeude_mit_eingang(typ):
    """Liest den vom Spiel gespeicherten Eingang statt ihn aus dem Grundriss zu raten."""
    z = " ".join(befehl({"gebaeude": {"spieler": SP, "typ": typ}}, 1.0, bis="GEBAEUDE:"))
    return {int(n): {"ort": (int(x), int(y)), "eingang": (int(ex), int(ey))}
            for n, x, y, ex, ey in re.findall(
                r"GEBAEUDE (\d+): Typ \d+, Spieler \d+, Ort \((-?\d+),(-?\d+)\), Eingang \((-?\d+),(-?\d+)\)", z)}


def kette():
    """Messpartie Eisen/Schmiede/Leder (Daniel 08.10. 00:18: "ja bitte und auch wirklich messen"). Vorher festgelegt:
    - Spielregel (Stronghold-Wiki "Resources"): ein Eisenarbeiter traegt je Gang ein Stueck zur Lagerstelle, Ochsen helfen
      nicht - die Rate haengt am Weg Mine <-> Lager. Liga: enable_iron_double_pickup (vermutlich 2 je Gang).
    - Ein zweites Lager geht nur angrenzend (Platzsuche 08.10.: 0 von 961 Plaetzen um (142,311), 5 von 27 neben dem Lager).
      Darum zieht das ganze Lager ans Eisenfeld (wie der Lagerumzug zu den Steinbruechen): alte Teile abreissen, neu bauen.
    - Drei Minen mit verschiedenem Weg (am Lager, ~25, ~45 Feldern) -> Eisen je 1.000 Ticks gegen Weglaenge.
    - Zwei Schmieden am Lager, auf Keulen gestellt (Spielbefehl 33), 20 Eisen gekauft -> Keulen je 1.000 Ticks bei Eisen satt.
    - 2 Milchviehhoefe + 1 Gerberei -> Kuehe, Leder je 1.000 Ticks.
    - Beliebtheit 100 ueber die Messumgebung (Aufbau-Messung 20:40: bei 0 gingen die Leute, 0 Kuehe in 12.000 Ticks).
    WIDERLEGT ist die Hoffnung "Eisen am Lager lohnt", wenn die Mine am Lager unter 1 Eisen je 1.000 Ticks bleibt.
    Gesetzt wird nur Gold; alles andere echt gebaut, gekauft, gezaehlt. Jede Runde komplett ins Lageprotokoll."""
    import messumgebung as M
    from lageprotokoll import Lageprotokoll
    import wegkarte as W
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    dauer, tempo = int(arg.get("ticks", 12000)), int(arg.get("tempo", 100))
    ziel = tuple(int(v) for v in arg.get("lager", "142,311").split(","))
    stempel = time.strftime("%Y%m%d_%H%M%S")
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    erg = {"bauten": [], "schritte": [], "proben": [], "start": stempel}
    setze(GOLD, 20000)
    # 1. Lager ans Eisenfeld: alte Teile weg, dann das erste Teil frei setzen, ein zweiter Block daneben
    alte = list(eigene(LAGER))
    for n in alte:
        befehl({"abreissen": {"nr": n}}, 0.8, bis="ABREISSEN")
    warte_ticks(10)
    erg["schritte"].append({"alte_lagerteile_abgerissen": alte, "rest": list(eigene(LAGER))})
    l1 = baue_und_warte(LAGER, ziel[0], ziel[1], 6, erg["bauten"], "Lager am Eisenfeld")
    if not l1["nr"]:
        print("ABBRUCH: Lager am Eisenfeld nicht gebaut", flush=True)
        return
    lx, ly = l1["x"], l1["y"]
    baue_und_warte(LAGER, lx, ly, 8, erg["bauten"], "Lager Block 2")
    # Drei Bloecke: Holz, Stein und Eisen brauchen gleichzeitig eigene Lagerteile. Ohne Reserve kann ein erfolgreicher
    # Marktkauf nirgends abgelegt werden; genau das verfaelschte den abgebrochenen Lauf vom 08.10.
    baue_und_warte(LAGER, lx, ly, 10, erg["bauten"], "Lager Block 3 (Kapazitaetsreserve)")
    # Markt, Kornspeicher und Huetten arbeiten nicht mit Eisen/Waffen. Sie duerfen den knappen Korridor um Lager,
    # Waffenlager und Werkstaetten nicht verbauen (Daniel 08.10., Bild-Gegenprobe).
    service = (E.BERGFRIED[0] - 25, E.BERGFRIED[1] - 20)
    markt_bau = baue_und_warte(MARKT, service[0], service[1], 25, erg["bauten"], "Markt ausserhalb Produktionskern")
    for art, lose in ((HOLZ, 25), (STEIN, 12)):
        for _ in range(lose):
            befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(10)
    erg["schritte"].append({"gekauft": bestand()})
    # 2. Minen ZUERST (Messpartie 08.10. 00:23: die Huetten der Messumgebung standen schon auf dem Eisenfeld - die Mine am
    #    Lager fand keinen Platz). Je Weglaenge die naechsten Kandidaten der Reihe nach, bis einer steht.
    def lies_platzkarte(pfad):
        zeilen = open(pfad, encoding="utf-8").read().split("\n")
        kopf = dict(t.split("=") for t in zeilen[0].split())
        x0, y0 = int(kopf["x0"]), int(kopf["y0"])
        return {(x0 + i, y0 + j) for j, reihe in enumerate(zeilen[1:]) for i, c in enumerate(reihe) if c == "+"}

    plaetze = lies_platzkarte(os.path.join(D, "start_M19_platz_eisenmine.txt"))
    weg = lambda q: max(abs(q[0] + 2 - (lx + 2)), abs(q[1] + 2 - (ly + 2)))
    # Eine Richtung reicht nicht: Die Weg-Ebene kann Einbahn-Verbindungen enthalten. Vor dem Bau muss der Eingang
    # sowohl vom Lager erreichbar sein als auch wieder zum Lager zurueckfuehren.
    k_vor = W.holen(max(min([lx] + [q[0] for q in plaetze]) - 10, 0), max(min([ly] + [q[1] for q in plaetze]) - 10, 0),
                    min(max([lx] + [q[0] for q in plaetze]) + 20, 399), min(max([ly] + [q[1] for q in plaetze]) + 20, 399))
    lagerfelder = [p for p, v in k_vor["f"].items() if v[5] == LAGER]
    lagerzugang = {n for p in lagerfelder for dx, dy in W.RICHTUNG.values()
                   for n in [(p[0] + dx, p[1] + dy)] if W.begehbar(k_vor, n)}

    from collections import deque
    def flut(starts, rueckwaerts=False):
        q, gesehen = deque(starts), set(starts)
        if rueckwaerts:
            nachbarn = {p: [] for p in k_vor["f"]}
            for p, v in k_vor["f"].items():
                for bit, (dx, dy) in W.RICHTUNG.items():
                    n = (p[0] + dx, p[1] + dy)
                    if v[0] & bit and n in nachbarn:
                        nachbarn[n].append(p)
        while q:
            p = q.popleft()
            ns = nachbarn[p] if rueckwaerts else ((p[0] + dx, p[1] + dy) for bit, (dx, dy) in W.RICHTUNG.items()
                                                   if k_vor["f"][p][0] & bit)
            for n in ns:
                if n in k_vor["f"] and n not in gesehen:
                    gesehen.add(n); q.append(n)
        return gesehen

    vom_lager, zum_lager = flut(lagerzugang), flut(lagerzugang, rueckwaerts=True)

    def mine_hin_und_zurueck(q):
        e = (q[0] + 2, q[1] + 4)       # Richtung 0; fuer Eisenminen live bestaetigt
        return e in vom_lager and e in zum_lager

    # Fuenf Entfernungsstufen: Unterhalb der Kippstelle kann der Traeger schneller sein als der Bergmann; die langen
    # Wege sollen die Stelle sichtbar machen, ab der Transport und nicht Abbau begrenzt.
    soll_liste = [int(s) for s in arg.get("minen", "0,20,40,70,100").split(",")]
    for soll in soll_liste:
        name = "Mine am Lager" if soll == 0 else "Mine ~%d Felder" % soll
        kand = sorted((q for q in plaetze if weg(q) >= 5 and mine_hin_und_zurueck(q)
                       and all(max(abs(q[0] - b["x"]), abs(q[1] - b["y"])) >= 5
                                                                  for b in erg["bauten"] if b["x"] is not None)),
                      key=lambda q: abs(weg(q) - soll))
        for q in kand[:12]:
            e = baue_und_warte(EISENMINE, q[0], q[1], 1, erg["bauten"], name)
            if e["nr"]:
                e["weg_soll"], e["weg_luftlinie"] = soll, weg(q)
                break
            erg["bauten"].pop()
    # Eisen kaufen, solange die Lagerreserve garantiert frei ist. Holz und Stein werden erst danach aufgefuellt.
    for _ in range(4):
        befehl({"spielbefehl": {"nr": 38, "werte": [0, EISEN]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(10)
    G_eisen = E.runde_lesen()[2]
    eisen_teil = next((n for n, g in G_eisen.items() if g["besitzer"] == SP and g["typ"] == LAGER and g.get("ware") == EISEN), None)
    if eisen_teil is None:
        raise SystemExit("ABBRUCH: kein freies erreichbares Lagerteil fuer gekauftes Eisen")
    sx, sy = (markt_bau["x"], markt_bau["y"]) if markt_bau["nr"] else service
    korn_vor = set(eigene(KORNSPEICHER))
    erg["schritte"].append({"messumgebung": M.vorbereiten(sx, sy, huetten=8)})
    korn_neu = set(eigene(KORNSPEICHER)) - korn_vor
    korn_nr = min(korn_neu) if korn_neu else None
    # 3. Hoefe zuerst, dann Werkstaetten ueber die ECHTE Wegkarte planen. Der fruehere Test setzte alle Bauten nur
    # moeglichst nah an dieselbe Mitte. Daniels Bilder vom 08.10. zeigen den Fehler: Gebaeude beruehrten sich und die
    # Arbeiter mussten aussen herum. Ab jetzt gilt: Luftlinie ist wertlos; jeder Eingang braucht einen echten Korridor.
    h1 = baue_und_warte(MILCH, lx, ly, 35, erg["bauten"], "Milchviehhof 1")
    h2 = baue_und_warte(MILCH, lx, ly, 35, erg["bauten"], "Milchviehhof 2")
    # Nach dem Minen-/Versorgungsbau die Produktionsmittel frisch auffuellen. Zwei Lagerbloecke reichen fuer Holz,
    # Stein und Eisen; die Bauten verbrauchen die Lose sofort wieder.
    for art, lose in ((HOLZ, 40), (STEIN, 14)):
        for _ in range(lose):
            befehl({"spielbefehl": {"nr": 38, "werte": [0, art]}}, 1.0, bis="SPIELBEFEHL")
    warte_ticks(10)
    import aufbau_planer as AP
    G_plan = E.runde_lesen()[2]
    k = W.holen(max(lx - 45, 0), max(ly - 45, 0), min(lx + 55, 399), min(ly + 55, 399))
    hof_orte = [(h["x"], h["y"]) for h in (h1, h2) if h["nr"]]
    # Alte Messung 0,59 Eisen/Mine/1.000 und ~0,45 Keulen/Schmiede/1.000: fuenf Minen brauchen rechnerisch rund
    # sieben Schmieden. Acht geben eine Gegenprobe mit etwas Verarbeitungsspielraum statt des alten Eisenstaus 5:2.
    n_schmieden = int(arg.get("schmieden", 8))
    plan_w, bericht_w = AP.plane(k, n_schmieden, 1, eisen_teil=eisen_teil, hoefe=hof_orte, r_max=32)
    erg["verhaeltnis"] = {"minen": len([b for b in erg["bauten"] if b["typ"] == EISENMINE and b["nr"]]),
                          "schmieden": n_schmieden}
    erg["wegplan"] = bericht_w
    namen = {WAFFENLAGER: "Waffenlager", SCHMIEDE: "Schmiede", GERBER: "Gerberei"}
    zaehler = {WAFFENLAGER: 0, SCHMIEDE: 0, GERBER: 0}
    geplant = []
    for art, x, y, richtung, eingang in plan_w.bauten:
        zaehler[art] += 1
        name = namen[art] + (" %d" % zaehler[art] if art == SCHMIEDE else "")
        b = baue_plan_und_warte(art, x, y, richtung, erg["bauten"], name)
        b["eingang_plan"] = list(eingang)
        geplant.append(b)
    # Gegenprobe an der NACH dem Bau neu gelesenen Wegkarte: Jeder Eingang muss zum Lager und jede Werkstatt zum
    # Waffenlager gelangen. Ein Erfolg des Baubefehls allein beweist keinen brauchbaren Weg.
    korn = gebaeude_mit_eingang(KORNSPEICHER).get(korn_nr) if korn_nr else None
    echte_eingaenge = {typ: gebaeude_mit_eingang(typ) for typ in (WAFFENLAGER, SCHMIEDE, GERBER, EISENMINE)}
    punkte = [(lx, ly), tuple(korn["eingang"]) if korn else (lx, ly)] + \
             [tuple(g["eingang"]) for g in echte_eingaenge[EISENMINE].values()]
    k_nach = W.holen(max(min(p[0] for p in punkte) - 20, 0), max(min(p[1] for p in punkte) - 20, 0),
                     min(max(p[0] for p in punkte) + 60, 399), min(max(p[1] for p in punkte) + 60, 399))
    p_nach = AP.Plan(k_nach)
    d_lager = p_nach.lager_abstand()
    lagerfelder_nach = [p for p, v in k_nach["f"].items() if v[5] == LAGER]
    lagerzugang_nach = {n for p in lagerfelder_nach for dx, dy in W.RICHTUNG.values()
                        for n in [(p[0] + dx, p[1] + dy)] if p_nach.boden(n)}

    def lager_hin_und_zurueck(e):
        hin = p_nach.abstand(e)
        rueck = d_lager.get(e)
        hin_lager = min((hin[z] + 1 for z in lagerzugang_nach if z in hin), default=None)
        return hin_lager, rueck, hin_lager is not None and rueck is not None

    wl = next(b for b in geplant if b["typ"] == WAFFENLAGER)
    wl_eingang = echte_eingaenge[WAFFENLAGER].get(wl["nr"], {}).get("eingang", tuple(wl["eingang_plan"]))
    d_waffen = p_nach.abstand(wl_eingang)
    wegprobe = []
    for b in geplant:
        e = echte_eingaenge[b["typ"]].get(b["nr"], {}).get("eingang", tuple(b["eingang_plan"]))
        hin_lager, rueck_lager, ok_lager = lager_hin_und_zurueck(e)
        ok_waffen = b["typ"] == WAFFENLAGER or (e in d_waffen and wl_eingang in p_nach.abstand(e))
        wegprobe.append({"name": b["name"], "eingang": list(e), "lager_felder": hin_lager,
                         "lager_rueck_felder": rueck_lager,
                         "waffenlager_felder": 0 if b["typ"] == WAFFENLAGER else d_waffen.get(e),
                         "erreichbar": ok_lager and ok_waffen})
    for b in (x for x in erg["bauten"] if x["typ"] == EISENMINE and x["nr"]):
        e = echte_eingaenge[EISENMINE].get(b["nr"], {}).get("eingang")
        hin_lager, rueck_lager, ok_lager = lager_hin_und_zurueck(e) if e else (None, None, False)
        b["eingang"] = list(e) if e else None
        b["weg_felder"] = hin_lager
        wegprobe.append({"name": b["name"], "eingang": list(e) if e else None,
                         "lager_felder": hin_lager, "lager_rueck_felder": rueck_lager,
                         "waffenlager_felder": None, "erreichbar": ok_lager})
    # Kornspeicher liegt absichtlich weit weg. Trotzdem muss sein echter Eingang zum gemeinsamen Wegenetz gehoeren;
    # gekauftes Essen im Zaehler allein beweist keine moegliche Anlieferung durch Bauern.
    if korn:
        ke = tuple(korn["eingang"])
        hin_lager, rueck_lager, ok_lager = lager_hin_und_zurueck(ke)
        wegprobe.append({"name": "Kornspeicher", "eingang": list(ke), "lager_felder": hin_lager,
                         "lager_rueck_felder": rueck_lager, "waffenlager_felder": None, "erreichbar": ok_lager})
    else:
        wegprobe.append({"name": "Kornspeicher", "eingang": None, "erreichbar": False})
    erg["wegprobe"] = wegprobe
    print("WEGPROBE:", wegprobe, flush=True)
    if not all(x["erreichbar"] for x in wegprobe):
        raise SystemExit("ABBRUCH: mindestens ein Produktionsweg ist nach dem Bau blockiert")
    for b in geplant:
        if b["typ"] == SCHMIEDE:
            befehl({"spielbefehl": {"nr": 33, "werte": [b["nr"], KEULE, b["uid"] or 0]}}, 1.0, bis="SPIELBEFEHL")
    # 4. Erst nach bestandener Wegprobe messen.
    erg["schritte"].append({"nach_aufbau": bestand()})
    # 5. Laufen lassen, jede Runde komplett mitschreiben
    lage = Lageprotokoll(os.path.join(D, "lage_kette_%s_i%d.jsonl.gz" % (stempel, E.INSTANZ)))
    erg["lageprotokoll"] = lage.pfad
    print("Lageprotokoll:", lage.pfad, flush=True)
    t0, runde = peek(TICK)[0], 0
    erg["t_messbeginn"] = t0
    erg["waffen_abfluss"] = {"keule": 0, "leder": 0, "vorgaenge": []}
    while peek(TICK)[0] - t0 < dauer:
        st = E.runde_lesen()[0]
        if st:
            lage.schreibe(st)
        runde += 1
        if runde % 20 == 0:
            M.pflegen(st)
        if runde % 10 == 0:
            p = bestand()
            # Ein volles Waffenlager blockiert die Ablieferung. Bei 40 von vermutlich 50 Plaetzen wird kontrolliert
            # ein Fuenferlos verkauft und separat gezaehlt; so bleiben mindestens zehn Plaetze frei und der Ertrag geht
            # in der Auswertung nicht verloren.
            while (p.get("keule", 0) or 0) + (p.get("leder", 0) or 0) >= 40:
                name, art = max((("keule", KEULE), ("leder", LEDER)), key=lambda x: p.get(x[0], 0) or 0)
                if (p.get(name, 0) or 0) < 5:
                    raise SystemExit("ABBRUCH: Waffenlager voll, aber kein verkaufbares Fuenferlos")
                vorher = p
                befehl({"spielbefehl": {"nr": 38, "werte": [1, art]}}, 1.0, bis="SPIELBEFEHL")
                warte_ticks(3)
                p = bestand()
                verkauft = max(0, (vorher.get(name, 0) or 0) - (p.get(name, 0) or 0))
                if not verkauft:
                    raise SystemExit("ABBRUCH: Waffenlager konnte trotz Fuellstand nicht entlastet werden")
                erg["waffen_abfluss"][name] += verkauft
                erg["waffen_abfluss"]["vorgaenge"].append({"t": p["t"], "ware": name, "menge": verkauft,
                                                              "gold_delta": p["gold"] - vorher["gold"]})
            erg["proben"].append(p)
            print("PROBE t=%s Keule %s Leder %s Eisen %s Gold %s Beliebt %.1f Leute %s" % (
                p["t"], p["keule"], p["leder"], p["eisen"], p["gold"], st.get("beliebt", 0) / 100.0, st.get("leute")), flush=True)
    befehl({"pause": True}, 0.5)
    pfad = os.path.join(D, "kette_messung_%s.json" % stempel)
    json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1)
    print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        kette() if "teil=kette" in sys.argv else main()
    finally:
        kanal.freigeben()
