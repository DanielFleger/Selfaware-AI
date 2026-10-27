# -*- coding: utf-8 -*-
"""B-278 lernende Eichung, Probe-Assassine, Hit & Run (Plan_Assassinen_Risiko.md; Daniel 23:27/23:30).
Soll vorher festgelegt:
  1. ohne Lernprofil: KALIB = 0,33 (alter Wert, die alten Pruefungen bleiben gleich)
  2. vorhergesagt 10.000, echt 1.500 -> KALIB sinkt; vorhergesagt 10.000, echt 20.000 -> KALIB steigt
  3. Nachlauf: ein Treffer 100 Takte nach dem Zielende zaehlt zum Angriff (Frage-Agent 23:32, Frage 2)
  4. Tod zaehlt das ganze Leben; Angriffe mit Nahkampf zaehlen nicht
  5. Lernprofil: Datei geschrieben und von einer neuen Eichung wieder gelesen
  6. Ziel nur ueber einen Weg im Blick eines Bogens mit Spaeher: ohne Probe kein Ziel; mit Probe PROBE-Zeile und Ziel
  7. nie zwei Proben zugleich; nicht unter PROBE_LEBEN
  9. (B-279) Assassine AM Gebaeude, Arbeiter 1 Feld daneben -> kein Mitnehmen, Ziel bleibt
 10. (B-279) unterwegs (Gebaeude 30 Felder weg) nimmt sie den Arbeiter mit; ist er tot -> zurueck zu ihrem Gebaeude
 11. (B-279) Eichung zaehlt nur Angriffe, die am Ziel ankamen (oder mit Tod endeten)
  8. Hit & Run: entdeckt (Armbrust visiert ihn an), nicht getroffen, Runde 15 Takte -> arbeitet weiter, Ziel bleibt;
     Runde 106 Takte (gemessen Partie 232139) -> "kein Hit & Run", die alten Regeln (fertig machen, Gegenwert, raus) entscheiden
Aufruf: python risiko_lernen_pruefen.py"""
import os
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
os.environ.pop("SHC_LEARNING_DIR", None)
import parteien
parteien.setzen(1, {1})
import risiko_lernen as RL
import assassinen as A
from funde_pruefen import neu, einheit


