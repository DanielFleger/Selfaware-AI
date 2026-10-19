# -*- coding: utf-8 -*-
"""Raids messen, bevor sie gebaut werden (Daniel 19.10. 16:57: "Sklaven waeren als Raid besonders am Anfang einer Partie
richtig OP - kosten wenig, und wenn Feuer erkannt werden kann, koenntest du so gut wie alles anzuenden, das waere billiger als
Assassinen"; "gesteuerte berittene Bogenschuetzen, die ja im Reiten schiessen koennen, koennten sehr pervers sein").

Bekannt: Sklave 5 Gold / 6.000 Leben, Pferdebogen 75 / 15.000 (L63); Sklave 12 Takte je Feld (L80). Websuche 19.10. (nur
Fan-Quellen, Crusader 2 / Definitive Edition): Sklaven tragen Fackeln und zuenden Gebaeude an, Feuer springt auf Nachbarn
ueber, Brunnen daemmen es ein; Pferdebogen schiesst im Reiten in jede Richtung. Fuer das Original NICHT belegt - darum hier.
Feuer am Gebaeude (Ghidra, daten/struktur_Building.txt): fireDuration short bei +702, ifFireThenResponsiblePlayer bei +734,
Ghidra-Offsets ab Datensatz + 0x14 (Probe: currentHealth +268 + 0x14 = 0x120 = G_LEBEN in logik.lua).

VORHER FESTGELEGT (Totschlagtest):
  M1 Sklave (Spieler 2) greift ein Gebaeude von Spieler 1 an (angriff "gebaeude", Art 9), 1.500 Ticks:
     BRAND belegt, wenn fireDuration am Ziel > 0 wird; UEBERGREIFEN belegt, wenn ein Nachbar (<= 2 Felder) danach > 0 hat;
     gemessen dazu: Leben des Ziels ueber die Zeit, zerstoert ja/nein und wann, lebt der Sklave.
  M1g Gegenprobe: ein Speertraeger (24) mit demselben Befehl auf ein gleichartiges Gebaeude -> fireDuration bleibt 0
     (sonst misst M1 nicht die Fackel).
  M2 Pferdebogen (Spieler 2) greift einen Holzfaeller (Einheit Typ 3) von Spieler 1 an: Ticks bis zum Tod.
  M2b nach dem ersten Treffer ein Laufbefehl 15 Felder weg: SCHIESST IM REITEN belegt, wenn das Ziel Leben verliert, waehrend
     sich der Pferdebogen zwischen zwei Proben bewegt hat; widerlegt, wenn ab dem Laufbefehl kein Treffer mehr kommt.
Aufruf (Spiel steht, Lenker aus, Testsperre): SHC_INSTANZ=4 python raid_messen.py [stand="Walltest 4"] [nur=m0,m1,m1g,m2]
Ergebnis: daten/raid_messung_<stempel>.json"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import befehl as K
from editor_messen import lage, setze
from laden import peek, befehl, lade_stand
from steuerkarte import tick

D = os.path.join(HIER, "..", "daten")
GEBAEUDE, G_SCHRITT = 0xF98520, 0x32C
FEUER, FEUER_WER = 0x14 + 702, 0x14 + 734
SKLAVE, SPEER, PFERDEBOGEN, HOLZFAELLER = 71, 24, 74, 3
ZIELARTEN = (3, 32, 31, 1, 30)          # Holzfaeller, Apfel, Hopfen, Huette, Getreide
NACHBAR_R = 3                            # 17:20: in "Walltest 4" hatte kein Ziel Nachbarn <= 2 Felder


def gebaeude():
    from waechter import lies_gebaeude
    K.sende({"befehle": [{"player": 1, "id": K.neue_id(), "lagebild": True}]}, 3.0, bis="LAGEBILD")
    return lies_gebaeude()


def feuer(nr):
    w = peek(GEBAEUDE + nr * G_SCHRITT + FEUER)[0]
    v = peek(GEBAEUDE + nr * G_SCHRITT + FEUER_WER)[0]
    return w & 0xFFFF, v & 0xFFFF


def groesse(typ):
    try:
        import bauen
        return bauen.NACH_TYP.get(typ, {"b": 2})["b"]
    except Exception:
        return 2


def abstand(g, h):
    bg, bh = groesse(g["typ"]), groesse(h["typ"])
    dx = max(h["x"] - (g["x"] + bg - 1), g["x"] - (h["x"] + bh - 1), 0)
    dy = max(h["y"] - (g["y"] + bg - 1), g["y"] - (h["y"] + bh - 1), 0)
    return max(dx, dy)


def warte_ticks(n, sekunden=60):
    t0 = tick() or 0
    ende = time.time() + sekunden
    while time.time() < ende and (tick() or 0) < t0 + n:
        time.sleep(0.3)


def ziel_mit_nachbarn(G, ausser=()):
    """Ein Gebaeude von Spieler 1 (Art aus ZIELARTEN) mit moeglichst vielen Nachbarn <= 2 Felder."""
    eig = {n: g for n, g in G.items() if g["besitzer"] == 1 and n not in ausser}
    best = None
    for n, g in eig.items():
        if g["typ"] not in ZIELARTEN:
            continue
        nb = [m for m, h in eig.items() if m != n and abstand(g, h) <= NACHBAR_R]
        if best is None or len(nb) > len(best[1]):
            best = (n, nb)
    return best


def brand_versuch(typ_einheit, ticks=1500, ausser=(), weg_nach_brand=False):
    """weg_nach_brand (M1c, 17:23): sobald das Ziel brennt, laeuft die Einheit 15 Felder weg - brennt es allein ab?"""
    G = gebaeude()
    wahl = ziel_mit_nachbarn(G, ausser)
    if wahl is None:
        return {"fehler": "kein Zielgebaeude"}
    nr, nachbarn = wahl
    g = G[nr]
    x, y = g["x"] - 6, g["y"]
    e = setze(2, typ_einheit, x, y)
    time.sleep(0.5)
    befehl({"player": 2, "angriff": {"einheiten": [e], "gebaeude": nr}}, 1.0, bis="ANGRIFF")
    t0 = tick() or 0
    reihe, brand_t, ueber_t, weg_t = [], None, None, None
    ende = time.time() + 120
    while time.time() < ende and (tick() or 0) < t0 + ticks:
        t = tick() or 0
        G2 = gebaeude()
        ziel = G2.get(nr)
        f_ziel = feuer(nr) if ziel else (0, 0)
        f_nb = {m: feuer(m)[0] for m in nachbarn if m in G2}
        _, L = lage()
        u = L.get(e)
        reihe.append({"t": t - t0, "ziel_leben": ziel["leben"] if ziel else None, "feuer": f_ziel[0], "verursacher": f_ziel[1],
                      "nachbarn_feuer": f_nb, "einheit_leben": u["leben"] if u and u["besitzer"] == 2 else None,
                      "einheit_zustand": u["zustand"] if u and u["besitzer"] == 2 else None})
        if brand_t is None and f_ziel[0] > 0:
            brand_t = t - t0
            if weg_nach_brand and u and u["besitzer"] == 2:
                befehl({"player": 2, "angriff": {"einheiten": [e], "lauf": [u["x"] - 15, u["y"]]}}, 1.0, bis="ANGRIFF")
        if ueber_t is None and any(v > 0 for v in f_nb.values()):
            ueber_t = t - t0
        if ziel is None and weg_t is None:
            weg_t = t - t0
        time.sleep(0.4)
    return {"einheit": typ_einheit, "ziel": nr, "ziel_typ": g["typ"], "nachbarn": nachbarn, "brand_tick": brand_t,
            "uebergreifen_tick": ueber_t, "zerstoert_tick": weg_t, "reihe": reihe}


def grube_abriss_versuch():
    """M0 (19.10., Kornring-Umbau L131): eine Fallgrube von Spieler 1 bauen und per Modulbefehl abreissen. Vorher festgelegt:
    gebaut -> Holz -4; 200 Ticks nach dem Abriss steht dort keine Grube mehr, Holz +2 (Haelfte, Abreissen.md A1/A2).
    Widerlegt, wenn die Grube danach noch steht."""
    from laden import peek as _peek
    PD = 0x0115BDF8
    holz = lambda: _peek(PD + 1 * 0x39F4 + 0x4D0 + 2 * 4)[0]
    G = gebaeude()
    eig = [g for g in G.values() if g["besitzer"] == 1 and g["typ"] not in (67,)]
    if not eig:
        return {"fehler": "kein Gebaeude von Spieler 1"}
    g = eig[0]
    import re
    z = " ".join(befehl({"player": 1, "platzsuche": {"spieler": 1, "mapper": 98, "groesse": 1, "x": g["x"] + 3, "y": g["y"] + 3,
                                                     "r": 8, "max": 1}}, 1.0, bis="PLATZSUCHE"))
    frei = [tuple(map(int, q)) for q in re.findall(r"\((\d+),(\d+)\)", z.split("geprueft:")[-1])]
    if not frei:
        return {"fehler": "kein Grubenplatz bei %s" % ((g["x"], g["y"]),)}
    p = frei[0]
    if holz() < 4:      # 17:20: "Walltest 4" hat 1 Holz - ein 5er-Los am Markt kaufen (Spielbefehl 38: kaufen = 0, Holz = 2)
        befehl({"player": 1, "spielbefehl": {"nr": 38, "werte": [0, 2]}}, 1.0, bis="SPIELBEFEHL")
        warte_ticks(20)
    h0 = holz()
    befehl({"player": 1, "baue": {"mapper": 98, "x": p[0], "y": p[1], "groesse": 1, "richtung": 0}}, 1.0, bis="BAUE")
    warte_ticks(60)
    G = gebaeude()
    nr = [n for n, b in G.items() if b["typ"] == 67 and (b["x"], b["y"]) == p]
    h1 = holz()
    if not nr:
        return {"platz": p, "gebaut": False, "holz": [h0, h1]}
    z2 = befehl({"player": 1, "abreissen": {"nr": nr[0]}}, 1.0, bis="ABREISSEN")
    warte_ticks(200)
    G = gebaeude()
    noch = [n for n, b in G.items() if b["typ"] == 67 and (b["x"], b["y"]) == p]
    return {"platz": p, "gebaut": True, "nr": nr[0], "holz": [h0, h1, holz()], "danach_steht": bool(noch),
            "modul": [l for l in z2 if "ABREISSEN" in l][-1:]}


def pferdebogen_versuch(ticks=2500, ziel_typ=None):
    """ziel_typ=24 (17:21): ein Holzfaeller starb am ersten Treffer - fuer "schiesst im Reiten" ein zaeheres Ziel (Speer)."""
    _, L = lage()
    hf = [n for n, u in L.items() if u["besitzer"] == 1 and u["typ"] == (ziel_typ or HOLZFAELLER) and u["leben"] > 0]
    if ziel_typ:
        G = gebaeude()
        g = next((g for g in G.values() if g["besitzer"] == 1), None)
        hf = [setze(1, ziel_typ, g["x"] + 6, g["y"] + 6)] if g else []
        time.sleep(0.5)
        _, L = lage()                      # 17:22: neu lesen - sonst fehlt die eben gesetzte Einheit (KeyError)
        hf = [n for n in hf if n in L]
    if not hf:
        # 17:20: in "Walltest 4" hat Spieler 1 keine Holzfaeller - einen setzen (gleiches Leben wie ein arbeitender)
        G = gebaeude()
        g = next((g for g in G.values() if g["besitzer"] == 1), None)
        if g is None:
            return {"fehler": "kein Holzfaeller und kein Gebaeude von Spieler 1"}
        n = setze(1, HOLZFAELLER, g["x"] + 6, g["y"] + 6)
        time.sleep(0.5)
        _, L = lage()
        hf = [n] if n in L else []
        if not hf:
            return {"fehler": "Holzfaeller setzen fehlgeschlagen"}
    z = hf[0]
    zx, zy = L[z]["x"], L[z]["y"]
    p = setze(2, PFERDEBOGEN, zx - 12, zy)
    time.sleep(0.5)
    befehl({"player": 2, "angriff": {"einheiten": [p], "ziel": z}}, 1.0, bis="ANGRIFF")
    t0 = tick() or 0
    reihe, erster, gelaufen, tod = [], None, None, None
    vorher = None
    ende = time.time() + 150
    while time.time() < ende and (tick() or 0) < t0 + ticks:
        t = tick() or 0
        _, L = lage()
        uz, up = L.get(z), L.get(p)
        zl = uz["leben"] if uz and uz["besitzer"] == 1 else 0
        pos = (up["x"], up["y"]) if up else None
        reihe.append({"t": t - t0, "ziel_leben": zl, "pferd": pos, "zustand": up["zustand"] if up else None,
                      "gelaufen": gelaufen is not None})
        if erster is None and vorher is not None and zl < vorher["ziel_leben"]:
            erster = t - t0
            # M2b: jetzt weglaufen lassen (15 Felder seitlich)
            if pos:
                befehl({"player": 2, "angriff": {"einheiten": [p], "lauf": [pos[0], pos[1] + 15]}}, 1.0, bis="ANGRIFF")
                gelaufen = t - t0
        if zl <= 0 and tod is None:
            tod = t - t0
            break
        vorher = reihe[-1]
        time.sleep(0.3)
    im_reiten = []
    for a, b in zip(reihe, reihe[1:]):
        if a["gelaufen"] and b["ziel_leben"] < a["ziel_leben"] and a["pferd"] and b["pferd"] and a["pferd"] != b["pferd"]:
            im_reiten.append((b["t"], a["ziel_leben"] - b["ziel_leben"]))
    return {"ziel": z, "erster_treffer": erster, "laufbefehl": gelaufen, "tod": tod, "treffer_im_reiten": im_reiten,
            "reihe": reihe}


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    nur = set(arg.get("nur", "m0,m1,m1g,m2").split(","))
    stand = arg.get("stand", "Walltest 4")
    from serie import zuruecksetzen
    print("Zuruecksetzen:", zuruecksetzen(), flush=True)
    print("geladen bei Tick", lade_stand(stand, mit_bild=False), flush=True)
    befehl({"eigenerPlatz": 1}, 0.8)
    befehl({"pause": False}, 0.5)
    warte_ticks(50)
    erg = {"stand": stand}
    if "m0" in nur:
        erg["m0"] = grube_abriss_versuch()
        m = erg["m0"]
        print("M0 Grube abreissen: %s" % {k: v for k, v in m.items()}, flush=True)
    if "m1" in nur:
        erg["m1"] = brand_versuch(SKLAVE)
        m = erg["m1"]
        print("M1 Sklave: Ziel %s (Typ %s), Brand bei %s, uebergreifen bei %s, zerstoert bei %s" % (
            m.get("ziel"), m.get("ziel_typ"), m.get("brand_tick"), m.get("uebergreifen_tick"), m.get("zerstoert_tick")), flush=True)
    if "m1c" in nur:
        erg["m1c"] = brand_versuch(SKLAVE, ticks=2000, weg_nach_brand=True)
        m = erg["m1c"]
        print("M1c Sklave zuendet und geht: Ziel %s, Brand bei %s, zerstoert bei %s, Leben/Feuer zuletzt %s" % (
            m.get("ziel"), m.get("brand_tick"), m.get("zerstoert_tick"),
            [(r["t"], r["ziel_leben"], r["feuer"], r["einheit_zustand"]) for r in m.get("reihe", [])[::6]][:12]), flush=True)
    if "m1g" in nur:
        erg["m1g"] = brand_versuch(SPEER, ausser=(erg.get("m1", {}).get("ziel"),) + tuple(erg.get("m1", {}).get("nachbarn", ())))
        m = erg["m1g"]
        print("M1g Speer (Gegenprobe): Ziel %s, Brand bei %s, zerstoert bei %s" % (
            m.get("ziel"), m.get("brand_tick"), m.get("zerstoert_tick")), flush=True)
    if "m2b" in nur:
        erg["m2b"] = pferdebogen_versuch(ziel_typ=SPEER)
        m = erg["m2b"]
        print("M2b Pferdebogen gegen Speer: erster Treffer %s, Laufbefehl %s, Ziel tot %s, Treffer im Reiten %s" % (
            m.get("erster_treffer"), m.get("laufbefehl"), m.get("tod"), m.get("treffer_im_reiten")), flush=True)
    if "m2" in nur:
        erg["m2"] = pferdebogen_versuch()
        m = erg["m2"]
        print("M2 Pferdebogen: erster Treffer %s, Laufbefehl %s, Ziel tot %s, Treffer im Reiten %s" % (
            m.get("erster_treffer"), m.get("laufbefehl"), m.get("tod"), m.get("treffer_im_reiten")), flush=True)
    befehl({"pause": True}, 0.5)
    pfad = os.path.join(D, "raid_messung_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(erg, open(pfad, "w", encoding="utf-8"), ensure_ascii=False)
    print("gesichert:", pfad)


if __name__ == "__main__":
    main()
