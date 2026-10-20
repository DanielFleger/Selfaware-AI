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

The exports are `samurai_version`, `samurai_takt`, and `samurai_einheiten`.
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
