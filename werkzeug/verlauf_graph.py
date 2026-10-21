# -*- coding: utf-8 -*-
"""B-155 Partie-Verlauf als Graphen (Daniel 21.10.2026 20:54: "lies die Endbildschirm-Werte waehrend des gesamten Spiels aus und
zeig mir daraus wie bei AoE2 eine Entwicklung ueber das ganze Spiel per Graph - Einheiten/Ressourcen/Gebaeude/Trades").
Quelle: ucp/villagestudio/verlauf.jsonl (logik.lua verlaufTick, alle 250 Takte je aktivem Spieler). Genommen wird die
letzte Partie (ab der letzten Zeile {"neu": ...}) oder die mit partie=N (1 = erste in der Datei). Ausgabe: eine
eigenstaendige HTML-Seite in daten/ (kleine Liniendiagramme je Kennzahl, eine Linie je Spieler, Werte beim Darueberfahren,
Tabelle der Endwerte) und die Rohdaten dieser Partie daneben.
Aufruf: SHC_INSTANZ=5 python werkzeug/verlauf_graph.py [partie=N]   -> druckt den Pfad der Seite
"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from befehl import SPIEL  # noqa: E402

QUELLE = os.path.join(SPIEL, "ucp", "villagestudio", "verlauf.jsonl")
DATEN = os.path.join(HIER, "..", "daten")

# (Schluessel, Titel, Teiler) je Gruppe - "Endbildschirm" = Werte aus SkirmishStatistics (dieselben Zahlen wie am Ende)
GRUPPEN = [
    ("Heer", [("soldaten", "Soldaten jetzt", 1), ("s_truppen", "Truppen ausgebildet (Endbildschirm)", 1),
              ("kills", "Abschuesse (Kill-Matrix)", 1), ("verluste", "Verluste (Kill-Matrix)", 1)]),
    ("Volk und Burg", [("leute", "Bevoelkerung", 1), ("arbeiter", "Arbeiter und Volk (Einheiten ohne Soldaten)", 1),
                       ("gebaeude", "Gebaeude", 1), ("beliebt", "Beliebtheit", 100)]),
    ("Vorrat jetzt", [("gold", "Gold", 1), ("holz", "Holz", 1), ("stein", "Stein", 1), ("eisen", "Eisen", 1),
                      ("nahrung", "Nahrung (Brot, Kaese, Fleisch, Aepfel)", 1), ("waffen", "Waffen und Ruestung", 1)]),
    ("Erzeugt seit Spielbeginn (Endbildschirm)", [("s_gold", "Gold", 1), ("s_holz", "Holz", 1), ("s_stein", "Stein", 1),
                                                  ("s_eisen", "Eisen", 1), ("s_pech", "Pech", 1), ("s_nahrung", "Nahrung", 1),
                                                  ("s_waffen", "Waffen", 1)]),
    ("Zerstoerung und Handel (Endbildschirm)", [("s_verbrannt", "Feindliche Gebaeude zerstoert", 1),
                                                ("s_zerstoert", "Eigene Gebaeude verloren", 1),
                                                ("s_erhalten", "Handel: Waren erhalten", 1), ("s_gesendet", "Handel: Waren gesendet", 1)]),
]


def lies_partien(pfad=QUELLE):
    partien, kopf, punkte = [], None, []
    with open(pfad, encoding="utf-8", errors="replace") as f:
        for z in f:
            z = z.strip()
            if not z:
                continue
            try:
                d = json.loads(z)
            except ValueError:
                continue
            if "neu" in d:
                if kopf is not None or punkte:
                    partien.append((kopf, punkte))
                kopf, punkte = d, []
            elif "t" in d:
                punkte.append(d)
    if kopf is not None or punkte:
        partien.append((kopf, punkte))
    return partien


SEITE = r"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Partie-Verlauf</title>
<style>
.viz-root { color-scheme: light; --surface-0:#f4f4f2; --surface-1:#fcfcfb; --text-primary:#0b0b0b; --text-secondary:#52514e;
  --text-muted:#7a7974; --grid:#e3e2de; --axis:#c9c8c2; --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100;
  --s5:#e87ba4; --s6:#008300; --s7:#6250d6; --s8:#e34948; }
@media (prefers-color-scheme: dark) { :root:where(:not([data-theme="light"])) .viz-root { color-scheme: dark;
  --surface-0:#121211; --surface-1:#1a1a19; --text-primary:#f0efec; --text-secondary:#c3c2b7; --text-muted:#8f8e86;
  --grid:#2c2c2a; --axis:#3d3d3a; --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#008300;
  --s7:#9085e9; --s8:#e66767; } }
:root[data-theme="dark"] .viz-root { color-scheme: dark; --surface-0:#121211; --surface-1:#1a1a19; --text-primary:#f0efec;
  --text-secondary:#c3c2b7; --text-muted:#8f8e86; --grid:#2c2c2a; --axis:#3d3d3a; --s1:#3987e5; --s2:#d95926; --s3:#199e70;
  --s4:#c98500; --s5:#d55181; --s6:#008300; --s7:#9085e9; --s8:#e66767; }
body { margin:0; background:#f4f4f2; }
@media (prefers-color-scheme: dark) { body { background:#121211; } }
.viz-root { background:var(--surface-0); color:var(--text-primary); font:14px/1.45 system-ui, "Segoe UI", sans-serif;
  padding:20px 16px 40px; min-height:100vh; box-sizing:border-box; }
h1 { font-size:22px; margin:0 0 4px; } h2 { font-size:16px; margin:28px 0 10px; color:var(--text-secondary); font-weight:600; }
.timestamps, .unter { color:var(--text-muted); font-size:12px; }
.legende { display:flex; flex-wrap:wrap; gap:14px; margin:14px 0 4px; }
.legende span { display:inline-flex; align-items:center; gap:6px; color:var(--text-secondary); }
.legende i { width:14px; height:3px; border-radius:2px; display:inline-block; }
.raster { display:grid; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); gap:12px; }
.karte { background:var(--surface-1); border-radius:10px; padding:10px 12px 6px; position:relative; }
.karte h3 { font-size:13px; font-weight:600; margin:0 0 4px; color:var(--text-primary); }
svg { width:100%; height:auto; display:block; overflow:visible; }
.tip { position:absolute; pointer-events:none; background:var(--surface-0); border:1px solid var(--axis); border-radius:6px;
  padding:6px 8px; font-size:12px; color:var(--text-primary); display:none; white-space:nowrap; z-index:2; }
table { border-collapse:collapse; font-size:12px; margin-top:8px; } td, th { padding:3px 10px; text-align:right;
  border-bottom:1px solid var(--grid); } th:first-child, td:first-child { text-align:left; }
details { margin-top:28px; } summary { cursor:pointer; color:var(--text-secondary); }
</style></head>
<body><div class="viz-root">
<h1>Partie-Verlauf</h1>
<div class="timestamps">Erstellt: __ERSTELLT__</div>
<div class="unter">__UNTER__</div>
<div class="legende" id="legende"></div>
<div id="gruppen"></div>
<details><summary>Tabelle: Endwerte je Spieler</summary><div id="tabelle"></div></details>
</div>
<script>
const DATEN = __DATEN__;
const GRUPPEN = __GRUPPEN__;
const spieler = DATEN.spieler;                       // [[nr, name], ...]
const farbe = nr => `var(--s${((nr - 1) % 8) + 1})`;
const leg = document.getElementById("legende");
spieler.forEach(([nr, name]) => { leg.insertAdjacentHTML("beforeend",
  `<span><i style="background:${farbe(nr)}"></i>${name} (Spieler ${nr})</span>`); });
const fmt = v => v == null ? "–" : Math.round(v).toLocaleString("de-DE");
const B = 300, H = 150, L = 44, R = 46, O = 8, U = 22;
function diagramm(karte, schl, teiler) {
  const ts = DATEN.punkte.map(p => p.t);
  const reihen = spieler.map(([nr]) => DATEN.punkte.map(p => { const s = p.sp[nr]; return s && s[schl] != null ? s[schl] / teiler : null; }));
  const alle = reihen.flat().filter(v => v != null);
  if (!alle.length || !ts.length) { karte.insertAdjacentHTML("beforeend", `<div class="unter">keine Daten</div>`); return; }
  let lo = Math.min(0, ...alle), hi = Math.max(...alle); if (hi === lo) hi = lo + 1;
  const t0 = ts[0], t1 = ts[ts.length - 1] === t0 ? t0 + 1 : ts[ts.length - 1];
  const x = t => L + (t - t0) / (t1 - t0) * (B - L - R), y = v => O + (1 - (v - lo) / (hi - lo)) * (H - O - U);
  let svg = `<svg viewBox="0 0 ${B} ${H}" role="img">`;
  for (let k = 0; k <= 3; k++) { const v = lo + (hi - lo) * k / 3, yy = y(v);
    svg += `<line x1="${L}" x2="${B - R}" y1="${yy}" y2="${yy}" stroke="var(--grid)" stroke-width="1"/>` +
           `<text x="${L - 6}" y="${yy + 4}" font-size="10" text-anchor="end" fill="var(--text-muted)">${fmt(v)}</text>`; }
  svg += `<text x="${L}" y="${H - 6}" font-size="10" fill="var(--text-muted)">Takt ${fmt(t0)}</text>` +
         `<text x="${B - R}" y="${H - 6}" font-size="10" text-anchor="end" fill="var(--text-muted)">${fmt(t1)}</text>`;
  const enden = [];
  reihen.forEach((r, i) => { let d = "", an = false;
    r.forEach((v, j) => { if (v == null) { an = false; return; } d += (an ? "L" : "M") + x(ts[j]).toFixed(1) + "," + y(v).toFixed(1); an = true; });
    svg += `<path d="${d}" fill="none" stroke="${farbe(spieler[i][0])}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`;
    const letzt = [...r].reverse().find(v => v != null);
    if (letzt != null) enden.push([y(letzt), i, letzt]); });
  enden.sort((a, b) => a[0] - b[0]);                  // Endbeschriftung ohne Ueberlappung
  let vorher = -99; enden.forEach(([yy, i, v]) => { const yl = Math.max(yy, vorher + 11); vorher = yl;
    svg += `<text x="${B - R + 4}" y="${yl + 3}" font-size="10" fill="var(--text-secondary)">${fmt(v)}</text>`; });
  svg += `<line class="kreuz" x1="0" x2="0" y1="${O}" y2="${H - U}" stroke="var(--axis)" stroke-width="1" visibility="hidden"/>`;
  svg += `<rect x="${L}" y="0" width="${B - L - R}" height="${H - U}" fill="transparent"/></svg>`;
  karte.insertAdjacentHTML("beforeend", svg + `<div class="tip"></div>`);
  const el = karte.querySelector("svg"), kreuz = el.querySelector(".kreuz"), tip = karte.querySelector(".tip");
  el.addEventListener("mousemove", ev => {
    const r = el.getBoundingClientRect(), px = (ev.clientX - r.left) / r.width * B;
    let j = 0, best = 1e18; ts.forEach((t, k) => { const dd = Math.abs(x(t) - px); if (dd < best) { best = dd; j = k; } });
    kreuz.setAttribute("x1", x(ts[j])); kreuz.setAttribute("x2", x(ts[j])); kreuz.setAttribute("visibility", "visible");
    tip.innerHTML = `<b>Takt ${fmt(ts[j])}</b><br>` + spieler.map(([nr, name], i) =>
      `<span style="color:${farbe(nr)}">■</span> ${name}: ${fmt(reihen[i][j])}`).join("<br>");
    tip.style.display = "block";
    const kx = (ev.clientX - karte.getBoundingClientRect().left);
    tip.style.left = Math.min(kx + 12, karte.clientWidth - tip.offsetWidth - 4) + "px"; tip.style.top = "30px"; });
  el.addEventListener("mouseleave", () => { kreuz.setAttribute("visibility", "hidden"); tip.style.display = "none"; });
}
const wurzel = document.getElementById("gruppen");
GRUPPEN.forEach(([titel, felder]) => {
  wurzel.insertAdjacentHTML("beforeend", `<h2>${titel}</h2><div class="raster"></div>`);
  const raster = wurzel.lastElementChild;
  felder.forEach(([schl, name, teiler]) => { raster.insertAdjacentHTML("beforeend", `<div class="karte"><h3>${name}</h3></div>`);
    diagramm(raster.lastElementChild, schl, teiler); }); });
const letzt = DATEN.punkte[DATEN.punkte.length - 1] || {sp: {}};
let tab = `<table><tr><th>Kennzahl</th>${spieler.map(([nr, n]) => `<th>${n}</th>`).join("")}</tr>`;
GRUPPEN.forEach(([titel, felder]) => felder.forEach(([schl, name, teiler]) => {
  tab += `<tr><td>${name}</td>${spieler.map(([nr]) => `<td>${fmt(letzt.sp[nr] && letzt.sp[nr][schl] != null ? letzt.sp[nr][schl] / teiler : null)}</td>`).join("")}</tr>`; }));
document.getElementById("tabelle").innerHTML = tab + "</table>";
</script></body></html>
"""


