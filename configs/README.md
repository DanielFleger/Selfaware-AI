# Local configuration

`local.example.toml` configures the new read-only diagnostics. Copy it to
`local.toml` and fill paths on the target machine, or use
`SELFAWARE_GAME_PATH`, `SELFAWARE_VILLAGE_STUDIO_PATH` and
`SELFAWARE_MODULE_SHA256`. `SELFAWARE_MODULE_INIT_PATH` selects the deployed
module entry file; its location is deliberately not guessed. Environment
settings take precedence.

Legacy scripts retain their existing `SHC_INSTANZ`, `SHC_SPIELER` and
`SHC_PARTNER` behavior and hard-coded/sibling paths. The new configuration does
not silently retarget those scripts. Porting that behavior is tracked in the
[handoff](../docs/HANDOFF.md).
