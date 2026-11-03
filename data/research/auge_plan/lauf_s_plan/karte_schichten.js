// B-142 Plan Lauf S: Schichten einer .map fuer die Flaechenrechnung auspacken. Nur lesen.
// Aufruf: node karte_schichten.js "<karte.map>" "<Ausgabe-Stamm>"
const fs = require('fs');
const K = require('C:/Users/danie/Documents/PC_Affe/Games/Stronghold_Crusader/Stronghold Crusader Modding/Tools/VillageStudio/lib/karte.js');
const pfad = process.argv[2], ziel = process.argv[3];
const buf = fs.readFileSync(pfad);
const k = K.leseAbschnitte(buf);
function roh(id) { const ab = k.abschnitte.find(a => a.id === id); return ab ? K.abschnittsDaten(k, ab) : null; }
const aus = {};
for (const [id, name] of [[1003, 'logik'], [1005, 'hoehe'], [1004, 'organismus'], [1012, 'gebaeude'], [1010, 'einheit']]) {
  const d = roh(id);
  aus[name] = d ? d.length : null;
  if (d) fs.writeFileSync(ziel + '.' + name + '.bin', d);
}
console.log(JSON.stringify(aus));
