# -*- coding: utf-8 -*-
"""B-286 Schadens-Tagebuch und Eichkurve. Soll vorher festgelegt:
  1. 40 Runden zu 100 Takten, Vorhersage 10 je Takt, echt 300 je Runde -> Faktor der Stufe 0,30
  2. Runden im Nahkampf zaehlen nicht
  3. unter MIN_TAKTE: kein Faktor (None) - die Assassine nimmt ihren bisherigen Wert (0,33 ohne Profil)
  4. Stufen sind getrennt: eine andere Vorhersagestufe bleibt ohne Faktor
  5. je Einheitentyp eine Datei im Lernprofil, wieder gelesen
  7. (Teil 3) Gebaeude fiel, vier Armbrueste 15 Felder weg sieht sie jetzt -> DECKUNG WEG, wartet am Rueckzugspunkt, keine Zielwahl
  8. ohne Schuetzen -> keine DECKUNG-Meldung
  6. Assassinen._f: Stufe mit Messung -> Kurvenfaktor, Stufe ohne Messung -> bisheriger Wert
Aufruf: python schaden_kurve_pruefen.py"""
import os
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
os.environ.pop("SHC_LEARNING_DIR", None)
import schadens_tagebuch as S


def fuellen(k, runden, vorhersage, verlust, nah=False):
    leben = 12500.0
    for r in range(runden):
        k.runde(r * 100, {1: {"leben": leben, "nahangreifer": 1 if nah else 0}}, lambda n: vorhersage)
        leben -= verlust


def main():
    f = []
    k = S.Kurve(73)
    fuellen(k, 41, 10.0, 300)
    f.append(("1 Faktor Stufe 10/Takt = %s" % k.faktor(10.0), k.faktor(10.0) is not None and abs(k.faktor(10.0) - 0.30) < 0.01))
    k2 = S.Kurve(73)
    fuellen(k2, 41, 10.0, 300, nah=True)
    f.append(("2 Nahkampf zaehlt nicht: %s Takte" % k2.st[S.stufe(10.0)]["takte"], k2.st[S.stufe(10.0)]["takte"] == 0))
    k3 = S.Kurve(73)
    fuellen(k3, 5, 10.0, 300)
    f.append(("3 unter MIN_TAKTE: %s" % k3.faktor(10.0), k3.faktor(10.0) is None))
    f.append(("4 andere Stufe ohne Messung: %s" % k.faktor(300.0), k.faktor(300.0) is None))
    d = tempfile.mkdtemp()
    os.environ["SHC_LEARNING_DIR"] = d
    k5 = S.Kurve(73)
    fuellen(k5, 41, 10.0, 300)
    k5.schreiben()
    k5b = S.Kurve(73)
    os.environ.pop("SHC_LEARNING_DIR")
    f.append(("5 Datei je Typ geschrieben und gelesen", os.path.exists(os.path.join(d, "schadens_kurve_73.json"))
              and k5b.faktor(10.0) == k5.faktor(10.0)))
    import parteien
    parteien.setzen(1, {1})
    from funde_pruefen import neu
    t = neu()
    t._kurve = k
    f.append(("6 _f: Stufe gemessen %.3f, Stufe ohne Messung %.3f (bisher %.3f)" % (t._f(10.0), t._f(300.0), t._kalib()),
              abs(t._f(10.0) - 0.30) < 0.01 and t._f(300.0) == t._kalib()))
    # 7/8 (Teil 3) Deckung faellt: Gebaeude 900 zerstoert, eine Armbrust 15 Felder weg sieht sie jetzt -> sofort raus
    from funde_pruefen import einheit
    import assassinen as A
    A.Einzeln.PROBE = A.Einzeln.HIT_RUN = False

    def deckung(mit_schuetze):
        t = neu(); t._raid_plaetze = 99
        L = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000)}
        if mit_schuetze:                 # vier Armbrueste - gegen eine allein gewinnt GEGENSCHLAG (B-213) zu Recht
            for i in range(4):
                L[600 + i] = einheit(23, 2, 115 + i, 100, leben=17500)
        t.aufnehmen([100]); t.ziel[100] = 900; t.ziel_typ[900] = 3; t.befohlen[100] = 0
        L[100].update(laufx=100, laufy=100, zustand=107)
        erg, _ = t.schritt(L, {}, sichere_orte=[(50, 50)], tick=10000)
        return t, erg
    t7, e7 = deckung(True)
    t8, e8 = deckung(False)
    f.append(("7 Deckung fiel, vier Armbrueste sehen sie: %s, wartet %s" % ([z[:50] for z in e7 if "DECKUNG WEG" in z][:1], t7.warte.get(100)),
              any("DECKUNG WEG 100" in z for z in e7) and 100 in t7.warte and not any(z.startswith("ZIELWAHL 100") for z in e7)))
    f.append(("8 ohne Schuetzen keine DECKUNG-Meldung", not any("DECKUNG WEG" in z for z in e8)))
    A.Einzeln.PROBE = A.Einzeln.HIT_RUN = True
    for name, ok in f:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(bool(ok) for _, ok in f), len(f)))
    return all(ok for _, ok in f)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
