# Selfaware-AI — Plan für eine selbstlernende Stronghold-Crusader-KI

**Stand: 30.09.2026.** Dies ist ein **Plan zum Durchsehen**, noch kein Bau
(Grundgesetz Regel 5: kein Bauen ohne Plan). Quellen: unsere eigene Doku
(`doku/Wissensstand.md`, `doku/Betriebsregeln.md`) plus eine faktengeprüfte
Web-Recherche über die stärksten Spiel-KIs (16 Agenten, jede Zahl gegen echte
Quellen geprüft, Links unten). Marken wie gewohnt: **belegt / gemessen /
abgelesen / vermutet**.

---

## Das Ziel — in einem Satz

> **Eine KI, die im gemoddeten Stronghold Crusader (UCP3) auf einer festen
> Karte im 1-gegen-1 die stärkste eingebaute bzw. Liga-KI (erster Gegner:
> der Wolf) in mindestens 8 von 10 Gefechten schlägt — und deren Können aus
> gespielten Partien nachgelernt ist, nicht von Hand gesetzt.**

Messbar, weil man es zählen kann (8 von 10). Selbstlernend, weil die
Siegquote über Partien hinweg eine Lernschleife steuert, nicht ein Mensch die
Werte dreht. Es baut auf allem auf, was wir schon haben.

---

## Teil 1 — Was uns die stärksten Spiel-KIs lehren

Kurzfassung der Recherche. Je KI: **wie sie lernt**, **was sie gekostet hat**,
**was sie vom Spiel sieht**, **was sich auf SHC überträgt**. Alle Zahlen belegt,
Quellen am Ende.

| KI / Spiel | Wie sie lernt | Rechenaufwand | Was sie sieht |
|---|---|---|---|
| **Stockfish** (Schach) | Baumsuche + kleines Bewertungsnetz (NNUE), überwacht trainiert | Consumer-GPU, Tage–Wochen | perfekte Information, rundenbasiert |
| **AlphaZero / Leela** (Schach) | reines Selbstspiel + Suche (MCTS) | AlphaZero ~9 h auf **5.000 TPUs**; 44 Mio. Partien | perfekte Information |
| **AlphaStar** (StarCraft II) | Nachahmung aus ~971.000 Replays, dann Liga-Selbstspiel | **384 TPUs, 44 Tage, ~3,2 Mio. $**; ~200 Spieljahre je Agent | Zustand als Zahlen (API), später Kamera + Nebel |
| **OpenAI Five** (Dota 2) | Selbstspiel von null (PPO) | **256 GPUs + 128.000 CPU-Kerne, 10 Monate, ~45.000 Spieljahre** | ~20.000 Zahlen über API, keine Pixel |
| **Age of Empires** (eingebaut) | **lernt nicht** — Regel-Skript (.per + Stellschrauben) | keiner | voller Zustand, kein echtes Cheaten im Skirmish |
| **Factorio (FLE, 2025)** | LLM schreibt Programme, liest Ausgabe | ~1.300 $ API-Kosten, ein Rechner | voller Zustand über Lua-API, **kein Gegner** |
| **Stronghold Crusader** (eingebaut + DE 2025) | **lernt nicht** — Regel-Logik fest, nur AIV+AIC als Daten | keiner | — |

**Die drei Lehren, die den Weg bestimmen:**

1. **Von-null-Selbstspiel ist außer Reichweite.** AlphaStar (~3,2 Mio. $) und
   OpenAI Five (256 GPUs, 10 Monate) funktionierten **nur**, weil ihr Spiel
   tausendfach parallel und viele Male schneller als Echtzeit lief. *(belegt)*

2. **Aber der Aufwand ist seit 2019 drastisch gesunken.** Auf einem
   Forschungs-RTS (Gym-microRTS) schlägt eine selbstlernende KI die
   Wettbewerbssieger nach **~60 Stunden auf einem einzigen Rechner** (1 GPU).
   EfficientZero erreicht Atari-Menschenniveau mit **2 Stunden** Spielerfahrung.
   Und schon **~4.600 gute Replays** bringen fast so viel wie 105.000 — Daten
   sind nicht der Engpass. *(belegt)*

3. **Die stärksten Spiel-KIs, die man wirklich spielt, sind Regel-Systeme.**
   Age of Empires und Stronghold — auch die neue Definitive Edition (Juli 2025)
   — nutzen **keine lernende KI**, sondern Bauvorlagen + Zahlenwerte von Hand.
   Und: **Evolution von nur 14 Parametern schlug etablierte StarCraft-Bots**
   (UAlbertaBot, Nova). Der Hebel „vorhandene Regel-KI, Zahlen automatisch
   optimieren" ist belegt wirksam. *(belegt)*