def bauen(partie=None):
    partien = lies_partien()
    if not partien:
        raise SystemExit("FEHLER: keine Partie in %s" % QUELLE)
    kopf, punkte = partien[(partie - 1) if partie else -1]
    kopf = kopf or {}
    nummern = sorted({int(n) for p in punkte for n in p.get("sp", {})})
    namen = kopf.get("namen", {})
    spieler = [[n, namen.get(str(n)) or "Spieler %d" % n] for n in nummern]
    daten = {"spieler": spieler, "punkte": punkte}
    stempel = time.strftime("%Y%m%d_%H%M%S")
    unter = "Partie ab %s, %d Messpunkte (alle 250 Takte), Takt %s bis %s - Quelle: logik.lua verlaufTick, %s" % (
        kopf.get("neu", "?"), len(punkte), punkte[0]["t"] if punkte else "-", punkte[-1]["t"] if punkte else "-",
        os.path.basename(QUELLE))
    html = (SEITE.replace("__ERSTELLT__", time.strftime("%d.%m.%Y %H:%M")).replace("__UNTER__", unter)
            .replace("__DATEN__", json.dumps(daten, ensure_ascii=False)).replace("__GRUPPEN__", json.dumps(GRUPPEN, ensure_ascii=False)))
    os.makedirs(DATEN, exist_ok=True)
    seite = os.path.abspath(os.path.join(DATEN, "verlauf_%s.html" % stempel))
    open(seite, "w", encoding="utf-8").write(html)
    with open(os.path.join(DATEN, "verlauf_%s.jsonl" % stempel), "w", encoding="utf-8") as f:
        f.write(json.dumps(kopf, ensure_ascii=False) + "\n")
        for p in punkte:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    return seite, len(punkte), spieler


if __name__ == "__main__":
    a = dict(x.split("=", 1) for x in sys.argv[1:])
    s, n, sp = bauen(int(a["partie"]) if "partie" in a else None)
    print("OK: %s (%d Messpunkte, Spieler %s)" % (s, n, sp))
