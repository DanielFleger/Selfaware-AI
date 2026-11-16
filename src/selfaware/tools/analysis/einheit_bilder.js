// Einheitenbilder fuer die Wertungsseite (Daniel 16.11.2026 18:18 "es fehlen auch noch Bilder von den einheiten ... sieh ai toolkit").
// Liest die Spielbilder gfx/chimpNN_<name>.tgx (NN = Einheitenart, wie im Lageprotokoll) und schreibt einheit_NN.png.
// Den TGX-Leser und den PNG-Schreiber nimmt es aus dem AI-Toolkit (src/node/gm1.js, src/node/pixel-image.js) - kein zweiter Weg.
// Aufruf: node einheit_bilder.js <AI-Toolkit-Ordner> <gfx-Ordner des Spiels> <Zielordner>
const fs = require('fs');
const path = require('path');
const [toolkit, gfx, ziel] = process.argv.slice(2);
const { tgxToRgba } = require(path.join(toolkit, 'src', 'node', 'gm1.js'));
const { encodeRgbaPng } = require(path.join(toolkit, 'src', 'node', 'pixel-image.js'));
fs.mkdirSync(ziel, { recursive: true });
let n = 0;
for (const name of fs.readdirSync(gfx)) {
  const m = /^chimp(\d+)_.*\.tgx$/i.exec(name);
  if (!m || m[1] === '00') continue;
  const roh = fs.readFileSync(path.join(gfx, name));
  const breite = roh.readUInt32LE(0), hoehe = roh.readUInt32LE(4);
  const rgba = tgxToRgba(roh.subarray(8), breite, hoehe, null);
  fs.writeFileSync(path.join(ziel, 'einheit_' + parseInt(m[1], 10) + '.png'), encodeRgbaPng(breite, hoehe, rgba));
  n++;
}
console.log(n + ' Einheitenbilder nach ' + ziel);
