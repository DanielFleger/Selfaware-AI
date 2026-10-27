# -*- coding: utf-8 -*-
"""Besitzbuch (B-273 Stufe 1, erster Baustein) und Steh-Augen fuer ALLE Einheiten (B-275; Daniel 27.10. 22:35 "kannst du das
Log auch fuer alle anderen Einheiten machen? hier stehen einfach auch Schwertkaempfer rum").

Anlass Partie 221355: Assassine 219 bekam ab Takt 3.830 immer wieder Ziel und Weg und stand trotzdem 10.189 Takte am selben
Fleck (die Haende kommen nicht an); 10 arab. Schwertkaempfer standen ab 25.806 in der eigenen Burg ohne eine einzige Logzeile
(kein Modul fuehrt sie).

merken(befehl): jeder Befehl, der durch befehl.sende geht - je Einheit der LETZTE Befehl mit Absender-Modul, Art, Ziel und
Zaehler; Doppelbefehle (zwei verschiedene Module in derselben Runde fuer dieselbe Einheit) werden gezaehlt.
steh_runde(t, L, sp, arten): jede eigene Einheit, die STEH_ERKLAER Takte auf demselben Feld steht (Zustand 0/1), meldet -
hoechstens alle STEH_ERKLAER Takte - wer sie zuletzt befehligt hat, womit und wann, oder dass kein Modul sie je befehligt hat."""
import sys

STEH_ERKLAER = 300
BEFEHLSARTEN = ("angriff", "halten", "aufloesen", "mauerziel", "lauf", "gruppe", "stapel")
FREMD = ("befehl", "laden", "besitzbuch", "lordschutz")

LETZTER = {}             # Einheit -> {"modul", "art", "ziel", "runde", "anzahl"}
DOPPELT = {}             # Einheit -> Zahl der Runden mit Befehlen aus zwei verschiedenen Modulen
RUNDE = [0]
_IN_RUNDE = {}           # Einheit -> Modul in der laufenden Runde
_STILL = {}              # Einheit -> (Feld, seit, zuletzt gemeldet)
# Haende fuer JEDE Einheit (Daniel 27.10. 22:48 "ja natuerlich und auch fuer jede Einheit"): ein Befehl, den das Spiel nicht
# annimmt (Einheit steht seit einer Runde, Laufziel = eigenes Feld), wird erkannt und SPERRE_RUNDEN lang nicht wiederholt
SPERRE_RUNDEN = 5
ABGELEHNT = {}           # Einheit -> (Zielschluessel, Runde der Ablehnung)
# B-277 A neu (Frage-Agent 23:12 rot: Endpunkte nie verschieben - Lordtrupp, Sturm und Klettern laufen mit Absicht in ein
# anderes Gebiet): wurde eine WEGKETTE (lauf + danach) abgelehnt, geht die naechste Kette dieser Einheit SPERRE_RUNDEN lang als
# Direktlauf zum selben Endpunkt - das Spiel sucht den Weg selbst. Rueckweg: HAENDE = False
HAENDE = True
KETTE_ABGELEHNT = {}     # Einheit -> Runde, in der ihre Wegkette abgelehnt wurde


def _schluessel(art, w):
    if not isinstance(w, dict):
        return (art, None)
    for k in ("lauf", "ziel", "gebaeude"):
        if w.get(k) is not None:
            v = w[k]
            return (art, k, tuple(v) if isinstance(v, list) else v)
    return (art, None)


def abgelehnt(n):
    """(Zielschluessel, Runde) der letzten Ablehnung dieser Einheit oder None - fuer Module, die umplanen wollen."""
    return ABGELEHNT.get(n)


def filtern(befehl):
    """Vor dem Senden: Einheiten aus Befehlen nehmen, deren gleicher Befehl in den letzten SPERRE_RUNDEN abgelehnt wurde.
    Gibt (Befehl oder None, Meldungen). Wirft nie."""
    try:
        liste = befehl.get("befehle") if isinstance(befehl, dict) and "befehle" in befehl else [befehl]
        meld, leer = [], 0
        for c in liste or []:
            if not isinstance(c, dict):
                continue
            for art in BEFEHLSARTEN:
                w = c.get(art)
                if not isinstance(w, dict) or not isinstance(w.get("einheiten"), list):
                    continue
                key = _schluessel(art, w)
                raus = [n for n in w["einheiten"] if n in ABGELEHNT and ABGELEHNT[n][0] == key
                        and RUNDE[0] - ABGELEHNT[n][1] <= SPERRE_RUNDEN]
                if raus:
                    w["einheiten"] = [n for n in w["einheiten"] if n not in raus]
                    meld.append("WIEDERHOLUNG VERHINDERT: %s an %s - das Spiel hat genau diesen Befehl vor kurzem abgelehnt" % (
                        key, raus))
                    if not w["einheiten"]:
                        leer += 1
        # Befehle, deren Einheitenliste leer wurde, fallen weg; bleibt nichts, wird nichts gesendet
        uebrig = [c for c in (liste or []) if not (isinstance(c, dict) and any(
            isinstance(c.get(a), dict) and isinstance(c[a].get("einheiten"), list) and not c[a]["einheiten"] for a in BEFEHLSARTEN))]
        if leer and not uebrig:
            return None, meld
        if leer and isinstance(befehl, dict) and "befehle" in befehl:
            befehl["befehle"] = uebrig
        if HAENDE and KETTE_ABGELEHNT:
            befehl, m_d = _direktlauf(befehl)
            meld += m_d
        return befehl, meld
    except Exception:
        return befehl, []


