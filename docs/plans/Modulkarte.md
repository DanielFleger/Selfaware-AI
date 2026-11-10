# Modulkarte

Erzeugt mit `python -m selfaware.baukasten.karte --schreiben`, nicht von Hand ändern. Quelle: `src/selfaware/baukasten/karte.py`. Plan: [Plan_Baukasten.md](Plan_Baukasten.md).

Gemessen: Der Lenker `runtime/live/erstes_spiel.py` hat 3857 Zeilen, `phase2` davon 1488. Er kennt 97 Schalter. 20 Klassen haben einen eigenen `schritt`, mit 16 verschiedenen Aufrufen.

Bausteine je Stand: Kern 1, eigene Datei 30, im Lenker 14, nicht benutzt 2, steckbar 18. Eine Stelle mit zwei Rollen zählt einmal.

| Stand | Bedeutung |
|---|---|
| steckbar | Eigene Klasse, der Lenker holt sie über den Steckplatz. Eine neue Version lässt sich per Aufstellung einsetzen. |
| nicht benutzt | Eigene Klasse, die der Lenker nie baut. |
| eigene Datei | Steht für sich, ist aber noch kein austauschbarer Baustein. |
| im Lenker | Steht noch in `erstes_spiel.py`. |
| Kern | Teil des Rust-Kerns. |

## Apfelwirtschaft

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Apfelplaetze | eigene Datei | `macro/nahrungswahl.py:apfel_plaetze`, `macro/nahrungswahl.py:apfel_rate` |  |
| Apfelgruppen | eigene Datei | `macro/wirtschaft.py:apfel_gruppen` | `b_versatz` |
| Erste Plantagen | eigene Datei | `macro/eroeffnung.py:plane_essen` |  |

## Brotwirtschaft

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Brotbau | steckbar | `macro/brotbau.py:BrotBau` |  |

## Bierwirtschaft

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Bierkette | steckbar | `macro/bierkette.py:Bierkette` | `bier` |

## Nahrung gesamt

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Nahrungswahl | eigene Datei | `macro/nahrungswahl.py` | `nahrung_ausbau` |
| Hoefe mischen | eigene Datei | `macro/farmen_mischen.py` |  |
| Hoefe packen | eigene Datei | `macro/farmen_packen.py` |  |
| Nahrungsmodell | eigene Datei | `macro/nahrungsmodell.py` |  |
| Jagd | steckbar | `macro/brotbau.py:JagdBau` |  |
| Vorrat kaufen | im Lenker | `Lenker nahrung_puffer`, `Lenker nahrung_notkauf`, `Lenker nahrung_auf_kante` | `rationen` |

## Waffenwirtschaft

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Produktion | im Lenker | `Lenker Produktion`, `Lenker produktions_hofplaetze`, `Lenker hofplaetze_live`, `Lenker plaetze_live`, `Lenker hofvorrat_erschoepft` | `produktion`, `produktion_fenster` |
| Lederkette | im Lenker | `Lenker LederKette` |  |
| Waffenlager | im Lenker | `Lenker waffenlager_ueberhang`, `Lenker waffenlager_ausgleich` |  |

## Grundwirtschaft

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Wirtschaft | steckbar | `macro/wirtschaft.py:Wirtschaft` | `je_arbeiter`, `vollbeschaeftigung`, `lager_max` |
| Alter Ausbau | nicht benutzt | `macro/wirtschaft.py:Ausbau` |  |
| Ertragsplaner | steckbar | `macro/ertragsplaner.py:Ertragsplaner` |  |
| Aufbauplan | eigene Datei | `macro/aufbau_planer.py` | `v14` |
| Haushalt | eigene Datei | `macro/haushalt.py` | `haushalt_rand`, `steuer_runter`, `steuer_ende`, `stufe2_beliebt`, `gute_dinge` |
| Lagerplatz | eigene Datei | `macro/standort.py` | `umzug` |
| Bauen und Platz | im Lenker | `Lenker freier_platz`, `Lenker haus_noetig`, `Lenker kosten_spiel`, `Lenker preis`, `Lenker platz_sauber`, `Lenker speicher_nachbauen`, `Lenker baue_schnell`, `Lenker baue_haus`, `Lenker lager_knapp`, `Lenker baue_lager`, `Lenker kosten_aller`, `Lenker wohnraum_fehlt`, `Lenker v14_sperrflaechen` | `abriss`, `huetten_voraus`, `neubau_sicher` |
| Holz und Stein | im Lenker | `Lenker v16_holzfaeller`, `Lenker haufen_hat_stein`, `Lenker stein_joche`, `Lenker v14_steinpflicht`, `Lenker stein_pflicht` | `holzfaeller_max`, `holzfaeller_je_baum`, `holzfaeller_vorab`, `holz_kaufen`, `holz_spam`, `stein_max`, `stein_parallel`, `steinbruch_zuerst`, `steinbrueche_frueh`, `joch_nach_stein` |
| Markt | im Lenker | `Lenker verkaufen` |  |

