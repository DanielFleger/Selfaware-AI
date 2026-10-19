# -*- coding: utf-8 -*-
"""Backlog: was wann wie gebaut wurde, wo es steht und was noch fehlt (Daniel 19.10.2026 21:52: "eine wirkliche
Backlog-Liste mit allem, was wann wie gemacht wurde und was noch fehlt - keine Todo-Liste, sondern eine dynamisch
wachsende, damit wir nichts vergessen und wissen, was schon gebaut ist und wo es steht").

EINE Quelle: docs/backlog/backlog.json (Punkte B-1, B-2, ...). Nie loeschen - nur der Stand aendert sich, jede Aenderung kommt mit
Zeit in den Verlauf des Punkts. Die Ansicht docs/backlog/Backlog.html wird daraus erzeugt, dazu:
  - je Punkt: Dateien unter "wo" werden nachgesehen (fehlt eine, steht sie rot da)
  - Chronik: alle Commits von Selfaware-AI und VillageStudio nach Tagen ("was wann gemacht")
  - "Ohne Punkt": Commits ab 19.10.2026, deren Nachricht keinen Punkt (B-Nummer) nennt - damit nichts verloren geht
Die alte Backlog.md (Abhakliste bis 11.10.) ist mit "import_alt" vollstaendig uebernommen (B-1 bis B-58).

Aufruf (aus Selfaware-AI):
  uv run selfaware run backlog neu --titel "..." --bereich Kampf --herkunft "Daniel 19.10. 21:52 ..." [--status offen]
                                 [--wo datei1,datei2] [--belege L142,L143] [--notiz "..."]
  uv run selfaware run backlog stand B-61 gebaut [--commit abc1234] [--wo ...] [--belege ...] [--notiz "..."]
  uv run selfaware run backlog zuordnen B-61 abc1234,def5678   (Commit ohne B-Nummer einem Punkt zuordnen)
  uv run selfaware run backlog rang B-114 1     (Rang 1 = ganz oben; Daniel 22:02: das Wichtigste, was ich jetzt mache, oben)
  uv run selfaware run backlog fokus           (was jetzt dran ist - vor jedem Schritt und jedem Bericht nachsehen)
  uv run selfaware run backlog liste [offen|gebaut|...]
  uv run selfaware run backlog bauen          -> Backlog.html (prueft dabei "wo" und die Commits)
"""

from selfaware import workspace as _workspace
import argparse
import html
import json
import os
import re
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = _workspace.ROOT
QUELLE = os.path.join(WURZEL, "docs", "backlog", "backlog.json")
ANSICHT = os.path.join(WURZEL, "docs", "backlog", "Backlog.html")
VILLAGE = _workspace.VILLAGE_STUDIO
STAENDE = ("in_arbeit", "offen", "gebaut", "zurueckgestellt", "verworfen")
STAND_TEXT = {"in_arbeit": "in Arbeit", "offen": "offen", "gebaut": "gebaut", "zurueckgestellt": "zurückgestellt",
              "verworfen": "verworfen"}
AB_ZUORDNUNG = "2026-10-19"      # ab hier nennt jede Commit-Nachricht ihren Punkt (B-Nummer)


def jetzt():
    return time.strftime("%Y-%m-%d %H:%M")


def lade():
    if not os.path.exists(QUELLE):
        return {"angelegt": jetzt(), "punkte": []}
    return json.load(open(QUELLE, encoding="utf-8"))


def speichere(b):
    tmp = QUELLE + ".neu"
    json.dump(b, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, QUELLE)


def liste(s):
    return [x.strip() for x in (s or "").split(",") if x.strip()]


def finde(b, nr):
    nr = nr.upper() if nr.upper().startswith("B-") else "B-%s" % nr
    for p in b["punkte"]:
        if p["nr"] == nr:
            return p
    raise SystemExit("Punkt %s gibt es nicht" % nr)