def _direktlauf(befehl):
    """Einheiten mit kuerzlich abgelehnter Wegkette aus jeder Wegkette (angriff mit lauf + danach) herausnehmen und als eigenen
    Befehl direkt zum Endpunkt schicken. Gibt (Befehl, Meldungen)."""
    liste = befehl.get("befehle") if isinstance(befehl, dict) and "befehle" in befehl else [befehl]
    neu, meld = [], []
    for c in list(liste or []):
        w = c.get("angriff") if isinstance(c, dict) else None
        if not isinstance(w, dict) or not w.get("danach") or not isinstance(w.get("einheiten"), list):
            continue
        direkt = [n for n in w["einheiten"] if n in KETTE_ABGELEHNT and RUNDE[0] - KETTE_ABGELEHNT[n] <= SPERRE_RUNDEN]
        if not direkt:
            continue
        ende = list(w["danach"][-1])
        d = {k: v for k, v in w.items() if k not in ("danach", "einheiten", "lauf")}
        d.update({"einheiten": direkt, "lauf": ende})
        neu.append(dict({k: v for k, v in c.items() if k != "angriff"}, angriff=d))
        w["einheiten"] = [n for n in w["einheiten"] if n not in direkt]
        meld.append("HAENDE %s: Direktlauf zum Endpunkt %s statt Wegkette (%d Punkte) - ihre Wegkette wurde vor %s Runden abgelehnt" % (
            direkt, tuple(ende), 1 + len(w["danach"]), "/".join(str(RUNDE[0] - KETTE_ABGELEHNT[n]) for n in direkt)))
    if not neu:
        return befehl, meld
    liste = [c for c in liste if not (isinstance(c, dict) and isinstance(c.get("angriff"), dict)
                                      and c["angriff"].get("einheiten") == [])] + neu
    if isinstance(befehl, dict) and "befehle" in befehl:
        befehl["befehle"] = liste
        return befehl, meld
    return {"befehle": liste}, meld


_KARTE = [None, None]    # (Runde, Gebiete der Wegkarte)


def _gebiet(p):
    if _KARTE[0] != RUNDE[0]:
        _KARTE[0] = RUNDE[0]
        try:
            import speicher
            _KARTE[1] = speicher.wegkarte()["gebiet"]
        except Exception:
            _KARTE[1] = None
    g = _KARTE[1]
    try:
        return int(g[p[0], p[1]]) if g is not None else None
    except Exception:
        return None


def ursache(n, e, b, L, G=None):
    """B-277 (Auge vor Hand): was am abgelehnten Befehl auffaellt - Gebiet der Einheit gegen Gebiet des Ziels (Wegkarte des
    Spiels), Ziel-Einheit am/auf einem Gebaeude, Ziel schon tot/weg. Nur sichtbare Dinge. Wirft nie."""
    try:
        teile = []
        k = b.get("schluessel") or ()
        ziel_ort = None
        if len(k) >= 3 and k[1] == "lauf":
            ziel_ort = k[2]
        elif len(k) >= 3 and k[1] == "ziel":
            z = L.get(k[2])
            if z is None:
                teile.append("Ziel-Einheit %s nicht mehr im Lagebild" % (k[2],))
            else:
                ziel_ort = (z["x"], z["y"])
                teile.append("Ziel %s (Typ %s) bei %s, %d Felder" % (k[2], z.get("typ"), ziel_ort,
                                                                    max(abs(z["x"] - e["x"]), abs(z["y"] - e["y"]))))
                if G:
                    am = [(nr, g.get("typ")) for nr, g in G.items()
                          if max(abs(g.get("x", -9) - z["x"]), abs(g.get("y", -9) - z["y"])) <= 1]
                    if am:
                        teile.append("Ziel steht an/auf Gebaeude %s" % am[:2])
        elif len(k) >= 3 and k[1] == "gebaeude" and G and k[2] in G:
            ziel_ort = (G[k[2]]["x"], G[k[2]]["y"])
        if ziel_ort is not None:
            g0, g1 = _gebiet((e["x"], e["y"])), _gebiet(ziel_ort)
            if g0 is not None and g1 is not None:
                teile.append("Gebiet Einheit %d, Ziel %d%s" % (g0, g1, " (anderes Gebiet)" if g0 != g1 else ""))
        return "; ".join(teile) or "keine sichtbare Ursache"
    except Exception as ex:
        return "Ursache nicht lesbar (%r)" % (ex,)


