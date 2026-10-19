# -*- coding: utf-8 -*-
"""Bilanz und Endspiel (Daniel 06.10. 21:13/21:21): "berechnen, wie viele Ressourcen schon eingesammelt sind, und dann
nach Minimal-/Maximalprinzip abreissen / das Ziel erfuellen - eine komplette Tabelle mit allen Ressourcen, die schon drin
sind / reinkommen, und dann, wie viel man WIRKLICH nur braeuchte, und dann alles abreissen und das Ziel erfuellen."

Jede Runde: Wert von Lager, Kornspeicher, Waffenlager (Verkaufspreise, gemessen) + Abriss-Rueckgabe aller Betriebe
(Haelfte, abgerundet - Wissensregister A1/A2) gegen den echten Bedarf fuer den Rest des Ziels (Keulen/Leder in 5er-Losen
kaufen, 20 Gold je Kaempfer, Kaserne/Waffenlager falls fehlend, freie Bauern). Reicht es -> Endspiel: abreissen, alles
verkaufen, kaufen, anwerben. Huetten, Lager, Kornspeicher, Markt, Kaserne, Waffenlager und Bergfried bleiben stehen.
Preise (Gold je Stueck): Holz 1, Stein 5, Eisen 27, Aepfel 3, Brot 4, Kaese 6, Fleisch 1 (verkaufspreise_liga.txt,
Messung 06.10. 21:22); Keule 30 / Leder 10 beim Verkauf, 60 / 32 beim Kauf (Messpartie 8). Unbekannt -> 0 (vorsichtig).
"""
import math

PREIS = {"holz": 1, "stein": 5, "eisen": 27, "apfel": 3, "brot": 4, "kaese": 6, "fleisch": 1}
WARE_NR = {"holz": 2, "stein": 4, "eisen": 6, "apfel": 13, "brot": 10, "kaese": 11, "fleisch": 12}
LOS = {"holz": 20, "stein": 5, "eisen": 5, "apfel": 5, "brot": 5, "kaese": 5, "fleisch": 5}
KAUF_LOS = {21: 300, 23: 160}
ANWERBEN = 20
BLEIBEN = {41, 71, 72, 73, 55, 1, 8, 9, 10, 11, 19, 21, 26, 56, 57, 58, 59}  # Bergfried, Tueren, Feuer, Huetten, Kaserne, Lager, Waffenlager, Kornspeicher, Steinhaufen (gehoert zum Steinbruch), Markt, Soeldnerposten (12.10.: Notwerbung braucht ihn), Exerzierplatz BT_PARADEGROUND2-5 = 56-59 (gehoert zur Kaserne - v6/v7 rissen Teile ab, danach keine Kaserne mehr)
ROHSTOFF_WERT = {"holz": 1, "stein": 5, "eisen": 27, "pech": 0, "gold": 1}


