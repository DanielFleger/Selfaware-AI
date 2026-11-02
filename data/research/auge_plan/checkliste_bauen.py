# -*- coding: utf-8 -*-
"""Baut Checkliste_Auge.md und versuche_szenario.csv: Gesamtproben, Versuchsplan aus den Spielaufzaehlungen und alle
Pruefpunkte aus funktionen_spiel.jsonl, je einem Lauf zugeteilt (F Burgenbau, K Gefecht, S Szenario).
Die Zuteilung geht nach live_art und Stichworten, sie ist ein Vorschlag. Lauf aus dem Repo-Stamm."""
import collections, csv, json, os, re
HIER = os.path.dirname(os.path.abspath(__file__))
G = "data/research/funktionswissen/funktionen_spiel.jsonl"
R = r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference"

# --- Einzelpunkte ---
LAUF = {"tabelle": "0", "markt": "F", "anwerben": "F", "bauen": "F", "wirtschaft": "F", "kampf": "S", "ki-welle": "K", "bewegung": "S"}
HAKEN = r"Hook|per Aufruf|Aufruf in der|Rückgabe|Haltepunkt"
NICHT = r"Maustaste|nur im Mehrspieler|Mitspieler|Netzwerk|DirectPlay|Resync|Desync|\bHost\b|mapSize 160|Kampagne|Mission|Tutorial|Editor|Bestenliste|Video|gesperrtem Gebäude|mit \d+ Spielern im Netz"
KI = r"\bKI\b|Welle|attackInfo|Gegner|Lord|besiegt|Gefecht mit|Bündnis|Team"
KAMPF = r"angriff|Angriff|Schaden|töte|tot\b|stirbt|Feind|Belager|Katapult|Tribok|Triböke|Ramme|Turm|Pfeil|Schuss|schieß|Feuer|Seuche|Graben|Pech|Öl|Falle|Hund"
ABSCHNITT = {
    "0": "Lauf F, Start: einmal auslesen, sobald die Karte geladen ist",
    "F": "Lauf F: Burgenbau, Wirtschaft, Bauen, Markt, Anwerben",
    "K": "Lauf K: Gefecht, was die KI tut",
    "S": "Lauf S: Szenario, Kampf und Bewegung",
    "H": "Nur mit Aufruf-Haken: Der Wert steht nicht dauerhaft im Speicher",
    "N": "Nicht in diesen Läufen: braucht anderen Spielmodus, andere Karte oder die Maus",
}
punkte = collections.defaultdict(list)
form = collections.Counter()
spielart = 0
for z in open(G, encoding="utf-8"):
    x = json.loads(z)
    live = (x["p3"].get("live") or "-").strip()
    if live in ("", "-"):
        continue
    art = x["p3"].get("live_art", "-")
    teile = [t.strip() for t in live.split("→")]
    if re.search(NICHT, live):
        k = "N"
    elif re.search(HAKEN, " ".join(teile[:-1])):  # nur Lage und Messung, nicht die Erwartung
        k = "H"
    elif art in LAUF:
        k = LAUF[art]
    else:
        k = "K" if re.search(KI, live) else ("S" if re.search(KAMPF, live) else "F")
    marke = ""
    if k != "K" and re.search(r"GM_|currentGameMode|gameMode", json.dumps(x["p2"], ensure_ascii=False)):
        marke = " **[Spielart]**"
        spielart += 1
    form["mit_erwartung" if len(teile) >= 3 else "ohne_klare_erwartung"] += 1
    if len(teile) >= 3:
        text = f"**Lage:** {teile[0]} · **Messen:** {' → '.join(teile[1:-1])} · **Erwartet:** {teile[-1]}"
    else:
        text = f"**Punkt ohne klare Erwartung, erst schärfen:** {live}"
    punkte[k].append((x["adr"], x["name"], text + marke))
nr = 0
aus = []
for k in ("0", "F", "K", "S", "H", "N"):
    aus.append(f"\n### {ABSCHNITT[k]} ({len(punkte[k])})\n")
    for a, n, t in punkte[k]:
        nr += 1
        aus.append(f"- [ ] P{nr:03d} `{n}` ({a}): {t}")

# --- Versuche aus den Aufzaehlungen des Spiels ---
ty = json.load(open(os.path.join(R, "types.json"), encoding="utf-8"))
def aufz(n):
    for t in ty:
        if t["path"].rsplit("/", 1)[-1] == n:
            return dict((a, int(b)) for a, b in re.findall(r"(\w+): (\d+)", t["definition"]))
