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
  GET  /api/spiele            Kurzfassung jedes schon gerechneten Spiels und der Stand der Hintergrundrechnung
  POST /api/regler            neue Regler (mit Grund) - alter und neuer Stand gehen in den Verlauf
  POST /api/regler/zurueck    letzte Aenderung zuruecknehmen (als neue Aenderung, der Verlauf behaelt beides)
  POST /api/handeln           Schalter "Regler wirken aufs Handeln" an/aus ({"an": bool}) - baukasten/regler.py, Daniel 16.11.2026 19:30
  GET  /bild/hintergrund      Hintergrundbild der UCP3-Oberflaeche, wenn es auf diesem Rechner liegt
Aufruf: python -m selfaware.tools.analysis.wertung_seite [port=8771]"""

import glob
import json
import os
import re
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from selfaware import workspace
from selfaware.baukasten import regler as RG
from selfaware.telemetry import wertung as W

HIER = os.path.dirname(os.path.abspath(__file__))
SEITE = os.path.join(HIER, "wertung_seite.html")
ZWISCHEN = os.path.join(workspace.DATA, "wertung", "zwischen")
UCP_BILD = os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "UCP3-GUI", "backgrounds", "bg_richard.webp"
)
# alle Aufzeichnungen seit 06.10., auch ohne _sp und mit Vorsilbe (lage_ablauf_fein_...) - nie mit Pfadteilen
NAME_OK = re.compile(r"^lage_[A-Za-z0-9_]*?\d{8}_\d{6}_i\w+\.jsonl\.gz$")
SPERRE = threading.Lock()
BILDER = os.path.join(
    workspace.DATA, "wertung", "bilder"
)  # Einheitenbilder aus den Spieldateien (nicht in git: Spielgrafik)
AUFSTELLUNGEN = os.path.join(workspace.DATA, "wertung", "aufstellungen.json")
# Plaetze der KI-Auswahl in der Reihenfolge des Spiels (UCP3 ucp-config.yml, Abschnitt ai)
PLAETZE = [
    "rat",
    "snake",
    "pig",
    "wolf",
    "saladin",
    "caliph",
    "sultan",
    "richard",
    "frederick",
    "phillip",
    "wazir",
    "emir",
    "nizar",
    "sheriff",
    "marshal",
    "abbot",
]
STAND = {"fertig": 0, "gesamt": 0, "laeuft": False, "fehler": []}


def _spielordner():
    try:
        from selfaware.game.ucp import instanzen

        return instanzen.spielordner("team-liga")
    except Exception:
        return None


def ki_tabelle():
    """Platz (1-16) -> {name, ordner} aus der ucp-config.yml der Team-Liga-Instanz: welcher Charakter des Team-Liga-Plugins auf welchem
    KI-Platz sitzt; der Name kommt aus meta.json des Charakters, das Bild ist portrait_small.png daneben."""
    sp = _spielordner()
    aus = {}
    if not sp:
        return aus
    try:
        t = open(os.path.join(sp, "ucp-config.yml"), "rb").read().decode("utf-8", errors="replace")
    except OSError:
        return aus
    i = t.find("\n        ai:")
    for m in re.finditer(
        r"\n          (\w+):\n            binks:\n(?:.*\n){0,4}?\s+root: ([^\n]+)",
        t[i:] if i >= 0 else "",
    ):
        if m.group(1) not in PLAETZE:
            continue
        ordner = os.path.basename(m.group(2).strip().rstrip("/"))
        meta = os.path.join(
            sp, "ucp", "plugins", _plugin(sp), "resources", "ai", ordner, "meta.json"
        )
        try:
            name = json.load(open(meta, encoding="utf-8"))["name"]
        except (OSError, ValueError, KeyError):
            name = ordner
        aus[PLAETZE.index(m.group(1)) + 1] = {"name": name, "ordner": ordner}
    return aus


def _plugin(sp):
    kand = sorted(glob.glob(os.path.join(sp, "ucp", "plugins", "Mod-KI-Team-Liga*")))
    return os.path.basename(kand[-1]) if kand else "Mod-KI-Team-Liga"


def spieler_anzeige(name, erg):
    """Je Spieler mit Lord: Nummer, Name, Bild, wann sein Lord fiel, ob wir es sind. Namen nur aus aufstellungen.json (belegt) -
    sonst 'Spieler N' (Daniel 18:16: wer gegen wen, wer gestorben, wer gewonnen)."""
    try:
        auf = (
            json.load(open(AUFSTELLUNGEN, encoding="utf-8"))
            .get("partien", {})
            .get(name, {})
            .get("plaetze", {})
        )
    except (OSError, ValueError):
        auf = {}
    ki = ki_tabelle() if auf else {}
    aus = []
    for sp in erg.get("spieler_liste") or []:
        a = auf.get(str(sp["nr"])) or {}
        k = ki.get(a.get("platz")) or {}
        aus.append(
            dict(
                sp,
                name=a.get("name") or k.get("name") or "Spieler %d" % sp["nr"],
                platz=a.get("platz"),
                bild=_bild(k, a.get("name") or k.get("name")),
                belegt=bool(a),
            )
        )
    return aus


def _bild(k, name):
    """Portrait: Team-Liga-Charakter des Platzes, sonst eigene KI aus assets/ai/<Name>/portrait_small.png (Daniel 16.11.2026 18:37
    "unser samurai profilbild fehlt noch")."""
    if k.get("ordner"):
        return "/bild/ki/" + k["ordner"]
    if name and os.path.exists(os.path.join(workspace.AI_ASSETS, name, "portrait_small.png")):
        return "/bild/eigen/" + name
    return None


def partien():
    aus = []
    for p in glob.glob(os.path.join(workspace.DATA, "lage_*.jsonl.gz")):
        n = os.path.basename(p)
        if not NAME_OK.match(n):
            continue
        m = re.search(r"(\d{4})(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)", n)
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
                "sortier": (m.group(0) if m else "") + n,
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
    if z is not None:
        z["spieler_anzeige"] = spieler_anzeige(name, z)
    if z is None:
        with SPERRE:
            z = _zwischen_lesen(name)
            if z is None:
                z = W.messen(os.path.join(workspace.DATA, name))
                os.makedirs(ZWISCHEN, exist_ok=True)
                with open(_zwischen_pfad(name), "w", encoding="utf-8") as f:
                    json.dump(z, f, ensure_ascii=False)
                with open(_kurz_pfad(name), "w", encoding="utf-8") as f:
                    json.dump(W.kurzfassung(z), f, ensure_ascii=False)
            z["spieler_anzeige"] = spieler_anzeige(name, z)
    return z


def _kurz_pfad(name):
    return os.path.join(ZWISCHEN, name.replace(".jsonl.gz", "") + ".v%d.kurz.json" % W.VERSION)


def kurz(name):
    """Kurzfassung eines Spiels (wertung.kurzfassung), None solange es noch nicht gerechnet ist."""
    p = _kurz_pfad(name)
    try:
        if os.path.getmtime(p) >= os.path.getmtime(os.path.join(workspace.DATA, name)):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    except (OSError, ValueError):
        pass
    if _zwischen_lesen(name) is not None:  # voll gerechnet, Kurzfassung fehlt noch
        z = W.kurzfassung(_zwischen_lesen(name))
        with open(p, "w", encoding="utf-8") as f:
            json.dump(z, f, ensure_ascii=False)
        return z
    return None


def spiele():
    aus = []
    for x in partien():
        k = kurz(x["datei"])
        if k is not None:
            aus.append(
                dict(
                    k,
                    datei=x["datei"],
                    zeit=x["zeit"],
                    spieler_anzeige=spieler_anzeige(x["datei"], k),
                )
            )
    return {"stand": dict(STAND), "spiele": aus}


def historie(n=400):
    """Die Code-Aenderungen (git log des Repos) - die Seite stellt sie zwischen die Spiele: was sich vor einem Spiel geaendert hat
    (Daniel 18:18 "die historie wie es dazu gekommen ist")."""
    import subprocess

    try:
        r = subprocess.run(
            [
                "git",
                "-C",
                workspace.ROOT,
                "log",
                "-%d" % n,
                "--format=%h%x09%ad%x09%s",
                "--date=format:%Y%m%d_%H%M%S",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
        )
        return [
            dict(zip(("hash", "zeit", "text"), z.split("\t", 2), strict=False))
            for z in r.stdout.splitlines()
            if z.count("\t") >= 2
        ]
    except Exception as ex:
        return [{"hash": "", "zeit": "", "text": "git log nicht lesbar: %s" % ex}]


def einheit_bilder():
    """Einheitenbilder einmal aus den Spieldateien umwandeln (tools/analysis/einheit_bilder.js mit dem TGX-Leser des AI-Toolkits)."""
    import subprocess

    if glob.glob(os.path.join(BILDER, "einheit_*.png")):
        return
    sp = _spielordner()
    toolkit = os.path.join(os.path.dirname(workspace.ROOT), "AI-Toolkit")
    if sp and os.path.isdir(toolkit):
        subprocess.run(
            [
                "node",
                os.path.join(HIER, "einheit_bilder.js"),
                toolkit,
                os.path.join(sp, "gfx"),
                BILDER,
            ],
            capture_output=True,
            timeout=120,
        )


def alle_rechnen():
    """Im Hintergrund: jedes Spiel einmal werten (neueste zuerst) - danach liest die Seite nur noch die Kurzfassungen."""
    liste = partien()
    STAND.update(gesamt=len(liste), fertig=0, laeuft=True)
    for x in liste:
        try:
            partie(x["datei"])
        except Exception as ex:  # ein kaputtes Protokoll haelt die anderen nicht auf - es steht in der Liste der Fehler
            STAND["fehler"].append("%s: %s: %s" % (x["datei"], type(ex).__name__, ex))
        STAND["fertig"] += 1
    STAND["laeuft"] = False


def regler_antwort():
    handeln = RG.handeln_lesen()
    # Regler-Verlauf und Schalter-Verlauf in einer Liste, neueste zuerst (ADR-072)
    verlauf = [
        {
            "zeit": v["zeit"],
            "wer": v.get("wer"),
            "grund": v.get("grund"),
            "aenderungen": _unterschied(v.get("alt") or [], v.get("neu") or []),
        }
        for v in W.verlauf_lesen()[-100:]
    ] + [
        {
            "zeit": v["zeit"],
            "wer": v.get("wer"),
            "grund": v.get("grund") or "Schalter",
            "aenderungen": [
                "Regler wirken aufs Handeln: %s -> %s"
                % ("an" if v.get("alt") else "aus", "an" if v.get("neu") else "aus")
            ],
        }
        for v in (handeln.get("verlauf") or [])[-100:]
    ]
    return {
        "handeln": {k: handeln.get(k) for k in ("an", "zeit", "wer", "grund")},
        "regler": W.regler_lesen(),
        "messgroessen": {
            k: {"name": n, "wort": w, "einheit": e, "richtung": r, "roh": W.ROH_EINHEIT.get(k, "")}
            for k, (n, w, e, r) in W.MESSGROESSEN.items()
        },
        "verlauf": sorted(verlauf, key=lambda v: v["zeit"], reverse=True),
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

    def _datei(self, pfad, art):
        if not os.path.exists(pfad):
            self._json({"fehler": "kein Bild"}, 404)
            return
        roh = open(pfad, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", art)
        self.send_header("Cache-Control", "max-age=3600")
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
            elif u.path == "/api/spiele":
                self._json(spiele())
            elif u.path == "/api/historie":
                self._json(historie())
            elif u.path.startswith("/bild/einheit/") and u.path[14:].isdigit():
                self._datei(os.path.join(BILDER, "einheit_%d.png" % int(u.path[14:])), "image/png")
            elif u.path.startswith("/bild/eigen/"):
                name = urllib.parse.unquote(u.path[12:])
                if name not in os.listdir(workspace.AI_ASSETS):
                    raise ValueError("unbekannte eigene KI")
                self._datei(
                    os.path.join(workspace.AI_ASSETS, name, "portrait_small.png"), "image/png"
                )
            elif u.path.startswith("/bild/ki/"):
                ordner = u.path[9:]
                if ordner not in {k["ordner"] for k in ki_tabelle().values()}:
                    raise ValueError("unbekannte KI")
                sp = _spielordner()
                self._datei(
                    os.path.join(
                        sp,
                        "ucp",
                        "plugins",
                        _plugin(sp),
                        "resources",
                        "ai",
                        ordner,
                        "portrait_small.png",
                    ),
                    "image/png",
                )
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
            elif u.path == "/api/handeln":
                if not isinstance(body.get("an"), bool):
                    raise ValueError("an muss true oder false sein")
                RG.handeln_setzen(body["an"], "Seite", body.get("grund") or "")
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
    threading.Thread(target=alle_rechnen, daemon=True).start()
    threading.Thread(target=einheit_bilder, daemon=True).start()
    print("Wertung: http://127.0.0.1:%d/" % port, flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
