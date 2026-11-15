"""Backlog = die GitHub-Issues dieses Repos (Daniel 15.11.2026 19:49: "es soll einfach wie ein klassischer Backlog in GitHub aufgebaut
sein. Mir ist es halt wichtig, dass ich sofort von ueberall und egal welcher Sitzung darauf zugreifen kann"; 19:53 "loesche dann
die backlog liste").

Es gibt keine zweite Liste. Die fruehere docs/backlog/backlog.json (B-1 bis B-442, 352 Punkte) ist am 15.11.2026 als Issues
uebernommen worden; ihr Titel beginnt mit der alten B-Nummer, die Datei selbst liegt nur noch in der Git-Geschichte. Aelter
bleibt der Wunsch vom 19.10.2026: nichts vergessen, wissen was gebaut ist und wo es steht - nie loeschen, nur der Stand aendert sich.

Etiketten: Kategorie und "Kategorie: Unterkategorie" aus docs/backlog/kategorien.json (Daniel 15.11.2026 14:01/14:18).
Stand: offen = offenes Issue; "in Arbeit" und "zurückgestellt" = Etikett; gebaut = geschlossen (erledigt);
verworfen = geschlossen (nicht geplant). "Fokus" = was jetzt dran ist; "Impact: hoch" = Daniel 19:53 "wir machen nur noch die
Punkte mit hoechstem impact value". Das Repo kommt aus dem Git-Remote origin, nicht aus dem Code.

Aufruf (aus Selfaware-AI):
  uv run selfaware run backlog neu --titel "..." --kategorie Kampf --unter Lord --herkunft "Daniel ..." [--notiz ...] [--wo a,b]
  uv run selfaware run backlog stand <#n|B-n> <offen|in_arbeit|zurueckgestellt|gebaut|verworfen> [--notiz ...] [--commit abc1234]
  uv run selfaware run backlog fokus      (Fokus, Impact: hoch, in Arbeit - vor jedem Schritt und jedem Bericht)
  uv run selfaware run backlog liste [offen|alle]
  uv run selfaware run backlog pruefen    (Commits seit dem Umzug ohne #n oder B-n; Rueckgabe 1 bei Befund)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

from selfaware import workspace

KATEGORIEN = os.path.join(workspace.ROOT, "docs", "backlog", "kategorien.json")
STAENDE = ("offen", "in_arbeit", "zurueckgestellt", "gebaut", "verworfen")
IN_ARBEIT, ZURUECK, FOKUS, IMPACT = "in Arbeit", "zurückgestellt", "Fokus", "Impact: hoch"
UMZUG = "2026-11-15 20:00"  # ab hier muss jeder Commit seinen Punkt (#n oder B-n) nennen; vorher galt backlog.json


def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", workspace.ROOT, *args], capture_output=True, check=True)
    return r.stdout.decode("utf-8", "replace").strip()


def repo() -> str:
    """owner/name aus dem Remote origin (https://github.com/owner/name(.git) oder git@github.com:owner/name.git)."""
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", git("remote", "get-url", "origin"))
    if not m:
        raise SystemExit("origin zeigt nicht auf GitHub - Backlog nicht erreichbar")
    return "%s/%s" % m.groups()


def _umgebung() -> dict:
    """GH_TOKEN des Repo-Besitzers, falls gh mehrere Konten kennt (das aktive Konto kann ein anderes sein)."""
    umg = dict(os.environ)
    if not umg.get("GH_TOKEN"):
        r = subprocess.run(
            ["gh", "auth", "token", "--user", repo().split("/")[0]], capture_output=True, text=True
        )
        if r.returncode == 0 and r.stdout.strip():
            umg["GH_TOKEN"] = r.stdout.strip()
    return umg


def gh_echt(methode: str, pfad: str, daten: dict | None = None):
    befehl = ["gh", "api", "-X", methode, pfad] + (["--input", "-"] if methode != "GET" else [])
    r = subprocess.run(
        befehl,
        input=json.dumps(daten or {}) if methode != "GET" else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_umgebung(),
    )
    if r.returncode:
        raise SystemExit(
            "GitHub lehnt ab: %s %s -> %s" % (methode, pfad, (r.stderr or r.stdout).strip()[:300])
        )
    return json.loads(r.stdout) if r.stdout.strip() else {}


GH = gh_echt  # in Tests ersetzt


def baum() -> list[tuple[str, list[str]]]:
    with open(KATEGORIEN, encoding="utf-8") as f:
        return [(k["name"], [u["name"] for u in k["unter"]]) for k in json.load(f)["kategorien"]]


def pruefe_kategorie(kategorie: str, unter: str) -> None:
    for k, us in baum():
        if k == kategorie:
            if unter not in us:
                raise SystemExit(
                    "Unterkategorie %r gibt es unter %s nicht: %s" % (unter, k, ", ".join(us))
                )
            return
    raise SystemExit("Kategorie %r unbekannt: %s" % (kategorie, ", ".join(k for k, _ in baum())))


def finde(nr: str) -> dict:
    """#n oder n -> Issue n; B-n -> das Issue, dessen Titel mit 'B-n ' beginnt."""
    if re.fullmatch(r"#?\d+", nr):
        return GH("GET", "repos/%s/issues/%s" % (repo(), nr.lstrip("#")))
    if not re.fullmatch(r"B-\d+", nr):
        raise SystemExit("Nummer %r: erwartet #n oder B-n" % nr)
    treffer = GH("GET", "search/issues?q=%s" % ("repo:%s+in:title+%%22%s%%22" % (repo(), nr)))
    passend = [i for i in treffer.get("items", []) if i["title"].startswith(nr + " ")]
    if len(passend) != 1:
        raise SystemExit("%s: %d passende Issues gefunden" % (nr, len(passend)))
    return GH(
        "GET", "repos/%s/issues/%d" % (repo(), passend[0]["number"])
    )  # Suchtreffer tragen nicht alle Felder


def neu(titel, kategorie, unter, herkunft, notiz="", wo=()):
    pruefe_kategorie(kategorie, unter)
    rumpf = ["**%s / %s**" % (kategorie, unter), "**Herkunft:** " + herkunft]
    if wo:
        rumpf.append("**Wo:** " + ", ".join("`%s`" % w for w in wo))
    if notiz:
        rumpf.append("**Notiz:** " + notiz)
    return GH(
        "POST",
        "repos/%s/issues" % repo(),
        {
            "title": titel,
            "body": "\n\n".join(rumpf),
            "labels": [kategorie, "%s: %s" % (kategorie, unter)],
        },
    )


def stand(nr, status, notiz="", commit=""):
    if status not in STAENDE:
        raise SystemExit("Stand %r unbekannt - %s" % (status, ", ".join(STAENDE)))
    i = finde(nr)
    pfad = "repos/%s/issues/%d" % (repo(), i["number"])
    etiketten = [e["name"] if isinstance(e, dict) else e for e in i.get("labels", [])]
    ohne = [e for e in etiketten if e not in (IN_ARBEIT, ZURUECK)]
    neu_et = ohne + {"in_arbeit": [IN_ARBEIT], "zurueckgestellt": [ZURUECK]}.get(status, [])
    zustand = (
        {"state": "closed", "state_reason": "completed" if status == "gebaut" else "not_planned"}
        if status in ("gebaut", "verworfen")
        else {"state": "open"}
    )
    text = " ".join(
        t for t in (("Stand: " + status), ("Commit " + commit) if commit else "", notiz) if t
    )
    GH("POST", pfad + "/comments", {"body": text})
    return GH("PATCH", pfad, dict(zustand, labels=neu_et))


def offene(etikett: str | None = None) -> list[dict]:
    """Alle offenen Issues (ohne Pull Requests), seitenweise zu je 100."""
    q = "repos/%s/issues?state=open&per_page=100" % repo() + (
        "&labels=%s" % etikett.replace(" ", "%20") if etikett else ""
    )
    aus, seite = [], 1
    while True:
        teil = GH("GET", "%s&page=%d" % (q, seite))
        aus += [i for i in teil if "pull_request" not in i]
        if len(teil) < 100:
            return aus
        seite += 1


def fokus() -> list[tuple[str, list[dict]]]:
    return [(e, offene(e)) for e in (FOKUS, IMPACT, IN_ARBEIT)]


def pruefen(seit: str = UMZUG) -> list[str]:
    """Commits seit dem Umzug, deren Nachricht weder #n noch B-n nennt."""
    log = git("log", "--since=%s" % seit, "--format=%h %s")
    return [z for z in log.splitlines() if z and not re.search(r"(#\d+|\bB-\d+)", z)]


def main() -> int:
    ap = argparse.ArgumentParser(description="Backlog SamurAI = GitHub-Issues")
    sub = ap.add_subparsers(dest="was", required=True)
    n = sub.add_parser("neu")
    n.add_argument("--titel", required=True)
    n.add_argument("--herkunft", required=True)
    n.add_argument("--kategorie", required=True)
    n.add_argument("--unter", required=True)
    n.add_argument("--notiz", default="")
    n.add_argument("--wo", default="")
    s = sub.add_parser("stand")
    s.add_argument("nr")
    s.add_argument("status")
    s.add_argument("--notiz", default="")
    s.add_argument("--commit", default="")
    sub.add_parser("fokus")
    li = sub.add_parser("liste")
    li.add_argument("welche", nargs="?", default="offen")
    sub.add_parser("pruefen")
    a = ap.parse_args()
    if a.was == "neu":
        i = neu(
            a.titel, a.kategorie, a.unter, a.herkunft, a.notiz, [w for w in a.wo.split(",") if w]
        )
        print("#%d angelegt: %s  %s" % (i["number"], i["title"], i.get("html_url", "")))
    elif a.was == "stand":
        i = stand(a.nr, a.status, a.notiz, a.commit)
        print("#%d jetzt %s (%s)" % (i["number"], a.status, i.get("state")))
    elif a.was == "fokus":
        for etikett, liste in fokus():
            print(
                "%s: %s"
                % (etikett, "; ".join("#%d %s" % (i["number"], i["title"]) for i in liste) or "-")
            )
    elif a.was == "liste":
        for i in offene():
            print("#%d %s" % (i["number"], i["title"]))
    elif a.was == "pruefen":
        ohne = pruefen()
        for z in ohne:
            print("OHNE PUNKT: " + z)
        print("%d Commits seit %s ohne #n oder B-n" % (len(ohne), UMZUG))
        return 1 if ohne else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