UT = aufz("UnitType")
BT = aufz("BuildingType")
SOLD = ["UT_E_ARCHER", "UT_E_XBOW", "UT_E_SPEAR", "UT_E_PIKE", "UT_E_MACE", "UT_E_SWORD", "UT_E_KNIGHT", "UT_E_LADDER", "UT_E_ENGINEER", "UT_TUNNELER", "UT_E_MONK",
        "UT_A_ARCHER", "UT_A_SLAVE", "UT_A_SLINGER", "UT_A_ASSASSIN", "UT_A_HARCHER", "UT_A_SWORDSMAN", "UT_A_FIRETHROWER", "UT_LORD"]
SIEGE = ["UT_S_CATAPULT", "UT_S_TREBUCHET", "UT_S_MANGONEL", "UT_S_BALLISTA", "UT_S_FBALLISTA", "UT_S_BATTERINGRAM", "UT_S_TOWER", "UT_S_SHIELD"]
SCHUETZEN = ["UT_E_ARCHER", "UT_E_XBOW", "UT_A_ARCHER", "UT_A_SLINGER", "UT_A_HARCHER", "UT_A_FIRETHROWER", "UT_S_MANGONEL", "UT_S_BALLISTA", "UT_S_FBALLISTA"]
GEG_GEB = ["UT_S_CATAPULT", "UT_S_TREBUCHET", "UT_S_BATTERINGRAM", "UT_S_FBALLISTA", "UT_S_MANGONEL", "UT_S_BALLISTA"]
FUSS = ["UT_E_SPEAR", "UT_E_PIKE", "UT_E_MACE", "UT_E_SWORD", "UT_E_KNIGHT", "UT_E_MONK", "UT_A_SLAVE", "UT_A_ASSASSIN", "UT_A_SWORDSMAN", "UT_LORD"]
assert all(u in UT for u in SOLD + SIEGE)
OHNE = r"UNKNOWN|PARADEGROUND|SIGNPOST|KEEPDOOR|^BT_(CATAPULT|TREBUCHET|BATTERINGRAM|SIEGETOWER|SHIELD|MANGONEL|BALLISTA|SIEGETENT|FIREBALLISTA|SIEGETOWER_PLACED|CAMPGROUND|CAMPFIRE|TUNNEL)$"
ZIELE = [b for b in BT if not re.search(OHNE, b)] + ["MAUER_STEIN", "MAUER_ZINNE", "MAUER_HOLZ"]
TEIL_ZIELE = ["BT_GATEHOUSE", "BT_GATEHOUSESMALL", "BT_WOODGATE1", "BT_TOWER1", "BT_HOVEL", "BT_STOCKPILE", "MAUER_STEIN", "MAUER_HOLZ"]
TEIL_ZIELE = [z for z in TEIL_ZIELE if z in ZIELE]
V = []
def neu(g, a, z, m, e):
    V.append({"nr": f"{g}.{sum(v['gruppe'] == g for v in V) + 1:03d}", "gruppe": g, "wer": a, "ziel": z, "messen": m, "erwartet_aus": e})
for u in SOLD + SIEGE:
    neu("V1", u, "-", "Leben, Gehtempo auf freier Fläche, Steigen, Reichweite und Schusstakt falls Schütze, Takte von Feind in Sicht bis Reaktion", "BASE_HP, UNIT_MOVEMENT_SPEED_ARRAY, UNIT_CLIMB, UNIT_ENEMY_NOTICE_RANGE, EntityTypeArrayForProjectileRange")
for a in SOLD:
    for b in SOLD:
        neu("V2", a, b, "Schaden je Treffer und Takte zwischen Treffern im Duell", "MELEE_DAMAGE[Angreifer][Opfer], processUnitAttackOtherUnit, processMeleeInitiation")
for a in SCHUETZEN:
    for b in SOLD:
        neu("V3", a, b, "Schaden je Treffer, Reichweite, Flugzeit, Trefferquote", "ARROW_DAMAGE, BOLT_DAMAGE, STONE_DAMAGE, processEntityDamageToUnit, acquireShootTarget")
for a in GEG_GEB:
    for z in ZIELE:
        neu("V4", a, z, "Reichweite zum Ziel, Schaden je Treffer, Takte bis zerstört, Wirkung auf die 3x3-Felder", "BuildingTypeHasHealth, processDamageToBuilding, processEntityDamageToBuildingCollateral")
for a in FUSS:
    for z in TEIL_ZIELE:
        neu("V4b", a, z, "Greift die Einheit an, Schaden je Schlag, Takte bis zerstört", "processDamageToBuilding")
