#!/usr/bin/env bash
# Commit im Zweig kern-s0 NUR wenn alles gruen ist (21.10.2026: zweimal hintereinander lief ein Commit trotz rotem Test bzw.
# roter Formatpruefung durch, weil die Pruefung mit ";" statt "&&" verkettet war). Prueft: kein neuer roter pytest-Test
# gegenueber $TEMP/rot_main.txt, ruff check + ruff format --check auf allen gestagten .py-Dateien, cargo test im Kern, wenn
# Rust-Dateien gestaged sind. Erst dann git commit -F <nachrichtendatei> und push. Jeder Fehlschlag: Abbruch mit Grund.
# Aufruf (im Arbeitsordner Selfaware-AI-kern, Dateien vorher gestaged):  bash ../Selfaware-AI/werkzeug/zweig_commit.sh <nachricht.txt> [push]
set -u
NACHRICHT="$1"
cd "$(git rev-parse --show-toplevel)" || exit 1
PY=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
RS=$(git diff --cached --name-only --diff-filter=ACM | grep '\.rs$')
if [ -n "$PY" ]; then
    ruff check $PY || { echo "ABBRUCH: ruff check rot"; exit 1; }
    ruff format --check $PY || { echo "ABBRUCH: ruff format rot (ruff format <datei>, neu stagen)"; exit 1; }
fi
if [ -n "$RS" ]; then
    (cd crates/samurai-kern && PATH="$HOME/.cargo/bin:$PATH" cargo test --target i686-pc-windows-gnu -q 2>&1 | grep -q "test result: ok") \
        || { echo "ABBRUCH: cargo test rot"; exit 1; }
fi
PYTHONPATH=src python -m pytest -q -p no:cacheprovider 2>&1 | grep -E "^(FAILED|ERROR)" | sed 's/ - .*//' | sort > "$TEMP/rot_zweig.txt"
NEU=$(comm -13 "$TEMP/rot_main.txt" "$TEMP/rot_zweig.txt")
[ -z "$NEU" ] || { echo "ABBRUCH: neue rote Tests:"; echo "$NEU"; exit 1; }
git commit -q -F "$NACHRICHT" || exit 1
git log --oneline -1
if [ "${2:-}" = "push" ]; then
    GH_TOKEN=$(gh auth token --user DanielFleger) git push -q origin "$(git branch --show-current)" || { echo "ABBRUCH: push"; exit 1; }
    echo "Server: $(GH_TOKEN=$(gh auth token --user DanielFleger) git ls-remote origin "refs/heads/$(git branch --show-current)" | cut -c1-8)"
fi
