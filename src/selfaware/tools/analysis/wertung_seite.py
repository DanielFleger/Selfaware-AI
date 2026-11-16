# -*- coding: utf-8 -*-
"""Seite zum Wertungsmesser (Daniel 16.11.2026 17:45 "eine oberflaeche mit reglern die einheiten belohnen/bestrafen ... audit pro einheit
als auch ein analysetool in einem ... komplett nachvollziehbar ... parameter abaendern/hinzufuegen/loeschen oder archivieren"; 17:54
"wichtig ist dass die analyse wirklich pro einheit pro spiel ist ... wo man am ende pro einheit genau sieht welche punkte sie wofuer
bekommen hat und man dann sortieren kann welche einheiten am effektivsten war"; 18:05 nur Prototyp fuer den Desktop).

Liefert lokal (nur 127.0.0.1) eine Seite und diese Wege:
  GET  /                      die Seite (wertung_seite.html)
  GET  /api/partien           alle Lageprotokolle, neueste zuerst
  GET  /api/partie?datei=...  Wertung einer Partie (telemetry/wertung.messen, je Datei zwischengespeichert)
  GET  /api/regler            Regler, Messgroessen, Verlauf
  POST /api/regler            neue Regler (mit Grund) - alter und neuer Stand gehen in den Verlauf
  POST /api/regler/zurueck    letzte Aenderung zuruecknehmen (als neue Aenderung, der Verlauf behaelt beides)
  GET  /bild/hintergrund      Hintergrundbild der UCP3-Oberflaeche, wenn es auf diesem Rechner liegt
Aufruf: python -m selfaware.tools.analysis.wertung_seite [port=8771]"""

import glob
import json
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from selfaware import workspace
from selfaware.telemetry import wertung as W

HIER = os.path.dirname(os.path.abspath(__file__))
SEITE = os.path.join(HIER, "wertung_seite.html")
ZWISCHEN = os.path.join(workspace.DATA, "wertung", "zwischen")
UCP_BILD = os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "UCP3-GUI", "backgrounds", "bg_richard.webp"
)
NAME_OK = re.compile(r"^lage_[0-9_]+_i\w+_sp\d+\.jsonl\.gz$")


def partien():
    aus = []
    for p in glob.glob(os.path.join(workspace.DATA, "lage_*.jsonl.gz")):
        n = os.path.basename(p)
        if not NAME_OK.match(n):
            continue
        m = re.match(r"lage_(\d{4})(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)", n)
        zeit = (
            "%s.%s.%s %s:%s" % (m.group(3), m.group(2), m.group(1), m.group(4), m.group(5))
            if m
            else ""
        )
        z = _zwischen_lesen(n)
        aus.append(
            {
                "datei": n,
                "zeit": zeit,
                "sortier": n,
                "groesse_kb": os.path.getsize(p) // 1024,
                "kill_takt": z.get("kill_takt") if z else None,
                "einheiten": len(z["einheiten"]) if z else None,
            }
        )
    return sorted(aus, key=lambda x: x["sortier"], reverse=True)


def _zwischen_pfad(name):
    return os.path.join(ZWISCHEN, name.replace(".jsonl.gz", "") + ".v%d.json" % W.VERSION)


def _zwischen_lesen(name):
    p = _zwischen_pfad(name)
    quelle = os.path.join(workspace.DATA, name)
    try:
        if os.path.getmtime(p) >= os.path.getmtime(quelle):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    except (OSError, ValueError):
        pass
    return None


def partie(name):
    if not NAME_OK.match(name or "") or not os.path.exists(os.path.join(workspace.DATA, name)):
        raise ValueError("unbekannte Partie: %r" % name)
    z = _zwischen_lesen(name)
    if z is None:
        z = W.messen(os.path.join(workspace.DATA, name))
        os.makedirs(ZWISCHEN, exist_ok=True)
        with open(_zwischen_pfad(name), "w", encoding="utf-8") as f:
            json.dump(z, f, ensure_ascii=False)
    return z


