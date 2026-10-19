# Native-code research captures

These are the original C decompilations and Java captures from `daten/`,
preserved byte for byte. They are research evidence tied to particular game
versions and addresses, not a portable runtime library. Original paths and
hashes are in [relocations.json](../../docs/relocations.json).

Extraction helpers are in `tools/research/`; the current Python native/file
channel implementation is in `src/selfaware/game/ucp/`. Validate addresses and
calling conventions against the actual game/module before live changes.
