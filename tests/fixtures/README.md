# Fixture provenance

`legacy_sample.jsonl` is a **synthetic schema fixture**, not a recorded match or
performance result. It uses the existing lageprotokoll envelope with a reduced
column header. Unit `zieluid` identifies a target, not the unit itself; the
decoder therefore leaves each unit's own UID unknown. Building UIDs are known.

Recorded `.jsonl.gz` traces in `daten/` can be inspected with the same CLI.
Malformed or incoherent records fail with their filename and line number.
