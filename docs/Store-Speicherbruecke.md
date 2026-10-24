# Store boundary candidate — 2026-10-24

Status: implemented source candidate, **not a released or signed Store module**.
The working local file-based installation has not been replaced.

## Rule and counterexamples

Persistent journals and models belong to the separate external application.
The UCP module may use only its own proxied read-only resources and volatile
in-process memory. A signed Store ZIP must never extract or start a runtime.
The ordinary external launcher must not replace that signed ZIP or disable
UCP security. The unsigned review bundle is explicitly separate.

Normal case: a command crosses one pagefile-backed Windows mapping; binary
snapshots and diagnostics return in that allocation. The external application
materializes these observations under Documents/Selfaware AI. Snapshot names
such as `ucp/villagestudio/abzug/lagebild.txt` are protocol resource keys; the
game module does not open the corresponding disk paths.

Counterexamples: malformed or escaping resource names are rejected before any
snapshot write. A timed-out command has unknown outcome and is not replayed.
An unconsumed response cannot be overwritten. Save/load, disk screenshots,
dynamic DLL replacement and window commands are rejected recursively, including
nested deferred batches. A missing Store module stops production setup before
changing its configuration. A foreign unsigned ZIP cannot replace the already
installed Store module.

## Components and build

* `store-module/`: self-contained `selfaware-bridge` source and custom build.
  UCP proxies its Lua and native DLL directly from the ZIP. The Store feature
  removes the kernel log, world-snapshot and mapping-discovery disk writers.
* `store-content/`: generated `Selfaware-AI` 0.2.0 content with bridge dependency.
* `distribution/prepare_store_source.py --check`: validates generated code against
  canonical source; tactical algorithms remain shared with the local prototype.
* `distribution/package_store.py`: creates separate normal external and unsigned
  developer-review bundles. Neither Store ZIP contains Python or the application.
* `.github/workflows/selfaware-store.yml`: Windows MSVC build and boundary checks.

The official UCP 3.0.7 custom-build contract was checked in
`scripts/compilation/compile-custom.ps1`; it invokes `build.ps1 -BuildType ...
-UCP3Path ...`. Store recipes can select the top-level `store-module` and
`store-content` source locations. Maintainers build and certificate-sign modules.

## Actual checks so far

Local commands, run from repository root on Windows:

```powershell
python distribution/prepare_store_source.py --check
$env:SAI_IPC_PEER="$PWD/build/store-module-native/i686-pc-windows-gnu/release/ipc_probe.exe"
python werkzeug/speicherkanal_pruefen.py
python werkzeug/store_bridge_pruefen.py
python werkzeug/befehl_speicher_pruefen.py
python werkzeug/distribution_boundary_pruefen.py
python werkzeug/local_launcher_pruefen.py
python werkzeug/desktop_shortcut_pruefen.py
python werkzeug/befehl_kanal_pruefen.py
python werkzeug/starttruppen_pruefen.py
python werkzeug/uebernahme_pruefen.py
python werkzeug/lernbuch_pruefen.py
python werkzeug/samurai_zuordnung_pruefen.py
python werkzeug/platzkarte_antwort_pruefen.py
python werkzeug/store_package_pruefen.py
cargo test --locked --manifest-path store-module/Cargo.toml --lib --target-dir build/store-module-native
```

Result: 54 Python tests passed across those thirteen suites; 23 Rust library tests
passed. The IPC suite uses an actual 32-bit Rust subprocess and 64-bit Python,
including binary NUL/0xff bytes, process death, missing peer, request bounds,
100 sequential exchanges and rejection of an unconsumed response. The synthetic
peer is a developer test tool, not a game and not packaged in the Store module.

The isolated Instanz4 setup succeeded with `shortcut=False`; the user's running
Instanz5 game and ordinary desktop shortcut were preserved. The DLL was loaded
through UCP in the isolated copy and a fresh native-menu game passed: takeover
at tick 0 for slots 2/3, human slot 1 retained, binary snapshots returned to the
external app, both controllers constructed their economy, and lobby AI values
were restored when leaving. Evidence: `daten/store_grenze_20261024/`.
The first failed run is retained too: memory log framing lost the tick field;
the controller therefore stopped before building. A regression test now compares
framework and memory log lines including their semantic pipe separators.
The user's running game is not stopped by the test tooling.

## Open release gates

* Final packaged Windows/MSVC artifact test. First public Store-boundary CI:
  [successful run 40112436515](https://github.com/UnofficialCrusaderPatch/Selfaware-AI/actions/runs/40112436515).
* MIT licensing approved by the project owner on 2026-10-24; notices are included
  in the module, content and external application. Third-party notices remain.
* UCP maintainer review, certificate signing and Store publication.

The implementation still uses Crusader 1.41-specific engine addresses and
checked hook signatures. It is not a universal engine API, a complete reverse
engineering of Crusader, or a completed OpenSHC port. Learning means local
measured game outcomes and model updates; the Store module itself keeps no
persistent state and requires the separate local application to play SamurAI.
