# Adaptive warfare, castle development and capability planning

Design requested on 20 October 2026; design record B-133. Implementation and
status live in [the authoritative backlog](../backlog/backlog.json), points
B-134 through B-139, with acceptance details below. These are proposed
behaviors. The current live bot has not acquired them by adding this document.

The aim is a bot that can build a useful castle, apply sustained pressure,
defend its economy, exploit an opportunity, and change its approach when the
evidence changes. Aggression should create advantages without repeatedly
feeding isolated units; defense should preserve the ability to counterattack.

## Existing foundations and game evidence

Reuse the actual implementation before adding another controller:

| Existing component | Starting point for the new behavior |
| --- | --- |
| `micro/tasks/raids.py`, `feldzug.py`, `assassinen.py` | Harassment, covered movement, army assembly and attack groups; B-72/B-74/B-75/B-118/B-129 |
| `micro/tasks/waechter.py`, `lordwache.py`, `fallenwache.py` | Threat response, Lord protection and intrusion response; B-46/B-76/B-77 |
| `macro/kornring.py` | Observed granary protection, staged temporary/permanent defenses; B-82/B-108 |
| `services/{uebersicht,bedrohung,sicht,gefahrenzone,wege}.py`, `micro/zuweisung.py` | Threat, visibility, path and combat estimates with their existing evidence limits |
| `macro/{wirtschaft,haushalt,eroeffnung,ertragsplaner,nahrungswahl}.py` | Worker logistics, food/popularity, build economics and opening plans; B-99/B-124/B-128/B-132 |
| `execution/auftragsbuch.py`, typed ledger and coordinator | Observed completion, pending commitments and exclusive actor/resource claims |
| `learning/lernen_1v1.py`, `partie_lernen.py`, `telemetry/gold_bilanz.py` | Experiment records and current evaluation proxies; B-119/B-120/B-130 |

Paths in this table are relative to `src/selfaware/`. Existing policy classes
still perform I/O and need extraction behind `Engine`; package location alone
does not make them pure. B-97/B-98/B-99/B-100 cover that migration.

The publisher's [Crusader/Extreme manual](https://shared.steamstatic.com/store_item_assets/steam/apps/16700/manuals/manual_english.pdf?t=1686069954),
sections 5-8, identifies weapon production, mercenaries, engineers, walls,
gatehouses, stairs, towers, traps, moats, mounted defenses and siege equipment.
Its multiplayer options include Strong Walls, which changes how fortifications
can be damaged. Treat these as a capability menu to verify in the installed
ruleset. The manual does not establish a working bot command for each feature.

