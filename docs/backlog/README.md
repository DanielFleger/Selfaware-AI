# Authoritative task list

`backlog.json` is the existing upstream task/status source, moved here without
discarding IDs or history. `Backlog.html` is generated from it. The old Markdown
list is preserved at `docs/research/Backlog.md`; engineering acceptance details
are in [../BACKLOG.md](../BACKLOG.md) and link to these authoritative point IDs.

```sh
uv run selfaware run backlog fokus
uv run selfaware run backlog liste offen
uv run selfaware run backlog bauen
```

Use the original `neu`, `stand`, `rang` and `zuordnen` commands to maintain
points. Since 15.11.2026 (B-192) every point has a category and subcategory from
[kategorien.json](kategorien.json) (`neu --kategorie ... --unter ...`); finished points (built,
discarded) stay but are not counted. The 150 points of the pre-relocation backlog were added with
`einordnen einordnung_20261115.json` as B-290..B-439, their old number kept in `alte_nr`. See the backlog/focus rules in [CLAUDE.md](../../CLAUDE.md). File inventory
entries under `wo` use checkout-relative paths. Historical notes retain their
original wording; [relocations.json](../relocations.json) translates old paths.