def abriss_wert(kosten):
    """Haelfte je Ware, abgerundet (A1/A2), in Gold."""
    return sum((kosten.get(w, 0) // 2) * ROHSTOFF_WERT[w] for w in ROHSTOFF_WERT)


def rechne(st, v, G, L, sp, ziel, kosten_von, leder_kommt=0, behalten=(),
           verkaufbare_waren=None, abriss_faktor=0.70, gold_puffer=50):
    """Gibt die Tabelle (Zeilen) und ob das Ziel JETZT durch Abriss + Verkauf erreichbar ist.
    v14: leder_kommt = Leder der eigenen Kette, das bald im Waffenlager ist (naechste Kuh je Gerber, geglaettet);
    behalten = Gebaeudearten, die nicht abgerissen werden (Hoefe + Gerberei, solange ihr Leder noch gebraucht wird)."""
    n = max(0, ziel - st.get("T26", 0))
    eig = {nr: g for nr, g in G.items() if g["besitzer"] == sp}
    zeilen = []
    lager_wert = 0
    verkaufbare_waren = set(PREIS) if verkaufbare_waren is None else set(verkaufbare_waren)
    for w, p in PREIS.items():
        menge = st.get(w, 0)
        if w in verkaufbare_waren:
            lager_wert += (menge // LOS[w]) * LOS[w] * p  # nur echte spaetere Verkaufslose
        zeilen.append((w, menge, menge * p))
    abriss = [nr for nr, g in eig.items() if g["typ"] not in BLEIBEN and g["typ"] not in behalten]
    abriss_gold = sum(abriss_wert(kosten_von(eig[nr]["typ"])) for nr in abriss)
    frei_werden = sum(1 for e in L.values() if e["besitzer"] == sp and e.get("arbeitsplatz") in abriss)
    keule, leder = v.get("keule", 0), v.get("leder", 0)
    lose_k = math.ceil(max(0, n - keule) / 5)
    lose_l = math.ceil(max(0, n - leder - leder_kommt) / 5)
    hat = {t: any(g["typ"] == t for g in eig.values()) for t in (9, 11, 26)}
    # Kaserne: aus eigenem Stein kostet sie nur dessen Verkaufswert (12 x 5), sonst gekauft (12 x 10); Waffenlager 5 Holz
    kaserne = 0 if hat[9] else (12 * PREIS["stein"] if st.get("stein", 0) >= 12 else 12 * 10)
    bedarf = lose_k * KAUF_LOS[21] + lose_l * KAUF_LOS[23] + n * ANWERBEN + kaserne + (0 if hat[11] else 5)
    habe = st.get("gold", 0) + lager_wert + abriss_gold
    # Dieselbe vorsichtige Rechnung gilt schon vor dem ersten Verkauf. Sonst kann die Vorpruefung die Wirtschaft
    # leeren und erst danach merken, dass die schwankende Abriss-Rueckgabe doch nicht sicher reicht.
    habe_sicher = st.get("gold", 0) + lager_wert + int(abriss_gold * abriss_faktor)
    bauern = st.get("feuer", 0) + frei_werden
    ok = n > 0 and hat[26] and habe_sicher >= bedarf + gold_puffer and bauern >= n
    tabelle = {"rest_kaempfer": n, "gold": st.get("gold", 0), "lager": zeilen, "lager_wert": lager_wert,
               "abriss_betriebe": len(abriss), "abriss_wert": abriss_gold, "keule": keule, "leder": leder,
               "lose_keule": lose_k, "lose_leder": lose_l, "leder_kommt": leder_kommt, "bedarf_gold": bedarf, "habe_gold": habe,
               "habe_gold_sicher": habe_sicher, "gold_puffer": gold_puffer,
               "bauern_frei": st.get("feuer", 0), "bauern_nach_abriss": bauern, "jetzt_erreichbar": ok,
               "abriss_liste": abriss}
    return tabelle


def text(t):
    lager = ", ".join("%s %d (%d G)" % (w, m, g) for w, m, g in t["lager"] if m)
    return ("BILANZ Rest %d Kaempfer | Gold %d + Lager %d (%s) + Abriss %d Betriebe %d = %d | Bedarf %d (Keulen da %d, "
            "Leder da %d + kommt %d, Lose %d+%d, Anwerben, Kaserne/Waffenlager) | sicher %d (Puffer %d) | Bauern frei %d, nach Abriss %d | %s" % (
                t["rest_kaempfer"], t["gold"], t["lager_wert"], lager or "leer", t["abriss_betriebe"], t["abriss_wert"],
                t["habe_gold"], t["bedarf_gold"], t["keule"], t["leder"], t.get("leder_kommt", 0), t["lose_keule"], t["lose_leder"],
                t["habe_gold_sicher"], t["gold_puffer"], t["bauern_frei"], t["bauern_nach_abriss"],
                "JETZT SICHER ERREICHBAR" if t["jetzt_erreichbar"] else "fehlt sicher %d Gold" % max(
                    0, t["bedarf_gold"] + t["gold_puffer"] - t["habe_gold_sicher"])))
