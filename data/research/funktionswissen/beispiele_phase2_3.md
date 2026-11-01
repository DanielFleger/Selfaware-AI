# Funktionswissen: Beispiele für Phase 1 bis 3

Quelle des Pseudocodes: `Selfaware-AI/research/native/dekomp_kauf_ki.c` und `dekomp_anwerben.c`.
Feldlagen stammen aus `VillageStudio/lib/strukturen.txt`.
Wichtige Basisadressen:
- `playerDataArray` = 0x0115BDF8, je Spieler 0x39F4.
- `GameStateStructures` = 0x0112B0B8. Sie ist daraus berechnet.

Kennzeichnung der Aussagen:
- **[Code]** = steht so im Pseudocode.
- **[Live]** = im laufenden Spiel bestätigt.
- **[Offen]** = noch nicht belegt.

---

## 1. Preis-Familie: getBatchBuyPrice / getBuyPriceForOneUnit / getBuyPrice
Adressen: 00458890 / 004588d0 / 004588a0

**Phase 1 – Durchsehen**
- Bereich: Wirtschaft, spielrelevant.
- Die drei Funktionen liefern Kaufpreise am Markt.

**Phase 2 – Analyse**
- `getBatchBuyPrice(spieler, ware)` gibt `buyAndSalesPriceArray[ware].buyPrice` zurück. Das ist der Preis für 5 Stück. [Code]
- `getBuyPriceForOneUnit(ware)` gibt `buyPrice / 5` zurück, ganzzahlig abgerundet. [Code]
- `getBuyPrice(spieler, ware, menge)` gibt `(buyPrice / 5) * menge` zurück. [Code]
- Der Spieler-Parameter wird nirgends benutzt. [Code]
- Die Preistabelle liegt bei 0x0117CFD4. Jede Ware hat dort 8 Byte: erst Kaufpreis, dann Verkaufspreis. [Code, Adresse berechnet, live ungeprüft]

**Phase 3 – Erklärung und Anwendung**
- Alle Spieler nutzen dieselbe Preistabelle. Die KI kauft aber über `buyGoods` mit abgerundetem Stückpreis mal Menge. Ist der Lospreis nicht durch 5 teilbar, zahlt sie bis zu 4 Gold weniger je 5 Stück. [Code, OpenSHC-Nachbau]
- Der Einzelpreis ist abgerundet. Bei einem Lospreis von 72 ergibt das 14 je Stück. Fünf mal 14 sind 70, bezahlt werden aber 72.
- Für das Gehirn heißt das:
  - Immer mit dem Lospreis rechnen, nie mit dem Einzelpreis.
  - Die Preise lassen sich direkt aus der Tabelle lesen. Dafür braucht es keinen Spielbefehl.
- Belege:
  - „Stein ~14 je Stück“ (L65) passt zu einem Lospreis um 70. [Live]
  - Die Tabellenadresse muss noch einmal live gelesen werden. [Offen]

---

## 2. ProcessBuyOrSell (00465e60)

**Phase 1 – Durchsehen**
- Bereich: Wirtschaft, spielrelevant.
- Die Funktion führt einen Kauf oder Verkauf am Markt aus.

**Phase 2 – Analyse**
- Eingaben: Spieler, Richtung (0 = kaufen, 1 = verkaufen), Ware.
- **Kaufen** [Code]:
  - Der Preis kommt aus `getBatchBuyPrice`.
  - Der Kauf läuft nur, wenn beide Bedingungen erfüllt sind:
    - Das Gold `currentResources[15]` ist mindestens so hoch wie der Preis.
    - `processResourceGain(spieler, ware, 5)` gelingt.
  - Erst danach werden Gold und `marketGold` um den Preis verringert.
- **Verkaufen** [Code]:
  - Die Menge kommt aus `getSellResourceAmount`, der Erlös aus `getSalesPrice`.
  - Gold, `marketGold` und die Endstatistik `finalGold` steigen um den Erlös.
  - Die Ware wird über `processResourceLoss` abgebucht.
- Geschriebene Felder: Gold (PlayerData +0x4D0 + 15·4), `marketGold` (+0x54) und `finalResults.finalGold`.
- Offene Fragen:
  - `processResourceGain` ist noch nicht gelesen. Vermutlich scheitert sie, wenn kein Lagerplatz frei ist. [Offen]
  - `getSellResourceAmount` ist noch nicht gelesen. [Offen]

