# Research data and match evidence

This is the original `daten/` corpus, preserving filenames, contents and match
identifiers. The flat corpus is retained deliberately because planners,
learning tools and analysis scripts share filename patterns and cross-run
references. Code and prose have been separated: C/Java captures moved to
`research/native/`; Markdown notes moved to `docs/research/notes/`.

Common groups:

| Pattern | Use |
| --- | --- |
| `lage_*.jsonl[.gz]`, `*_konsole.txt`, `angriff_live_*`, `ertrag_live_*` | Match observations, launch/environment evidence and action measurements |
| `start_*`, `eroeffnung_plan_*`, `baeume_*`, `rohstoffe_*`, `platzkarte_*` | Captured map inputs and reproducible opening plans |
| `ertrag_startwerte_*`, `ertrag_gelernt_*`, `kausal_modell.json` | Measured model inputs and learned state |
| `schussrate_*`, `nahkampf_raten.json`, `gebaeude_arbeit.json`, `lagen_belegt.json` | Measured combat/production model evidence |
| `arbeitsgang_*`, `stein_*`, `streitkolben_*`, other dated experiments | Raw measurements and their analyses |

`selfaware.workspace.DATA` resolves this directory for current code. New
records use the same patterns. Do not rewrite raw captures to make replay pass;
the known mixed-tick record is tracked in [DATA-01](../../docs/BACKLOG.md).
The mandatory post-match evidence rule is in [README.md](../../README.md).
The old/new path and original SHA256 of each file are recorded in
[relocations.json](../../docs/relocations.json).