def neu(b, titel, bereich, herkunft, status="offen", wo=(), belege=(), notiz="", seit=None, gebaut=None, commits=(),
        quelle=None):
    if status not in STAENDE:
        raise SystemExit("Stand %r unbekannt - %s" % (status, ", ".join(STAENDE)))
    nr = "B-%d" % (max([int(p["nr"][2:]) for p in b["punkte"]] or [0]) + 1)
    p = {"nr": nr, "titel": titel, "bereich": bereich, "status": status, "seit": seit or jetzt(), "herkunft": herkunft,
         "gebaut": gebaut, "commits": list(commits), "wo": list(wo), "belege": list(belege), "notiz": notiz,
         "verlauf": [{"zeit": jetzt(), "was": "angelegt (%s)" % STAND_TEXT[status] + (" - aus %s" % quelle if quelle else "")}]}
    b["punkte"].append(p)
    return p


def stand(b, nr, status, commit=None, wo=(), belege=(), notiz=""):
    p = finde(b, nr)
    if status not in STAENDE:
        raise SystemExit("Stand %r unbekannt - %s" % (status, ", ".join(STAENDE)))
    alt = p["status"]
    p["status"] = status
    if status == "gebaut" and not p.get("gebaut"):
        p["gebaut"] = jetzt()
    if commit:
        p["commits"].append(commit)
    p["wo"] += [w for w in wo if w not in p["wo"]]
    p["belege"] += [x for x in belege if x not in p["belege"]]
    if notiz:
        p["notiz"] = (p["notiz"] + " | " if p["notiz"] else "") + notiz
    p["verlauf"].append({"zeit": jetzt(), "was": "%s -> %s" % (STAND_TEXT[alt], STAND_TEXT[status])
                         + (" (Commit %s)" % commit if commit else "") + (": " + notiz if notiz else "")})
    return p


def rang(b, nr, platz):
    """19.10. 22:02 (Daniel: "das Wichtigste, also das, was du jetzt machst, ganz oben"): Rang 1 = ganz oben. Der Punkt
    wird an `platz` eingeschoben, alle mit gleichem oder hoeherem Rang ruecken eins nach unten."""
    p = finde(b, nr)
    alt = p.get("rang")
    andere = sorted((q for q in b["punkte"] if q.get("rang") and q is not p), key=lambda q: q["rang"])
    andere.insert(max(0, min(platz - 1, len(andere))), p)
    for i, q in enumerate(andere, 1):
        q["rang"] = i
    p["verlauf"].append({"zeit": jetzt(), "was": "Rang %s -> %d" % (alt if alt else "-", p["rang"])})
    return p


def fokus(b, n=5):
    """Was jetzt dran ist: Punkte in Arbeit, dann die naechsten nach Rang."""
    arbeit = sorted((p for p in b["punkte"] if p["status"] == "in_arbeit"), key=lambda p: p.get("rang") or 999)
    weiter = sorted((p for p in b["punkte"] if p["status"] == "offen" and p.get("rang")), key=lambda p: p["rang"])[:n]
    return arbeit, weiter


def ordnung(p):
    """Reihenfolge der Ansicht: in Arbeit, dann offene nach Rang, offene ohne Rang, gebaut (neueste zuerst), Rest."""
    gruppe = {"in_arbeit": 0, "offen": 1 if p.get("rang") else 2, "gebaut": 3, "zurueckgestellt": 4, "verworfen": 5}[p["status"]]
    return (gruppe, p.get("rang") or 9999, -int(p["nr"][2:]))


def zuordnen(b, nr, commits):
    """Commits einem Punkt zuordnen, ohne seinen Stand zu aendern (fuer Commits, deren Nachricht keine B-Nummer nennt)."""
    p = finde(b, nr)
    neu_c = [c for c in commits if c not in p["commits"]]
    p["commits"] += neu_c
    if neu_c:
        p["verlauf"].append({"zeit": jetzt(), "was": "Commits zugeordnet: %s" % ", ".join(neu_c)})
    return p, neu_c


