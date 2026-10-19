# -*- coding: utf-8 -*-
"""Messpartie fuer den Ertrags-Planer (Daniel 05.10. 19:14: "ja, fang mit der Messpartie an").

PRUEFSTAND, kein Spiel gegen Rotkaeppchen: unser Spieler bekommt nur fuer die Messung Gold und Stein gesetzt (poke),
damit je EIN Gebaeude jeder Art gleichzeitig stehen kann. Gemessen wird, was jedes Gebaeude liefert:
  Steinbruch + Ochsenjoch, Eisenmine, Jaegerhuette (an Rehen), Holzfaeller (am Baum), Apfelplantage.
Dazu Lager nahe Stein/Eisen, Kornspeicher an der Apfelplantage, Markt, Huetten fuer Arbeiter.
Alle STICH Ticks: Bestand jeder Ware (Modulbefehl vorrat). Am Ende je ein Los Stein und Eisen verkaufen (Preis).
Ergebnis: data/research/ertrag_messung.txt (Verlauf) und data/research/ertrag_messung.json (je Ware: erste Lieferung, Menge, Rate
je 1.000 Ticks ab erster Lieferung, Weg zum naechsten Lager bzw. Kornspeicher).

Aufruf:  uv run python -m selfaware.tools.experiments.messpartie [ticks=8000] [stich=250]
"""

from selfaware import workspace as _workspace
import json, os, sys, time

from selfaware.game.ucp.laden import befehl, peek, lade_stand
from selfaware.game.ucp.steuerkarte import laufe, tick
from selfaware.game.ucp.bauen import vorrat, gebaeude_von
from selfaware.micro.tasks.waechter import lies_lagebild, schach
import selfaware.runtime.live.erstes_spiel as es

D = os.path.join(_workspace.DATA)
PD = 0x0115BDF8 + 0x39F4
WAREN = ("holz", "stein", "eisen", "fleisch", "apfel")

def setze(adr, wert):
    befehl({"poke": adr, "wert": wert}, 0.8, bis="POKE")

