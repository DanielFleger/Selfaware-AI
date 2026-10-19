# UCP integration boundary

The runnable VillageStudio module is an **external, currently unpinned
dependency**. This checkout contains dated research copies of `logik.lua` in
`bridge/snapshots/`, but not the complete module's `init.lua`, metadata, catalogue or
instance helper. Those snapshots must not be mistaken for an installable module.

The new package defines `selfaware.game.ports.GamePort` and an offline replay
adapter. A live implementation still needs to be extracted and tested against
the actual installed module. Start with the [connector backlog](../docs/BACKLOG.md).

Before live work, capture the module revision/hash, catalogue revision/hash,
UCP version, game executable hash, map/config and selected instance/player.
Use the doctor to inventory files; it does not validate native addresses or
declare the game safe to control. Preserve the raw command channel until the
full request/result contract is understood. There must be one channel owner per
game instance across all player contexts.

The current Python sender and native helpers are in `src/selfaware/game/ucp/`.
They retain the audited behavior; relocating them does not resolve the open
connector findings.
