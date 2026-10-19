# -*- coding: utf-8 -*-
"""MIKRO - wen schicke ich gegen wen (Daniel 19.10. 18:07: "und ein Mikro: wie kann ich diese am besten einsetzen - dann
wuerde sicher nicht so etwas passieren wie hier und man haette 40 Schwertkaempfer, die einfach nur einen Assassinen
abwehren wollen").

Zwei Fragen fuer jede eigene Einheit gegen ein Ziel:
  1. HOLT SIE ES EIN? Ein Schuetze erreicht ein Ziel, das er beschiessen kann. Ein Nahkaempfer nur, wenn das Ziel steht
     (es kaempft, reisst ab, zuendet an) oder wenn er schneller laeuft (Lauftempo L80, gefecht.TEMPO_ART: kleiner =
     schneller). Unbekanntes Tempo zaehlt gegen ein laufendes Ziel nicht.
  2. REICHT ES? gefecht.simuliere mit den gemessenen Schadenswerten (Editor-Duelle, Lord aus Partien).
kleinste_gruppe(): aus den Kandidaten (bevorzugte zuerst, dann die naechsten) die kleinste Zahl, mit der die Rechnung
gewinnt - nicht das ganze Heer. Jede Antwort sagt, ob ungemessene Paare in der Rechnung steckten.
Pruefung ohne Spiel: src/selfaware/tools/checks/zuweisung_pruefen.py."""
import selfaware.services.gefecht as gefecht

STUFEN = (1, 2, 3, 4, 6, 9, 13, 20, 30, 45, 70)


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def einholbar(wir_typ, sie_typ, sie_steht):
    if wir_typ in gefecht.FERN_REICH:
        return True
    if sie_steht:
        return True
    tw, ts = gefecht.TEMPO_ART.get(wir_typ), gefecht.TEMPO_ART.get(sie_typ)
    return tw is not None and ts is not None and tw <= ts


def ungemessen(wir, sie):
    """Arten-Paare (x, y) in beiden Richtungen, fuer die nur Ersatzwerte vorliegen."""
    aus = set()
    for a in {e["typ"] for e in wir}:
        for b in {e["typ"] for e in sie}:
            for x, y in ((a, b), (b, a)):
                if not gefecht.gemessen(x, y, d=2 if x in gefecht.FERN_REICH else 1):
                    aus.add((x, y))
    return aus


def kleinste_gruppe(kandidaten, sie, fest=(), ziel_steht=True, vorrang=()):
    """kandidaten: eigene Einheiten (dict nr, typ, leben, x, y); sie: Feinde (dict typ, leben, x, y [, steht]);
    fest: eigene Einheiten, die sowieso mitkaempfen (z. B. der Lord, steht=True); vorrang: Nummern, die zuerst genommen
    werden (z. B. die Heimwache vor dem Feldzug). Gibt (gewaehlt [nr], gewinnt, Text)."""
    if not sie:
        return [], True, "keine Feinde"
    mitte = (sum(e["x"] for e in sie) / len(sie), sum(e["y"] for e in sie) / len(sie))
    fangen = [k for k in kandidaten if all(einholbar(k["typ"], e["typ"], ziel_steht or e.get("steht")) for e in sie)]
    weg = len(kandidaten) - len(fangen)
    ordnung = sorted(fangen, key=lambda k: (k["nr"] not in vorrang, schach((k["x"], k["y"]), mitte)))
    fest = [dict(e, steht=True) for e in fest]
    sie_s = [dict(e) for e in sie]
    ug = ungemessen(fest + ordnung, sie_s)
    hinweis = (" - UNGEMESSEN %s" % sorted(ug)) if ug else ""
    langsam = (" - %d holen es nicht ein" % weg) if weg else ""
    def rechne(teil):
        """Sieg = alle Feinde tot UND jede feste Einheit (der Lord) lebt."""
        rest = []
        rw, rs, t, sieg = gefecht.simuliere(fest + [dict(e) for e in teil], sie_s, rest_aus=rest)
        return rw > 0 and rs <= 0 and all(r > 0 for r in rest[:len(fest)]), t
    if fest:
        ok, t = rechne([])
        if ok:
            return [], True, "reicht ohne Hilfe (nach %d Takten)%s" % (t, hinweis)
    for k in STUFEN:
        if k > len(ordnung):
            break
        ok, t = rechne(ordnung[:k])
        if ok:
            return [e["nr"] for e in ordnung[:k]], True, "kleinste Gruppe %d von %d: Sieg nach %d Takten%s%s" % (
                k, len(ordnung), t, langsam, hinweis)
    if ordnung:
        ok, t = rechne(ordnung)
        return [e["nr"] for e in ordnung], ok, "alle %d, die es einholen: %s nach %d Takten%s%s" % (
            len(ordnung), "Sieg" if ok else "reicht nicht", t, langsam, hinweis)
    return [], False, "niemand holt es ein%s" % langsam


def schaden_je_leben(feind_typ, feind_leben, eigene_typen):
    """Wie viel Schaden je Takt die feindliche Einheit an unseren Arten macht (Mittel), je Lebenspunkt, den wir ihr nehmen
    muessen - der Massstab "wen zuerst toeten, um den meisten Schaden zu vermeiden" (Daniel 19.10. 18:03)."""
    tb = gefecht.tabelle()
    typen = list(eigene_typen) or [75]
    d = sum(gefecht.dps(feind_typ, t, tb[0], tb[2] if len(tb) > 2 else None, 2 if feind_typ in gefecht.FERN_REICH else 1)
            for t in typen) / float(len(typen))
    return d / float(max(1, feind_leben))


def abwehr_rang(feinde, eigene, steht=None):
    """19.10. 18:35 (Schritt 2 im Plan Einheitenlenker): Reihenfolge der Abwehrziele. feinde: {nr: einheit}; eigene: Liste
    eigener Einheiten (dict typ); steht(nr) -> True/False/None (Uebersicht). Nur Ziele, die mindestens eine eigene Einheit
    einholt; vorn das mit dem meisten Schaden je Leben. Gibt [(nr, wert)] absteigend."""
    typen = {e["typ"] for e in eigene}
    aus = []
    for n, f in feinde.items():
        st = steht(n) if steht else None
        ziel_steht = st is not False or f.get("nahziel", -1) > 0
        if not any(einholbar(t, f["typ"], ziel_steht) for t in typen):
            continue
        aus.append((n, schaden_je_leben(f["typ"], f["leben"], typen)))
    return sorted(aus, key=lambda z: -z[1])
