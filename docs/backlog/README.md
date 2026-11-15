# Backlog

The backlog is the **GitHub issues** of this repository:
https://github.com/DanielFleger/Selfaware-AI/issues (Daniel 15.11.2026: one list, reachable from anywhere and from every session).

- `kategorien.json` defines the labels: one category and one `Category: Subcategory` per issue.
- State: open issue = open; labels `in Arbeit`, `zurückgestellt`; closed as completed = built; closed as not planned = discarded.
- `Fokus` = what is being worked on now; `Impact: hoch` = the highest-impact issues, the only ones to work on (Daniel 15.11.2026 19:53);
  the label is set only with Daniel's yes.
- The former `backlog.json` (B-1 … B-442) was migrated on 15.11.2026; each issue title starts with its old B-number.
  The file itself remains in the git history (last version: commit before the migration).

```sh
uv run selfaware run backlog fokus
uv run selfaware run backlog liste
uv run selfaware run backlog neu --titel "..." --kategorie Kampf --unter Lord --herkunft "..."
uv run selfaware run backlog stand #123 gebaut --commit abc1234
uv run selfaware run backlog pruefen
```
