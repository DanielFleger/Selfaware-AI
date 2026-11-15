# Plan: unit status log, action dictionary, damage-based fighting, error catalog (B-182 follow-up)

Origin: Daniel 2026-11-12 19:50 (chat, session "SAI - Raid-Liga"):
- "kämpft ist für mich eine Einheit macht Schaden an eine andere entweder durch Nah- oder Fernkampf" - distance rules are wrong
  (animations, stacked units, no line of sight, no AOE in Crusader; plague/fire spread is not fighting; building damage counts only
  when it is proven and caused by melee/ranged attacks, including fire set by slaves or fire throwers).
- "Gedanken der Einheit zu jedem Spiel oder Anweisungen des Kriegsführers zu jeder Einheit/Zeit" - then testing is fast: see the
  wrong reasoning, pause, save, change the reasoning, load the save, check the fix.
- "Ohne Auftrag ist für mich das Schlimmste - es sollte immer eine Begründung geben, selbst 'warten um für Push zu sammeln'."
- Make a dictionary of unit actions (a matrix with ifs and whens) and an error list with categories "ok, can continue",
  "warning, could get worse", "pause/stop now", each with an analysis after the stop.
- Config (ucp-config.yml, AIV, AIC, start troops) can be changed while the game runs; it reloads when a game is loaded or a new
  battle starts (Daniel's knowledge, not yet tested by us).
- Code and everything that talks to the game in English; German docs can be generated.

Status: GO from Daniel 2026-11-12 19:59 ("Fange nachdem du meine Antworten eingearbeitet hast mit den Statuslogbuch je Einheit an").
Step 1 built 2026-11-12 20:30 (section 6), not committed (Daniel: commit and push only on his yes). First game with the log: game 16
(12.11. 20:34, raid_wirkung_pp, instance 2): 278 rounds with a log up to tick 25,054, 0 units without order, 0 log errors; stopped by
F2 at tick 29,678 (a false alarm the log explained - section 3, STALE_TARGET).
Measured in game 16 up to tick 25,054 (share of each type's unit-rounds, from the position log): E_SPEAR 24 at home 84 % (stacked
42 %, no_threat_stays 42 %), digging 15 %; A_SLAVE 71 walking to its target 70 %, at the target 8 %, waiting without a free target
16 % (typical counts: danger 30, taken 2, burning 1); A_ARCHER 70 in range with an attack order 59 %; LORD 55 holds 100 %.
"In range with an attack order" is not fighting - proven damage is step 2.

Daniel's answers 2026-11-12 19:59:
- Config hot reload: test it first (sandbox) - change start troops in ucp-config.yml between battles and check that the next battle
  uses them. Goal: Daniel says "change the start troops / the behaviour" and the session does it while the game runs, first with his
  guidance, later on its own ("KI-betreutes selbständiges Lernen").
- Fighting: only damage counts. Melee attack animations without damage are not fighting ("davor wackeln die Einheiten nur rum").
- Many STOPs at the start are wanted: catch the 80 % of states with 20 % of the effort, the rest are edge cases.
- After a STOP: report, stop, save, analyse; add the detector as a new stopper if it is new; fix; test; then decide and tell Daniel
  why: load the same save again (small programming error - typo, comma: stage 1 or 2) or restart (logic error; often the better way).
- English for code. Commit and push only after Daniel says yes.

## 1. Fighting = proven damage

A unit "fights" in a round only if damage it caused is proven in that round:
- Unit damage: an enemy unit's `leben` dropped since the previous round AND our unit had that victim as its current attack target
  (game fields: `schusseinheit`, `nahziel`, `zieleinheit` with `zielart` 4) AND our unit was in an attack state (zustand codes to be
  measured per unit type in the sandbox: shooting, swinging) AND, for ranged units, line of sight existed (sicht.Lage rules L75-L79).
  Several attackers on one victim: the damage is shared; report "shared" instead of guessing.
- Building damage: the building's `leben` dropped, or its fire started (`fireDuration` 0 -> >0), while our unit targeted it
  (`attackAtTile` / building target) and stood in attack state. Fire spread to neighbours is NOT our fighting (report separately).
- Everything else (in range, next to target, target set) is "approach" or "waiting", never "fighting".
Output per unit and per type: damage dealt (units, buildings), rounds with proven damage, kills with evidence, own losses, gold.

## 2. Action dictionary (every own fighter has exactly one action per round, with owner and reason)

| action | owner modules | required fields | valid when | becomes an error when |
|---|---|---|---|---|
| ATTACK_UNIT | Vorstoss, Reiterjagd, Nahkampf-Raid, Waechter, Assassinen | target, reason | target alive and reachable | no proven damage for N rounds while "attacking" |
| ATTACK_BUILDING / SET_FIRE | Brandtrupp, Nahkampf-Raid | target, reason | building alive, not burning | no damage/fire after N rounds at the target |
| MOVE_TO_ATTACK | module via Wegfuehrung | target, waypoint, reason | route safe or freed (TROTZ_GEFAHR) | no progress (stuck) |
| MOVE_TO_STAGING / WAIT_STAGING | Brandtrupp ("no free target"), Vorstoss ("gather for push") | point, reason | point safe | waiting longer than a limit without the reason changing |
| GATHER | Vorstoss (stragglers) | group point | group waits | never arrives |
| RETREAT / FLEE | Vorstoss, Reiterjagd | from whom, to | real danger (per-type range, line of sight) | fleeing from units that cannot hit |
| HOLD_POST / DEFEND | Waechter | post or threat, reason | castle guard | holding while a raid could use the unit (to decide) |
| DIG | Kornring | tile | moat unfinished | moat finished |
| GAME_PATH (direkt) | Wegfuehrung | handover point | our map had no path | longer than DIREKT_BIS |
| NO_ORDER | nobody | - | never | always: severity STOP |

Every action carries `reason` as a short English code plus parameters, e.g. `WAIT_STAGING reason=all_targets_covered covered_by=2xT23`.
The dictionary grows; each new reason is added here before it is used in code.

## 3. Error catalog with severity

Severity: CONTINUE (log only), WARN (log + count; escalates to STOP above a limit), STOP (pause, save the game, write the analysis).
From tonight's games 1-15 (2026-11-11/12) and earlier notes:

| code | seen | severity | analysis after stop |
|---|---|---|---|
| CORE_UNREADABLE | game 15: link file read before the game wrote the new memory name; all 1,877 recruitments refused | STOP | which reader, memory name, link-file time |
| WATCH_BLIND | game 15: watch got no state for the whole game | STOP | same |
| LIMIT_EXCEEDED (F1) | rule 20 fighters | STOP | who was recruited when |
| NO_ORDER | game 17 (12.11. 20:45): 4 lines, assassins 498 (tick 17,203) and 494 (35,371, 38,166, 38,208) - the target choice found no target ("alle gefaehrlich"), the unit already stood safe near the front and stayed without an order; the decision was written nowhere. Built: the module keeps the reason per unit (no_reachable_target / all_targets_taken / all_targets_dangerous), the log reports WAIT_STAGING at its own place with that reason | STOP | which unit, last owner, last action |
| CLAIM_WITHOUT_EVIDENCE (F4) | games 8, 13, 14 (late read, stale attack memory, missed short shot) | WARN, STOP if neither core nor position log shows it | attacker, victim, last target record |
| PATH_PENDULUM | game 5: target given up and re-chosen 5x ("kein_weg") | WARN -> STOP | map cell, walk layer |
| WALK_POINT_UNWALKABLE | game 7: advance point on our own farm | WARN | point, building |
| UNIT_STUCK | game 2: same waypoint 2,000 ticks | WARN -> STOP | position, waypoint, walk layer |
| COMMAND_IGNORED | game 7: 3 archers accepted a walk order, none moved | WARN -> STOP | order, target tile |
| MODULES_DISAGREE | game 12: Vorstoss chose target, Wegfuehrung refused all stands | WARN | both decisions |
| FLEE_FROM_OUTRANGED | game 11: retreated 8x from slingers (range 22) | WARN | enemy types, distances |
| STRAGGLER | game 10: archer 53 fields behind its waiting group | WARN | member, group point |
| MERCENARY_IDLE (F3) | games 9, 10 | replaced by NO_ORDER / WAIT too long | - |
| STALE_TARGET (F2) | games 6, 7, 11, 12: dig tile or old shot target kept while holding; game 16 (12.11. 20:34, tick 29,678): assassin 474 waited at a safe place (WAIT_STAGING wait_safe_place), the core still held its old building tile - built: F2 reads the UNIT lines and stays silent while the log says WAIT/HOLD with a reason (zielart cannot tell: real building attacks have zielart 0 just as often, measured in game 16) | CONTINUE if the action says HOLD/WAIT with reason, else WARN | action and reason |
| NO_DAMAGE (at the target) | game 20 (12.11. 22:44, Daniel 22:46 with a screenshot: "warum wird das Spiel hier nicht angehalten? ... der Assassine hatte das Ziel, hat aber dann nicht den Steinbruch weiterangegriffen"): assassin 418 stood 2 fields from enemy worker 327 (type 7) at the quarry with the game's attack order on it (zieleinheit 327) from tick 22,722 to 23,217, idle (state 1), the worker kept 10,000 life; the module let the worker go ("dauert zu lange") and took it along again at once. Neither the watch (F2 counts 3 fields as fighting) nor the chain audit (link 4 counted arrival) looked at damage. Built: chain audit NO DAMAGE (in reach, target life unchanged for DAMAGE_TICKS 300, self-set), the watch stops on every CHAIN line (F5), the assassin does not take back a worker it let go for ARBEITER_SPERRE 1000 ticks (self-set) | STOP | unit state, target life over time |
| COMMAND_IGNORED (assassin route) | game 19 (12.11. 21:03, F2 at tick 33,126, a REAL stop): assassin 475 should raid building 239 via 2 waypoints (log: ATTACK_BUILDING raid_building_route), its game walk target stayed its own field (283, 92) for 610 ticks. Terrain is not the cause (measured on the paused game's walk layer: start walkable, 71,287 fields reachable, the field next to the target too). The module saw the stall itself ("STILLSTAND geloest" 3x) and chose the same target and route again each time - a loop without effect. The core ring took the orders ("6 Einheiten, 6 unterwegs"). OPEN: measure the ring's result per order | WARN -> STOP | order, ring result, walk target |
| NO_ORDER (injured, discovered) | game 19, ticks 23,517-23,816: assassin 489, hit (11,830 -> 5,830), "Fluchtweg toedlich", then "ROUTE GEFAEHRLICH: Ziel aufgegeben" - three rounds without any order, died at 23,979 (the module's own death record: "Auftrag zuletzt: ohne Auftrag"), a T23 11 fields away. OPEN: the target choice skips discovered units without a safe outside job, and nothing else takes them | STOP | unit, discovery, life |
| MODULES_DISAGREE (intercept) | game 19, tick 17,487: the Waechter's "Abfangen" sent spearmen to the enemy's destination with a hold order but did not release them from the Wegfuehrung, which kept them at the stack point (path_target) - they never intercepted. Built: release before the hold order, like every other Waechter order | WARN | both decisions |
| CORE_BUSY | game 18 (12.11. 20:53, tick 26,793): the limit (Obergrenze) read the core while it was writing, got None and crashed - the raid purchase of that round failed ("RAIDS FEHLER ... 'einheiten'"). Built: an empty read counts like "not readable" (limit reached, counted) | WARN, STOP above a limit | how often per game |
| NUMBER_REUSED | game 18, tick 24,021: archer 582 (A_ARCHER 70) died, the game gave its number to an own type-52 unit, the Wegfuehrung led it on as an advance archer. Built: an order belongs to the unit it was given for - a different type ends it | WARN | old and new type |
| MODULES_DISAGREE (stale target) | game 18, tick 2,566: the Vorstoss said "waits, no target", the Wegfuehrung still led its archers to the old target U322 (path_target, 45 lines). Built: a Vorstoss round without a target releases the old one | WARN | both decisions |
| MODULES_DISAGREE (hand-over) | game 16, tick 1,139: the Graben took spearmen 331-334 as diggers while the Wegfuehrung still led them to the Waechter's stack (path_target) - built: the Graben releases its diggers from the Wegfuehrung before the dig order | WARN | both owners, path_target |
| PURCHASE_UNUSABLE | game 12: 4 archers bought, advance could not use them | WARN | purchase reason vs module check |
| RESERVE_BLOCKS_RAID | games 5, 7: first slave at tick 3902/6775 | CONTINUE (info) | gold vs reserve |
| RAN_INTO_ENEMIES | game 5: slave on game pathing died to T23 + slinger | WARN | route source (ours/game) |

Earlier history (to be filled from Wissensregister, Handbuch and memory notes before building): commands on the wrong player,
start troops counted as recruits, lord in danger.

## 4. Test workflow: pause - save - fix - load - check

1. Every round each module writes its actions (section 2) to the position log (`lage_*.jsonl.gz`, new table `intents`) and a console
   line when a unit's action changes.
2. The checks (section 3) run on actions + proven damage. On STOP: pause the game, save it under a name with the stamp, write the
   analysis (unit, action history, reason, damage) next to the save.
3. To test a fix: load the save, restart the Lenker on it, watch the same units. Open point: modules keep memory the save does not
   have (targets, blocks, waits) - the Lenker must rebuild it from the `intents` of the last rounds or start the modules fresh.
4. Start troops, AIV, AIC: become lineup switches; new values apply with the next battle (Daniel 19:50).

## 5. Order of work

1. Action dictionary as code (English enum + reason codes), every module reports its units each round; NO_ORDER check.
2. Damage attribution from consecutive rounds; "fighting" in reports means proven damage only.
3. Checks with severity; STOP saves the game; analysis file.
4. Save/load test loop (incl. Lenker resume).
5. Then: spearmen raid when the castle is quiet (Daniel 19:28 "ja natürlich"), slaves under fire (open question to Daniel).

Language: new code, identifiers and game-facing text in English; existing German code keeps its names until it is touched.

## 6. Step 1 design (build now)

Refined 2026-11-12 while building: a unit has TWO things each round - the module's intent (what and why) and, if the Wegfuehrung
leads it, the movement phase (what it physically does). The first design folded both into one action and lost one of them
(a slave walking to its target showed MOVE_TO_ATTACK, its reason "free target, best value per field" was gone). Now both are kept:
`intent` from the module, `path` from the Wegfuehrung. MOVE_TO_ATTACK, GAME_PATH and WAIT_SAFE_TARGET for path problems became
path phases; the actions stay for modules that move units themselves (Deckung, Reiterjagd flight, Vorstoss retreat).

1. New module `src/selfaware/micro/unit_log.py` (English):
   - `Action` (str constants): ATTACK_UNIT, ATTACK_BUILDING, SET_FIRE, MOVE_TO_ATTACK, MOVE_TO_STAGING, WAIT_STAGING, GATHER,
     RETREAT, FLEE, HOLD_POST, DEFEND, DIG, GAME_PATH, WAIT_SAFE_TARGET, NO_ORDER.
   - `UnitLog(sp)`: `report(unit, owner, action, target=None, reason="", **params)` (latest report of a round wins) and
     `report_many(owner, {unit: (action, target, reason, params)})` for the modules; `path(unit, owner, phase, target, waypoint)`
     for the Wegfuehrung; `close_round(tick, L)` merges both - a guided unit without module report gets the action from its
     path target (unit -> ATTACK_UNIT, building -> ATTACK_BUILDING, point -> MOVE_TO_STAGING / WAIT_STAGING) and
     reason `no_module_reason`; every own living fighter (baukasten.obergrenze.KAEMPFER, not the lord) with neither gets NO_ORDER;
     returns the change lines; `no_order()`; `table()` for the position log.
   - Targets as text: `U<nr>` unit, `B<nr>` building, `(x,y)` point. Unit types as code name and number (`A_SLAVE 71`;
     type 23 only as `T23`).
2. Path phases (Wegfuehrung status -> phase): neu new, unterwegs walking, greift_an attacking, am_ziel at_point,
   gefahr danger_at_stand, kein_weg no_path, direkt game_path, steckt stuck, wartet command_budget, ziel_weg target_gone.
   Is the module's target not the path target, the entry carries `path_target` (MODULES_DISAGREE signal).
3. Modules fill `absicht` (unit -> (action, target, reason, params)) each round: Brandtrupp (SET_FIRE best_value_per_distance /
   keeps_target; WAIT_STAGING no_free_target with counts taken/burning/blocked/danger), Reiterjagd (ATTACK_UNIT worker_in_range /
   nearest_safe_worker; FLEE melee_near; WAIT_SAFE_TARGET no_safe_worker), Deckung, Vorstoss (one intent for the group, GATHER
   straggler), Nahkampf-Raid, Waechter (last order per unit stays until the situation changes: start_post, intruder, intercept,
   behind_lord, fight_not_worth, melee_takes_over, stack_with_archers, lord_low_health; else HOLD_POST no_threat_stays /
   threat_not_engaged), Graben (DIG moat_unfinished), Assassinen (from their own state, like `_taetigkeit`).
4. Lenker (erstes_spiel.py): one UnitLog per game; reports after each module, paths after `wegf.schritt`, then `close_round`;
   change lines go to the console as `UNIT t=<tick> <nr> (<type>) <owner> <action> ...`; `table()` goes into the NEXT line of the
   position log as key `intents` (the table's first line names the tick it belongs to - the line is written at round start).
5. Check: NO_ORDER for a fighter = STOP (later in the watch v2; first as a console line `UNIT_NO_ORDER` and a test).
6. Tests: report/close_round/NO_ORDER/merge; Wegfuehrung `absichten`; every module's `absicht`; Lenker wiring (text check).

## 7. Chain audit per order (built 2026-11-12 22:50)

Daniel 2026-11-12 22:34, on the finding "assassin 475 does not get going": "das ist der Vorteil wenn wir die komplette Chain
auditen - uns faellt sofort auf wenn sie bricht. Wegberechnung -> Kern bekommt Befehle -> Ausfuehrung -> Aktion im Spiel".

`src/selfaware/micro/chain_audit.py` follows every unit order that leaves the Lenker:
1. planned - the unit log (section 6) has owner, intent and reason.
2. sent - observers at the two exits: `befehl.sende` (module channel befehl.json -> logik.lua, after the lord lock) and
   `kernweg.Kernweg` (order ring of the Rust core, with the ring's own result per order: wirkt / wirkt nicht / verfallen / doppelt ...).
3. seen in the game state - walk and hold: the game's walk target at the point; attack unit: the target in zieleinheit, nahziel or
   the core's schusseinheit; attack building: the core's attack tile or the walk target at the building; dig: tile or target kind 6.
4. progress - the unit gets closer to the target (or is there).
A break gives one console line per order (`CHAIN ... NOT SEEN ...` or `CHAIN ... NO PROGRESS ...`); every 100 rounds
`CHAIN summary:` counts per kind and channel: sent, taken, not_seen, arrived, no_progress and the ring results. The words name what
is measured (the game state), not a cause. Self-set, not measured: TAKE_TICKS 150, ACT_TICKS 300, the distances.
Measured before building (game 19, core ring report): assassin orders via the ring - walk 216x "wirkt", building attack 25x
"wirkt nicht", 2x "verfallen", 0x "wirkt"; walk 4x "doppelt" (an order already in the ring is not dispatched again).
Not followed yet: zigzag orders of the core (AUSWEICHEN).

## 8. Attack chain with measured timing (plan 2026-11-12 22:58, replaces DAMAGE_TICKS)

Daniel 2026-11-12 22:55 on "NO DAMAGE after 300 ticks": "Nein das ist ein dummes Kettenglied, bitte behebe es schlau. Du weisst
alles ueber den Angriff: Leben von Angriffsziel und Angreifer ... wie lange die Angriffsanimation vom Assassinen ist und wann sie
anfaengt ... nach wie vielen Ticks tatsaechlich der Schaden durchkommt: Ziel waehlen -> Am Ziel (erkannt, sonst Pause) -> sollte
instant Angriffsanimation starten (sonst Pause) -> fuehrt erste Angriffsanimation aus -> Schaden (sonst Pause)." Every link must be
detected, so that the brain can later weigh e.g. "take this arrow to finish the swing, so the building gets one more damage
instance from this unit".

Links per attack, each with an expectation per unit type and target class (measured, never guessed):
1. target chosen - the order (section 7).
2. at the target - in reach (melee: next to the unit / at the building footprint; ranged: range + line of sight) by the expected
   tick = order tick + path length x ticks per field (spielwerte.takte_je_feld) + measured margin. Else STOP.
3. attack starts - unit state becomes the attack state (106 unit, 107 building; ranged: measure) within the measured delay
   after arrival (Daniel expects "instant"). Else STOP.
4. first swing - the core's `bildzyklus` (animationCycleNumber) advances within one measured cycle length. Else STOP.
5. damage - the target's life drops by the measured damage per hit (type vs target) at the measured hit offset in the cycle;
   one damage instance per swing. Accounting per round: swings (delta bildzyklus) vs damage instances (delta life / damage per
   hit), several attackers on one target counted together. Else STOP.

Data available: core fields per own unit `zustand`, `bild` (animationFrame), `bildzyklus` (animationCycleNumber), attack tile,
target unit; building `currentHealth` per tick; measured melee damage per hit and pair, shot intervals, aiming times, ticks per field
(spielwerte_gemessen.json, Lauf S 2026-11-03). Missing, to measure first (instance 2, per tick from the core at low game speed):
per type the delay arrival -> attack state, the cycle length, the frame/tick of the hit inside the cycle, damage per hit against
building classes. First pair: A_ASSASSIN 73 vs quarry / ox tether (game 20, assassin 418 and 486 at buildings 7 and 59).

Measured 2026-11-12 23:00-23:10 on instance 2 (game 20 paused at tick 23,561, Lenker stopped; per tick from the core at game speed 20,
no tick missing; files data/research/schlag_messung_20261112/*.jsonl). A_ASSASSIN 73 against an enemy building (type 30, 200 life;
assassin 418 ordered by hand at tick 23,961):
- order -> walking (state 101): 2 ticks. Walking: 41 fields in 797 ticks, then 13 fields in 308 ticks (about 19-24 ticks per field).
- at the target (next to the building) -> attack state 107: 0 ticks (the same tick, 25,069).
- one swing: frames 1 -> 24 in 93 ticks (a frame step every 3 ticks; frames 4, 10, 16/17 held longer); the core's `bildzyklus`
  counts frame steps, not swings.
- hit: exactly at frame 24 -> 0, 93 ticks after the attack started, then every 93 ticks (25,162 / 25,255 / 25,348).
- damage: 75 per hit (200 -> 125 -> 50 -> -25, destroyed after 3 swings); also seen: quarry B7 350 -> 275 -> 200 -> 50, B59 (type 4)
  100 -> 25, B200 25 -> -50.
- after destruction: state 0 for one tick, then 1 (standing).
Assassin 418 against worker 327 in game 20: in reach with the game's attack order for 495 ticks, state stayed 1 - with these links
the break is link 3 (attack does not start), visible one round after arrival instead of 300 ticks later.
Still to measure: assassin against units (state 106), the other types (slave fire, archers, horse archers, swordsmen), damage per hit
against each building class.

Built 2026-11-12 23:05 (replaces DAMAGE_TICKS): chain_audit links 3 and 5 - in reach and not walking (state 101), the attack state
(106/107) must show at the next check, else "ATTACK DID NOT START"; after the attack state the target must lose life within the
measured swing of this type against this target class (ATTACK_TIMING), else "NO DAMAGE AFTER A SWING"; pairs without a
measurement give one "CHAIN_INFO ... UNMEASURED" line (no stop) - each one is a measurement still to do.

Link 2 next (Daniel 2026-11-12 23:00): walking speed per unit type AND terrain (e.g. swamp) is needed to compute the next step;
disruptions on the way - enemy units, terrain, the population (it can block the way or even do damage, so that one walks into a
shot) - must be detected and taken into account in the order: evade smartly, click through, or kill. Expected arrival = sum over
the path cells of the measured ticks per field for the cell's terrain; a delay beyond it names its cause (blocked by whom/what).

### Measurement plan (Daniel 2026-11-12 23:04: "ja alle Einheitenarten, dann Glied 2 fuer alle - das kannst du in der Sandbox
testen, Terrain kannst du eigentlich auch so messen - Erhebung machen und dann einfach jeweils testen")
Tool: extend `src/selfaware/tools/experiments/editor_messen.py` (map editor, module commands setzeEinheit / setzeGebaeude /
toeteAlle; instance 2 only) with two series, each writing data/research/editor_messung_<stamp>.jsonl:
1. "schlag": for each own type (22, 23, 24, 25, 26, 27, 28, 55, 70, 71, 72, 73, 74, 75, 76) against (a) an enemy building of each
   building class that raids hit (hut 1, woodcutter 3, quarry 20, ox tether 4, granary 19, barracks/mercenary post, market) and
   (b) an enemy unit (worker 7, peasant 1, spearman 24): per tick from the core - attacker zustand, bild, bildzyklus, position;
   target life (unit leben / building currentHealth) and fireDuration. Derive: delay arrival -> attack state, swing ticks, hit
   offset, damage per hit, for slaves the fire start. Fill chain_audit.ATTACK_TIMING (one entry per type and target class).
2. "laufen": survey of the terrain kinds of the maps we play (from the walk layer / terrain layer), then per own type and terrain
   kind: walk a straight line of N fields over that terrain, ticks per field from the core per tick. Also measure blocking by
   own/enemy units and population (crowd on the path) and its delay. Fill a table TICKS_PER_FIELD[(type, terrain)] for link 2.
Status 2026-11-12 23:10: measurement not started yet. Sandbox = map editor (not the running game: `toeteAlle` would also kill our
lord). Open it with `editor_test.py schritte '<json>'` (menu steps via the module's "knopf" command; the step list is in the
Handbuch, section Testing). Placement: `setzeEinheit` {spieler, typ, x, y}, `setzeGebaeude` {spieler, x, y, mapper, groesse};
known mappers: Holzfaellerhuette 51/3, Kornspeicher 80/4, Lagerplatz 52/5, Apfelplantage 72/10, Kaserne 87/5, Wachturm 110/3,
Bergfried 61/7 (quarry and ox tether still to look up). Record per tick from the core (kern_leitung.Leitung: einheiten zustand,
bild, bildzyklus; gebaeude leben) as in the game-20 measurement (data/research/schlag_messung_20261112).
Editor steps (Handbuch, Testing, measured 2026-10-17): {"menue": 41} -> {"hauptmenue": 9} -> {"knopf": "CustomScenarios_Main", "nr": 2}
-> {"knopf": "NewMapMaptype_Buttons", "nr": 3} -> {"knopf": "NewMapMapsize_Buttons", "nr": 4} -> {"menue": 12} (empty 400x400 map;
time runs, units act and fight, no workers, no AI). Trap: a silent load dialog may open - {"laden": 17} closes it.
First editor trials 2026-11-12 23:07 (schlag_messen.py, data/research/schlag_messung_20261112_230707.jsonl, speed 20): A_ASSASSIN 73
vs woodcutter hut (mapper 51): attack state 2 ticks after the order, hit 93 ticks later, 75 damage, frame 24 -> 0 (same as in game
20). A_SLAVE 71: attack state after 2 ticks, first life loss 477 ticks later, then 4 every 20 ticks = fire, not a swing (measure
fireDuration for the fire start). A_SWORDSMAN 75: spoiled - the burning hut of the slave trial stood on the same spot; fix: every
trial on its own spot (and record building fire).

### Measured 2026-11-12 23:20-23:40: links 3-5 for every fighting type (map editor, instance 2, speed 40, every tick read)
Tool `src/selfaware/tools/experiments/schlag_messen.py` (one trial per free spot, an exclusive lock per instance, tests in
tests/test_schlag_messen.py). Files in data/research: _232130 (melee vs hut), _232707 (shooters, slaves vs hut), _233412 (melee vs
E_SPEAR from 8 fields with a second order), _233549 / later runs (shooters vs a standing assassin at 12 / 30 / 17 / 8 fields).
The hut (mapper 54, core type 1) has 200 life; a building's x, y in the core is the corner of its footprint (placed at (184,200), read
(184,200)). Placement traps: a second granary or stockpile of a player must touch the first (the game places nothing, the module still
says ok=true); quarry, iron mine, pitch rig and apple farm need their ground - not on the empty editor map.

| type | vs building: swing (ticks) / damage per hit | vs E_SPEAR: damage per tick | second order: ticks without damage |
|---|---|---|---|
| A_ASSASSIN 73 | 93 / 75 | 120 | 4 |
| A_SWORDSMAN 75 | 96 / 100 | 125 | 8 |
| E_SPEAR 24 | 48 / 10 | 25 | 4 |
| E_PIKE 25 | 28 / 40 | 30 | 8 |
| E_MACE 26 | 48 / 80 | 70 | 4 |
| E_SWORD 27 | 60 / 100 | 150 | 12 |
| E_KNIGHT 28 | 72 / 100 | 150 | 4 |
| E_MONK 37 | 24 / 20 | 50 | 8 |
| A_SLAVE 71 | fire: burning 370-372 ticks after the attack start (4 trials), then 4 life every 20 ticks | 10 | 4 |

- Melee vs a building: the attack state 107 starts 1-2 ticks after the order (standing next to it); the hit lands when the
  animation frame wraps to 0 (73: 24 -> 0, 75: 27 -> 0, 24/26/27/28: 12 -> 0, 25: 1 -> 0, 37: 2 -> 0); the first hit 0-3 ticks
  before a full swing. The frame never stood longer than 12 ticks during a swing.
- Melee vs a unit: NO swings - the target loses life every tick from the contact on (both ways), the core shows state 106 only
  3-11 ticks after the first loss. Approach from 8 fields: 65-186 ticks.
- A second identical attack order to a fighting melee unit: 9 of 9 types walk again (state 101 at +3) and do no damage from +2 for
  4 / 8 / 12 ticks (by speed class). Shooters: no gap (the next hit one cycle later). Our modules resend orders (wegfuehrung
  NEU_ALLE = 6 rounds) - every resend to a fighting melee unit costs this.
- Shooters vs a building: 1 damage per hit and most shots miss (E_ARCHER 5 losses of 1 in 1,500 ticks, T23 1, A_ARCHER 5, A_SLINGER
  5, A_HARCHER 5) - an attack order on a building is of no use for them. A_FIRETHROWER 76: 1 per shot, the building burns 493
  ticks after the attack start (one trial). The core shows a shooter's building attack in `zielgebaeude` (= building number) and
  `zielart` 9, a melee attacker's in the attack tile (mauerx, mauery = a tile of the building), zielgebaeude 0 (measured 23:44).
- Shooters vs a standing assassin 12 fields away: states aim 4 -> shot 5 -> reload 6 -> 0 (one tick) -> aim; cycle E_ARCHER 129,
  T23 228, A_ARCHER 90, A_SLINGER 56, A_HARCHER 78 (aim state only); all 5-6 shots hit (one trial per type) (6000 T23, 1200 the archers and horse archer,
  900 the slinger); first loss after the aim start 122 / 176 / 80 / 74 / 72 ticks. 30 fields: E_ARCHER and T23 0 hits of 4,
  A_ARCHER first loss at 109 (+29), A_HARCHER 99 (+27) - about 1.6 ticks per field of flight. A_SLINGER at 17 fields: 0 of 4.
  A_FIRETHROWER at 8 fields: first loss 80 and 359 ticks after the aim start (2 trials), then fire damage every tick.

Built from it (chain_audit.ATTACK, tests/test_chain_audit.py, 7 sabotages each red): link 3 per type (melee 106/107, shooters
4/5/6, 0 between two shots is no break); link 5 deadline per type and target - building: one swing, fire start + 20, shooters "NO
USEFUL ATTACK" at once; unit: melee 13 ticks (longest measured gap 12 + 1), shooters first shot + one cycle up to 12 fields, beyond
12 fields one CHAIN_INFO "not checked" (misses measured); link 4: in the attack state the frame (bild, bildzyklus) must change - the
same frame in every look up to the deadline is "ANIMATION STANDS", else "NO DAMAGE AFTER ..." with the frames seen; "RESEND WHILE
FIGHTING" once per order when the same order goes out again to a fighting melee unit; reach to a building measured to its footprint
(sicht.GROESSE), so the far side of a 6x6 quarry is in reach; out of reach again (target stepped away) the clocks start anew.
Not covered yet: endless chasing of a fleeing target (each chase restarts the clock), several attackers on one target (any loss
counts for each), damage per hit against walls / towers / gates, melee damage against other unit types (the live table in
spielwerte has the matrix; E_SPEAR measured here).

### Link 2 measured and built (2026-11-12 23:43 - 2026-11-13 00:30)
- Flat ground (editor, `lauf_messen.py`, 24 fields straight and 20 diagonal, the same): 12 ticks per field for E_SPEAR, E_MACE,
  A_SLAVE, E_ARCHER, A_ARCHER, A_SLINGER; mounted E_KNIGHT and A_HARCHER 10.6 (field ticks 8, 12, 12 - three micro steps a move;
  the median 12 hid it until 00:50); 16 A_ASSASSIN; 24 A_SWORDSMAN, E_PIKE, E_MONK, A_FIRETHROWER, T23;
  32 E_SWORD. The core's speed value `tempo` is 1 / 1 / 2 / 3 - the 12-tick types walk with a run of 1. The path index `wegindex`
  moves exactly one field per field (20 of 20).
- Terrain survey (`gelaende_erheben.py`, all six Team-Liga maps, fresh skirmish each): per field path links, building, LogicLayer,
  height (module command wegkarte) and the MacroLayer (peek) -> data/research/gelaende_<map>.txt / _macro.txt, counts in
  gelaende_wasser_20261113.json.
- The rule comes from the game itself: calculateUnitMovementSpeed (0x0052F7E0) decompiled from the OpenSHC reference (Ghidra
  headless, Dekompilieren.java). Water = LogicLayer 0x20000000 unless the MacroLayer (0x01DCFCB8, 2 bytes a tile, & 0x3f) is 1
  there, or LogicLayer 0x40000000; speed value +3, +4, +6 as the wetness grows (every 8 ticks), +3 lingers after leaving; mud
  (LogicLayer 0x200000) +2; climbing +1..+5. This explained the first trials: on line y=195 of Paradise Plains 12 of 16 water-bit
  fields carry MacroLayer 1 (no effect) - the assassin walked them in 16 ticks and slowed only at x=263-264 (MacroLayer 4) and two
  fields after (lingering wetness).
- Model `services/laufmodell.py` (TYPES = measured speed value and run per type, the rule above; tests/test_laufmodell.py, 7
  sabotages red). The speed update comes every 8th MOVE of the unit, not every 8th tick (the code counts its own calls; measured
  on the slope: 24 / 40 / 48 ticks between two changes at speed value 2 / 4 / 5). Against 60 walks on Paradise Plains (all 15 types,
  water line, mud line, free line, slope; data/research/lauf_gelaende_20261113_001457.jsonl; command `lauf_messen modell lauf=...
  gelaende=...`): 9 walks blocked (on one field more than twice as long as the game's own speed value allows, 7 of them at
  x=210-217 of the free line y=23 - cause not measured) and left out; the other 51 over all 8 update phases (no fitting): foot
  units water line exact (13 of 13), mud line -6 % .. +7 %, free line -13 % .. 0 %, slope -14 % .. +10 %; mounted (E_KNIGHT,
  A_HARCHER) up to -28 % .. +25 % depending on the phase; the flat model up to -49 %.
  Effective water per map (fields of the map diamond only - translationMatrix, data/research/kartenraute_400.json; a first
  count at 00:05 took fields outside the diamond too, where the layers give the data of other fields): Battle Brother's Strife 0
  (flat, no mud), Branching Fortunes 569, Dwarven Dream 28 (mud 649, height steps up to 153), Green Trench 572, Paradise Plains
  433 (mud 414), Grumpy Neighbors 149; water bit without effect 0-2,012 (gelaende_wasser_20261113.json).
- Live link 2 in chain_audit (`_walk`): per check the path index must move as the game's own speed value of the unit says (one move
  every speed + run + 1 ticks, (run + 1) of 8 micro steps); SLOW_FIELDS = 4 fields behind since it was last on time (self-set,
  above the model error) -> "WALK BEHIND THE GAME'S SPEED" once per order, with the units within 1 field (own / enemy /
  population / neutral). Terrain is counted by the game's speed value already - it is named ("terrain slowed it in N checks"),
  no break. 2 tests, 2 sabotages red.
- Not yet: the planning side (expected arrival of an order from the path and the model before sending it, choosing a path around
  water), moveDelay (crowding) and troops walking with their slowest member in the model, the reaction (evade, click through,
  kill) - that is the brain's part.

### Link 2 in the real games (2026-11-13 21:55, Wissensregister S121)
tools/analysis/lauf_stoerungen.py over the 6 games of 12.11. on Paradise Plains: 7,086 walking sections - on time 79 %, slow 18 %
(upper bound, straight line), disrupted 3 % (219); per disrupted section: own fighters within 1 field in 101, nobody in 113 (cause
not measured - detour or a new walk target), enemies or population in 5. Next: own crowding (archer groups 26-27 % slow) and the 113
unexplained stops.
Built 2026-11-13 22:00 (Daniel: "Ja, abstellen", S118): execution/kampfschutz.py on both order ways (befehl.sende after the lord
lock, kernweg.senden before the ring), fed by the Lenker each round (kampfschutz.stand(L)): a melee unit in state 106 whose
zieleinheit/nahziel is the target is taken out of an attack order on that target. Not covered: building targets (not measured).

13.11.2026 21:58 (Daniel "Ja, messen"): kampfschutz.py also covers building targets (S122: a second order mid-swing restarts the swing; a unit in state 107 next to that building's footprint is taken out; Lenker passes stand(L, G)). Core ring verdict for building attacks measured (S123): the attack works, the verdict is wrong - the game keeps the target building in the group record (Trupp +0x2D0), the unit's own field +0x336 stays 0, and haende.rs wirkung_pruefen compares the unit's field. Fix proposed, not built (needs Daniel's yes): compare the group's zielgebaeude for ANGRIFF_GEBAEUDE.

13.11.2026 22:06 (Daniel 21:59: "Gerne dann aber direkt partie"): core 26 built and loaded on instance 2 (haende.rs: a building attack also counts when the group record carries the target; test gebaeudeangriff_wirkt_ueber_das_ziel_der_gruppe, sabotage red; one ring attack on a hut afterwards: 'wirkt/gebaeude'). Game 1 (22:02:49) was stopped by the error watch at tick 2449 with F5 NO PROGRESS for a digging spearman - a false alarm (S124: state 124 = digging); chain_audit counts a digger in state 124 as working (test test_a_digger_at_work_is_no_stop_even_away_from_its_tile, sabotage red). Game 2 started 22:05:25.

[ENTFERNT 13.11. 23:02, siehe unten] 13.11.2026 22:41 (Daniel 22:37 "Ja, mitziehen" on "Sollen die wartenden Speertraeger den Bogenschuetzen auf den Vorstoss folgen?"): waechter.schritt(begleiten=vorstoss.mitglieder) - without a threat the melee stack onto the field of the advance's archers (reason follow_archers_advance); the start post (stellung) skips units another module leads (game 4: the post order went to the advance's archers, archer 310 never walked, chain check stopped the game). Chain check: a dig order ends when the digger reaches the moat or digs (game 3: digger 332 walked on to the next tile). Test from the game 3 scene, two sabotages red; replay of game 3's rounds: 4 follow orders for 333-335 (none after tick 1120 before). Suite 759 passed, 78 skipped; test_relocation_manifest red because today's games appended 163 lines to data/research/wissen_ablauf.jsonl (by design). Game 5 started 22:41:57.

### 9. Expected result per unit (Daniel 13.11.2026 22:45 "jede Einheit muss ja sagen was sie macht und was das erwartete
ergebenis ist"; 22:49 "Ja, einbauen" on "Soll jede Einheit im Logbuch ihr erwartetes Ergebnis nennen und die Kettenpruefung es
pruefen?")

Plan (22:52):
1. micro/chain_audit.py: one function expectation(action, type, position, goal, kind) built only from the measured tables the
   check already uses (ATTACK, SHOT_CHECKED, the far-shot trials, laufmodell flat speed) - unmeasured says UNMEASURED.
   Measurement per point: unit test with the scene of game 5 (S126); negative run: sabotage the table lookup -> red.
2. micro/unit_log.py: close_round(tick, L, G) adds expect=... to every UNIT change line (G for building targets); collect_round passes
   G. Measurement: tests on the exact lines; the error watch's UNIT regex still parses (test).
3. chain_audit: shots on units beyond 12 fields are checked for the measured trial size (4 shots, +1.6 ticks per field for the first
   hit) where a far-shot trial exists (E_ARCHER/T23 0 of 4 at 30, A_ARCHER/A_HARCHER 3 of 3 at 30, A_SLINGER 0 of 4 at 17); other
   types stay "not checked". Measurement: test with game 5's archers (36 fields, no loss) -> NO DAMAGE after 4 shots; negative run.
Risks: games will stop more often at far shots (by design - the advance picks targets up to 38 fields); exact-line tests change.
Not touched: the advance's target choice (SCHUSS 38) - next step, own question to Daniel.

13.11.2026 23:02 - Stapeln entfernt (Daniel: "dass Nahkaempfer die Bogenschuetzen schuetzen. bitte diese regel ueberall entfernen
ich hatte gesagt keine komoischen allgmeinen regeln. Das ist nie eine regel gewesen vielleicht habe ich es mal gesagt ... so etwas
muss erstmal begruendet sein und getestet ... Fuer den fall braucht du keine sonderregel sondern die Kampfregeln gelten ganz klar -
raiden"). Removed: the guard's stacking of melee onto the archers' field (since 12.10., reason stack_with_archers) and its follow
extension of 22:41 (begleiten, follow_archers_advance). Kept: vorstoss.anspruch for the start post (one leader per unit - not this
rule). Open: who leads the start melee for raiding - question to Daniel.

### 10. Role per unit, every round (Daniel 13.11.2026 23:07 "Ist das nicht einfach eine berechnung- Was macht der gegner und wird
verteidigung, raid oder angriff gebraucht? Und dann wird bestimt was pro einheit passiert. Ich persoenlich sehe in dem fall keinen
grund nicht zu raiden"; 23:14 "Ja, bauen" on "Soll ich jetzt die Rollen-Rechnung je Runde bauen?")

Plan (23:20):
1. micro/rollen.py: bedrohungen(L, buildings, sp, protected) - the guard's threat rule moved here unchanged (enemy troops at our
   buildings: position <= 8 or walk target <= 6 fields; attackers of our units up to ANGREIFER_R 40 fields); the guard calls it
   (one place). verteilen(L, buildings, sp, candidates, protected, raid): no threat -> every candidate raids; threat -> the smallest
   group the battle calculation wins with (zuweisung.kleinste_gruppe, nearest first) defends, the rest raids; no group wins -> all
   stay with the guard (as before - not a new rule, open question to Daniel). Without a melee raid module nobody raids.
2. Candidates: own living units the melee raid can lead (nahkampf.KANN) that no other module leads (graben, vorstoss, brandtrupp,
   reiterjagd, feldzug, assassin troupe), plus the raid's current members. The lord never (catalog: defence only).
3. NahkampfRaid.zuteilen(join, leave): role members join, defenders leave (released from the Wegfuehrung). The Lenker computes the
   roles before the guard's step and leaves the raid members out of the guard; one ROLLEN line per change.
Measurement per point: tests with the scene of game 7 (start, no threat -> spearmen raid) and a threat scene (one slave at our
building -> one defender, the rest raids); negative runs (sabotage). Not touched: attack (Feldzug), shooters (Vorstoss), assassins.
Risks: units flip between raid and defence when threats come and go; the Wegfuehrung release on every switch.

14.11.2026 00:14 (Daniel 00:12 "Ja, Nummern"): game/ucp/befehl.sende writes one console line per order to units with their numbers and the game tick of execution from the module's reply ('BEFEHL Tick N angriff {...} an k Einheiten: [..]'; '?' without an execution line) - to trace orders that did not take (games 5 and 12, S126/S135; sandbox: a second walk order to a walking unit was taken 3 of 3 times, S136). Tests tests/test_befehl_nummern.py, sabotage red; suite 775 passed.

14.11.2026 19:55 (game 14, S138; Daniel 19:31 "Ja, Partie"): the walk check with the terrain map follows each unit's way (micro/chain_audit._Trail) over its orders - wetness, climb height and the 8 possible move counts go on (services/laufmodell.Walker, the same rule as walk(), checked equal on 400 random ways), the clock is set anew at every new path; a new order the game shows one round late does not cut the way; the fields walked are at least the straight line between two positions (no longer cut to the path index). The Lageprotokoll writes wegindex/weglaenge/tempo of own units; tools/analysis/spur_laufpruefung.py replays one unit's way from console and Lageprotokoll through the check. tools/experiments/soldaten_mitschrift.py waits for the core instead of breaking off. Tests: tests/test_chain_audit.py (ford + new order, late order, standing still), tests/test_spur_laufpruefung.py, tests/test_soldaten_mitschrift.py, tests/test_lageprotokoll_eigen.py; sabotage red each; suite 780 passed.

14.11.2026 20:50 (game 15, S139): tools/analysis/befehle_greifen.py - per walk order of a game: did the unit's walk target come within 3 fields of the target within 20 ticks (console BEFEHL lines + per-tick recording, group from ucp3.log). Game 15: 108 of 109 took; the one that did not (309, tick 3404) got no planned destination at all. Test tests/test_befehle_greifen.py, sabotage red.

14.11.2026 21:05 - Plan (Daniel 20:56 "Ja, mitschreiben"; S139/S140: a walk order that did not take, the game planned no new destination - giveTribeMoveInstruction skips a unit by state fields nobody records). Offsets from the Ghidra project OpenSHC-ref, struct Unit (1168 bytes; dump data/research/funktionswissen/unit_struktur_openshc_20261114.txt; known fields agree with the kern: destinationX +200, plannedDestinationX +732, tribeID +728): logicalState +140, moveRelatedFlag +148, goToRallyPoint +176, usingTeleport +670, dying +672, field_0x413 +1043 (byte), rallyRelatedFlag +1068, moveableUnk +1094.
1. Kern (crates/samurai-kern): welt.rs reads the 8 fields into Einheit; fuer_fremde sets them 0 (own units only, the stricter reading of the Sichtschranke); leitung.rs: AUFBAU 5 -> 6, unit record 108 -> 124 bytes (8 x i16 after the 23 i16), assert; lib.rs VERSION 27. Measure: kern tests (record layout, fuer_fremde), build i686.
2. Python: game/kern_leitung.py AUFBAU 6, EINHEIT 124, EINHEIT_FORMAT '<ii12h7i31h2x', 8 names (logikzustand, laufmerker, sammelgang, teleport, sterbend, merker413, sammelmerker, beweglich) in EINHEIT_SPIELFELD and NUR_EIGEN; telemetry/lageprotokoll EIGEN_FELDER + the 8; tools/experiments/soldaten_mitschrift FELDER + the 8 at the end (old indices stay); tools/analysis/befehle_greifen names the 8 before and after an order that did not take. Measure: tests with packed bytes (tests/test_kern_leitung.py), recorder and analysis tests; negative runs.
3. Live check on Instanz 2 (the paused game 15): swap in samurai_kern_27.dll, read the 8 fields of 309 through the kern AND by peek at the same offsets - they must agree.
Not touched: Instanz 4/5, the game module (logik.lua), the Lenker's decisions. Risks: a wrong offset gives plausible-looking numbers (the peek cross-check catches a kern bug, not a wrong offset - the offsets come from OpenSHC for the base exe; the kern's known fields at OpenSHC offsets work, so the layout is the same); old protocols/recordings keep their shorter rows.

14.11.2026 21:08 - done as planned, with two changes: 6 fields, not 8 (dying is already a condition of the kern's list; field_0x413 is 'meaning unknown' in the Sichtschranke - unused until cleared); foreigners follow the Sichtschranke table, which tests/test_kern_leitung.py enforces (logicalState, moveableUnk visible; the other four 0) instead of 'all own only'. Recorder rows also carry planx/plany/gruppe. Kern tests 47, suite 783 passed; negative runs red; live cross-check 14 of 14 (S141). Instanz 2 start version now kern 27 (backup samurai_kern.dll.v26-20261114).

14.11.2026 22:23 - game 16 (Daniel 22:13 "Ja, Partie"; S142): all 169 new walk orders took, the S139 case did not recur. The watch stopped at tick 4885 on a walk line for spearman 332 that said 'blocked or crowded; within 1 field: nobody' - the per-tick record shows a melee fight (state 106, nahziel 365, an enemy woodcutter 2 fields away). Fixed in micro/chain_audit.py: in its attack state the line names the fight and the opponent ('FIGHTS INSTEAD OF WALKING - ...'); the line and the stop stay. Test test_link_2_a_walker_that_fights_is_named_as_fighting_not_as_blocked (negative run red), suite 784 passed, replay of game 16 gives the new text. Open for Daniel: the melee raid kept worker 307 as target since tick 1894 and its walk order of tick 4745 took 332 out of the fight with 365 for 10 ticks - module not changed.

14.11.2026 22:34 - Plan (Daniel 22:31 "Ja, Raid ändern" on the proposal "Kämpft ein Raid-Soldat schon gegen einen gegnerischen Arbeiter, nimmt der Raid diesen Arbeiter als Ziel und schickt keinen neuen Laufbefehl"; S142):
1. micro/tasks/nahkampf.py: per member, before it keeps its target: core state 106 and nahziel (else zieleinheit) is an enemy worker among the raid's targets (WK.ziele, key ("e", nr)) -> that worker becomes its target (the old one released, one console line), greift = (target, round) - the unit attacks it, the attacker stands in the data; while it fights that target, the target is not dropped for 'success 0'. The Wegfuehrung leads it as before: within NAH_AM_ZIEL (4 fields) its order is the attack {"ziel": nr}, which the fight guard holds back (the unit fights exactly that target) - no walk order. Measure: test with the game-16 values (332 fights worker 365, target 307): target ("e", 365), no walk order goes out; negative run.
2. execution/kampfschutz.py: hooks ERFUELLT get the held part of an order; micro/chain_audit.py from_guard: a held attack order becomes the unit's order (channel "guard"), not a resend; runtime/live/erstes_spiel.py wires KETTE.from_guard. Without it the chain audit keeps the old walk order and stops the game on 'FIGHTS INSTEAD OF WALKING'. Measure: test walk order, then a held attack on the fought target -> no line, the walk order is gone; the S118 case (the same attack order again) unchanged; negative run.
3. Suite, module map, register.
Not touched: Wegfuehrung, the other raid modules (Brandtrupp, Assassinen, Reiter), the kern, the game module. Limits: a fight against a soldier, or against a worker without value for the raid (not in raids.ARBEITER), is not taken over - as before.

14.11.2026 22:39 - done as planned (S142 updated), one change: the fight guard's hook passes (building?, target, units), not an order dict - tests/test_wegfuehrung_sperre.py counts every {"angriff": ...} outside the Wegfuehrung as a new order site, and the hook sends nothing. Tests: test_nahkampf_raid_nimmt_den_arbeiter_den_sein_soldat_schon_bekaempft, test_an_attack_the_fight_guard_holds_back_becomes_the_units_order, wiring in test_kampfschutz; negative runs red (takeover off, hook off); suite 786 passed. Replay on the position logs: game 16 - 332 against 365 at rounds 4763 and 4885 taken over (336 fought its own target 350: only counted as attacking); game 15 - no case. Chain audit on the held attack: held, taken, arrived, attack started, damage - no line. Not checked in a game.

14.11.2026 22:47 - game 17 (Daniel 22:42 "Ja, Partie"; S143): stop at tick 3284 on NOT SEEN for spearman 333 - a walk order that did not take, the fourth such case (games 5, 12, 15, 17). The six recorded filter fields were the same as before all 100 walk orders of the game that took (2,0,0,0,0,1): refuted as the cause of this case. Open: field_0x413, 'state 0xCF', the early return 0 (tile, area, path search). The melee-raid takeover (S142) did not occur. tools/analysis/befehle_greifen.py: an order without TAKTE recorded ticks after it is 'offen' (my first run read the recording before it was complete - 6 'not taken', 5 of them had taken); test with negative run; suite 787 passed.

14.11.2026 22:50 - Plan (Daniel 22:48 "Ja, mitschreiben" on "das Feld field_0x413 für eigene Einheiten mitschreiben ... Kern 28"; S143): units[].field320_0x413 (+1043, byte; Ghidra: one writer, UpdateAssassin; Sichtschranke so far eigen 'unbekannt', fremd 'verboten').
1. Kern: welt.rs Einheit.merker413 (u8 at +1043 as i16), fuer_fremde sets it 0, test; leitung.rs AUFBAU 6 -> 7, the unit record stays 120 bytes (the new i16 takes the 2 padding bytes: 32 + 7*4 + 30*2), writer appends it after beweglich; lib.rs VERSION 28. Measure: kern tests, record layout assert.
2. Python: game/kern_leitung.py AUFBAU 7, EINHEIT_FORMAT '<ii12h7i30h', merker413:field320_0x413 in EINHEIT_SPIELFELD and NUR_EIGEN; telemetry/lageprotokoll EIGEN_FELDER, tools/experiments/soldaten_mitschrift FELDER (20 values), befehle_greifen takes them from FELDER. Sichtschranke (data/research/auge_plan/sichtschranke.csv): eigen 'erlaubt' by Daniel's yes, fremd stays 'verboten'; feldliste_gehirn.csv gets the row (tests check the leitung against it). Measure: suite, negative run (field not blanked for foreigners -> red).
3. Live check on Instanz 2 (game 17 paused): load samurai_kern_28.dll, read the field of all own soldiers through the kern and by peek - must agree; start DLL v28 (backup v27).
Not touched: the Lenker's decisions, the game module, Instanz 4/5.

14.11.2026 22:54 - done as planned (S144): kern 28 (Aufbau 7), field320_0x413 as merker413 for own units only; Sichtschranke eigen 'erlaubt', feldliste_gehirn.csv row added (CRLF kept). Kern tests 47, suite 787 passed, negative run (merker413 not own-only) red in 2 tests. Live: 13 of 13 own soldiers kern == memory, all 0; 16 foreign soldiers without the key. Start DLL of Instanz 2 = kern 28 (backup samurai_kern.dll.v27-20261114). Left as it was: kern_liest/python_sieht in feldliste_gehirn.csv still 'nein' for the six fields of S141 (column meaning not checked).

14.11.2026 22:57 - game 18 (Daniel 22:54 "Ja, Partie"; S145): stop at tick 2677 on NOT SEEN for spearman 331 (walk to (246,174), executed at tick 2566, group 1246; walk and planned target stayed (238,182)). All 7 filter fields as before the 82 orders that took. Evaluated after the recorder's end (offen 0). Games 15-18: 462 new walk orders, 3 not taken; per target: (186,154) 14 of 15 took, (242,202) 3 of 4, (246,174) 0 of 1. Left: the early return 0 (tile, area, path search) - not measured. Game 18 stays paused at the end.

14.11.2026 23:00 - probe in paused game 18 (Daniel 22:57 "Ja, pruefen"; S146): the same order to 331 -> (246,174) did not take again; the module's move check: target in area 0 (kannHin=0); the game's walk layer blocks (246,174) - inside enemy building 63 (type 31). Cause of S145: a waypoint on a blocked tile. The Wegfuehrung snaps to its own map, read every WEGKARTE_RUNDEN = 20 rounds, a successful read is not logged. S139 and S143: targets in area 1 and walkable now - open.

14.11.2026 23:04 - Plan (Daniel 23:03 "ja probieren wir es so, sollte es zu sehr laggen müssen wir das vlt schlauer gestalten. Aber bitte so testen" on "die Wegführung liest die Weg-Ebene neu, sobald ein Gebäude dazukommt, und schreibt jedes Lesen mit"; S146):
1. services/wegkarte.neu_lesen(runde, letzte_runde, gebaeude, bekannt, alle): reason to read or None - first map, a building number (or its type) not in the last read, or 'alle' rounds since. Measure: test (new building -> read; same buildings -> none; destroyed building only -> none; after 'alle' rounds -> read); negative run.
2. runtime/live/erstes_spiel.py: the refresh asks neu_lesen; each read in the console 'WEGKARTE gelesen Runde N Takt T (reason), x.xx s'; timing in ZEITEN as 'wegkarte'.
3. Game 19 (Daniel: "bitte so testen"): number of reads, seconds per read and in sum against the round times in ZEITEN; whether a walk order still lands on a tile the walk layer blocks (befehle_greifen + NOT SEEN lines).
Not touched: how the Wegfuehrung snaps (_begehbar_nah), the walk layer itself, the modules. Risk: own buildings appear often - many reads; measured in game 19, judged by Daniel.

14.11.2026 23:09 - done as planned and tested in game 19 (S147): 19 reads in 28 rounds, 0.28-0.33 s each, ZEITEN wegkarte 4.34 s after 20 rounds; ticks per Lenker round median 158 against 116-125 in games 16-18; 153 of 153 new walk orders took. Tests: test_wegkarte_neu_lesen (negative run red), test_wegfuehrung updated to the new call; suite 790 passed. Side findings from my own S142 work that stopped the game: from_guard registers a held attack as not yet seen (NOT SEEN for 331); the chain check judges a game-started fight one round before the module can take it over (330). Proposed, not built: read only a rectangle around new buildings (31x31: 0.04 s against 0.25 s), from_guard counts as taken, the chain check waits one round on a fight the order did not ask for.

14.11.2026 23:11 - Plan (Daniel 23:10 "Ja, beide bauen" on "Soll ich beide Verbesserungen bauen und mit Partie 20 testen?": 1. Karte nur um neue Gebäude lesen, 2. Kettenprüfung richtigstellen; S147):
1. services/wegkarte: ausschnitte(neue Gebaeude) -> one rectangle per new building (footprint sicht.GROESSE plus RAND fields), ausschnitt_holen(x0, y0, x1, y1) and flicken(karte, k) (the rectangle replaces its cells in the old map). Full read at the first map, every WEGKARTE_RUNDEN rounds and when more than AUSSCHNITT_BIS buildings are new (measured 23:09: full 0.25 s, 31x31 0.04 s -> about 6 rectangles cost one full read). Lenker: neu_lesen gives the new buildings; console 'WEGKARTE gelesen ... Ausschnitte n' / 'ganz'. Measure: tests (rectangle per building, patch keeps the rest, too many -> full); negative run; game 20: seconds per read and ticks per round against game 19.
2. micro/chain_audit: from_guard counts as taken at once (the guard saw the fight on this round's state). check(): a unit in its attack state against something its order did not ask for (walk order, or another target) - the first check that sees this fight does not judge (walk orders go on with judge=False, the trail stays), the next one does. Measure: tests for the game-19 cases (330 walk + fight, taken over in the same round: no line; 331 held attack, then another opponent: no NOT SEEN); the S142 test now gets its line one check later; S118 and resend tests unchanged; negative runs.
3. Suite, module map, game 20 with recorder and watch.
Not touched: the raid module, the Wegfuehrung's snapping, the kern.

14.11.2026 23:18 - done as planned and tested in game 20 (S148): 18 map reads (2 whole, 16 in rectangles, 0.03 s each), ZEITEN wegkarte 1.52 s after 20 rounds (game 19: 4.34 s), ticks per round median 126 (game 19: 158). The two chain-audit changes did not occur in the game (no takeover, one guard hold) - tested only by the unit tests (negative runs red), suite 794 passed. New: walk alarm for 330 on a hill (height 9 -> 15 -> 8, 241 ticks where the model says 182) - laufmodell; 1 walk order not taken (334 -> (210,178)); 'unit inside a building footprint' refuted for all four open cases.

14.11.2026 23:21 - Plan (Daniel 23:19 "Ja, mitschreiben" on "je Takt mitschreiben, in welchem Gebiet jede eigene Einheit steht"; S148): the area id of the PathConnectionLayer (Wegnetz) at the unit's tile, exactly as the module's ZUGPRUEFUNG reads it (tile = fine position / 8, kern wege::gebiet; the game rebuilds the layer at most every 200 ticks - logik.lua note).
1. Kern: welt.rs Einheit.gebiet = wege::gebiet(feinx / 8, feiny / 8); leitung.rs AUFBAU 7 -> 8, unit record 120 -> 124 bytes (31 i16 + 2 padding), writer appends it; lib.rs VERSION 29. The Sichtschranke lists PathConnectionLayer[] as eigen and fremd 'erlaubt' (map data everyone sees) - the kern does not blank it; the recorder keeps own soldiers only. Measure: kern tests.
2. Python: kern_leitung AUFBAU 8, EINHEIT 124, EINHEIT_FORMAT '<ii12h7i31h2x', EINHEIT_ABGELEITET {"gebiet": "PathConnectionLayer[]"} (a map field, not a unit field) checked against the field list; lageprotokoll EIGEN_FELDER, soldaten_mitschrift FELDER (21 values), befehle_greifen shows it per untaken order. Measure: suite, negative run.
3. Live on Instanz 2 (game 20 paused): load samurai_kern_29.dll; for own soldiers the kern's gebiet against the module's ZUGPRUEFUNG 'bei (x,y) Gebiet n' - a second, independent reader (Lua); start DLL v29 (backup v28).
Not touched: the Lenker's decisions, the game module.

14.11.2026 23:23 - done as planned (S149): kern 29 (Aufbau 8, record 124 bytes), gebiet per unit; kern tests 47, suite 794 passed, negative runs red (gebiet marked own-only; writer without gebiet). Live: 15 of 15 own soldiers kern == module ZUGPRUEFUNG (field and area). Start DLL of Instanz 2 = kern 29 (backup samurai_kern.dll.v28-20261114). For the cross-check game 20 ran 88 ticks on (4790 -> 4878).

14.11.2026 23:28 - game 21 (Daniel 23:23 "Ja, Partie"; S150) and Daniel's question 23:25 why spearmen walked back: the Wegfuehrung's safe path - 333: 66 cells with danger 50 against the straight 24 cells with danger 193, first waypoints south-west; target choice (wert_je_takt) uses the straight distance. 1 walk order not taken (331 -> (250,202)): unit area 1, all fields normal, target passes laufziel_ok now. Walk alarm 336: flat, four diagonal steps at 16-20 ticks.

14.11.2026 23:38 - Plan (Daniel 23:29 "Niemals nach luftlinie warum auch? Es geht hier um die Wegfindung"; 23:32 "kein komischer wert bitte es geht hier um den gebaeudewert, gefahr und zeit und werteberechnung"; 23:34 "Ja, mit einbauen" on "Angreifer gleich mit in die neue Zielwahl einrechnen"; S150):
Measured first (94 position logs 10.-14.11.): an own unit fought an enemy soldier (state 106, nahziel) and walked >= 3 fields by the next round - 1 of 18 times the soldier was within 2 fields after, 17 not (round resolution, mostly assassins and slaves). The field nahangreifer is no 'attacked by' (mostly an OWN woodcutter, 3072 times on own slaves) - not used.
1. services/schussfeld.Gitter.laengen(start): the same cheapest-path search as weg() over the whole grid, per cell the number of cell steps of that path (no early stop). micro/wegfuehrung.Wegfuehrung.weglaenge(ort, typ, L, G) -> function ziel -> fields (steps x ZELLE, schach for the start cell) or None (no path); the danger picture and grid of a round cached by (L, G) and used by schritt as well.
2. baukasten/wirkung: wert_je_takt(..., felder=None) - with felder the time is the safe path, not schach; rechnen_mit(typ, z, leben, nah) - success with a given own life and defenders (_rechnen uses it).
3. micro/tasks/nahkampf: with the Wegfuehrung every target is valued by its safe path; unreachable targets drop out; each round each member takes the target with the highest value per tick from where it stands (switch only when strictly higher - no margin), except the worker it fights (S142). Fighting an enemy soldier (state 106, nahziel enemy melee type): value of fighting on (time to kill from the duel table, own life after, success at the target without that defender when it covers the target - within raids.GEFAHR_NAH) against walking on (the soldier does not follow - measured 17 of 18) - the higher one wins; fighting on = the Wegfuehrung leads to the soldier this round (the fight guard holds the attack).
Measure: tests per point with negative runs; suite; game 22: switches with values in the console, ticks per round, NOT SEEN / walk lines.
Not touched: other raid modules, the Wegfuehrung's planning, the kern.

14.11.2026 23:47 - done as planned (S151), one change: no shared danger cache between raid and Wegfuehrung (an in-place change of the state gave a stale picture in a test; a fresh picture costs 0.026 s) - the raid builds one grid per round for all its units. Tests: 5 new (path length = planned path, value with the path, choice behind a wall, switch on the way, fight back a defender / walk on), 4 negative runs red; suite 799 passed. Game 22: 22 switches, no soldier fight; a new walk order costs a walking unit about 6 ticks (15.9 against 9.5 per field); rounds longer (first 13: median 194 against 147).

14.11.2026 23:48 - Plan (Daniel 23:48 "Ja, einbauen" on "die gemessenen 6 Takte je Wechsel in die Wertrechnung aufnehmen"; S151): micro/tasks/nahkampf.py WECHSEL_TAKTE = 15.9 - 9.5 = 6.4 (measured 23:47 from the recordings of games 20-22: field change of a walking unit with a walk order in between against without). A switch adds them to the new target's time: value per tick of the new target = Wert x Erfolg / (Takte + WECHSEL_TAKTE); the current target has no switch. Decision in one function _lohnt_wechsel; test with the numbers of the rule and a negative run; the switch line names the cost. Not touched: the first choice (no switch), the fight-back decision (a held attack sends nothing).

14.11.2026 23:49 - done as planned (S152): WECHSEL_TAKTE in the re-choice, test with negative run red, suite passed (see suite run). Not in a game yet.

15.11.2026 00:06 - Daniel 00:04 on the proposal "keine unangreifbaren Arbeiter, Kampf nur wenn er sich rechnet": "ja aber eine einheit geht nicht einfach weiter sie braucht noch weitere laufbefehle um durch eine einheit durchzuspammen" - measured fits (game 16: after the walk order at tick 4745, 332 walked 10 ticks and fought 365 again from 4756). Open to build (not started): when the value says walk on, the walk order goes out again each time the unit is back in a fight it did not ask for (not only every NEU_ALLE rounds). Also: "Außerdem will ich jetzt mal endlich eine partie laufen sehen ... vielleicht sehe ich ja mal etwas längeres spiel?" - game 24 started 00:05 without the stopping watch (it has no report-only mode), recorder on; chain lines stay in the console.

15.11.2026 00:11 - STOP (Daniel 00:07) handled wrong first: I ended the Lenker with the STOP file - Daniel: "stop heisst nicht lenker beenden du pausierst du fixt das problem und fraegst ob du weiterlaufen laesst oder neustarten sollst" (memory saved). Built (S154): stonemason at work no target, measured worker kill time (24/71 vs 3), S142 takeover withdrawn, walk order re-sent when stuck in an unasked worker fight. Suite 800 passed, negative run (stonemason rule) red. OPEN for Daniel: the value calc still prefers an adjacent worker (own losses in worker fights not counted). Game 24 paused at tick 16277, Lenker ended.

15.11.2026 00:20 - Plan (Daniel 00:20 "Ja, Kern bauen" on "Neu-Befehlen je Takt im Kern"; Daniel 00:18: "die einheiten sollen gefaelligst raiden und nicht neben den gebaeuden warten"):
Found: the raid's walk orders go via the game module (Wegfuehrung -> befehl, chain lines 'via module'), the kern's order book (haende.rs Buch) never sees them; the Buch also refuses a repeated order on purpose (Annahme::Doppelt, "kein Dauer-Neubefehl").
1. Kern haende.rs: a walk order can carry 'durchsetzen' (new Anspruch flag, set by Python over the ring). Each tick, for such an order whose unit is in its fight state (106/107, shooters 4-6) against something the order did not ask for, the kern sends the same walk again (laufen(), not through the Doppelt check) - every tick until the unit walks (101) or the order is over; count per order for the Leitung/log. Interval: every tick (game 16: the unit fought again 10 ticks after one walk order - measured; a per-tick resend is the smallest the kern can do).
2. Ring/Leitung: the flag in the ring entry (kern_leitung + kernweg), Aufbau/VERSION up; Python tests on layout.
3. Python: the Wegfuehrung sends the walk orders of 'nahkampfraid' through kernweg with durchsetzen (the raid decides by value whether it walks on - S154); the per-round loslassen from S154 stays as fallback when no kern.
4. Tests: Rust test for the Buch decision (resend only when fighting an unasked target, not when attacking its own target, not when walking); Python tests for routing and flag; negative runs; build kern 30, load in Instanz 2, new game (Daniel: restart after the build).
Open before building: whether the game accepts a walk order every tick without side effects (each order stops a walking unit briefly - measured 6.4 ticks per order) - resend only while fighting.

15.11.2026 00:22 - S155 Stand: Kern 30 gebaut (crates/samurai-kern: haende.rs LAUF_DURCHSETZEN = 18, Buch.durchsetzen / durchsetzen_pruefen / durchgesetzt; lib.rs haende_takt ruft durchsetzen_pruefen jeden Takt mit Zustand 106/107; VERSION 30). Kern-Tests 48, Test s155_... , Gegenprobe rot. DLL crates/samurai-kern/target/i686-pc-windows-gnu/release/samurai_kern.dll (00:22:27) - NOCH NICHT nach Instanz 2 kopiert, nicht geladen.
NAECHSTE SCHRITTE: (1) Python kern_leitung: LAUF_DURCHSETZEN = 18; execution/kernweg.uebersetze: Befehl {"angriff": {"lauf": [x,y], "durchsetzen": True}} -> Art 18. (2) Raid-Laufbefehle ueber den Kern: heute geht die Wegfuehrung ueber befehl (Modul); der Kernweg ist nur fuer Assassinen und aus (erstes_spiel KERNWEG = False, kernweg_senden Zeile ~971, 'noch nicht im Spiel erprobt') - pruefen, ob der Raid ihn mit eigenem Auftraggeber nutzen kann (uebernehmen/freigeben der Raid-Einheiten). (3) Tests + Gegenprobe, Testreihe. (4) samurai_kern_30.dll nach Instanz 2, laden im Gefecht, Startfassung tauschen (Sicherung v29). (5) Neustart Partie 25 (Daniel: nach dem Kernbau neu starten), mit Mitschrift; auswerten: durchgesetzt-Zahl, Kaempfe gegen Arbeiter, Steinmetze.

15.11.2026 00:40 - S155 gebaut: Kern 30 mit Art 18 (durchsetzen) und Art 19 (erlaubter Gegner, damit der Kern eine Einheit nicht von ihrem eigenen Ziel wegzieht - Fund beim Bauen: ohne Art 19 haette er einen Soldaten, der seinen Ziel-Arbeiter bekaempft, bis zur naechsten Runde weggeschickt); nur Zustand 106 (107 = Gebaeudeangriff kommt nur nach einem Angriffsbefehl). Python: Wegfuehrung.kern / KERN_ZWECKE / _ueber_kern, kernweg.erlauben + RAID = 4 + oeffnen(mindestens), Lenker raid_kern() je Runde, Schalter raid_kern. Kern 30 nach Instanz 2 (Startfassung, Sicherung v29-20261115), geladen 00:38. Partie 25 gestartet 00:39 mit Mitschrift, ohne Wache. Auswerten: RAIDKERN-Zeilen in der Konsole, 'durchsetzen tick' im samurai_kern.log (Beginn/Ende, Takte, mal), befehle_greifen mit kern=.

15.11.2026 00:50 - S156: Partie 25 ausgewertet (Register S156). Durchsetzen wirkt unterwegs; am Laufziel war es sinnlos (858 von 982) - Kern 31 setzt nur noch weiter als AM_LAUFZIEL = 3 Felder vom Laufziel durch. Kern 31 in Instanz 2 (Startfassung, Sicherung v30-20261115, geladen 00:50). Neues Werkzeug tools/analysis/durchsetzen_auswerten.py. Offen: Tode der Raid-Nahkaempfer sauber trennen; Assassinen, die auf Laufbefehle nicht reagieren (alter Fall); naechste Partie nur mit Daniels Ja.

15.11.2026 01:03 - S157: Partie 26 ausgewertet, Daniels vier Fragen (Deckung, Speertraeger und Gebaeude, waghalsige Angriffe, Stocken) gemessen; Vorschlaege A-F im Blatt docs/plans/Plan_S157_Raid_Deckung_Stocken_SAI-Raid-Liga.html. Wartet auf Daniels Wahl. Nichts gebaut.

15.11.2026 01:09 - S157 Blatt neu auf der Portal-Vorlage (Daniel 01:06: "keine bau html", nur Takte): C:/Users/danie/Documents/DD-Berichte/SAI/SAI_2026-11-15_raid-deckung-stocken.html (blatt-pruefen GRUEN, 8 Punkte). Empfehlung gedreht nach Daniels Frage 01:07 (warum nicht ueber den Kern): B (Kern gibt Wegpunkte je Takt) mit F zuerst, dann D (Kern: Deckung), dann A. Das erste Blatt ohne Vorlage liegt in docs/plans/_beiseite_20261115/.

15.11.2026 01:19 - S158 (Daniel 01:13 "einbauen und schauen obs klappt"): schnelle Steuerung im Lenker - jede Schleife steuert Waechter, Assassinen, Raid, Wegfuehrung, Kern; Wirtschaft (Notwerbung, Stillstand, Kornring, Fallen, Speicher, Jagd/Brot, Auftragsbuch, Markt/Verkauf, Raid-Werbung, Bier, wirt/ausbau, Huetten, ausbau.beobachte, Heereskasse, Hunger-Notkauf, Endspurt) nur alle WIRTSCHAFT_TAKTE = 170 (Median Partie 26); runde zaehlt nur Wirtschaftsrunden; mit Streitkolben jede Runde voll. Schalter schnelle_steuerung=nein. Zeile "STEUERUNG: ..." alle 10 Wirtschaftsrunden. Tests 811 gruen. Partie 27 gestartet 01:18. Risiko: rundenbasierte Startwerte der Wegfuehrung (STECKT_RUNDEN, NEU_ALLE) und des Raids greifen in Takten frueher.

15.11.2026 01:29 - S158 gemessen (Partie 27): schnelle Steuerung half NICHT - 167 Schleifen, Median 236,5 Takte zwischen zwei Schleifen (Partie 26: 169,5); jede Schleife dauerte laenger als WIRTSCHAFT_TAKTE, also war fast jede voll. Steuerteile allein = 47 % einer Schleife (ZEITEN-Anteile), gerechnet rund 110 Takte. Schalter bleibt (aendert nichts, solange eine Schleife laenger als 170 Takte dauert).
15.11.2026 01:29 - S159 gebaut: Kern 32 Wegpunktkette (Art 20 WEGPUNKT, 21/22 DANACH_EINHEIT/GEBAEUDE): der Kern gibt den naechsten Schritt im Takt, in dem die Einheit hoechstens 3 Felder vor dem jetzigen Wegpunkt steht, zuletzt den Angriff. Wegfuehrung: Kette nur mit den Eckpunkten (_kette_punkte, wie _naechster), Lenker liest das Laufziel im Spiel (laufx/laufy) und schickt nicht zurueck. Tests: Kern 52, Python 815, Gegenproben rot (2 Kern, 3 Python). Kern 32 in Instanz 2 (Startfassung, Sicherung v31-20261115, geladen 01:29). Partie 28 gestartet 01:29. Auswerten: 'wegkette tick' im samurai_kern.log, Stehen/Laufen, Tode.

15.11.2026 01:41 - S160 FUND: Auftragsring kaputt seit Partie 26 Takt 36.547 (Lesezaehler 21.461.675 vor Schreibzaehler 4.268, gelesen 01:35) - der Kern las jeden Takt 256 alte Eintraege neu, Python fand den Ring voll; Partien 27 und 28 liefen ohne Kern-Weg (kein Durchsetzen, keine Wegpunktkette - die Messung zu Kern 32 ist wertlos). Ursache NICHT gefunden (ein Prozess, keine Threads). Kern 33: ring_heilen setzt den Lesezaehler zurueck und meldet 'LESEZAEHLER ... VOR SCHREIBZAEHLER'. Test + Gegenprobe rot.
15.11.2026 01:41 - S161 (Daniel 01:32 "allen auch diese faehigkeiten geben nicht nur assassinen"): Nahkampf-Raid wie die Assassinen - Gebaeudewerte assassinen.WERT (Daniels Rangfolge), Zeit je Gebaeudeart = Arbeit der Assassine (gebaeude_arbeit.json, sonst Median) x Gebaeudeschaden 73/Art aus der aktiven Balance (services/balance.py), Arbeiter nur mitnehmen bis ARBEITER_MIT = 2 Felder. Tests 818, Gegenproben rot (3). Kern 33 geladen 01:40, Partie 29 gestartet 01:40. OFFEN fuer Daniel: 19.10. 17:58 'Bauern am Lagerfeuer zuerst' (Raid) gegen 19.10. 'nie aktiv jagen, nur mitnehmen' (Assassinen) - jetzt gilt fuer den Raid die Assassinen-Regel.

15.11.2026 01:45 - S161 gemessen (Partie 29, Kern 33): Ring bei Takt 3 geheilt, danach 0 festgefahrene Takte, 255 Wegpunkt-Schritte des Kerns. Speertraeger 288x Gebaeude / 12x Arbeiter als Ziel (Partie 26: 0/428); Speer+Schwert: Gebaeude (107) 11 % ihrer Takte (vorher 0 %), stehen 17 % (vorher 27-37 %), Raid neu/tot 9/0, zerstoert 32. Neue gegnerische Gebaeude: 37 waehrend der Partie gesehen, 34 wurden Ziel, Median 0 Takte (nicht gemessen: ob die NAECHSTE Einheit wechselt). Assassinen stehen 79 % ihrer Takte: 'LORD WARTET: Raiden geht vor - 9 Assassinen, 2 lohnende Raid-Plaetze' (Daniels Regel 17.10.) - 7 ohne Aufgabe; Grund in UNIT-Zeilen all_targets_dangerous/wait_safe_place. Schlussangriff aller Einheiten auf den Lord: gibt es nicht (nur Assassinen-Lordtrupp). Wartet auf Daniels Entscheidung, wann der Schlussangriff beginnt.

15.11.2026 01:55 - S162 (Daniel 01:50 "ich will den gegnerischen lord so schnell und erbarmungslos wie moeglich killen"; Bild: zwei Hopfenfarmen nie angegriffen; 5.000 Gold uebrig, 70 Jaegerhuetten, Truppen 14-16 - gemessen im Lageprotokoll Partie 29): (1) Hopfenfarm 31 und Art 10 fehlten seit S161 in der Wertetabelle (meine Regression) - eingetragen (70, 40, aus dem Verhaeltnis der alten Raid-Tabelle); Test: jede Art aus raids.WERT bleibt Ziel. (2) Ursache kein Lord-Angriff: mit ohne_angriff/Feldzug setzt der Lenker trupp.lord_aus = True. Neu: Schalter lord_sofort (Standard ja) - Assassinen auf den Lord sobald die Rechnung reicht (LORD_SPAETESTENS 0), Nachwerben fuer den Lord-Bedarf trotz wartender Assassinen, Raid-Nahkaempfer gehen mit (nahkampf.lord). Lord-Sperre bis Takt 9.600 bleibt. Tests 820, Gegenprobe rot. NICHT gebaut: Ablenkung durch Fernkaempfer, Gold allgemein ins Heer statt Jaeger (nur Assassinen fuer den Lord). Partie 30 gestartet 01:55.

15.11.2026 01:57 - S163 (Daniel 01:55, Bilder: Ochsenjoche nicht direkt am Steinhaufen, Eisenminen-Platz frei, keine Waffenwirtschaft, Einheiten nicht ab Takt 1): Waffenwirtschaft ist per Aufstellung aus (START-BEFEHL produktion=nein). Takt 1: Lenker hob die Pause vor seiner ersten Runde auf, erste Runde fertig bei Takt 677 (Partie 30) - jetzt bleibt das Spiel angehalten, bis die erste Runde ihre Befehle gegeben hat (start_pause, Zeile 'START: erste Runde fertig'). OFFEN: Ochsenjoch-Platz am Steinhaufen, Eisenmine, Ablenkung durch Fernkaempfer, Gold ins Heer statt Jaegerhuetten.

15.11.2026 02:03 - S164 (Daniel 01:59 "nimm jetzt den offenen spielstand und toete den gegnerischen lord ohne neustart"; 02:00 "4,2k gold aber er rekrutiert nicht"): Werkzeug tools/experiments/lord_toeten.py auf Partie 30 (ohne Neustart): 21 Kaempfer im Kern freigegeben, alle auf den Lord, mit dem Gold 29 Assassinen geworben (4.257 -> 2.857 Gold). Lord 239: 71.567 Leben bei Takt 40.042, verschwunden bei Takt 40.863; Gegenprobe 02:03: Spiel over=1, einziger Lord auf dem Feld ist unserer (150.000 Leben) - der gegnerische Lord ist tot. Beleg: data/research/lord_toeten_20261115_020211.txt. Zwei Startfehler im Werkzeug (falscher Name SPIEL; Ring voll, weil im Stand 256 Freigaben) behoben, bevor ein Befehl ans Spiel ging. Dazu: Lagerplatz 10 aus raids.WERT und assassinen.WERT (S162 hatte ihn uebernommen - meine Regression), UNZERSTOERBAR = {10, 21}, Test + Gegenprobe rot. Tests 821.

15.11.2026 02:07 - S165 (Daniel 02:04 "bau ein, dass der lenker das gold selbst ins heer steckt; dann die restlichen kleinen, dann direkt partie"): Heer aus dem Ueberschuss - je Wirtschaftsrunde wird Gold ueber Ruecklage + HEER_GOLD_RAND (150) zu Assassinen, so viele wie Bauern am Feuer (Tor BESTELLUNG.darf("raid"), Schalter heer_ueberschuss); Wachtest Rekrutierstellen 9 -> 10. Ochsenjoch: weitere Joche so nah wie moeglich am Steinhaufen des Bruchs (verbund) statt am Bruch - ohne Test (der Ertragsplaner hat keine). Eisenmine NICHT gebaut: haengt an der Waffenkette (produktion=nein in raid_wirkung_pp). Tests 821. Partie 31 gestartet 02:07. Pruefen: 'START: erste Runde fertig', 'HEER AUS DEM UEBERSCHUSS', Lord-Angriffe, Joch-Abstand zum Haufen.

15.11.2026 02:09 - Partie 31 (Daniel 02:08 "warum ist es jetzt so viel schlechter? die speertraeger haben nur gewartet, einer wechselte zu einem Ochsen statt dem Steinbruch"): gemessen - (1) S163 wirkt NICHT: 'START: erste Runde fertig bei Takt 676', eine fruehere Stelle hebt die Pause schon auf (Kandidaten erstes_spiel Zeilen ~141/220/278) - offen. (2) Speertraeger: 272x Gebaeude-Ziel, davon 92x 'better_value_on_path' mit Kleinstunterschieden ('0.0014 statt 0.0013 Wert je Takt'); Gebaeudeschaden 10 macht jeden Wert je Takt winzig, sie springen zwischen Ochsenjoch (4), Steinbruch (20), Farmen. Naechster Schritt: echten Gebaeudeschaden der Speertraeger in den Lageprotokollen 29/31 messen (Lebensverlust je Takt bei Zustand 107), dann ihre Rolle festlegen.

15.11.2026 02:09 - Daniel 02:09 "warum wird nicht stein verkauft um mehr assassinen zu kaufen?": Partie 31 Takt 25.628 Stein 88 im Lager, in der Partie 1x Stein verkauft. Verkauf nur jede 3. Wirtschaftsrunde; gezielt fuer Assassinen nur bei gold_bremst (Gold reicht nicht fuer den naechsten); vermutlich zweite Stein-Ruecklage (stein_reserve des Planers) - nicht geprueft. Vorschlag: Stein ueber dem gemessenen Baubedarf verkaufen, sobald Assassinen fuer Lord/Heer gekauft werden koennen. Reihenfolge offen bei Daniel: Takt 1, Speertraeger-Rolle, Steinverkauf.

15.11.2026 02:11 - S166 (Daniel 02:09 "start ab takt 1, besseres raiden direkt angreifen"): Ursache Takt 676: gefecht_starten hebt die Pause beim Gefechtsstart auf (Daniel 22:52-23:13 "ohne Pausen") - S163 (Start-Pause) griff nie, zurueckgenommen. Neu erster_angriff(): direkt nach dem Gefechtsstart greift jeder Nahkaempfer der Starttruppe das naechste gegnerische Gebaeude mit Wert an (nie Lager/Steinhaufen), ueber eine Wegfuehrung (test_wegfuehrung_sperre), ohne Pause; Zeile 'ERSTER ANGRIFF bei Takt ...'. Tests 821. Partie 32 gestartet. OFFEN: Speertraeger springen zwischen Zielen mit Kleinstunterschieden; Steinverkauf fuer Assassinen.

15.11.2026 02:14 - Partie 32 (Lenker allein, ohne Eingriff): SIEG bei Takt 27.586 - 'Lord von Spieler 2 getoetet durch Spieler 1'. Zwei Lord-Angriffe (5, dann 9 Assassinen; der erste brachte den Lord auf 114.300), Heer aus dem Ueberschuss lief (je Runde 2-3 Assassinen, 36 Assassinen neu in der Partie), Raid neu/tot 39/9, zerstoert 17. ERSTER ANGRIFF wirkte NICHT: 'ERSTER ANGRIFF: 1 Ziele, 0 Nahkaempfer' - beim Gefechtsstart sieht das Lagebild die Starttruppe noch nicht (oder nicht als eigene); offen.

### S167 – Erster Angriff nimmt jede Welle der Starttruppe (15.11.2026 11:41)
- Befund Partie 32: erster_angriff lief bei Takt 149, die Starttruppe war noch nicht da ("1 Ziele, 0 Nahkaempfer"); Lagebild Takt 673/1120: Speertraeger 330-336 standen am Bergfried, erst ab Takt 1357 unterwegs.
- Umbau: erster_angriff(wann) nach Gefechtsstart, nach den ersten Baubefehlen, nach dem Werben und am Ende der Eroeffnung; Ziele aus NahkampfRaid (derselben Rechnung wie der Raid), Befehle ueber Wegfuehrung + Kern; erster_angriff_uebergeben gibt Ziele und Kern an den Raid. Test tests/test_raid_kern_lenker.py (Negativlauf rot).
- Partie 33 (Instanz 2, per Skript gestartet - Daniel 11:31: nie wieder per Skript): "ERSTER ANGRIFF nach dem Werben bei Takt 623: 7 neue Nahkaempfer", SIEG bei Takt 24316 (Partie 32: 27586), Nahkampf-Raid 38 Gebaeude zerstoert.

### S168 – Ochsenjoch am Steinhaufen mit einem freien Feld (15.11.2026 11:41)
- Daniel 11:29: "die Ochsenjoche sollten dort, wo die Steinablage ist, und im besten Fall mit einem Abstand". Gemessen Partie 33: 9 von 11 Jochen links am Bruch, 9 Felder vom Haufen; 2 direkt am Haufen.
- Gemessen 60 Lageprotokolle, 240 Steinbrueche, alle vier Kartenviertel: Haufen immer bei Bruch + (7, 2).
- Umbau: macro/joch.py (eine Stelle), baue_schnell(frei_von=...), baue_joch; alle Jochbauten im Spiel (Steinpflicht, kausal, Nachruesten, Ertragsplaner x2, Wirtschaft) ueber die Regel. Unveraendert: die vier festen V14-Jochplaetze (im Volltest 145/144 Steine). Test tests/test_joch.py (zwei Negativlaeufe rot). Nicht im Spiel geprueft.

### S169 – Spielstart: Wissensdatenbank und Startsperre (15.11.2026 11:54)
- Daniel 11:31/11:33/11:44: nie per Skript starten, erst fragen (Karte, Gegner, Teams, Positionen, Gold), "mach daraus keine Disziplin".
- Wissensdatenbank mit Fragebogen: VillageStudio/doku/Partie-starten.md; Verweis in Selfaware-AI-fw/CLAUDE.md, SessionStart-Hook shc_wissensstand.py (Zeile 0), Gedaechtnis.
- Startsperre execution/startsperre.py in befehl.sende: eigenesGefecht nur mit data/research/partie_freigabe.json (Daniels Wortlaut, weg=befehl), einmal gueltig. tests/test_startsperre.py, zwei Negativlaeufe rot.
- Offen: der Menueweg Kreuzzug -> Eigenes Spiel -> Lobby ist nicht gemessen.

### S170 – Alle Stein- und Eisenstellen nach Laufzeit (15.11.2026 11:54)
- Daniel 11:44: "immer erst die, wo der Laufweg am wenigsten Zeit braucht (bewusst nicht gesagt die kuerzesten), dann die weiter weg bis zur ganzen Karte", keine Anzahl.
- Gemessen Partie 33 (Paradise Plains): 62 Stein-/45 Eisenvorkommen ab 4 Feldern (dazu 462/544 mit 1-3 Feldern), genutzt 5/3; alle Brueche/Minen kamen vom Kausalmodell, die Steinpflicht bestellte rund 70-mal vergeblich auf einen belegten Platz.
- Umbau: macro/rohstoffe.py + erstes_spiel.rohstoffe_bauen: Stellen aus der platzkarte des Spiels (ganze Karte), Laufzeit = Felder auf dem Laufweg der Weg-Ebene x 24 Takte (G1), ein Bau je Wirtschaftsrunde, Arbeiter zuerst, Mine ohne Stein -> naechster Bruch; Kausal/Planer/Steinpflicht bauen 20/5 nicht mehr (Schalter rohstoffe=nein = alt); Heer laesst die Arbeiter der naechsten Stelle am Feuer. tests/test_rohstoffe.py, vier Negativlaeufe rot. Ordnen 400x400: 0,26 s. Nicht im Spiel geprueft.

### S172/S173 – SamurAI über das Menü, Partie 34 (15.11.2026 13:09)
- Instanz 2 lädt jetzt selfaware-runtime (Kopie Instanz 5, aktuelle logik.lua): Befehlsbesitzer, Übernahme vor Takt 0, Starttruppen. Partie 34 (Battle Brother_s Strife, SamurAI Schild 3 vs Kriegsfürst Schild 4, Tempo 100): baut und wirbt, pausiert bei Takt 22783.
- Gefixt: Wache Platz 16 + fester Paketpfad; Eröffnung ohne Nahrungs-Warten auf KI-Platz; Antwortzeilen beider Modulnamen; Starttruppen 5 Bogen + 7 Speer (wirkt ab nächster Partie); Joche je Bruch = kausal.ochsen_fuer(Laufweg) statt 1 (Negativlauf rot).
- OFFEN (Daniel 13:06-13:09): Assassinen "läuft nicht los" (Kernweg für Spieler 2?), berittene Bogenschützen bekommen 1 Jagdbefehl (Arbeiter 179, 100 Felder) und stehen dann, Vorstoß-Schützen springen jede Runde zum nächsten Ziel (122 Mal), Kornspeicher nicht am kleinsten Laufweg der Apfelplantagen, Wache liest das Übernahme-Signal des Moduls (uebernahme.json) noch nicht.