The [UCP personality reference](https://github.com/UnofficialCrusaderPatch/UnofficialCrusaderPatch-wiki/wiki/UCP2-AI-Personality)
provides inspiration for rallying, siege support and defense allocations; it
describes UCP2 fields, not this bot's UCP3 API. The current source audit and
[Sharky mapping](../../audit/SHARKY_ARCHITECTURE.txt) supply the manager/task
pattern. All thresholds, scoring functions and tactical combinations below
are design hypotheses to evaluate, not measured game advantages.

Local evidence is more specific: [Wissensregister](../research/Wissensregister.md)
records ruleset-dependent costs, assassin behavior and line-of-fire findings;
[Spielkarte](../research/Spielkarte.md) records command execution and placement.
`kornring.py` documents rejected wall variants, placement restrictions and the
fact that walls alone do not stop assassins. Preserve those limitations.

## States and gates

<a id="states-gates"></a>

B-134 extends B-97/B-100 with several cooperating state machines. Scope their
state to instance, player and game epoch. A castle can develop while a small
raid remains active; an alert at one mine does not require recalling every
unit. A separate emergency level can restrict any strategic posture.

| State dimension | States | Owner and effect |
| --- | --- | --- |
| Strategic posture | `ESTABLISH`, `CONTEST`, `PRESSURE`, `CONTAIN`, `PREPARE_SIEGE`, `COMMIT_ASSAULT`, `RECOVER` | Strategy selects objectives, risk limits and budget targets |
| Emergency level | `NORMAL`, `ALERT`, `CRISIS` | Defense evaluates threats to Lord, food, population and critical access; can suppress optional spending and releases requests for reinforcements |
| Economic mode | `SURVIVE`, `GROW`, `RESERVE`, `CONVERT_TO_ARMY`, `REBUILD` | Macro selects investment horizons and affordable production; no authority to spend outside the coordinator |
| Castle phase | `SURVEY`, `PROTECT_VITALS`, `SECURE_FRONT`, `ENCLOSE`, `GARRISON`, `EXTEND` | Castle planner advances observed, usable defense goals |
| Per-group task | `ASSEMBLE`, `APPROACH`, `ENGAGE`, `REPOSITION`, `DISENGAGE`, `REGROUP`, `COMPLETE` | Task/commander owns a bounded objective, actor claims, retreat path and progress check |

Use explicit transitions rather than a growing set of independent attack flags:

| Transition | Entry evidence | Exit, abort or recovery |
| --- | --- | --- |
| `ESTABLISH -> CONTEST` | Food/worker recovery is sustainable; a reachable economic objective and spare response force exist | Return to establishment/recovery when essential logistics fail |
| `CONTEST -> PRESSURE` | Repeated reachable opportunities; raid reinforcement and escape routes are affordable | Disengage threatened groups; change objective when defenders adapt |
| `PRESSURE -> CONTAIN` | Enemy exits/resource routes can be covered without exposing home or splitting too thinly | Fall back if an exit opens, relief force arrives or upkeep exceeds denial value |
| Any normal posture `-> PREPARE_SIEGE` | Valuable fortified target; direct attack gate fails; a supported siege method has a complete plan | Abort if prerequisites, home coverage or protected staging fail |
| `PREPARE_SIEGE -> COMMIT_ASSAULT` | Breach/access is observed, assault force assembled, reserves held, target legal and advantage sufficient | Stop issuing fresh assault orders when access closes or loss/coverage gates fail; reconcile units already engaged |
| Any posture `-> RECOVER` | Loss of food/production, excessive attrition or severe structural damage | Leave only after recovery indicators remain stable; do not oscillate on a single good sample |
| `NORMAL/ALERT -> CRISIS` | Current evidence of imminent critical loss, including a credible route to the Lord | Respond immediately; exit after a configurable quiet period and restored coverage |

Every planned action and posture change passes named gates. A gate returns
`PASS`, `FAIL` or `UNKNOWN`, a stable reason code, observed values, thresholds,
source snapshot IDs, evidence age and model/ruleset version. Unknown enemy
strength is not zero. Unknown prerequisites cannot enable a new capability.

| Gate | Question and required evidence |
| --- | --- |
| Session/coherence | Is this the same player/epoch, with a coherent fresh sample and valid entity UIDs? Invalid input prevents submission |
| Observability | Which enemy facts are observed, remembered or unknown under the match's observation profile? Age and uncertainty must follow remembered facts |
| Rules/capability | Is the objective allowed, and is this exact operation verified for the deployed game/module/settings? |
| Survival reserve | After existing commitments and this allocation, can food recovery, emergency recruitment and essential repair still be funded? |
| Home coverage | Can the retained force reach and handle the credible home threats before critical damage? Include travel time and multiple fronts |
| Local advantage | Is a conservative, composition/terrain-aware estimate sufficient for the objective and permitted losses? Raw unit count alone is insufficient |
| Route/access | Is there a usable approach, target access and fallback route for these unit types? Recheck after wall/gate/terrain changes |
| Readiness | Are the required units, weapons, staff and staging positions actually ready? A queued recruit/build receipt does not satisfy this gate |
| Opportunity | Will the expected gain arrive within the relevant horizon after travel, losses and diverted labor? |
| Hazard | Do fire, exposure, congestion and likely reinforcement paths fit the risk budget? Unknown propagation/range cannot establish safety |
| Commitment/progress | Is a conflicting order pending, has this target been attempted, and is observable progress occurring? |
| Stability | Has entry evidence persisted, has the minimum dwell/cooldown elapsed, and is the exit threshold distinct from entry? Emergency entry bypasses normal dwell |

Use game ticks for dwell, quiet periods and deadlines; an epoch reset clears
them. Specify separate entry/exit thresholds and a maximum objective duration.
Tie-break equal candidates deterministically. Keep the current target while it
remains adequate, but let a critical event interrupt the normal reassessment
cadence. Thresholds belong to a versioned experiment profile; uncalibrated
numbers must not become silent live defaults.

For example, a raid may enter only when capability, route, spare force,
survival reserve and home coverage all pass. A failed readiness gate requests
assembly; an unknown route requests better information or a known safe
alternative. If food recovery fails, reduce optional pressure and propose
recovery spending. If Lord safety becomes critical, request cancellation or
transfer of eligible tasks before allocating their units to defense. Pending
actions retain their reservations until reconciliation; a posture change does
not cancel a command already in the game.

## Aggressive repertoire

<a id="aggression"></a>

B-137 extends B-98/B-118/B-129. Each task declares its objective, minimum viable
group, unit roles, maximum commitments, progress condition and exit condition.
Support units count as part of the task's cost and claims.

| Idea | Decision gate and execution concept | Success evidence / disengagement |
| --- | --- | --- |
| Sustained economic harassment | Rotate small covered groups onto exposed production or worker routes; keep a replenishment budget | Production/route denial observed; leave when defenders erase the local advantage |
| Two-axis pressure | Send a bounded diversion while another group attacks a different reachable objective; budget both together | Defender displacement and second objective progress; abort if the split compromises either group's escape or home coverage |
| Counterattack after a failed enemy wave | Detect actual enemy losses and surviving spare force; choose a short objective before reinforcements arrive | Valuable target removed or position gained; return before the measured opportunity closes |
| Protected fire raid | Couple the existing slave/cover concept to fire-risk, route and retreat gates | Damage/denial compared with own losses and hazards; do not infer value from an ignition acknowledgement |
| Assassin infiltration | Use the measured detection/climbing model and target access; stage a sufficient group | Target access and damage observed; abort on exposure, blocked access or changed garrison |
| Resource containment | Patrol selected enemy production approaches instead of blindly walking into the keep | Economic activity denied at acceptable attrition; change lanes when bypassed |
| Siege battery with screen | Plan verified engine/staff/ammunition prerequisites, protected staging and a reserve against sorties | Fortification degradation and observed access; suspend when crews, supply or screening fail |
| Breach exploitation | Reserve an assault group and ranged support; commit only after a usable breach is observed | Group enters intended route and advances; replan immediately when the breach closes |
| Relief interception | Attack a vulnerable reinforcement route while another group maintains pressure | Reinforcements delayed/defeated without a losing pursuit; release task if the route becomes unsafe |
| Feigned withdrawal | Explore a bounded retreat-to-cover followed by a counterattack only when pursuit is observed | Enemy separation actually occurs; do not assume the opponent follows or sacrifice the retreating group |

Target value should include future output denied, travel time, exposure,
rebuild cost and opportunity elsewhere. Repeated low-value rebuilding must not
inflate a damage proxy indefinitely. Preserve an option to rotate out a weak
group and reinforce another; sustained pressure does not require every unit
to attack continuously. Do not initiate an all-in just because the economy
has failed; the assault and objective legality gates still apply.

## Defensive repertoire

<a id="defense"></a>

B-138 extends B-46/B-77/B-82/B-108 and the B-98 ownership work.

| Idea | Trigger and allocation | Boundary |
| --- | --- | --- |
| Vital asset defense | Prioritize Lord, food storage, recovery production and critical routes by consequence and time-to-loss | Protect the actual threatened asset; do not order the entire army home for a harmless scout |
| Layered anti-infiltration | Combine existing guards, granary protection and traps with access/detection evidence | Track consumed defenses and alternate entry routes; walls alone do not establish assassin exclusion |
| Ranged defense with melee screen | Assign reachable, supplied firing positions and a response group covering their approaches | Verify stairs/access, firing effectiveness and evacuation; a tower without usable defenders is incomplete |
| Mobile reserve | Keep a response force able to reach several fronts, with a defined maximum pursuit distance/time | Reserve size follows credible threats and travel time; it is not an unconditional permanent army tax |
| Choke and fallback defense | Hold favorable terrain while preserving a route to a protected rally point | Re-evaluate flank access and congestion; withdraw before losing the fallback route |
| Counter-siege sortie | Use spare mobile units against exposed siege support or engines | Require a return route and positive expected trade; do not chase into the main enemy force |
| Fire response | Detect actual spread and threatened essentials; prioritize verified firefighting access/capacity and relocation of combat groups | Any isolation/demolition tactic needs supported commands and measured consequences; never remove critical cover blindly |
| Breach response | Mark the lost sector, move an eligible reserve and protect the inner fallback while proposing restoration | Enemy proximity may forbid building; contain first and retry only when placement conditions change |
| Distributed industry defense | Escort or relocate exposed critical production according to route risk and replacement time | Avoid enclosing the keep while silently losing every worker route |
| Recover then resume pressure | Restore essential output, replace critical losses, reopen routes and reassess offensive opportunities | Recovery ends from observed conditions; the bot must not remain permanently passive |

## Castle development

<a id="castle"></a>

B-135 extends B-54/B-82/B-99/B-108. Represent a castle as zones, corridors,
defense sectors and dependent goals, fitted to the map and current economy.
An AIV can seed candidate geometry; verify it against current placement and
logistics rather than assuming the entire template is usable.

| Phase | Deliverable and dependency | Advance only when observed |
| --- | --- | --- |
| `SURVEY` | Keep and vital assets, approach sectors, terrain, buildable areas, production land, worker/army corridors, rally and fallback positions | A feasible plan preserves access between required endpoints |
| `PROTECT_VITALS` | Affordable protection for food/Lord and minimum recovery economy; adapt the existing granary ring | Protected assets remain operational and required entry routes work |
| `SECURE_FRONT` | Highest-risk sector first, with temporary defenses only where appropriate and affordable | Complete useful segments and an assigned response group exist |
| `ENCLOSE` | Connected wall/gate goals with reserved entrances, construction space and later expansion corridors | Segment state, access and ownership are confirmed; no false completion from queued orders |
| `GARRISON` | Access structures, staffed firing positions, ammunition/crew needs and reserve routes | Defenders can reach positions, act effectively and withdraw |
| `EXTEND` | Additional layers, protected industry, advanced defenses or a forward position | Marginal defense value exceeds investment cost without starving production or army replacement |

The planner must reserve footprints and corridor constraints alongside full
costs, available workers and production capacity. Those reservation dimensions
are future extensions to the current resource/actor allocator, not existing
`Intent` guarantees. Never spend the same stone on wall completion and trade,
or the same gold on recruitment and recovery. B-132's army budget is a useful
policy input, not a second authority over the shared balance.

Score candidate layouts by protected value, coverage, approach control,
construction time, upkeep and worker detour. Penalize blocked granary/stockpile
entrances, unstaffable towers, broken stairs, trapped units, dead production
land and excessive perimeter. Preserve scarce farm sites and transport routes.
Prefer a usable partial defense over a large unfinished perimeter.

Handle destruction as a graph change: invalidate affected routes and sectors,
reassess coverage, and propose repair/rebuild only when legal and affordable.
Compare repair and replacement with their measured costs, downtime and cover
loss. Gatehouse capture, blocked openings and enemy occupation can invalidate
the geometry without a building disappearing. Recheck ownership and access.

Record placement rejection reasons and conditions. Enemy proximity, occupied
tiles and insufficient resources have different recovery paths; an identical
rejected placement every tick wastes command capacity. Do not exploit the
known zero-stone wall behavior documented in `kornring.py`.

## Capabilities and technology choices

<a id="capabilities"></a>

B-136 extends B-95/B-115/B-128. Model technology as a graph of available
production, staffing, equipment, construction and control capabilities for the
installed Crusader ruleset. Do not introduce an assumed SC2 research tree.
Separate game availability from bot command support and policy authorization.

For each logical capability record: executable/UCP/module/balance/settings
fingerprints, mapper/type identifiers resolved by the adapter, prerequisites,
resource/worker/staff/space costs, observation requirements, supported
operations, evidence references and observed postconditions. Evidence levels
are `SOURCE_KNOWN`, `OFFLINE_CHECKED`, `LIVE_CHECKED`, with a separate enabled
flag. A source enum alone does not enable an operation. Evidence is valid only
for its recorded scope; relevant deployment changes require revalidation.

Capability families for experiments include weapon/armor chains and barracks,
mercenaries, mounted units, engineer-supported engines, defensive structures,
traps/moats, fire systems and popularity/production support. Validate each
operation independently; a build command does not prove staffing, targeting,
capture, repair or removal works.

| Planning option | Decision to investigate | Required proof before policy use |
| --- | --- | --- |
| Produce weapons or buy/recruit | Compare complete chains, trade and mercenary reinforcement at the actual deadline | Current prices/costs, staffing, delivery, storage and recruitment postconditions |
| Add production capacity | Expand the bottleneck rather than every producer equally | Input supply, worker access, productive occupancy and observed output |
| Change army composition | Choose counters from observed enemy roles, terrain and measured combat estimates | Available equipment/recruits, assembly time and viable group behavior |
| Add mounted response | Evaluate a faster reserve or raid group against its entire setup cost | Current unit prerequisites, travel performance and controlled retreat |
| Add siege capacity | Compare supported breach methods with bypass/containment and reinforcement alternatives | Engine creation, crews, targeting, supply, effect and actual access; respect Strong Walls when enabled |
| Improve fortifications | Compare useful coverage and response time against extra field units | Placement, ownership, access, staffing and measured durability/effect |
| Add fire/trap/moat defenses | Fit a specific approach and enemy threat to the supported defense | Placement/activation, consumed state, friendly access, hazard and reset behavior |
| Invest in food/ale/religion/fear policies | Compare sustained population/production effects and opportunity cost under current rules | Full chain, staffing, popularity/productivity observations and recovery from shortages |

At an investment decision, propose a feasible prerequisite bundle with a
deadline and explanation. Compare time-to-use, future output, lost work,
recruitment delay and emergency reserve. A building already paid for is a sunk
cost; a destroyed prerequisite can make continuing its chain a poor choice.
Use a rolling horizon when match end is unknown. Capabilities specific to an
edition or mode require that mode's explicit evidence and configuration.

## Integration and decision records

These proposed components fit the existing boundaries; their names below are
implementation destinations, not files already delivered:

| Responsibility | Suggested home |
| --- | --- |
| Typed derived observations: threats, routes, coverage, availability | `services/` plus versioned domain contracts |
| Strategic posture, objective selection and gate evaluation | `strategy/` |
| Per-group aggressive/defensive tasks and progress handling | `micro/tasks/` |
| Castle goals, prerequisites and production/budget proposals | `macro/` |
| Capability lookup and native command/effect verification | `game/` adapter and `crates/samurai-kern/` boundary |
| Actor transfer, footprints, capacity and pending-action ownership | `coordination/` and `execution/` |
| Transition/gate traces, match attribution and evaluation | `telemetry/` and `learning/` |

The current `Snapshot.facts` accepts integers only, and snapshots lack several
needed terrain, order, staffing and uncertainty fields. Design a versioned,
immutable derived-world contract for these values. Do not smuggle mutable
objects into facts or manufacture missing observations. Add only fields that
have defined provenance, age and unavailable behavior.

First migrate one existing raid/guard pair to the common ownership boundary,
then add shadow decisions and gate traces, then one bounded behavior at a
time. Use LIVE-01/LIVE-02 and B-97/B-98/B-99 as integration dependencies. Port
contracts across the Rust boundary as needed; do not create a second writer.
An urgent defense request cannot simply steal actors with unresolved orders.

Every decision record should include session and snapshot IDs, tick, state
before/after, objective and candidate alternatives, all gate results, selected
actors/budget, risk limit, deadline, and policy/model/capability hashes. Link
proposal ID, arbitration decision, transport receipt and later effect as
separate records. Capture reasons for declined opportunities as well as orders.

## Acceptance and evaluation

<a id="evaluation"></a>

B-139 extends B-100/B-130. Before enabling a proposed behavior, exercise its
gates and state transitions against deterministic offline scenarios:

| Counterexample | Required decision |
| --- | --- |
| Profitable raid but food recovery cannot be funded | Reject optional spending; preserve recovery; explain the failed reserve gate |
| Lord threatened while a distant raid is assembling | Request eligible task release/cancellation and reallocate only after reconciliation |
| Enemy leaves sight, then an entity slot is reused | Preserve uncertainty, reject stale identity and avoid pursuit of an invented target |
| Tower built but stairs or defenders missing | Castle goal remains incomplete; do not count its intended firepower |
| Wall order acknowledged but corridor still open | Remain in the earlier phase; reconcile the observed structure and pending cost |
| Enemy closes a breach or captures a gate | Recompute access and assault readiness; stop fresh unsafe commitment |
| Threat estimate alternates around a threshold | Dwell/hysteresis prevents churn; a genuine crisis still interrupts immediately |
| New module or balance changes a capability | Require appropriately scoped evidence; do not reuse obsolete cost/effect assumptions |
| Many low-value rebuilt buildings inflate damage | Do not treat proxy growth as a win or justify unlimited attrition |
| One cheap threat tries to recall the whole army | Allocate a sufficient bounded response and retain justified pressure elsewhere |

Trace replay can validate decisions, invariants and reproducibility. It cannot
establish the outcome of a different castle or attack. Native operation probes
must precede actual-match policy comparisons. Record exact versions, settings,
map/positions, seeds where available, opponents, observation profile, code,
models and any manual intervention. Keep technically invalid runs separate.

For real policy evaluation use paired starts/side swaps, repeated maps and
held-out opponents. Change one behavior family at a time. Report actual
win/loss/objective outcomes, survival, essential-service downtime, economic
loss, time-to-useful-defense, sustained pressure, unit attrition, blocked
movement, command latency and decision churn. Cost-calibrate asset values for
the actual ruleset and distinguish temporary denial from permanent damage.
Keep training and held-out evaluation separate; publish sample counts and
uncertainty. A single high-scoring run is not proof of improvement.

After every real match follow the repository's recording, training-data and
commit/push rules. No real match or native capability probe was run for B-133.
