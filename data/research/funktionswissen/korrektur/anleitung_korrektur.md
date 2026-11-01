# Korrekturauftrag: große Funktionen prüfen und berichtigen

Je Funktion bekommst du den Code (`--- CODE ---`) und die bisherige Erklärung (`--- ERKLAERUNG ---`, eine JSON-Zeile im Format aus `anleitung.md`).
Die bisherigen Erklärungen großer Funktionen sind oft zu grob. In einer Stichprobe enthielten 7 von 18 eine falsche Aussage. Typische Fehler:
- Grenzen um eins verschoben, etwa `if (0x51 < x) x = 0x50` gelesen als „höchstens 0x50“.
- Bit-Ausdrücke falsch aufgelöst: `(v ^ 0xfffffff8) & 0xf == 0` heißt `v & 0xf == 8`.
- „genau ein“ statt „mindestens ein“.
- Werte, die *vor* einer Prüfung geschrieben werden, als „nichts wird geändert“ dargestellt.
- Bedingungen weggelassen, etwa „Ton nur wenn animationActive != 0“ oder „nur im Zweig != GM_SOLITARY“.
- Vermutungen über Felder mit `Unk`/`field…` als Tatsache formuliert, besonders in `gehirn` und `live`.
- Wichtige Zweige oder gesetzte Werte fehlen.

**Aufgabe:** Prüfe jede Aussage gegen den Code und schreibe die Erklärung **vollständig neu und berichtigt**: dasselbe JSON-Format, dieselben Felder, auch `live` und `live_art`.
- Bei großen Funktionen sind bis zu 15 `regeln` erlaubt. Jede Regel muss am Code belegbar sein.
- Unklares gehört nach `offen` oder bekommt das Wort „vermutlich“.
- Stimmt die bisherige Erklärung, übernimm sie unverändert.

Schreibe `korrektur/ergebnisse/<paket>.jsonl` mit genau einer JSON-Zeile je Funktion. Jede Zeile ist die berichtigte Erklärung plus das Zusatzfeld `"korrigiert":"ja|nein"` und `"aenderung":"ein Satz, was falsch war, oder \"-\""`.