def _absender():
    f = sys._getframe(2)
    while f is not None:
        m = f.f_globals.get("__name__", "?")
        if m.split(".")[-1] not in FREMD:
            return "%s.%s" % (m, f.f_code.co_name)
        f = f.f_back
    return "?"


def _einheiten(wert):
    if isinstance(wert, dict):
        for k in ("einheiten", "nr"):
            v = wert.get(k)
            if isinstance(v, list):
                return [int(x) for x in v if isinstance(x, int)]
            if isinstance(v, int):
                return [v]
    return []


def merken(befehl):
    """Aus einem Befehl (auch {"befehle": [...]}) je Einheit den letzten Befehl festhalten. Wirft nie."""
    try:
        liste = befehl.get("befehle") if isinstance(befehl, dict) and "befehle" in befehl else [befehl]
        modul = None
        for c in liste or []:
            if not isinstance(c, dict):
                continue
            for art in BEFEHLSARTEN:
                if art not in c:
                    continue
                ns = _einheiten(c[art])
                if not ns:
                    continue
                modul = modul or _absender()
                w = c[art]
                ziel = w.get("ziel") or w.get("gebaeude") or w.get("lauf") or (w.get("x"), w.get("y")) if isinstance(w, dict) else None
                for n in ns:
                    alt = LETZTER.get(n, {})
                    LETZTER[n] = {"modul": modul, "art": art, "ziel": ziel, "runde": RUNDE[0], "anzahl": alt.get("anzahl", 0) + 1,
                                  "schluessel": _schluessel(art, w), "kette": bool(isinstance(w, dict) and w.get("danach"))}
                    vor = _IN_RUNDE.get(n)
                    if vor is not None and vor != modul.split(".")[0]:
                        DOPPELT[n] = DOPPELT.get(n, 0) + 1
                    _IN_RUNDE[n] = modul.split(".")[0]
    except Exception:
        pass


def steh_runde(t, L, sp, arten, G=None):
    """Am Ende jeder Lenker-Runde: Runde weiterzaehlen und STEHT-Zeilen fuer stehende eigene Einheiten der arten."""
    RUNDE[0] += 1
    _IN_RUNDE.clear()
    aus = []
    for n, e in L.items():
        if e.get("besitzer") != sp or e.get("typ") not in arten:
            continue
        f = (e["x"], e["y"])
        alt = _STILL.get(n)
        if e.get("zustand") not in (0, 1) or alt is None or alt[0] != f:
            _STILL[n] = (f, t, None)
            continue
        seit, gemeldet = alt[1], alt[2]
        b = LETZTER.get(n)
        if (b is not None and seit < t and RUNDE[0] - b["runde"] <= 2 and (e.get("laufx"), e.get("laufy")) == f
                and ABGELEHNT.get(n, (None,))[0] != b.get("schluessel")):
            ABGELEHNT[n] = (b.get("schluessel"), RUNDE[0])
            if b.get("kette"):
                KETTE_ABGELEHNT[n] = RUNDE[0]
            aus.append("BEFEHL ABGELEHNT %d (Art %d) bei %s: %s schickte '%s %s'%s, das Spiel nahm ihn nicht an (Laufziel = eigenes "
                       "Feld) - %d Runden keine Wiederholung%s | auffaellig: %s" % (
                           n, e["typ"], f, b["modul"], b["art"], b["ziel"], " als Wegkette" if b.get("kette") else "",
                           SPERRE_RUNDEN, ", naechste Wegkette als Direktlauf" if b.get("kette") and HAENDE else "",
                           ursache(n, e, b, L, G)))
        if t - seit < STEH_ERKLAER or (gemeldet is not None and t - gemeldet < STEH_ERKLAER):
            continue
        _STILL[n] = (f, seit, t)
        b = LETZTER.get(n)
        if b is None:
            wer = "KEIN Modul hat ihr je einen Befehl gegeben"
        else:
            wer = "zuletzt %s: %s %s vor %d Runden (%d Befehle insgesamt%s)" % (
                b["modul"], b["art"], b["ziel"], RUNDE[0] - b["runde"], b["anzahl"],
                ", %d Runden mit Doppelbefehl" % DOPPELT[n] if DOPPELT.get(n) else "")
            if RUNDE[0] - b["runde"] <= 2:
                wer += " - Befehl frisch, sie bewegt sich trotzdem nicht"
        aus.append("STEHT %d (Art %d) seit %d Takten bei %s: %s" % (n, e["typ"], t - seit, f, wer))
    for n in [n for n in _STILL if n not in L]:
        del _STILL[n]
    return aus