def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    ticks, stich = int(arg.get("ticks", 8000)), int(arg.get("stich", 250))
    plan = json.load(open(os.path.join(D, "eroeffnung_plan_M19.json"), encoding="utf-8"))
    K = tuple(plan["bergfried_eingang"])
    lade_stand(plan["spielstand"], mit_bild=False)
    befehl({"eigenerPlatz": 1}, 0.8)
    befehl({"tempo": 1000}, 0.5)
    # Speicherstelle der Waren pruefen (PlayerData +0x4D0 + Ware*4): Holz (2) muss dem Modulwert entsprechen
    v = vorrat(1)
    if peek(PD + 0x4D0 + 2 * 4)[0] != v["holz"]:
        print("ABBRUCH: Warenstelle stimmt nicht (peek %d, vorrat %d)" % (peek(PD + 0x4D0 + 8)[0], v["holz"])); sys.exit(1)
    # Nur Gold setzen (Pruefstand). Waren NICHT setzen: gemessen 05.10. - gesetzte Zaehler verschwanden mit dem
    # abgerissenen Lager, es zaehlt, was physisch im Lager liegt. Waren werden am Markt gekauft (je Kauf 5 Stueck).
    setze(PD + 0x50C, 4000)
    z = open(os.path.join(D, "rohstoffe_M19.txt")).read().splitlines()[1:]
    info = json.load(open(os.path.join(D, "start_M19.json"), encoding="utf-8"))
    F = tuple(info["feind_bergfried"]["2"]["eingang"])
    eigen = lambda p: schach(p, K) < schach(p, F)
    feld = lambda c: sorted([(x, y) for y, r in enumerate(z) for x, ch in enumerate(r) if ch == c and eigen((x, y))], key=lambda p: schach(p, K))
    stein, eisen = feld("b")[0], feld("i")[0]
    L = lies_lagebild(neu_holen=True)
    rehe = [(e["x"], e["y"]) for e in L.values() if e["typ"] == 44 and eigen((e["x"], e["y"])) and schach((e["x"], e["y"]), K) <= 70]
    herde = max(rehe, key=lambda p: sum(1 for q in rehe if schach(p, q) <= 15)) if rehe else None
    bau = {}
    # Plaetze aus den Platzkarten dieses Starts (gueltige Ankerpunkte laut Spielpruefung), nicht der naechste Rohstoff-Fleck
    from selfaware.macro.farmen_mischen import lies_karte
    karte = lambda n: [p for p in lies_karte(os.path.join(D, "start_M19_platz_%s.txt" % n)) if eigen(p)]
    # Lauf 2 (Daniel 19:27): Steinbruch nahe am Eisen, Lager zwischen beiden - Weg zum Lager klein halten
    q = min(karte("steinbruch"), key=lambda p: schach(p, eisen))
    # ein neues Lagerteil schliesst an ein vorhandenes an (vermutet aus 9i/9p) - darum zuerst das Startlager abreissen
    for n_alt, _, _ in gebaeude_von(1, 10):
        befehl({"abreissen": {"nr": n_alt}}, 0.8, bis="ABREISSEN")
    laufe(2)
    mitte = ((q[0] + eisen[0]) // 2, (q[1] + eisen[1]) // 2)
    lk = min(karte("lager_keins"), key=lambda p: schach(p, mitte) + (0 if min(schach(p, q), schach(p, eisen)) >= 7 else 100))
    bau["markt"] = es.baue_schnell(26, K[0], K[1], 25)
    bau["lager"] = es.baue_schnell(10, lk[0], lk[1], 3)
    laufe(30)
    def kaufe(nr, lose):
        es.sende({"befehle": [{"player": 1, "id": es.neue_id(), "spielbefehl": {"nr": 38, "werte": [0, nr]}} for _ in range(lose)]},
                 2.0, bis="SPIELBEFEHL")
        laufe(10)
    kaufe(2, 18)      # 90 Holz - mit 150 war das Lager voll (4 Teile je 48), kein Platz mehr fuer Stein
    kaufe(4, 3)       # 15 Stein (Eisenmine braucht 6)
    # Kornspeicher ERST jetzt (5 Holz): Messpartie 3 baute ihn bei 0 Holz - er entstand nie, kein Essenskauf moeglich
    bau["kornspeicher"] = es.baue_schnell(19, plan["kornspeicher"][0], plan["kornspeicher"][1], 6)
    laufe(150)
    steht = [g for g in gebaeude_von(1, 19)]
    print("Kornspeicher steht:", steht, flush=True)
    kaufe(13, 10)     # 50 Aepfel - ohne Nahrung gingen die Leute (Messpartie 1: 10 -> 4)
    print("nach Kauf:", {k: v for k, v in vorrat(1).items() if v}, flush=True)
    bau["steinbruch"] = es.baue_schnell(20, q[0], q[1], 3)
    if bau["steinbruch"]:
        bau["ochsen"] = es.baue_schnell(4, bau["steinbruch"][0] + 3, bau["steinbruch"][1] - 4, 8)
    bau["eisenmine"] = es.baue_schnell(5, eisen[0], eisen[1], 12)
    bau["apfel"] = es.baue_schnell(32, plan["aepfel"][0][0], plan["aepfel"][0][1], 6)
    bau["jaeger"] = es.baue_schnell(7, herde[0], herde[1], 12) if herde else None
    baeume = [w.split() for w in open(os.path.join(D, "baeume_M19.txt")).read().splitlines()[1:]]
    baeume = [(int(w[3]), int(w[4])) for w in baeume if len(w) >= 7 and w[2] == "2" and int(w[5]) < 4 and int(w[6]) > 0]
    if bau["lager"]:
        b = min(baeume, key=lambda p: schach(p, bau["lager"]))
        bau["holzfaeller"] = es.baue_schnell(3, b[0], b[1], 4)
    for i in range(3):
        bau["huette%d" % i] = es.baue_schnell(1, K[0] - 7, K[1] - 2, 25)
    print("Gebaut:", bau, flush=True)
    t0 = tick()
    reihe = []
    aus = open(os.path.join(D, "ertrag_messung.txt"), "w", encoding="utf-8")
    aus.write("# %s Messpartie (Pruefstand, Gold/Stein/Holz gesetzt), Bauten %s\ntick %s leute\n" % (
        time.strftime("%d.%m.%Y %H:%M"), bau, " ".join(WAREN)))
    import selfaware.game.ucp.befehl as befehlskanal
    while tick() - t0 < ticks:
        befehlskanal.belege()
        laufe(stich)
        v = vorrat(1)
        st = " ".join(befehl({"status": 1}, 1.5, bis="STATUS"))
        import re
        leute = int(re.search(r"leute=(\d+)", st).group(1)) if "leute=" in st else -1
        reihe.append((tick() - t0, {w: v.get(w, 0) for w in WAREN}, leute))
        aus.write("%d %s %d\n" % (reihe[-1][0], " ".join(str(reihe[-1][1][w]) for w in WAREN), leute))
        aus.flush()
    # Preise Stein und Eisen
    preis = {}
    for ware, nr in (("stein", 4), ("eisen", 6)):
        a = vorrat(1)
        befehl({"spielbefehl": {"nr": 38, "werte": [1, nr]}}, 1.0, bis="SPIELBEFEHL")
        laufe(5)
        b = vorrat(1)
        menge = a.get(ware, 0) - b.get(ware, 0)
        preis[ware] = {"stueck": menge, "gold": b["gold"] - a["gold"], "je_stueck": round((b["gold"] - a["gold"]) / menge, 2) if menge else None}
    # Auswertung je Ware (Holz: Anfangsbestand 300 minus Bauten - nur Zuwachs ab dem ersten Anstieg zaehlt)
    erg = {}
    for w in WAREN:
        werte = [(t, r[w]) for t, r, _ in reihe]
        erst = next((t for (t, x), (_, y) in zip(werte, werte[1:]) if y > x), None)
        zuwachs = sum(max(0, y - x) for (_, x), (_, y) in zip(werte, werte[1:]))
        dauer = (werte[-1][0] - erst) if erst is not None else 0
        erg[w] = {"erste_lieferung_tick": erst, "zuwachs": zuwachs, "je_1000_ticks": round(1000.0 * zuwachs / dauer, 1) if dauer else 0}
    lagerort = bau.get("lager")
    wege = {k: (schach(bau[k], lagerort) if bau.get(k) and lagerort else None) for k in ("steinbruch", "eisenmine", "holzfaeller")}
    wege["apfel->kornspeicher"] = schach(bau["apfel"], bau["kornspeicher"]) if bau.get("apfel") and bau.get("kornspeicher") else None
    wege["jaeger->kornspeicher"] = schach(bau["jaeger"], bau["kornspeicher"]) if bau.get("jaeger") and bau.get("kornspeicher") else None
    ergebnis = {"bauten": bau, "ertrag": erg, "preise": preis, "wege": wege, "ticks": ticks}
    json.dump(ergebnis, open(os.path.join(D, "ertrag_messung.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(ergebnis, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    import selfaware.game.ucp.befehl as befehlskanal
    befehlskanal._kanal_frei()        # laeuft schon ein anderer Lauf? dann sofort laut abbrechen
    befehlskanal.belege()
    try:
        main()
    finally:
        befehlskanal.freigeben()