---

## Teil 2 — Was Stronghold heute schon hergibt

Der Kern von Daniels Gedanken: Mit Zugriff aufs Innere ist der Zustand offen.
Hier steht, was davon **belegt** lesbar ist, was wir schon **schreiben** können
und die vier Grenzen, die den Weg vorzeichnen.

### Den Zustand LESEN (der „offene Backend"-Zustand)
- **Jede Einheit**: Besitzer, Typ, Position, **Ziel und ganzer Wegplan**,
  Leben, wen sie angreift *(gemessen im Gefecht)*.
- **Bevölkerung** je Spieler (Einheiten zählen) *(gemessen)*.
- **Jedes Geschoss**: Typ, Position, Ziel, Schütze *(abgelesen)*.
- **Rohstoffe** je Spieler, alle 25 Waren inkl. Gold *(belegt)*.
- **Gebäude** und **die Baupläne der KIs** Schritt für Schritt *(belegt/gemessen)*.
- **Karte**: gezeichnetes Bild, Geländeart, Höhe, Mauerbesitzer, Schaden, alle
  80.400 Kacheln *(belegt)*.
- **Zeit/Tempo/Kosten/Preise** *(belegt)*.

→ Position, Ziel und Wegplan **jeder** Einheit sind lesbar — „woher/wohin" ist
für Einheiten schon beantwortet. Für saubere **Vorausberechnung** fehlt noch:
Geschosse sind erst *abgelesen* (nicht live erprobt), Trefferrechnung nur teils
bekannt.

### In den Zustand EINGREIFEN (schon gebaut)
Einheit auf ein Feld schicken *(belegt)* · Einheit echt umwandeln *(belegt)* ·
Baukosten pro Tick ändern *(belegt)* · Gold/Waren verschieben *(belegt)* ·
Mauer kostenlos nachbauen *(gemessen)* · Lord-Tod erkennen *(gemessen)* ·
Tempo live setzen *(belegt)* · Bild aus dem Speicher *(belegt)* · Gefecht ohne
Menü starten und wieder ins Menü *(belegt)*.

### Die vier Grenzen — das „Grundgesetz" der Plattform *(alle belegt)*
1. **Nur im Prozess.** Von außen ist alles gesperrt. Die KI muss **im Spiel
   selbst** laufen (unser Lua-Modul) oder über den Dateikanal.
2. **Hohes Tempo, Obergrenze noch offen.** Ticks/s = Tempowert; die Mod
   erlaubt bis ~1000 als Einstellung (Daniel). Wie viele Ticks/s daraus
   **wirklich** werden (der Zeichentakt deckelt), ist zu messen — Schritt 0a.
3. **Parallelbetrieb offen.** Die Betriebsregeln maßen nur, dass eine zweite
   Instanz **derselben** Installation im „läuft schon"-Dialog hängt. Ob mehrere
   SHC nebeneinander laufen (eigene Kopien/Installationen), ist **nicht**
   geklärt — Daniel hält es für möglich. Prüfen in Schritt 0b. Geht es, wird
   die Lernschleife um diesen Faktor schneller und ein späterer Weg 6 rückt
   näher.
4. **Kein folgenloses Headless bekannt** — das Zeichnen lässt sich nicht
   einfach abschalten.

**Was das für „selbstlernend" heißt:** Ein Gefecht dauert bei hohem Tempo grob
eine halbe bis wenige Minuten; wie viele Partien/Stunde wirklich drin sind,
hängt an Tempo (0a) und Parallelbetrieb (0b) — deshalb sind das die ersten
Messungen. Selbst im besten Fall bleibt Tabula-rasa-Selbstspiel (Millionen
Partien) weit weg. **Also: nicht von null lernen, sondern eine vorhandene KI
aus vergleichsweise wenigen Partien nachlernen.** Genau Daniels zweite Lesart.

---

## Teil 3 — Die Weg-Entscheidung

Fünf mögliche Wege, für SHC bewertet (aus der Recherche, verifiziert):

| Weg | Für SHC | Warum |
|---|---|---|
| **1. Selbstspiel-RL von null** (AlphaStar-Art) | ✗ vorerst | braucht massive Parallelität + Schnelltempo; Tempo/Parallelbetrieb werden erst in Schritt 0 gemessen; selbst dann Millionen-Aufwand |
| **2. Menschliche Partien nachahmen** | ✗ | SHC zeichnet keine Replays im nötigen Format auf — Datenmangel |
| **3. Regel-KI behalten, Stellschrauben lernen** | ✅ **empfohlen** | die eingebaute KI **ist** ein Regelsystem mit **169 Zahlen je Lord + Bauplan**; man sucht im exakt richtigen Raum, in der Original-Engine, in Echtzeit; Evolution solcher Parameter hat belegt Bots geschlagen |
| **4. Suche mit gelerntem Weltmodell** (MuZero-Art) | ✗ | braucht einen schnellen Simulator, den es nicht gibt |
| **5. LLM-Agent** | ✗ für „stärkste schlagen" | am wenigsten echtzeittauglich; im Test schlug ein LLM nur mittlere StarCraft-Stufen, nicht die höchsten |

