// Burgplan (AIV) eines Gegners lesbar machen (SAI 11.10., Daniel: "seinen Code anschauen, aiv/aic ist wohl ein Schluessel").
// Liest mit dem Decoder aus VillageStudio; gibt Bergfried-Lage, Bauten je Gruppe und die Bauschritte in Reihenfolge aus.
// Aufruf: node aiv_lesen.js <datei.aiv> [schritte=60]
const fs = require('fs');
const path = require('path');
const workspace = process.env.SELFAWARE_WORKSPACE || path.resolve(__dirname, '..', '..');
const villageStudio = process.env.SELFAWARE_VILLAGE_STUDIO_PATH || path.resolve(workspace, '..', 'VillageStudio');
const VS = path.join(villageStudio, 'lib');
const { decode, GRID } = require(path.join(VS, 'aiv.js'));
const G = require(path.join(VS, 'gebaeude.json')).gebaeude;

const datei = process.argv[2];
const zeigen = parseInt((process.argv[3] || 'schritte=60').split('=')[1], 10);
const a = decode(fs.readFileSync(datei));
const name = (id) => (G[id] ? G[id].name : 'Nr ' + id);
const gruppe = (id) => (G[id] ? G[id].gruppe : '?');

// je Bauschritt: Bauwerk, Feldzahl, linke obere Ecke
const schritte = new Map();
for (let i = 0; i < GRID * GRID; i++) {
  const t = a.bauten[i], s = a.schritte[i];
  if (!t || t === 1 || t === 2) continue;
  const x = i % GRID, y = Math.floor(i / GRID);
  const e = schritte.get(s) || { typ: t, felder: 0, x0: x, y0: y, x1: x, y1: y };
  e.felder++; e.x0 = Math.min(e.x0, x); e.y0 = Math.min(e.y0, y); e.x1 = Math.max(e.x1, x); e.y1 = Math.max(e.y1, y);
  schritte.set(s, e);
}
const liste = [...schritte.entries()].sort((p, q) => p[0] - q[0]);

const jeGruppe = {};
for (const [, e] of liste) {
  const g = gruppe(e.typ);
  jeGruppe[g] = jeGruppe[g] || {};
  jeGruppe[g][name(e.typ)] = (jeGruppe[g][name(e.typ)] || 0) + 1;
}
const berg = liste.find(([, e]) => e.typ === 38);
console.log('Datei', path.basename(datei), '| Bauschritte', liste.length, '| Pausen', JSON.stringify(a.pausen), '| Pausenlaenge', a.pausenlaenge);
console.log('Bergfried', berg ? 'Schritt ' + berg[0] + ' bei (' + berg[1].x0 + ',' + berg[1].y0 + ')-(' + berg[1].x1 + ',' + berg[1].y1 + ')' : 'KEINER');
for (const g of Object.keys(jeGruppe)) console.log('  ' + g + ':', JSON.stringify(jeGruppe[g]));
console.log('Einheiten/Feuer/Flaggen (Abschnitt 2012, Zeilen ungleich 0):');
(a.einheiten || []).forEach((r, i) => { if (r.some((v) => v)) console.log('  Zeile', i, JSON.stringify(r)); });
console.log('Erste', zeigen, 'Bauschritte (Schritt: Bauwerk @ Ecke, Felder):');
console.log('  ' + liste.slice(0, zeigen).map(([s, e]) => s + ':' + name(e.typ) + '@' + e.x0 + ',' + e.y0 + (e.felder > 1 ? '/' + e.felder : '')).join(' | '));