## Bestellung Raid

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Raid-Werbung | steckbar | `baukasten/raid.py:RaidBestellung`, `micro/tasks/raids.py:werbung`, `baukasten/bestellung.py` | `bestellung`, `raids`, `raid_reihenfolge` |
| Assassinen werben | im Lenker | `Lenker phase1`, `Lenker phase2`, `Lenker loewen_am_posten` |  |
| Kauf nach Wirkung | eigene Datei | `baukasten/wirkung.py:kaufen`, `baukasten/wirkung.py:Wissen`, `baukasten/einheiten.py` |  |

## Bestellung Angriff

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Streitkolben | im Lenker | `Lenker ruestung_kaufen`, `Lenker anwerbewelle`, `Lenker anwerbe_menge`, `Lenker werbung_freigegeben`, `Lenker werbung_gemerkt`, `Lenker abwanderer_zuerst`, `Lenker kaserne_am_feuer` | `streitkolben`, `schub`, `einzelkauf`, `aufloesen` |
| Bilanz | im Lenker | `Lenker bilanz_schritt`, `Lenker bestzeit_split`, `strategy/bilanz.py` |  |
| Heer | im Lenker | `Lenker phase2` | `heer_anteil` |
| Endspurt | eigene Datei | `strategy/endspurt.py` | `endspurt` |

## Bestellung Verteidigung

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Notwerbung | im Lenker | `Lenker phase2` | `notwerbung` |

## Einsatz Raid

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Raid-Einsatz | steckbar | `baukasten/raid.py:RaidEinsatz` | `ohne_angriff` |
| Nahkampf-Raid | steckbar | `micro/tasks/nahkampf.py:NahkampfRaid` |  |
| Brandtrupp | steckbar | `micro/tasks/raids.py:Brandtrupp` |  |
| Reiterjagd | steckbar | `micro/tasks/raids.py:Reiterjagd` |  |
| Deckung | steckbar | `micro/tasks/raids.py:Deckung` |  |
| Vorstoss | steckbar | `micro/tasks/vorstoss.py:Vorstoss` | `vorstoss`, `vorstoss_bis` |
| Assassinen einzeln | steckbar | `micro/tasks/assassinen.py:Einzeln` | `assassinen` |

## Einsatz Angriff

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Feldzug | steckbar | `micro/tasks/feldzug.py:Feldzug` | `weg`, `angriff_ab` |
| Alter Angriffstrupp | nicht benutzt | `micro/tasks/assassinen.py:Angriffstrupp` |  |
| Lord-Anlauf der Assassinen | steckbar | `micro/tasks/assassinen.py:Einzeln` |  |

## Einsatz Verteidigung

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Waechter | steckbar | `micro/tasks/waechter.py:Waechter` | `waechter` |
| Lordwache | eigene Datei | `micro/tasks/lordwache.py` | `lord_feuer` |
| Fallenwache | steckbar | `micro/tasks/fallenwache.py:Fallenwache` | `fallen` |
| Kornring | steckbar | `macro/kornring.py:Kornring` | `kornring`, `gruben` |
| Graben | steckbar | `macro/kornring.py:Graben` | `graben` |
| Graben und Mauer setzen | im Lenker | `Lenker plane_graben`, `Lenker schicke_graeber`, `Lenker setze_mauer`, `Lenker setze_grube` |  |

## Werkzeugkasten

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Ausweichen | eigene Datei | `baukasten/ausweichen.py`, `kern/ausweichen.rs`, `Lenker ausweichen_kern` | `ausweichen` |
| Breite Aufstellung | eigene Datei | `baukasten/formation.py:breit` |  |
| Stapeln | eigene Datei | `micro/tasks/assassinen.py:_stapel_rechnung` |  |
| Zuweisung | eigene Datei | `micro/zuweisung.py` |  |