**Phase 3 – Erklärung und Anwendung**
- Gekauft wird immer genau ein Los zu 5 Stück. Scheitert die Einlagerung, passiert gar nichts: Es wird kein Gold abgezogen und es kommt keine Meldung.
- Für das Gehirn heißt das:
  - Ein Kaufbefehl ist kein Kauf.
  - Danach den Bestand nachmessen.
  - Vorher prüfen, ob Gold mindestens den Lospreis deckt und ob im passenden Lager Platz ist: Kornspeicher, Lager oder Waffenkammer.
- Belege:
  - Die 5er-Lose passen zu unserem Lenker:
    - `wirtschaft.py:288` sagt: „Verkaeufe gehen nur in 5er-Losen“.
    - Spielbefehl 38 nutzt kaufen = 0, Stein = 4.
  - Die Goldstelle +0x4D0 + 15·4 ist dieselbe, die `logik.lua` liest. [Live]

---

## 3. GetUnitRecruitPermission (00464e80)

**Phase 1 – Durchsehen**
- Bereich: Einheiten/Anwerben, spielrelevant.
- Die Funktion prüft, ob ein Einheitentyp angeworben werden darf.

**Phase 2 – Analyse**
- Eingabe: der Einheitentyp. **Einen Spieler-Parameter gibt es nicht.** Sie liest immer den aktuellen Spielerplatz `currentPlayerSlotID` (0x01A275DC). [Code]
- Rückgabewerte [Code]:

| Wert | Bedeutung | Bedingung |
|---|---|---|
| 2 | Typ gesperrt | Freigabe-Merker des Typs ist 0. Ghidra benennt das Feld irreführend als `playerIsAlive+typ*2+0x16`. [Offen: genaue Bedeutung] |
| 3 | Heergrenze erreicht | `armySizeLimit` ≤ `armySize` (+0x53C) + `count_2` (+0x3904) |
| 0 | zu wenig Gold | Gold < Goldpreis des Typs (`TroopDefinedData +0x210 + typ·4`) |
| 4 | kein freier Bauer | `availablePeasants` (+0x8C) − `count` ≤ 0 |
| 1 | erlaubt | sonst |

- Waffen werden hier **nicht** geprüft. [Code]
- `armySizeLimit` liegt bei 0x0117EF5C. [Adresse berechnet, live ungeprüft]
- Die Eingabe ist vermutlich der Einheitentyp. Aber `field279_0x210` hat nur 38 Einträge, und Söldnertypen reichen bis 0x4C. Der Wertebereich ist also noch unklar. [Offen]
- Gegenprobe mit `ProcessRecruitUnit` (00464ef0), dem Anwerben, das das Spiel ausführt:
  - Diese Funktion bekommt den Spieler ausdrücklich übergeben. [Code]
  - Sie prüft nur die Heergrenze. [Code]
  - Danach verteilt sie nach Typ:
    - Ingenieur, Leiterträger und Tunnelgräber → Gilde.
    - Mönch → Kathedrale.
    - Arabische Söldner → Söldnerposten.
    - alle übrigen → Kaserne.
  - Gold, Waffen und Bauern müssen also in `euroRecruit` bzw. `nonEuroRecruit` geprüft werden. [Offen]

**Phase 3 – Erklärung und Anwendung**
- Anwerben hat zwei Prüfstellen:
  - Die Erlaubnisprüfung schaut auf den Spieler, der gerade „am Zug“ ist. Vermutlich steuert sie, ob der Knopf in der Leiste grau ist. Aufrufer: [Offen].
  - Die eigentliche Ausführung prüft nur die Heergrenze des übergebenen Spielers. Der Rest steckt tiefer.
- Für Spieler 2 (1 gegen 1) zählt deshalb vor allem, wem der Befehl beim Ausführen zugeordnet wird. Das passt zu L117–L121: Spielerplatz bis zum nächsten Takt halten. Diese Funktion allein beweist das aber nicht.
- Für das Gehirn heißt das:
  - Die Heergrenze ist eine harte Obergrenze. Ist sie erreicht, wird der Befehl ohne Meldung verworfen.
  - Gold, freie Bauern und Waffen vorher selbst prüfen.
  - Nach dem Befehl die Einheitenzahl nachmessen, statt blind zu wiederholen.