def main():
    f = []
    e = RL.Eichung()
    f.append(("1 ohne Profil KALIB %.3f" % e.kalib, abs(e.kalib - 0.33) < 1e-9 and e.datei is None))

    def angriff(vorher, leben_danach, tot=False, nah=False, spaet=None):
        e = RL.Eichung()
        e.start(1, 900, vorher, 12500, 0)
        e.runde({1: {"leben": 12500, "nahangreifer": 1 if nah else 0}}, {1: 900}, 100)
        if tot:
            return e, e.runde({}, {}, 200)
        e.runde({1: {"leben": leben_danach}}, {}, 200)                 # Ziel weg (z. B. ENTDECKT)
        if spaet is not None:
            e.runde({1: {"leben": spaet}}, {}, 300)                    # Treffer auf der Flucht
        return e, e.runde({1: {"leben": spaet if spaet is not None else leben_danach}}, {}, 200 + RL.NACHLAUF)
    e_ab, m_ab = angriff(10000, 11000)
    e_auf, _ = angriff(10000, 12500 - 20000 if False else 0)
    e_auf2 = RL.Eichung(); e_auf2.start(1, 9, 10000, 30000, 0); e_auf2.runde({1: {"leben": 10000}}, {}, 10)
    m_auf2 = e_auf2.runde({1: {"leben": 10000}}, {}, 10 + RL.NACHLAUF)
    f.append(("2 lernt: echt 1.500 -> %.3f (sinkt), echt 20.000 -> %.3f (steigt)" % (e_ab.kalib, e_auf2.kalib),
              e_ab.kalib < 0.33 < e_auf2.kalib and m_ab and m_auf2))
    e_n, m_n = angriff(10000, 12500, spaet=9000)
    f.append(("3 Nachlauf: Treffer nach Zielende zaehlt (%s)" % (m_n[0][-90:] if m_n else m_n), m_n and "echt 3500" in m_n[0]))
    e_t, m_t = angriff(10000, 0, tot=True)
    e_h, m_h = angriff(10000, 2000, nah=True)
    f.append(("4 Tod = ganzes Leben, Nahkampf zaehlt nicht", m_t and "echt 12500" in m_t[0] and e_h.zahl == 0 and e_h.nahkampf == 1))
    d = tempfile.mkdtemp()
    os.environ["SHC_LEARNING_DIR"] = d
    e5 = RL.Eichung(); e5.start(1, 9, 10000, 12500, 0); e5.runde({}, {}, 50)
    e5b = RL.Eichung()
    os.environ.pop("SHC_LEARNING_DIR")
    f.append(("5 Lernprofil geschrieben und gelesen (%.3f = %.3f)" % (e5.kalib, e5b.kalib),
              os.path.exists(os.path.join(d, "assassinen_eichung.json")) and abs(e5.kalib - e5b.kalib) < 1e-9 and e5b.zahl == 1))

    # 6/7 Probe: Ziel hinter einem Durchgang, den Bogen + Spaeher sehen (wie funde 14-16, Spaeher naeher)
    zeilen = []
    for y in range(400):
        z = ['G'] * 400
        if not (96 <= y <= 103):
            for x in range(112, 128):
                z[x] = 'X'
        zeilen.append(''.join(z))

    def lage(probe, leben=12500, zwei=False):
        A.Einzeln.PROBE, A.Einzeln.HIT_RUN = probe, False
        t = neu(); t._raid_plaetze = 99
        t.gelaende = zeilen
        L = {100: einheit(73, 1, 100, 100, leben=leben), 500: einheit(55, 2, 390, 390, leben=30000),
             650: einheit(24, 2, 120, 88, leben=10000)}
        for i in range(6):
            L[600 + i] = einheit(23, 2, 118 + i, 87, leben=17500)
        if zwei:
            L[101] = einheit(73, 1, 100, 104, leben=leben)
        G = {900: {"besitzer": 2, "typ": 3, "x": 140, "y": 98, "leben": 100, "uid": 1, "erreichbar": 1}}
        t.aufnehmen([n for n in L if 100 <= n < 200])
        erg, _ = t.schritt(L, G, sichere_orte=[(50, 50)], tick=10000)
        return t, erg
    t6a, e6a = lage(False)
    t6b, e6b = lage(True)
    f.append(("6 ohne Probe kein Ziel (%s), mit Probe Ziel %s + PROBE-Zeile" % (t6a.ziel.get(100), t6b.ziel.get(100)),
              t6a.ziel.get(100) is None and t6b.ziel.get(100) == 900 and any(z.startswith("PROBE 100") for z in e6b)))
    t7, e7 = lage(True, zwei=True)
    t7s, e7s = lage(True, leben=5000)
    f.append(("7 zwei Assassinen -> eine Probe (%d); 5.000 Leben -> keine (%s)" % (sum(z.startswith("PROBE") for z in e7),
                                                                                    t7s.ziel.get(100)),
              sum(z.startswith("PROBE") for z in e7) == 1 and t7s.ziel.get(100) is None))

    # 8 Hit & Run
    def entdeckt(runde_takte):
        A.Einzeln.PROBE, A.Einzeln.HIT_RUN = False, True
        t = neu(spielwahrheit=True); t._raid_plaetze = 99
        L = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000),
             600: dict(einheit(23, 2, 130, 100, leben=17500), zieleinheit=100), 601: einheit(24, 2, 112, 100, leben=10000)}
        G = {900: {"besitzer": 2, "typ": 3, "x": 101, "y": 101, "leben": 100, "uid": 1, "erreichbar": 1}}
        t.aufnehmen([100])
        t.ziel[100] = 900; t.ziel_typ[900] = 3; t.befohlen[100] = 0
        L[100].update(laufx=101, laufy=101, zustand=107)
        t._runde_ticks = runde_takte
        erg, _ = t.schritt(L, G, sichere_orte=[(50, 50)], tick=10000)
        return t, erg
    t8a, e8a = entdeckt(15)
    t8b, e8b = entdeckt(106)
    f.append(("8 Hit & Run: Runde 15 -> Ziel %s %s; Runde 106 -> Ziel %s %s" % (
        t8a.ziel.get(100), [z[:60] for z in e8a if "HIT&RUN" in z][:1], t8b.ziel.get(100), [z[:60] for z in e8b if "HIT&RUN" in z][:1]),
        t8a.ziel.get(100) == 900 and any("arbeitet weiter" in z for z in e8a)
        and any("kein Hit & Run" in z for z in e8b) and not any("arbeitet weiter" in z for z in e8b)))
    # 9/10 Arbeiter mitnehmen
    def mitnehmen(abstand_gebaeude):
        A.Einzeln.PROBE, A.Einzeln.HIT_RUN = False, False
        t = neu(); t._raid_plaetze = 99
        L = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000), 700: einheit(3, 2, 101, 100, leben=1000)}
        G = {900: {"besitzer": 2, "typ": 3, "x": 100 + abstand_gebaeude, "y": 102, "leben": 100, "uid": 1, "erreichbar": 1}}
        t.aufnehmen([100])
        t.ziel[100] = 900; t.ziel_typ[900] = 3; t.befohlen[100] = 0
        L[100].update(laufx=100 + abstand_gebaeude, laufy=102, zustand=107 if abstand_gebaeude <= 2 else 101)
        erg, _ = t.schritt(L, G, sichere_orte=[(50, 50)], tick=10000)
        return t, L, G, erg
    t9, _, _, e9 = mitnehmen(1)
    f.append(("9 am Gebaeude: kein Mitnehmen, Ziel %s" % t9.ziel.get(100),
              t9.ziel.get(100) == 900 and not any("nimmt Arbeiter" in z for z in e9)))
    t10, L10, G10, e10 = mitnehmen(30)
    jagd10 = t10.jagd.get(100)
    del L10[700]
    e10b, _ = t10.schritt(L10, G10, sichere_orte=[(50, 50)], tick=10030)
    f.append(("10 unterwegs: Jagd %s, danach Ziel %s %s" % (jagd10, t10.ziel.get(100), [z[:50] for z in e10b if "zurueck" in z][:1]),
              jagd10 == 700 and t10.ziel.get(100) == 900 and any("zurueck zu Gebaeude 900" in z for z in e10b)))
    # 11 Eichung: nur angekommene Angriffe
    e11 = RL.Eichung()
    e11.start(1, 900, 20000, 12500, 0, ziel_ort=(200, 200))
    e11.runde({1: {"leben": 12500, "x": 100, "y": 100}}, {}, 10)
    e11.runde({1: {"leben": 12500, "x": 100, "y": 100}}, {}, 10 + RL.NACHLAUF)
    e11.start(2, 901, 20000, 12500, 0, ziel_ort=(200, 200))
    e11.runde({2: {"leben": 12000, "x": 199, "y": 201}}, {}, 10)
    e11.runde({2: {"leben": 11000, "x": 150, "y": 150}}, {}, 10 + RL.NACHLAUF)
    f.append(("11 nie angekommen zaehlt nicht (%d gezaehlt, %d nicht da)" % (e11.zahl, getattr(e11, "nicht_da", 0)),
              e11.zahl == 1 and getattr(e11, "nicht_da", 0) == 1 and abs(e11.echt - 1500) < 1))
    A.Einzeln.PROBE = A.Einzeln.HIT_RUN = True
    for name, ok in f:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(bool(ok) for _, ok in f), len(f)))
    return all(ok for _, ok in f)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