def import_alt(b):
    """Backlog.md (Stand 11.10.) vollstaendig uebernehmen: jede Zeile "- [ ]"/"- [x]" ein Punkt, Bereich = Ueberschrift."""
    if any(p.get("quelle") == "Backlog.md" for p in b["punkte"]):
        raise SystemExit("Backlog.md ist schon uebernommen")
    bereich, n = "Allgemein", 0
    for z in open(os.path.join(WURZEL, "docs", "research", "Backlog.md"), encoding="utf-8"):
        z = z.rstrip("\n")
        if z.startswith("## "):
            bereich = re.sub(r"\s*\(.*$", "", z[3:]).strip()
            bereich = "Wirtschaft" if bereich.startswith("06.10.2026") else bereich
            continue
        m = re.match(r"- \[( |x)\] (.*)$", z)
        if not m:
            continue
        text = m.group(2)
        fett = re.match(r"\*\*(.+?)\*\*[:\s]*(.*)$", text)
        titel = (fett.group(1) if fett else re.split(r" \(|: | - ", text)[0]).rstrip(":").strip()
        datum = re.search(r"(\d{2})\.(\d{2})\.", text)
        seit = "2026-%s-%s" % (datum.group(2), datum.group(1)) if datum else "vor 2026-10-11"
        p = neu(b, titel[:160], bereich, "Backlog.md (Abhakliste bis 11.10.2026)",
                status="gebaut" if m.group(1) == "x" else "offen", notiz=text, seit=seit,
                gebaut="vor 2026-10-11" if m.group(1) == "x" else None, quelle="Backlog.md")
        p["quelle"] = "Backlog.md"
        n += 1
    return n


def git_log(repo, seit=None):
    if not os.path.isdir(os.path.join(repo, ".git")):
        return []
    cmd = ["git", "-C", repo, "log", "--date=format:%Y-%m-%d %H:%M", "--format=%h\x1f%ad\x1f%s"]
    if seit:
        cmd.append("--since=%s" % seit)
    aus = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    return [tuple(z.split("\x1f")) for z in aus.splitlines() if z.count("\x1f") == 2]


def e(s):
    return html.escape(str(s if s is not None else ""))


