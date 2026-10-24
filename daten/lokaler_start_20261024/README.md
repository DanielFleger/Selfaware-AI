# Local Selfaware startup — 24 October 2026

The user requested a normal local start while official Store review is pending.
The desktop shortcut `C:\Users\danie\Desktop\Selfaware AI (lokal).lnk`
starts the separate Instanz5 copy with `--ucp-no-security`. This is an explicitly
local unsigned test setup, not a signed Store release. The base game's files,
shortcut and global UCP launch settings were not changed.

Installed module SHA256:
`69D70354398495D2DC7D16DFD603C9E2DCC2C3797721BCF0C2AE3C703A779E8A`.
This is the exact MSVC artifact of successful Windows build 40082726869,
source commit 8ae0a3677223f287ac6400efa918d353cd05cbe2.

The game automatically started the packaged watcher and two controllers in a
fresh Branching Fortunes match, selected through native menu handlers. No save,
mouse/keyboard automation, external assistant, or tactical change was used.
The test was deliberately left via the native menu; both receipts correctly
record an unverified outcome. It was not a victory/performance benchmark.

The shortcut itself was then launched. Native memory confirms main menu 41,
tick zero. The same effective profile was selected; the model file survived
byte-for-byte and the installed `gefahrenschutz.raten_laden()` read its exact
recorded values. See verification.json, receipts, console START-BEFEHL lines,
and preserved generated plans/logs. No screenshots are included.

For local play: launch **Selfaware AI (lokal)**, create a fresh custom skirmish,
and select **SamurAI** (the replaced Abbot slot). Human slots are not controlled.
Learning and receipts remain under the runtime's local AppData directory.
Official signing, Store installation and secure-mode Selfaware validation remain
external release gates; this local shortcut does not satisfy those gates.
