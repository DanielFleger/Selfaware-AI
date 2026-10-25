# -*- coding: utf-8 -*-
"""B-251 Pruefung des Auges am laufenden Spiel (Sandkasten, Instanz aus SHC_INSTANZ).

Punkt 2 (Geschosse): stimmt die vorhergesagte Ankunft (sre_rest_takte) mit dem echten Aufschlag ueberein? Ist der
Schuetze (unitID_OR_seaGullID) ein Bogenschuetze, das Ziel (unitID) ein Feind, der Abschuss-Takt (field21_0x34) der
Takt des ersten Auftauchens?
Punkt 1 (Wegpunkte): welche Halbbyte-Reihenfolge und Richtungszuordnung des Wegplans (pathPlanStart) passt zu den
Feldern, die die Einheit danach wirklich betritt?

Ablauf: freie Reihe nahe unserem Burgherrn suchen, Bogenschuetzen (E_ARCHER 22) und Speertraeger (E_SPEAR 24) des
Gegners setzen, Spiel laufen lassen, alle ~20 ms ein Auge-Schnappschuss, danach anhalten und auswerten.
Totschlagtest vorher festgelegt: Ankunft daneben > 3 Takte im Mittel = Flugformel falsch; keine Wegplan-Variante mit
>= 80 % Treffern = Wegplan-Lesart falsch.
"""
import json
import os
import sys
import threading
import time

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER))
import auge  # noqa: E402
import shc  # noqa: E402
import speicher  # noqa: E402
from laden import befehl  # noqa: E402

DATEN = os.path.join(os.path.dirname(os.path.dirname(HIER)), "daten")


def freie_reihe(lord, laenge, suchweite=40):
    k = speicher.wegkarte()
    frei = (k["gebiet"] > 0) & (k["gebaeude"] == 0) & (k["hoehe"] == k["boden"])
    lx, ly = lord
    beste = None
    for dy in range(-suchweite, suchweite + 1):
        y = ly + dy
        if not (2 <= y < 398):
            continue
        for dx in range(-suchweite, suchweite + 1):
            x0 = lx + dx
            if not (2 <= x0 and x0 + laenge < 398):
                continue
            if frei[x0:x0 + laenge, y].all() and len(set(k["gebiet"][x0:x0 + laenge, y].tolist())) == 1:
                d = abs(dx) + abs(dy)
                if beste is None or d < beste[0]:
                    beste = (d, x0, y)
    return beste


class Aufnehmer(threading.Thread):
    def __init__(self, pfad, spieler=(1, 2), alle_ms=20.0):
        super(Aufnehmer, self).__init__(daemon=True)
        self.pfad, self.spieler, self.alle, self.lauf, self.n = pfad, spieler, alle_ms / 1000.0, True, 0
        self.fehler = None

    def run(self):
        """Erst nur lesen und behalten (3 ms je Takt), nach dem Lauf serialisieren - sonst kommt nur jeder 3. Takt."""
        letzter = None
        self.roh = []
        hoehe = None
        while self.lauf:
            try:
                s = auge.Schnappschuss(mit_trupps=False, mit_feldern=hoehe is None)
                if hoehe is None:
                    hoehe = s.hoehe
            except Exception as e:  # noqa: BLE001
                self.fehler = repr(e)
                time.sleep(0.1)
                continue
            if s.takt != letzter:
                d = s.behalten(self.spieler)
                d["hoehe"] = hoehe
                self.roh.append(d)
                self.n += 1
                letzter = s.takt
            if self.alle > 0:
                time.sleep(self.alle)

    def schreiben(self):
        with open(self.pfad, "w", encoding="utf-8") as f:
            for d in self.roh:
                s = auge.Schnappschuss.aus_behalten(d)
                e = s.entities
                roh_e = [[int(s._id("entities", i)), int(e[i]["entityType"]), int(e[i]["logicalState"]), int(e[i]["uid"])]
                         for i in range(len(e))]
                f.write(json.dumps({"kopf": s.kopf(), "geschosse": s.geschosse(), "einheiten": s.einheiten_liste(self.spieler),
                                    "entities_roh": roh_e}, ensure_ascii=False) + "\n")


RICHTUNGEN = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