def bauen(b):
    punkte = b["punkte"]
    repos = [("Selfaware-AI", WURZEL), ("VillageStudio", VILLAGE)]
    log = [(name, h, d, s) for name, r in repos for (h, d, s) in git_log(r)]
    log.sort(key=lambda x: x[2], reverse=True)
    bekannte = {c for p in punkte for c in p["commits"]}
    ohne = [(n, h, d, s) for (n, h, d, s) in log if d[:10] >= AB_ZUORDNUNG and n == "Selfaware-AI"
            and not re.search(r"\bB-\d+", s) and h not in bekannte]
    fehlt_wo = []
    karten = []
    for p in sorted(punkte, key=ordnung):
        wo_html = []
        for w in p["wo"]:
            da = os.path.exists(os.path.join(WURZEL, w)) or os.path.exists(w)
            if not da:
                fehlt_wo.append((p["nr"], w))
            wo_html.append('<code class="%s">%s</code>' % ("da" if da else "fehlt", e(w)))
        verlauf = "".join("<li>%s - %s</li>" % (e(v["zeit"]), e(v["was"])) for v in p["verlauf"])
        karten.append(
            '<div class="punkt %s" data-id="%s" data-stand="%s" data-bereich="%s">'
            '<h2><span class="nr">%s</span>%s %s <span class="stand %s">%s</span></h2>'
            '<div class="meta"><b>Bereich:</b> %s · <b>seit:</b> %s · <b>wer/warum:</b> %s</div>'
            '%s%s%s%s%s'
            '<details><summary>Verlauf (%d)</summary><ul>%s</ul></details>'
            '<div class="zeile"><select class="ampel"><option>offen</option><option>gruen</option><option>gelb</option>'
            '<option>rot</option></select><textarea placeholder="Notiz"></textarea></div></div>' % (
                p["status"], e(p["nr"]), p["status"], e(p["bereich"]), e(p["nr"]),
                (' <span class="rang">Rang %d</span>' % p["rang"]) if p.get("rang") and p["status"] in ("offen", "in_arbeit") else "",
                e(p["titel"]), p["status"],
                STAND_TEXT[p["status"]], e(p["bereich"]), e(p["seit"]), e(p["herkunft"]),
                ('<div><b>gebaut:</b> %s</div>' % e(p["gebaut"])) if p.get("gebaut") else "",
                ('<div><b>Commits:</b> %s</div>' % ", ".join("<code>%s</code>" % e(c) for c in p["commits"])) if p["commits"] else "",
                ('<div><b>wo:</b> %s</div>' % " ".join(wo_html)) if wo_html else "",
                ('<div><b>Belege:</b> %s</div>' % e(", ".join(p["belege"]))) if p["belege"] else "",
                ('<div class="notiz">%s</div>' % e(p["notiz"])) if p["notiz"] else "",
                len(p["verlauf"]), verlauf))
    arbeit, weiter = fokus(b)
    jetzt_html = ("<b>Jetzt dran:</b> " + "; ".join("%s %s" % (e(p["nr"]), e(p["titel"])) for p in arbeit)
                  if arbeit else "<b>Jetzt dran:</b> nichts in Arbeit") + \
        ("<br><b>Danach:</b> " + " → ".join("%s %s" % (e(p["nr"]), e(p["titel"][:60])) for p in weiter) if weiter else "")
    zaehl = {s: sum(1 for p in punkte if p["status"] == s) for s in STAENDE}
    bereiche = sorted({p["bereich"] for p in punkte})
    tage = {}
    for n, h, d, s in log:
        tage.setdefault(d[:10], []).append((n, h, d[11:], s))
    chronik = "".join('<details%s><summary>%s - %d Commits</summary><ul>%s</ul></details>' % (
        " open" if i < 2 else "", t, len(c), "".join("<li><code>%s</code> %s <span class=\"leise\">%s</span> %s</li>" % (
            e(h), e(z), e(n), e(s)) for n, h, z, s in c)) for i, (t, c) in enumerate(sorted(tage.items(), reverse=True)))
    ohne_html = "".join("<li><code>%s</code> %s %s</li>" % (e(h), e(d), e(s)) for n, h, d, s in ohne) or "<li>keine</li>"
    fehlt_html = "".join("<li>%s: <code>%s</code></li>" % (e(n), e(w)) for n, w in fehlt_wo) or "<li>keine</li>"
    seite = VORLAGE.format(
        erzeugt=time.strftime("%d.%m.%Y, %H:%M"), anzahl=len(punkte),
        zaehlung=" · ".join("%s %d" % (STAND_TEXT[s], zaehl[s]) for s in STAENDE),
        bereiche="".join('<option>%s</option>' % e(x) for x in bereiche), karten="".join(karten),
        chronik=chronik, commits=len(log), ohne=ohne_html, jetzt=jetzt_html, n_ohne=len(ohne), fehlt=fehlt_html, n_fehlt=len(fehlt_wo),
        ab=AB_ZUORDNUNG)
    open(ANSICHT, "w", encoding="utf-8").write(seite)
    return len(punkte), len(log), len(ohne), len(fehlt_wo)


VORLAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Backlog SamurAI</title>
<style>
  :root {{ --bg:#f6f5f2; --karte:#ffffff; --text:#222; --leise:#666; --rand:#ddd; --gruen:#2e8b57; --gelb:#d4a017; --rot:#c0392b; --akzent:#3a5a8c; --blau:#2f6fb0; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg:#1e1f22; --karte:#2a2c30; --text:#e6e6e6; --leise:#aaa; --rand:#444; --akzent:#8fb0e0; --blau:#7fb0e8; }} }}
  body {{ background:var(--bg); color:var(--text); font:16px/1.5 system-ui, sans-serif; margin:0; padding:16px; }}
  main {{ max-width:960px; margin:0 auto; }}
  h1 {{ font-size:1.6em; margin:0 0 4px; }} .timestamps, .leise {{ color:var(--leise); font-size:.9em; }}
  .punkt {{ background:var(--karte); border:1px solid var(--rand); border-radius:10px; padding:10px 14px; margin:10px 0; border-left:6px solid var(--rand); }}
  .punkt.in_arbeit {{ border-left-color:var(--blau); }} .punkt.offen {{ border-left-color:var(--gelb); }} .punkt.gebaut {{ border-left-color:var(--gruen); }}
  .punkt.zurueckgestellt, .punkt.verworfen {{ border-left-color:var(--leise); opacity:.8; }}
  .punkt h2 {{ font-size:1.05em; margin:0 0 4px; }} .nr {{ color:var(--leise); font-weight:400; }}
  .stand {{ font-size:.75em; padding:1px 8px; border-radius:8px; border:1px solid var(--rand); margin-left:6px; font-weight:400; }}
  .meta, .notiz {{ font-size:.9em; }} .notiz {{ color:var(--leise); margin-top:4px; }}
  code {{ font-size:.88em; word-break:break-word; }} code.fehlt {{ color:var(--rot); text-decoration:line-through; }} code.da::before {{ content:"✓ "; color:var(--gruen); }}
  .zeile {{ display:flex; gap:10px; align-items:flex-start; margin-top:6px; }}
  select, textarea, input {{ font:inherit; color:var(--text); background:var(--bg); border:1px solid var(--rand); border-radius:6px; padding:4px 6px; }}
  textarea {{ width:100%; min-height:32px; box-sizing:border-box; }}
  .knoepfe {{ position:sticky; top:0; background:var(--bg); padding:8px 0; display:flex; gap:8px; flex-wrap:wrap; z-index:2; }}
  button {{ font:inherit; padding:6px 12px; border-radius:6px; border:1px solid var(--akzent); background:var(--karte); color:var(--text); cursor:pointer; }}
  .kasten {{ background:var(--karte); border:1px solid var(--rand); border-radius:10px; padding:10px 14px; margin:14px 0; }}
  details summary {{ cursor:pointer; }}
  .kasten.jetzt {{ border-left:6px solid var(--blau); }} .rang {{ font-size:.75em; padding:1px 8px; border-radius:8px; background:var(--blau); color:#fff; margin-left:6px; font-weight:400; }}
</style>
</head>
<body>
<main>
<h1>Backlog SamurAI</h1>
<div class="timestamps">Erstellt: 19.10.2026, 22:05 · zuletzt erzeugt {erzeugt} aus <code>docs/backlog/backlog.json</code> mit <code>uv run selfaware run backlog bauen</code> · {anzahl} Punkte: {zaehlung}</div>
<p class="leise">Nichts wird gelöscht, nur der Stand ändert sich, jede Änderung steht mit Zeit im Verlauf. „wo“ wird bei jedem Erzeugen nachgesehen: ✓ heißt, die Datei ist da, durchgestrichen heißt, sie fehlt.</p>
<div class="knoepfe">
  <input id="suche" placeholder="Suchen…" oninput="filtern()">
  <select id="stand" onchange="filtern()"><option value="">alle Stände</option><option value="in_arbeit">in Arbeit</option><option value="offen">offen</option><option value="gebaut">gebaut</option><option value="zurueckgestellt">zurückgestellt</option><option value="verworfen">verworfen</option></select>
  <select id="bereich" onchange="filtern()"><option value="">alle Bereiche</option>{bereiche}</select>
  <button onclick="kopieren()">Kopieren</button><button onclick="herunterladen()">Herunterladen</button>
</div>
<div class="kasten jetzt">{jetzt}</div>
<div class="kasten"><b>Zur Kontrolle:</b> Commits ab {ab} ohne Punkt-Nummer: {n_ohne} · Dateien unter „wo“, die fehlen: {n_fehlt}
<details><summary>Commits ohne Punkt</summary><ul>{ohne}</ul></details>
<details><summary>Fehlende Dateien</summary><ul>{fehlt}</ul></details></div>
{karten}
<div class="kasten"><h2 style="font-size:1.15em;margin:0 0 6px">Chronik: was wann gemacht wurde ({commits} Commits, Selfaware-AI und VillageStudio)</h2>{chronik}</div>
</main>
<script>
function filtern() {{
  const q = document.getElementById('suche').value.toLowerCase(), s = document.getElementById('stand').value, b = document.getElementById('bereich').value;
  document.querySelectorAll('.punkt').forEach(p => {{
    const ok = (!q || p.textContent.toLowerCase().includes(q)) && (!s || p.dataset.stand === s) && (!b || p.dataset.bereich === b);
    p.style.display = ok ? '' : 'none';
  }});
}}
function zustand() {{
  return [...document.querySelectorAll('.punkt')].map(p => ({{ titel: p.querySelector('h2').textContent,
    ampel: p.querySelector('.ampel').value, notiz: p.querySelector('textarea').value }}));
}}
function kopieren() {{
  const t = zustand().filter(z => z.ampel !== 'offen' || z.notiz).map(z => z.titel + ' [' + z.ampel + ']' + (z.notiz ? ': ' + z.notiz : '')).join('\\n');
  navigator.clipboard.writeText('Backlog SamurAI - Notizen\\n' + t);
}}
function herunterladen() {{
  document.querySelectorAll('textarea').forEach(t => t.textContent = t.value);
  document.querySelectorAll('select').forEach(s => [...s.options].forEach(o => o.toggleAttribute('selected', o.value === s.value)));
  const b = new Blob(['<!doctype html>\\n' + document.documentElement.outerHTML], {{ type: 'text/html' }});
  const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'Backlog_Notizen.html'; a.click();
}}
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="Backlog SamurAI")
    sub = ap.add_subparsers(dest="was", required=True)
    n = sub.add_parser("neu")
    n.add_argument("--titel", required=True); n.add_argument("--bereich", required=True); n.add_argument("--herkunft", required=True)
    n.add_argument("--status", default="offen"); n.add_argument("--wo", default=""); n.add_argument("--belege", default="")
    n.add_argument("--notiz", default=""); n.add_argument("--seit"); n.add_argument("--gebaut"); n.add_argument("--commits", default="")
    s = sub.add_parser("stand")
    s.add_argument("nr"); s.add_argument("status"); s.add_argument("--commit"); s.add_argument("--wo", default="")
    s.add_argument("--belege", default=""); s.add_argument("--notiz", default="")
    z = sub.add_parser("zuordnen"); z.add_argument("nr"); z.add_argument("commits")
    r = sub.add_parser("rang"); r.add_argument("nr"); r.add_argument("platz", type=int)
    sub.add_parser("fokus")
    l = sub.add_parser("liste"); l.add_argument("status", nargs="?")
    sub.add_parser("bauen")
    sub.add_parser("import_alt")
    a = ap.parse_args()
    b = lade()
    if a.was == "neu":
        p = neu(b, a.titel, a.bereich, a.herkunft, a.status, liste(a.wo), liste(a.belege), a.notiz, a.seit, a.gebaut,
                liste(a.commits))
        speichere(b)
        print("%s angelegt: %s [%s]" % (p["nr"], p["titel"], STAND_TEXT[p["status"]]))
    elif a.was == "stand":
        p = stand(b, a.nr, a.status, a.commit, liste(a.wo), liste(a.belege), a.notiz)
        speichere(b)
        print("%s jetzt %s" % (p["nr"], STAND_TEXT[p["status"]]))
    elif a.was == "zuordnen":
        p, neu_c = zuordnen(b, a.nr, liste(a.commits))
        speichere(b)
        print("%s: %d Commits zugeordnet" % (p["nr"], len(neu_c)))
    elif a.was == "rang":
        p = rang(b, a.nr, a.platz)
        speichere(b)
        print("%s jetzt Rang %d" % (p["nr"], p["rang"]))
    elif a.was == "fokus":
        arbeit, weiter = fokus(b)
        print("JETZT DRAN: " + ("; ".join("%s %s" % (p["nr"], p["titel"]) for p in arbeit) or "nichts in Arbeit"))
        for p in weiter:
            print("  danach Rang %d: %s %s" % (p["rang"], p["nr"], p["titel"]))
    elif a.was == "liste":
        for p in b["punkte"]:
            if not a.status or p["status"] == a.status:
                print("%-6s %-15s %-14s %s" % (p["nr"], STAND_TEXT[p["status"]], p["bereich"][:14], p["titel"][:90]))
    elif a.was == "import_alt":
        k = import_alt(b)
        speichere(b)
        print("%d Punkte aus Backlog.md uebernommen" % k)
    elif a.was == "bauen":
        n_p, n_c, n_o, n_f = bauen(b)
        print("Backlog.html: %d Punkte, %d Commits in der Chronik, %d Commits ohne Punkt, %d fehlende Dateien" % (n_p, n_c, n_o, n_f))


if __name__ == "__main__":
    main()
