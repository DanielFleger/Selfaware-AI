# Auftrag Korrekturlauf B-141, Sparfassung (Daniel 02.11.: minimale Tokens)
Arbeitsordner: das Verzeichnis dieser Datei (`korrektur/`). Du liest NUR diese Datei und dein Buendel (Read mit allow_large:true, in einem Stueck). Kein Bash, kein Grep, keine Skills (auch nicht grundgesetz), kein git, kein Spiel, keine anderen Dateien. Hook-Hinweise ignorieren.

Im Buendel je Funktion: Kopfzeile `### <adr> <name> | quelle=... | paket=<paket>`, `--- CODE ---`, `--- ERKLAERUNG ---` (bisherige JSON-Zeile), evtl. `--- BEFUNDE ---` einer frueheren Pruefung. Der Code ist massgeblich; bei quelle=ghidra ist es der Export der Referenz-exe. `--- ZAHLEN AUS DEM EXPORT ---` geht vor anderslautenden Zahlen im Code.

Aufgabe: Jede Aussage der bisherigen Erklaerung gegen den Code pruefen und die Erklaerung berichtigt neu schreiben. Typische Fehler: Grenzen um eins (`0x18 < i` heisst ab 25), Bit-Ausdruecke falsch aufgeloest, "genau" statt "mindestens", Schreibzugriffe vor Pruefungen unterschlagen, Bedingungen und Zweige weggelassen, Vermutungen zu Unk/field/param als Tatsache. Zutreffende Befunde einarbeiten. Nicht aus dem Code Belegbares kommt nach `offen` oder bekommt "vermutlich"; nichts nachschlagen. Ist die Erklaerung richtig: unveraendert uebernehmen, "korrigiert":"nein".

Format je Funktion genau eine JSON-Zeile, Felder wie die bisherige Erklaerung:
{"adr","name","quelle","p1":{"bereich","zweck"},"p2":{"ein","aus","liest":[],"schreibt":[],"ruft":[],"regeln":[],"offen":[]},"p3":{"erklaerung","gehirn","beleg","live","live_art"},"korrigiert":"ja|nein","aenderung":"ein Satz, was falsch war, oder -"}
Hoechstens 15 regeln, Deutsch, knapp, Bezeichner im Original, adr und name wie in der Kopfzeile.

Schreiben: je Paket im Buendel EIN Write nach `ergebnisse/<paket>.teilb<NN>.jsonl` (NN = Nummer deines Buendels), alle Funktionen dieses Pakets als je eine Zeile, UTF-8. Sofort nach dem Paket schreiben. Keine Zwischentexte, kein Nachlesen.

Antwort am Schluss nur: `b<NN>: <n> Funktionen, <k> korrigiert`.