## Scaling

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Raid-Sollzahlen | eigene Datei | `micro/tasks/raids.py:werbung` | `sklaven_soll`, `reiter_soll`, `deckung_soll` |
| Bevoelkerung und Kasse | steckbar | `macro/wirtschaft.py:Wirtschaft` | `bevoelkerung_ziel`, `kasse`, `kasse_grenze`, `kasse_stufe`, `gold_ziel`, `wachstum_boden`, `penner` |

## Acceleration

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Eroeffnung | eigene Datei | `macro/eroeffnung.py` | `eroeffnung` |
| Kausal-Entscheider | eigene Datei | `learning/kausal.py` | `entscheider`, `kausal_horizont`, `kausal_sparen` |

## Haende

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Befehlsweg | eigene Datei | `execution/kernweg.py`, `game/kern_port.py`, `kern/haende.rs`, `kern/leitung.rs`, `kern/wege.rs`, `kern/lib.rs`, `Lenker kernweg_senden` | `kernweg` |
| Auftragsbuch | eigene Datei | `execution/auftragsbuch.py`, `execution/ledger.py` |  |
| Lord-Sperre | eigene Datei | `execution/lordschutz.py` |  |
| Spielbefehle | eigene Datei | `game/ucp/befehl.py`, `game/ucp/bauen.py`, `game/ucp/drehwert.py` |  |

## Augen

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Lagebild | im Lenker | `Lenker lords`, `Lenker lage`, `Lenker betriebe`, `Lenker karte_laden`, `Lenker pruefe_begehbar`, `Lenker wegtest`, `Lenker lies_mauer`, `Lenker lies_logik`, `Lenker lies_haltung`, `Lenker runde_lesen`, `Lenker eigene_gebaeude`, `Lenker steht_bei` |  |
| Weltbild des Kerns | Kern | `kern/welt.rs`, `kern/beschuss.rs`, `kern/feuer.rs`, `kern/waechter.rs`, `game/kern_leitung.py` |  |
| Dienste | eigene Datei | `services/bedrohung.py`, `services/gefahrenzone.py`, `services/gefecht.py`, `services/schussfeld.py`, `services/sicht.py`, `services/spielwerte.py`, `services/uebersicht.py`, `services/wegkarte.py` |  |
| Spiel lesen | eigene Datei | `game/ucp/aufbau.py`, `game/ucp/steuerkarte.py` |  |

## Lernen

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Lernkreis | eigene Datei | `learning/lernen.py`, `learning/lernen_1v1.py`, `learning/partie_lernen.py` | `trainingsstand`, `trainingsstand_ab` |

## Rahmen

| Modul | Stand | Stelle | Schalter |
|---|---|---|---|
| Start und Ablauf | im Lenker | `Lenker signal_da`, `Lenker s32`, `Lenker schreib`, `Lenker partie_pruefen`, `Lenker warte_bis`, `Lenker saat_laden`, `Lenker saat_lesen`, `Lenker saat_merken`, `Lenker gefecht_starten`, `Lenker ki_aus`, `Lenker angleichen`, `Lenker eins_gegen_eins_start`, `Lenker anhaengen`, `Lenker uebernehmen_start`, `Lenker phase1`, `Lenker phase2`, `Lenker main` | `angleich_tick`, `anhaengen`, `bis_tick`, `eins_gegen_eins`, `experiment`, `fehlerprobe`, `gegner`, `gegner_erwartet`, `gegner_ki`, `karte`, `kurz`, `leere_ki`, `mensch`, `mensch_gegner`, `minuten`, `nur_phase2`, `pauseprobe`, `plan`, `plaetze`, `regel50`, `start`, `startliste`, `stopp_tote`, `tempo`, `uebernehmen`, `verbuendet`, `ziel_tick`, `zuschau_tempo` |
| Wachen | eigene Datei | `runtime/live/partner.py`, `runtime/live/stillstand.py`, `runtime/live/zielwaechter.py`, `runtime/live/samurai_wache.py` |  |
| Laden und Speichern | eigene Datei | `game/ucp/laden.py`, `game/ucp/speichern.py` |  |
| Baukasten | eigene Datei | `baukasten/aufstellung.py`, `baukasten/karte.py` |  |