def regler_antwort():
    return {
        "regler": W.regler_lesen(),
        "messgroessen": {
            k: {"name": n, "wort": w, "einheit": e, "richtung": r}
            for k, (n, w, e, r) in W.MESSGROESSEN.items()
        },
        "verlauf": [
            {
                "zeit": v["zeit"],
                "wer": v.get("wer"),
                "grund": v.get("grund"),
                "aenderungen": _unterschied(v.get("alt") or [], v.get("neu") or []),
            }
            for v in reversed(W.verlauf_lesen()[-100:])
        ],
    }


def _unterschied(alt, neu):
    a = {r["id"]: r for r in alt}
    n = {r["id"]: r for r in neu}
    aus = []
    for k in sorted(set(a) | set(n)):
        ra, rn = a.get(k), n.get(k)
        if ra is None:
            aus.append("%s neu (Gewicht %s)" % (rn.get("name", k), rn.get("gewicht")))
        elif rn is None:
            aus.append("%s fehlt" % ra.get("name", k))
        else:
            for feld in ("gewicht", "arten", "archiviert", "name"):
                if ra.get(feld) != rn.get(feld):
                    aus.append(
                        "%s: %s %s -> %s" % (rn.get("name", k), feld, ra.get(feld), rn.get(feld))
                    )
    return aus


def regler_pruefen(liste):
    """Nur bekannte Messgroessen, Zahl als Gewicht, Arten 'alle' oder Liste von Zahlen; nie loeschen - fehlende alte Regler bleiben archiviert."""
    if not isinstance(liste, list):
        raise ValueError("Regler muessen eine Liste sein")
    ids = set()
    for r in liste:
        if r.get("messgroesse") not in W.MESSGROESSEN:
            raise ValueError("unbekannte Messgroesse: %r" % r.get("messgroesse"))
        r["gewicht"] = float(r["gewicht"])
        if r.get("arten", "alle") != "alle":
            r["arten"] = [int(x) for x in r["arten"]]
        r["archiviert"] = bool(r.get("archiviert"))
        if not r.get("id") or r["id"] in ids:
            raise ValueError("Regler ohne oder mit doppelter Kennung")
        ids.add(r["id"])
    for alt in W.regler_lesen():  # Daniel 17:45 "loeschen oder archivieren": geloescht wird nichts (P4.1) - Fehlendes kommt ins Archiv
        if alt["id"] not in ids:
            liste.append(dict(alt, archiviert=True))
    return liste


class Seite(BaseHTTPRequestHandler):
    def _json(self, daten, code=200):
        roh = json.dumps(daten, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(roh)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(roh)

    def log_message(self, fmt, *args):
        sys.stderr.write("wertung_seite: " + (fmt % args) + "\n")

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                roh = open(SEITE, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(roh)
            elif u.path == "/api/partien":
                self._json(partien())
            elif u.path == "/api/partie":
                self._json(partie((q.get("datei") or [""])[0]))
            elif u.path == "/api/regler":
                self._json(regler_antwort())
            elif u.path == "/bild/hintergrund" and os.path.exists(UCP_BILD):
                roh = open(UCP_BILD, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "image/webp")
                self.end_headers()
                self.wfile.write(roh)
            else:
                self._json({"fehler": "nicht gefunden: %s" % u.path}, 404)
        except Exception as ex:  # Fehler sichtbar, nicht still (REGELN 5)
            self._json({"fehler": "%s: %s" % (type(ex).__name__, ex)}, 500)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        try:
            laenge = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(laenge) or b"{}")
            if u.path == "/api/regler":
                W.regler_schreiben(
                    regler_pruefen(body.get("regler")), "Seite", body.get("grund") or ""
                )
                self._json(regler_antwort())
            elif u.path == "/api/regler/zurueck":
                if not W.regler_zuruecknehmen("Seite"):
                    raise ValueError("nichts zum Zuruecknehmen")
                self._json(regler_antwort())
            else:
                self._json({"fehler": "nicht gefunden: %s" % u.path}, 404)
        except Exception as ex:
            self._json({"fehler": "%s: %s" % (type(ex).__name__, ex)}, 400)


def main():
    port = 8771
    for a in sys.argv[1:]:
        if a.startswith("port="):
            port = int(a.split("=", 1)[1])
    srv = ThreadingHTTPServer(("127.0.0.1", port), Seite)
    print("Wertung: http://127.0.0.1:%d/" % port, flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
