# Host tools

`windows/` contains the original PowerShell process/window tools. Their
`workspace.ps1` resolves the external VillageStudio helper from
`SELFAWARE_VILLAGE_STUDIO_PATH` or the previous sibling-project location.

`research/` contains the original AIV decoder client and Ghidra extraction
script. The decoder uses the same external-project setting. Native captures
are in `research/native/`.

Python utilities are installed under `selfaware.tools.setup`, `.analysis`,
`.checks` and `.experiments`, so imports and child processes work consistently.
Use `uv run selfaware modules` to find a tool, then `uv run selfaware run NAME`
with its original arguments. See [ORGANIZATION.md](../docs/ORGANIZATION.md).