for g, t in [(20, "Nahkampf gemischt"), (100, "Nahkampf gemischt"), (500, "Nahkampf gemischt"), (1000, "Nahkampf gemischt"), (100, "Schützen gegen Nahkampf"), (500, "Schützen gegen Nahkampf"), (500, "Europäer gegen Araber"), (1200, "fast volles Einheitenfeld")]:
    neu("V5", f"{g} gegen {g}", t, "Überlebende je Takt, Plätze im Einheitenfeld, Lesedauer und Spieltempo (A4)", "MELEE_DAMAGE, ARROW_DAMAGE, Grenze 2.500 Einheiten")
for g, t in [(10, "ein Feld frei"), (100, "ein Feld frei"), (500, "ein Feld frei"), (100, "ein Torhaus"), (500, "ein Torhaus"), (100, "ein Turm"), (100, "Lücke in der Mauer"), (500, "Lücke in der Mauer")]:
    neu("V6", f"{g} Einheiten", t, "Ankunft je Einheit, Stau, Wegwahl, Einheiten je Feld, ohne Beschuss", "commitUnitPathPlanUsingWalkLayer, processMeleeInitiation")
for t, m, e in [("Feuer an Gebäude und Einheit", "Ausbreitung, Schaden, Löschen", "UpdateFireEntity, spawnRandomFireEffectOnBuilding"), ("Pechgraben anzünden", "Brenndauer, Schaden je Takt", "giveLightPitchInstructionToUnitClosestToPitch"), ("Kochöl", "Reichweite, Schaden", "aiRecruitEngineerForOilDuty, Geschossart Öl"), ("Mordloch und Hunde", "Auslöser, Schaden, Zielwahl", "BT_KILLINGPIT, BT_DOGCAGE, UT_CAGEDOG"), ("Seuche durch Kuhwurf", "Einschlag, Dauer, Schaden, Heilung", "UpdateEntity_PoisonCloud, processEntityDamageToUnit"), ("Graben graben und füllen", "Takte je Feld, Fortschritt bis Stufe 4", "advanceMoatDigProgress"), ("Leiter und Belagerungsturm", "Anlegen, Steigen, Besetzung", "UT_E_LADDER, UpdateSiegeTower"), ("Tunnel", "Grabziel, Schaden am Gebäude", "algTunnelerFindTarget, applyTunnelDamageAlongPathPlan"), ("Schild gegen Pfeile", "Treffer und Schaden hinter dem Schild", "UT_S_SHIELD, processEntityDamageToUnit"), ("Höhe: Schütze auf Turm und Mauer", "Reichweite und Schaden gegen die Bodenwerte", "acquireShootTarget, UNIT_CLIMB"), ("Tor öffnen und schließen", "Zustand, Durchgang, Reaktion auf Feinde", "UpdateGateHouseSmall, GateOpenOrClose")]:
    neu("V7", t, "-", m, e)
with open(os.path.join(HIER, "versuche_szenario.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["nr", "gruppe", "wer", "ziel", "messen", "erwartet_aus", "status"], delimiter=";")
    w.writeheader()
    for v in V:
        w.writerow({**v, "status": "offen"})
NAME = {"V1": "Steckbrief je Einheit und Gerät", "V2": "Duell: jede Einheit gegen jede", "V3": "Beschuss: jeder Schütze gegen jede Einheit", "V4": "Belagerung gegen alle Gebäude, Türme und Mauern", "V4b": "Fußtruppen gegen Tore, Türme, Mauern", "V5": "Massenschlachten", "V6": "Angriff auf einen Punkt, ohne Beschuss", "V7": "Umgebung und Sonderfälle"}
c = collections.Counter(v["gruppe"] for v in V)
tab = "| Gruppe | Was | Anzahl |\n|---|---|---|\n" + "\n".join(f"| {g} | {NAME[g]} | {c[g]} |" for g in NAME)

kopf = open(os.path.join(HIER, "checkliste_kopf.md"), encoding="utf-8").read()
ers = {"GESAMT": nr, "F0": len(punkte["0"]), "F": len(punkte["F"]), "K": len(punkte["K"]), "S": len(punkte["S"]), "H": len(punkte["H"]), "N": len(punkte["N"]), "OHNE": form["ohne_klare_erwartung"], "SPIELART": spielart, "VERSUCHE": len(V), "VERSUCHSTABELLE": tab}
for a, b in ers.items():
    kopf = kopf.replace("{{" + a + "}}", str(b))
assert "{{" not in kopf
open(os.path.join(HIER, "Checkliste_Auge.md"), "w", encoding="utf-8").write(kopf + "\n".join(aus) + "\n")
print(ers, dict(c))
print("Ziele", len(ZIELE), ZIELE)
for k in ("H", "N"):
    for a, n, t in punkte[k]:
        print(k, n, t[:110])
