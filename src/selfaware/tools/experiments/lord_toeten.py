# -*- coding: utf-8 -*-
"""S164 (Daniel 15.11.2026 01:59 "nimm jetzt den offenen spielstand und toete den gegnerischen lord ohne neustart"; 02:00 "wir haben 4,2k
gold aber er rekrutiert nicht"): im laufenden Spiel alle eigenen Kaempfer auf den gegnerischen Lord. Vorher gibt der Kern alle eigenen
Einheiten frei (sonst holt er sie mit alten Lauf- und Wegpunkt-Befehlen weg). Jede Runde: mit dem Gold am Soeldnerposten nachwerben (so
viele, wie Bauern am Feuer stehen) und jedem Kaempfer, der nicht schon den Lord angreift, den Angriff befehlen - bis der Lord tot ist.
Nur Befehle, die ein Spieler auch geben kann (Angriff, Werben, Pause aus) - nichts am Spiel veraendert.

Aufruf (PYTHONPATH=src, SHC_INSTANZ=2): python -m selfaware.tools.experiments.lord_toeten [minuten=10] [werben=73]
Schreibt jede Runde eine Zeile nach data/research/lord_toeten_<Datum_Zeit>.txt.
"""

import os
import sys
import time

from selfaware import workspace as _workspace

KAEMPFER = {22, 23, 24, 25, 26, 27, 28, 70, 71, 72, 73, 74, 75, 76}
LORD = 55
SOELDNERPOSTEN = 8
PREIS = {73: 70, 75: 100, 70: 60}  # Anwerbepreis in Gold (assassinen.EINHEIT_WERT, L63 gemessen)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a.split("=", 1) for a in argv if "=" in a)
    minuten, art = float(arg.get("minuten", 10)), int(arg.get("werben", 73))
    from selfaware.execution import kampfschutz
    from selfaware.execution import kernweg as KW
    from selfaware.game import kern_leitung as KL
    from selfaware.game.ucp import befehl as B
    from selfaware.game.ucp.bauen import werbe
    from selfaware.runtime.live import erstes_spiel as ES

    pfad = os.path.join(_workspace.DATA, "lord_toeten_%s.txt" % time.strftime("%Y%m%d_%H%M%S"))
    log = open(pfad, "w", encoding="utf-8")

    def schreib(z):
        print(z, flush=True)
        log.write(z + "\n")
        log.flush()

    B.belege()
    st, L, G = ES.runde_lesen()
    # erst fortsetzen: der Kern arbeitet den Ring nur in laufenden Takten ab (02:01: angehalten war er nach 256 Freigaben voll)
    B.sende({"player": ES.SP, "pause": False}, 0.5)
    eigene = [n for n, e in L.items() if e.get("besitzer") == ES.SP and e["typ"] in KAEMPFER]
    k = KW.oeffnen(B.SPIEL)
    frei = 0
    if k is not None:
        for n in eigene:
            try:
                k.leitung.auftrag(KL.FREIGEBEN, n)
                frei += 1
            except RuntimeError:
                time.sleep(0.2)  # Ring voll: der Kern braucht ein paar Takte
        schreib("KERN: %d von %d eigenen Kaempfern freigegeben" % (frei, len(eigene)))
    ende, geworben = time.time() + 60 * minuten, 0
    while time.time() < ende:
        B.belege()
        st, L, G = ES.runde_lesen()
        lords = [
            (n, e)
            for n, e in L.items()
            if e["typ"] == LORD and e.get("besitzer") not in (0, ES.SP) and e.get("leben", 0) > 0
        ]
        if not lords:
            schreib(
                "Takt %s: KEIN GEGNERISCHER LORD MEHR - tot (oder nicht sichtbar)" % st.get("t")
            )
            break
        ln, le = lords[0]
        kampfschutz.stand(L, G)
        posten = [
            n for n, g in G.items() if g.get("besitzer") == ES.SP and g["typ"] == SOELDNERPOSTEN
        ]
        n_w = min(st.get("gold", 0) // PREIS.get(art, 100), st.get("feuer", 0), 10) if posten else 0
        for _ in range(n_w):
            werbe(art, posten[0])
        geworben += n_w
        kaempfer = [
            n
            for n, e in L.items()
            if e.get("besitzer") == ES.SP and e["typ"] in KAEMPFER and e.get("leben", 0) > 0
        ]
        neu = [n for n in kaempfer if L[n].get("zieleinheit") != ln]
        if neu:
            ES.befehl({"angriff": {"einheiten": neu, "ziel": ln}}, 1.0, bis="ANGRIFF")
        schreib(
            "Takt %s: Lord %d Leben %d bei (%d,%d) | Kaempfer %d, neu befohlen %d | Gold %d, Bauern am Feuer %d, geworben %d (zusammen %d)"
            % (
                st.get("t"),
                ln,
                le.get("leben", 0),
                le["x"],
                le["y"],
                len(kaempfer),
                len(neu),
                st.get("gold", 0),
                st.get("feuer", 0),
                n_w,
                geworben,
            )
        )
        time.sleep(1.0)
    B.freigeben()
    schreib("-> %s" % pfad)


if __name__ == "__main__":
    main()
