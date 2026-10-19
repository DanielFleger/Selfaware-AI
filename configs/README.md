# Local configuration

`local.example.toml` configures the new read-only diagnostics. Copy it to
`local.toml` and fill paths on the target machine, or use
`SELFAWARE_GAME_PATH`, `SELFAWARE_VILLAGE_STUDIO_PATH` and
`SELFAWARE_MODULE_SHA256`. `SELFAWARE_MODULE_INIT_PATH` selects the deployed
module entry file; its location is deliberately not guessed. Environment
settings take precedence.

Current-bot modules retain `SHC_INSTANZ`, `SHC_SPIELER`, `SHC_PARTNER` and the
existing Steam installation default. Their external catalogue/helpers now honor
`SELFAWARE_VILLAGE_STUDIO_PATH`, with the previous sibling `VillageStudio/`
location as the default. `SELFAWARE_WORKSPACE` selects the checkout containing
research data/assets. `SELFAWARE_STATE_DIR` overrides `var/legacy/` for process
state; every process controlling the same game must use the same directory.

TOML diagnostic settings do not retarget the existing sender. See the
[repository map](../docs/ORGANIZATION.md) for launches and state migration.
