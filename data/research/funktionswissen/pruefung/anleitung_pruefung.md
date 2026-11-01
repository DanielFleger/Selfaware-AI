# Prüfauftrag: Erklärungen widerlegen

Je Funktion bekommst du den Code (`--- CODE ---`) und die fertige Erklärung (`--- ERKLAERUNG ---`, eine JSON-Zeile).
**Deine Aufgabe ist, Fehler zu finden, nicht zu bestätigen.** Prüfe jede Aussage gegen den Code:
- Stimmen Zahlen, Grenzen, Bedingungen und Fehlercodes? Rechne Bit-Ausdrücke selbst nach.
- Ist eine Vermutung als Tatsache formuliert, besonders bei Feldnamen mit `Unk`, `field…` oder `param_…`?
- Fehlt etwas Wichtiges, zum Beispiel eine Zahl oder ein Sonderfall?
- Ist `gehirn` oder `live` irreführend?

Schreibe `pruefung/ergebnisse/<paket>.jsonl` mit genau einer JSON-Zeile je Funktion:
```json
{"adr":"0x...","name":"...","urteil":"richtig|kleiner_fehler|falsch","befunde":["konkreter Fehler mit Begründung aus dem Code"],"korrektur":"berichtigter Text oder \"-\""}
```
- `richtig` = keine sachlichen Fehler; Stilfragen zählen nicht.
- `kleiner_fehler` = Ungenauigkeit ohne Folgen für die Nutzung.
- `falsch` = mindestens eine Aussage widerspricht dem Code oder würde das Gehirn in die Irre führen.

Im Zweifel ist es kein Fehler. Nur melden, was du am Code belegen kannst.