def wegplan_varianten(plan, idx, n, x, y, schritte=6, ab=0):
    """{variante: [(x, y), ...]} fuer Halbbyte-Reihenfolge x Drehung x Drehsinn. plan beginnt bei Byte `ab`."""
    aus = {}
    for reihenfolge in ("tief_zuerst", "hoch_zuerst"):
        nibbles = []
        for k in range(idx, min(n, idx + schritte)):
            if k // 2 - ab >= len(plan):
                break
            b = int(plan[k // 2 - ab])
            lo, hi = b & 0xF, b >> 4
            nibbles.append((lo if k % 2 == 0 else hi) if reihenfolge == "tief_zuerst" else (hi if k % 2 == 0 else lo))
        for dreh in range(8):
            for sinn in (1, -1):
                px, py, pfad = x, y, []
                for d in nibbles:
                    dx, dy = RICHTUNGEN[((d & 7) * sinn + dreh) % 8]
                    px, py = px + dx, py + dy
                    pfad.append((px, py))
                aus["%s/dreh%d/%s" % (reihenfolge, dreh, "cw" if sinn == 1 else "ccw")] = pfad
    return aus


def auswerten(pfad):
    zeilen = [json.loads(z) for z in open(pfad, encoding="utf-8") if z.strip()]
    takte = [z["kopf"]["takt"] for z in zeilen]
    # --- Geschosse: je uid erste und letzte Sichtung
    flug = {}
    for z in zeilen:
        for g in z["geschosse"]:
            e = flug.setdefault(g["uid"], {"erst": None, "letzt_flug": None, "erst_liegt": None, "reihe": []})
            e["reihe"].append((z["kopf"]["takt"], g))
            if e["erst"] is None:
                e["erst"] = (z["kopf"]["takt"], z["kopf"]["takt_kern"], g)
            if g["sre_zustand"] == "fliegt":
                e["letzt_flug"] = (z["kopf"]["takt"], g)
            elif e["erst_liegt"] is None:
                e["erst_liegt"] = (z["kopf"]["takt"], g)
    einheit_art = {}
    for z in zeilen:
        for u in z["einheiten"]:
            einheit_art[u["id"]] = (u["unitType"], u["owner"])
    geschosse = []
    verschwunden = []
    for uid, e in flug.items():
        t0, tk0, g0 = e["erst"]
        if g0["sre_zustand"] == "fliegt" and e["erst_liegt"] is None and e["letzt_flug"] is not None:
            tl, gl = e["letzt_flug"]
            bahn = g0.get("sre_bahn") or []
            verschwunden.append({"uid": uid, "erst_takt": t0, "erst_travelled": g0["travelledDistance"], "letzt_takt": tl,
                                 "letzt_feld": gl["jetzt_feld"], "letzt_h": gl["jetzt_mikro"][2], "ziel_feld": g0["ziel_feld"],
                                 "ziel_einheit": g0["unitID"], "bahn_landung_takt": (t0 + bahn[-1][0]) if bahn else None,
                                 "abschuss_minus_kern": g0["field21_0x34"] - tk0})
        if g0["sre_zustand"] != "fliegt" or e["erst_liegt"] is None:
            continue
        t_liegt = e["erst_liegt"][0]
        vorher = g0["sre_rest_takte"]
        echt = t_liegt - t0
        # Schrittweite je Takt gemessen: travelledDistance-Zuwachs zwischen zwei Sichtungen
        r = [(t, g["travelledDistance"]) for t, g in e["reihe"] if g["sre_zustand"] == "fliegt"]
        je_takt = None
        if len(r) >= 2 and r[-1][0] > r[0][0]:
            je_takt = (r[-1][1] - r[0][1]) / float(r[-1][0] - r[0][0])
        gl = e["erst_liegt"][1]
        bahn = g0.get("sre_bahn") or []
        land = bahn[-1] if bahn else None
        geschosse.append({"bahn_landung_takt_vorher": (t0 + land[0]) if land else None, "bahn_landung_feld": land[4:6] if land else None,
                          "bahn_landung_abweichung_takte": ((t0 + land[0]) - t_liegt) if land else None,
                          "bahn_laenge": len(bahn),"uid": uid, "art": g0["sre_art"], "erst_takt": t0, "abschuss_feld": g0["field21_0x34"],
                          "abschuss_minus_kern": g0["field21_0x34"] - tk0, "schuetze": g0["unitID_OR_seaGullID"],
                          "schuetze_art": einheit_art.get(g0["unitID_OR_seaGullID"]), "ziel_einheit": g0["unitID"],
                          "ziel_art": einheit_art.get(g0["unitID"]), "rest_takte_vorhergesagt": vorher,
                          "takte_bis_liegt": echt, "abweichung": echt - vorher,
                          "je_takt_vorhergesagt": g0["sre_mikroschritte_je_takt"], "je_takt_gemessen": je_takt,
                          "gesamt": g0["field58_0x8c"], "travelled_am_ende": gl["travelledDistance"],
                          "ziel_feld": g0["ziel_feld"], "liegt_feld": gl["jetzt_feld"],
                          "ziel_getroffen_feld": gl["jetzt_feld"] == g0["ziel_feld"]})
    # --- Wegplan: je Einheit und Schnappschuss mit Restweg die naechsten echten Felder
    pos = {}   # id -> [(takt, (x, y))]
    for z in zeilen:
        for u in z["einheiten"]:
            pos.setdefault(u["id"], []).append((z["kopf"]["takt"], tuple(u["feld"])))
    treffer = {}
    proben = 0
    for z in zeilen:
        for u in z["einheiten"]:
            idx, n = u["currentIndexInPathPlan"], u["totalSizeOfPathPlan"]
            if n <= idx or n > 800 or u["state"] != 101:
                continue
            # echte Folge der naechsten Felder nach diesem Takt
            folge, letzte = [], tuple(u["feld"])
            for t, p in pos[u["id"]]:
                if t <= z["kopf"]["takt"]:
                    continue
                if p != letzte:
                    folge.append(p)
                    letzte = p
                if len(folge) >= 4:
                    break
            if len(folge) < 2:
                continue
            proben += 1
            if not u.get("wegplan_roh"):
                continue
            roh = bytes.fromhex(u["wegplan_roh"])
            for name, pf in wegplan_varianten(roh, idx, n, u["feld"][0], u["feld"][1], schritte=len(folge),
                                              ab=u.get("wegplan_roh_ab", 0)).items():
                ok = sum(1 for a, b in zip(pf, folge) if a == b)
                t = treffer.setdefault(name, [0, 0])
                t[0] += ok
                t[1] += len(folge)
    beste = sorted(((v[0] / float(v[1]) if v[1] else 0, k, v) for k, v in treffer.items()), reverse=True)[:5]
    return {"takte": [min(takte), max(takte)] if takte else None, "schnappschuesse": len(zeilen),
            "takt_luecken": int(sum(1 for a, b in zip(takte, takte[1:]) if b - a > 1)),
            "geschosse": geschosse, "verschwunden": verschwunden, "wegplan_proben": proben, "wegplan_beste": beste}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dauer", type=float, default=12.0)
    ap.add_argument("--abstand", type=int, default=12)
    ap.add_argument("--schuetzen", type=int, default=4)
    ap.add_argument("--speere", type=int, default=3)
    ap.add_argument("--nur_auswerten", default="")
    a = ap.parse_args()
    if a.nur_auswerten:
        print(json.dumps(auswerten(a.nur_auswerten), ensure_ascii=False, indent=1))
        return 0
    z = shc.zustand()
    print("Zustand:", z["text"])
    if z.get("gameover") or not z.get("pause"):
        print("FEHLER: Partie nicht bespielbar oder nicht angehalten:", z)
        return 1
    s = auge.Schnappschuss(mit_trupps=False, mit_feldern=False)
    lord = next((p["lord"]["feld"] for p in s.spieler_liste() if p["spieler"] == 1 and "feld" in p["lord"]), None)
    print("Takt", s.takt, "Lord Spieler 1 bei", lord)
    reihe = freie_reihe(lord, a.abstand + 4)
    if not reihe:
        print("FEHLER: keine freie Reihe gefunden")
        return 1
    _, x0, y = reihe
    print("freie Reihe ab", (x0, y))
    print(shc.setze("1", "22", str(x0), str(y), str(a.schuetzen)))
    print(shc.setze("2", "24", str(x0 + a.abstand), str(y), str(a.speere)))
    stempel = time.strftime("%Y%m%d_%H%M%S")
    pfad = os.path.join(DATEN, "auge_pruefung_%s.jsonl" % stempel)
    rec = Aufnehmer(pfad, alle_ms=0.0)
    rec.start()
    time.sleep(0.3)
    befehl({"pause": False, "tempo": 40}, 0.3)
    t0 = time.time()
    time.sleep(a.dauer)
    befehl({"pause": True}, 0.3)
    rec.lauf = False
    rec.join(2.0)
    rec.schreiben()
    print("Aufnahme %.1f s, %d Schnappschuesse -> %s (Fehler: %s)" % (time.time() - t0, rec.n, pfad, rec.fehler))
    erg = auswerten(pfad)
    aus = os.path.join(DATEN, "auge_pruefung_%s.json" % stempel)
    json.dump(erg, open(aus, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in erg.items() if k != "geschosse"}, ensure_ascii=False))
    for g in erg["geschosse"][:12]:
        print(" ", json.dumps(g, ensure_ascii=False))
    for g in erg["verschwunden"][:12]:
        print("  weg:", json.dumps(g, ensure_ascii=False))
    print("Ergebnis ->", aus)
    return 0


if __name__ == "__main__":
    sys.exit(main())