**Die Entscheidung: Weg 3.** Er ist der billigste (ein PC, keine Cloud, kein
ML-Gerüst), der schnellste (baut auf allem, was wir haben) und der einzige, der
von sich aus in Echtzeit läuft, weil die getunte KI in der Original-Engine
spielt.

**Der ehrliche Vorbehalt** *(vermutet)*: Dass reines Stellschrauben-Tuning
reicht, um die **stärkste** Werks-KI zu schlagen, ist nicht bewiesen — das muss
ein Messlauf zeigen. Reicht es nicht, ist Weg 1 der Zweitweg, aber erst nach
einem eigenen Vorprojekt (schnelle SHC-Abstraktion bauen). Dann belegt
Gym-microRTS, dass Selbstspiel-RL auf **einer** GPU Wettbewerbssieger schlägt.

---

## Teil 4 — Der Aufbau: Strategie unten, Taktik oben, ein Ziel

Daniel will **Taktik UND Strategie** und die **zwei Stufen** (erst alles wissen,
dann Wissen wegnehmen). Beides fügt sich in einen einzigen Aufbau — keine zwei
KIs nebeneinander.

```
  ┌─────────────────────────────────────────────────────────┐
  │  TAKTIK-Schicht  (unser Lua-Modul, jeden Tick)           │
  │  liest Live-Zustand, greift in Echtzeit ein:             │
  │  Ausweichen, Mauer-Nachbau, Lord-Tod-Kette, Ausfall      │
  │  → nutzt die schon gebauten Befehle                      │
  └───────────────────────────▲─────────────────────────────┘
                              │ sitzt auf
  ┌───────────────────────────┴─────────────────────────────┐
  │  STRATEGIE-Schicht  (AIV-Bauplan + AIC-169-Zahlen)       │
  │  Wirtschaft, Burg, Armee, Aggression — GELERNT per       │
  │  Evolution über viele Partien (Fitness = Siegquote)      │
  │  läuft in der Original-Engine                            │
  └─────────────────────────────────────────────────────────┘
```

- **Strategie = gelernt** (Schritt 3 unten): die langfristigen Pläne, die
  ganze Burg und Wirtschaft. Das ist der selbstlernende Teil.
- **Taktik = reaktiv in Echtzeit** (Schritt 4): das Modul reagiert auf den
  Gegner Zug um Zug mit den Handgriffen, die wir schon haben.

**Die zwei Stufen sind eine Einstellung an der Taktik-Schicht, keine zweite
KI:**
- **Stufe 1 — alles wissen.** Die Taktik-Schicht liest den ganzen Zustand
  (alle Einheiten, alle Geschosse), ohne Nebel des Krieges. So wie Warcraft es
  anfangs machte.
- **Stufe 2 — nur Menschenwissen.** Derselben Schicht wird das Wissen
  **weggenommen**: sie darf nur noch lesen, was im Sichtbereich eigener
  Einheiten/Türme liegt, plus eine eingebaute Reaktionsverzögerung. Übermenschlich
  schnell, aber mit menschlichen Augen — genau Daniels Formulierung.

---

## Teil 5 — Der Fahrplan (jeder Schritt mit Prüfpunkt)

**Schritt 0a — Echtes Tempo messen.** Tempo live auf das Maximum setzen
(Einstellung bis ~1000) und über die Uhr zählen, wie viele Ticks/Sekunde
wirklich herauskommen (der Zeichentakt deckelt). *Prüfpunkt:* gemessene Ticks/s
und daraus die Dauer eines vollen Gefechts in Sekunden.

**Schritt 0b — Parallelbetrieb prüfen.** Testen, ob mehrere SHC nebeneinander
laufen (eigene Kopien/Installationen), ohne dass die „läuft schon"-Sperre oder
die gemeinsame Konfiguration die Messung verdirbt. *Prüfpunkt:* entweder
„N Instanzen laufen sauber parallel" oder ein belegter Grund, warum nicht.
0a und 0b zusammen ergeben die Partien/Stunde — die Größe der Lernschleife.

**Schritt 1 — Messgerüst und Fitness.**
Automatischer Ablauf: unsere AIC/AIV setzen → Gefecht → Sieg/Niederlage plus
Restleben des Lords und Wirtschaft aus dem Speicher lesen → zurück ins Menü →
wiederholen. *Prüfpunkt:* 10 Partien ohne einen einzigen Mausklick gelaufen und
ausgewertet.

