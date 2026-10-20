# Native game core

The existing `samurai_kern` DLL from B-115 lives here. Its C ABI and package
name remain unchanged. The Python policies and offline framework live in
`src/selfaware/`; this crate is the native game boundary.

Build from the repository root on Windows with Rust and the MSVC C++ build tools:

```powershell
rustup target add i686-pc-windows-msvc
cargo build --locked --release --target i686-pc-windows-msvc --manifest-path crates/samurai-kern/Cargo.toml
```

Output: `crates/samurai-kern/target/i686-pc-windows-msvc/release/samurai_kern.dll`.
Crusader is a 32-bit process; the host's default 64-bit target is unsuitable.
CI compiles this target on Windows alongside the offline Python checks.

The exports are `samurai_version`, `samurai_takt`, `samurai_einheiten` and (since
version 2, B-145 S0) `samurai_test_fehler`. The existing C signatures are unchanged.

Version 2 (B-145 stage S0, `docs/plans/Plan_Kern.md`):

- **Tick watcher** (`src/waechter.rs`): each call is classified as new tick, pause,
  epoch change (load/new match) or no match. The core is called after every game tick
  and also while paused, so a call is not always a new tick.
- **Measurement baseline**: every 500 ticks the log gets a `waechter` line with counters,
  mean/max core time per call and wall time per tick.
- **Error catching**: `panic = "unwind"` plus `catch_unwind` at every export. A panic
  switches the core off (every export then returns -2) instead of killing the game.
  `samurai_test_fehler(0x5A4D)` triggers this deliberately as a counter-check.
- **Swap without restart**: the game keeps a loaded DLL file locked, but a copy under a
  new name in the module folder loads while the game runs:
  `{"kern": {"laden": "samurai_kern_2.dll"}}` (dispatch in
  `bridge/snapshots/logik_stand_20261020.lua`, `kernBefehl`). Way back:
  `{"kern": {"laden": "samurai_kern.dll"}}`. Measured on instance 5, 20.10.2026
  (`docs/research/Wissensregister.md` L155).

Deploying a new version: copy the DLL under a new name (`samurai_kern_<n>.dll`) into the module folder, write that
name into `ucp/villagestudio/kern_aktuell.txt` and send `{"kern": {"laden": "samurai_kern_<n>.dll"}}`. After a reload of
logik.lua or a game restart, logik.lua loads the name from `kern_aktuell.txt` (fallback `samurai_kern.dll`).

Offline checks: `cargo test --target i686-pc-windows-gnu` (or the MSVC target) runs only
the parts that do not touch game memory.
The unit-count and tick functions access fixed game addresses and must run
inside the supported game process. Do not load or call them in offline tests.
Build output and logs are ignored.

The dated Lua snapshot `bridge/snapshots/logik_stand_20261019.lua` loads
`ucp/villagestudio/samurai_kern.dll` in a game instance. Building this crate
does not deploy it or update the external VillageStudio module. Compare actual
versions, hashes and native postconditions before using a newly built DLL.
The upstream match evidence for B-115 is preserved at
`data/research/kern_live_20261019_225806.txt`; relocation/build checks are
separate from that recorded integration result.
