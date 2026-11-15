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

## Final Windows/MSVC package check

The exact artifacts from [Windows CI run 40115190829](https://github.com/UnofficialCrusaderPatch/Selfaware-AI/actions/runs/40115190829)
at source `c6ac85f1a977a0f59a2250a245d02510ebcf2f2d` were installed in
Instanz4 and tested on 2026-10-24. Their ZIP and installed runtime hashes are in
`daten/store_grenze_20261024/paket_ci_msvc.json`; the Store recipe stays pinned
to this tested source. The stronger external test harness is kept separately
from the packaged controller and records its own hash.

```powershell
python werkzeug/store_match_pruefen.py --start-record build/store-start-result.json --output daten/store_grenze_20261024/gefecht_ci_msvc.json
```

Passed: fresh native-menu match, takeover recorded at tick 0 for slots 2/3,
human slot 1 retained, both controller processes alive at tick 4150, and 31/30
non-start building objects counted respectively. These counts include building
objects of different kinds, not a claim that every object produces resources.
The controller logs also record recruited assassins for both players. Returned
unit/building/fire snapshots had valid headers and recorded byte counts/hashes.
Lobby assignments were restored on leaving and the legacy game IPC tree had
the same before/after file hashes. That last comparison is not a complete
filesystem-operation trace and does not rule out transient operations elsewhere.

Both external match journals recorded changed shared learning-model data and
correctly labelled the deliberately aborted match `unbestaetigt`; no victory
or measured improvement in win rate is claimed. The transcripts, new maps/plans,
compressed state histories and learning receipts are under
`daten/store_grenze_20261024/ci_msvc_daten/`. The legacy label `Instanz 1` in some
worker filenames denotes its default namespace; the actual executable path and
process identity were verified as the isolated Instanz4. Only that test game
was closed afterwards. The ordinary user shortcut was not replaced.

This was the explicitly unsigned review bundle. It proves the tested local
runtime/bridge path, not a certificate-signed Secure-Load or full tournament run.
The initial harness timeout while the startup menu was still loading is retained
in `menue_anlauf_ci.json`; the bounded menu-readiness wait was increased before
the successful run. MIT licensing was approved by the project owner; notices
are included in module, content and app, with third-party notices preserved.

## Remaining release gates

* UCP maintainer review, certificate signing and Store publication.

The implementation still uses Crusader 1.41-specific engine addresses and
checked hook signatures. It is not a universal engine API, a complete reverse
engineering of Crusader, or a completed OpenSHC port. Learning means local
measured game outcomes and model updates; the Store module itself keeps no
persistent state and requires the separate local application to play SamurAI.