**Schritt 2 — Basislinie gegen den Wolf.**
Wie oft gewinnt unsere ungetunte KI gegen den **Wolf** (Daniels gewählter
Gegner) auf der festen Karte? *Prüfpunkt:* eine Siegquote als Ausgangswert, den
die Lernschleife heben muss.

**Schritt 3 — Lernschleife (Strategie).**
Evolution / stichprobensparende Suche (z. B. N-Tuple-Bandit) über die
169 AIC-Zahlen und die AIV-Auswahl; Fitness = Siegquote gegen den **Wolf**.
*Prüfpunkt:* unsere gelernte KI schlägt den Wolf in **≥ 8 von 10** auf der
festen Karte. **Hier ist das Ziel formal erreicht.**

**Schritt 4 — Reaktive Taktik (Echtzeit).**
Das Modul greift live ein, mit schon gebauten Handgriffen: Lord-Tod-Kette,
Mauer-Nachbau, Einheiten-Mikro und **Ausweichen** (Geschosse je Tick lesen,
bedrohte Einheit versetzen). *Prüfpunkt:* gemessene Verbesserung der
Siegquote/Lord-Überlebenszeit mit Taktik-Schicht an gegenüber aus.

**Schritt 5 — Stufe 2: Wissen wegnehmen.**
Die Taktik-Schicht auf Menschenwissen einschränken (Sichtbereich +
Reaktionsverzögerung). *Prüfpunkt:* Die KI gewinnt weiter ≥ X von 10 unter der
Einschränkung, und wir können genau zeigen, welche Felder/Einheiten sie
„sehen" durfte.

**Schritt 6 (optional, Zweitprojekt) — Voll-RL.**
Nur falls Schritt 3–5 an eine Decke stoßen. Braucht zuerst eine schnelle
SHC-Abstraktion. Eigenes Projekt, eigener Chip.

---

## Teil 6 — Meine Empfehlung

**Mit Schritt 0 anfangen: den Durchsatz messen.** Er ist die Weiche für alles
Weitere, kostet kein ML und beantwortet die eine offene Zahl, an der die ganze
Lernschleife hängt. Danach Schritt 1–3 — das ist Weg 3, der belegt billigste und
schnellste Weg zum Ziel, und er nutzt restlos, was wir schon gebaut haben
(Speicherzugriff, Befehle, Hotswap, AIV/AIC-Editoren). **Nicht** mit Selbstspiel
von null anfangen.

**Stand der Freigabe (30.09.2026):** Weg 3 ist freigegeben, der Gegner steht
(**Wolf**). Schritt 0 (Tempo + Parallelbetrieb messen) läuft an. Offen ist nur
noch die **feste Testkarte**.

---

## Offene Fragen und Risiken (ehrlich getrennt)
- **Reicht Stellschrauben-Tuning gegen die *stärkste* KI?** *(vermutet, unbewiesen)* —
  Schritt 2/3 zeigen es. Wenn nein: Weg 6.
- **Wie viele Partien/Stunde wirklich?** *(offen)* — Schritt 0 misst es; die ~100
  sind gerechnet.
- **Geschosse live** sind erst *abgelesen*, nicht im Spiel erprobt — nötig fürs
  Ausweichen (Schritt 4).
- **Sichtbereich/Nebel** für Stufe 2 müssen wir im Speicher erst finden —
  eigener Messschritt.

---

## Quellen (Auswahl, alle geprüft)
- AlphaZero: arXiv 1712.01815; en.wikipedia.org/wiki/AlphaZero
- AlphaStar: nature.com/articles/s41586-019-1724-z; deepmind-Blog; theregister.com (~3,2 Mio. $)
- OpenAI Five: cdn.openai.com/dota-2.pdf; en.wikipedia.org/wiki/OpenAI_Five
- Age of Empires: aok.heavengames.com; forums.aiscripters.com (Rehoboam); gdcvault.com (AoE IV ML)
- Factorio FLE: arXiv 2503.09617
- Forschungsstand: EfficientZero arXiv 2111.00210; DreamerV3 arXiv 2301.04104; SCC arXiv 2012.13169; Gym-microRTS arXiv 2105.13807; Cicero science.org/doi/10.1126/science.ade9097; Voyager arXiv 2305.16291
- Machbarkeit: Gym-microRTS arXiv 2105.13807; ECSLBot (14-Parameter-Evolution) cse.unr.edu; N-Tuple-Bandit arXiv 1705.01080; SHC 169 AIC-Parameter (UCP-Wiki „AI Personality")
