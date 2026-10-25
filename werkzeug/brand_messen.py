# -*- coding: utf-8 -*-
"""Zuendung durch Sklaven im Sandkasten messen (B-243, Daniel 25.10.2026 10:06: "im Spiel wirkt es sehr zufaellig, wann etwas
brennt und ob/wie das Feuer ueberspringt" - SRE liest im Code: beim zweiten Hieb sicher, Hieb alle 93 Takte).

Je Wiederholung: Sandkasten neu laden (shc.sandkasten), EIN Sklave (A_SLAVE 71) von Spieler 1 drei Felder neben ein brennbares
Gebaeude von Spieler 2 setzen, Angriffsbefehl auf das Gebaeude, Tempo 40, alle ~0,3 s lesen (Leitung): Takt, Zustand und Ort
des Sklaven, feuer/leben des Ziels und aller Gebaeude bis 8 Felder (Ueberspringen). Gemessen wird:
  kontakt   - erster Takt mit Zustand 106/107 (Abriss/Hieb) oder Abstand <= 2
  zuendung  - erster Takt mit feuer > 0 am Ziel; takte_bis_zuendung = zuendung - kontakt
  nachbarn  - Takt, an dem ein Nachbargebaeude feuer > 0 bekommt (Ueberspringen), bis NACH Takte nach der Zuendung
Mit unterbrechen=ja laeuft der Sklave UNTERBRECH_NACH Takte nach dem Kontakt 6 Felder weg (WEG Takte) und greift dann wieder an:
zaehlt der Hieb-Zaehler weiter (Zuendung kurz nach dem zweiten Kontakt) oder beginnt er von vorn (wieder ~186 Takte)?
Aufruf: SHC_INSTANZ=5 python werkzeug/brand_messen.py [wiederholungen=3] [unterbrechen=nein|ja] [nach=120] [typ=3]
Gemessen 25.10. 10:11 (Holzfaellerhuette 63, 3 Wiederholungen ohne Unterbrechung): Zuendung 151-153 Takte nach dem ersten
Kontakt (Abstand <= 2) - SRE-Code: eine Hieb-Animation 93 Takte, davor Anlauf/Drehen; mit Unterbrechung erst bei nach=120
kam die Zuendung (152) VOR dem Weglaufen - zweite Messung mit nach=40.
Ergebnis: eine Zeile je Wiederholung in daten/brand_messung.jsonl."""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
os.environ.setdefault("SHC_INSTANZ", "5")
D = os.path.join(HIER, "..", "daten")
NACH = 900                 # so viele Takte nach der Zuendung auf Ueberspringen warten
UNTERBRECH_NACH = 120      # Takte nach dem Kontakt weglaufen (nach dem ersten Hieb bei 93, vor dem zweiten bei 186)
WEG = 100                  # so lange weg bleiben
HOECHSTENS = 3000          # Takte je Wiederholung


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main(argv):
    arg = dict(a.split("=", 1) for a in argv if "=" in a)
    wdh, unterbrechen, typ = int(arg.get("wiederholungen", 3)), arg.get("unterbrechen", "nein") == "ja", int(arg.get("typ", 3))
    global UNTERBRECH_NACH
    UNTERBRECH_NACH = int(arg.get("nach", UNTERBRECH_NACH))
    tempo = int(arg.get("tempo", 10))        # 10: eine Lesung je ~10-20 Takte (bei 40 lagen 150 Takte zwischen zwei Lesungen)
    import shc
    from laden import befehl
    from befehl import SPIEL
    sys.path.insert(0, os.path.join(HIER, "..", "..", "Selfaware-AI-kern", "src"))
    from selfaware.game.kern_leitung import Leitung
    aus = []
    for w_i in range(wdh):
        print("OK:", shc.sandkasten(), flush=True)
        w = Leitung(SPIEL).lesen()
        lord1 = next(((e["x"], e["y"]) for e in w.einheiten.values() if e["typ"] == 55 and e["besitzer"] == 1), (0, 0))
        ziele = sorted((g for g in w.gebaeude.values() if g.get("besitzer") == 2 and g["typ"] == typ and g.get("feuer", 0) == 0),
                       key=lambda g: schach((g["x"], g["y"]), lord1))
        if not ziele:
            raise shc.Fehler("kein Gebaeude Typ %d von Spieler 2 im Sandkasten" % typ)
        z = ziele[0]
        zp = (z["x"], z["y"])
        nachbarn = {g["nr"]: (g["x"], g["y"], g["typ"]) for g in w.gebaeude.values()
                    if g["nr"] != z["nr"] and g.get("besitzer") == 2 and schach((g["x"], g["y"]), zp) <= 8}
        text = shc.setze(spieler="1", typ="71", x=str(zp[0] - 3), y=str(zp[1]), anzahl="1")
        nr = int(text.split("Nummern")[1].strip(" []").split(",")[0])
        print("Ziel Nr %d Typ %d bei %s (Leben %s), Sklave %d, %d Nachbarn bis 8 Felder" % (z["nr"], typ, zp, z.get("leben"), nr, len(nachbarn)), flush=True)
        befehl({"angriff": {"einheiten": [nr], "gebaeude": z["nr"]}}, 1.0)
        befehl({"pause": False, "tempo": tempo}, 0.3)
        t0 = Leitung(SPIEL).lesen().tick
        spur, kontakt, zuendung, weg_ab, zurueck, unterbrochen = [], None, None, None, None, False
        nachbar_feuer = {}
        letzter = None
        ende = time.time() + 600
        while time.time() < ende:
            w = Leitung(SPIEL).lesen()
            t = w.tick
            if t == letzter:
                time.sleep(0.05)
                continue
            letzter = t
            s = w.einheiten.get(nr)
            g = w.gebaeude.get(z["nr"])
            if s is None or g is None:
                spur.append((t, "weg"))
                break
            zust, ort = s["zustand"], (s["x"], s["y"])
            spur.append((t, zust, ort[0], ort[1], g.get("feuer", 0), g.get("leben")))
            if kontakt is None and (zust in (106, 107) or schach(ort, zp) <= 2):
                kontakt = t
            if unterbrechen and kontakt is not None and not unterbrochen and t - kontakt >= UNTERBRECH_NACH and zuendung is None:
                befehl({"angriff": {"einheiten": [nr], "lauf": [zp[0] - 8, zp[1]]}}, 0.5)
                weg_ab, unterbrochen = t, True
            if unterbrochen and zurueck is None and t - weg_ab >= WEG:
                befehl({"angriff": {"einheiten": [nr], "gebaeude": z["nr"]}}, 0.5)
                zurueck = t
            if zuendung is None and g.get("feuer", 0) > 0:
                zuendung = t
            for n_, (x_, y_, t_) in nachbarn.items():
                gn = w.gebaeude.get(n_)
                if gn is not None and gn.get("feuer", 0) > 0 and n_ not in nachbar_feuer:
                    nachbar_feuer[n_] = (t, t_, schach((x_, y_), zp))
            if (zuendung is not None and t - zuendung >= NACH) or t - t0 >= HOECHSTENS:
                break
            time.sleep(0.05)
        befehl({"pause": True}, 0.3)
        erg = {"wiederholung": w_i + 1, "typ": typ, "unterbrech_nach": UNTERBRECH_NACH if unterbrechen else None, "ziel": z["nr"], "ort": list(zp), "leben_start": z.get("leben"), "sklave": nr,
               "unterbrochen": unterbrechen, "t0": t0, "kontakt": kontakt, "weg_ab": weg_ab, "zurueck": zurueck, "zuendung": zuendung,
               "takte_bis_zuendung": (zuendung - kontakt) if (zuendung is not None and kontakt is not None) else None,
               "takte_ab_rueckkehr": (zuendung - zurueck) if (zuendung is not None and zurueck is not None) else None,
               "nachbarn": len(nachbarn), "nachbar_feuer": {str(k): v for k, v in nachbar_feuer.items()},
               "zustaende": sorted({p[1] for p in spur if len(p) > 2}), "spur_ende": spur[-1] if spur else None,
               "zeit": time.strftime("%Y-%m-%d %H:%M")}
        aus.append(erg)
        with open(os.path.join(D, "brand_messung.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(erg) + "\n")
        print("OK: Wdh %d: Kontakt %s, Zuendung %s (%s Takte nach Kontakt%s), Nachbarn mit Feuer %d von %d, Zustaende %s" % (
            w_i + 1, kontakt, zuendung, erg["takte_bis_zuendung"],
            ", %s nach Rueckkehr" % erg["takte_ab_rueckkehr"] if zurueck else "", len(nachbar_feuer), len(nachbarn), erg["zustaende"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
