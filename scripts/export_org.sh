#!/usr/bin/env bash
# Optional: export editable Org source to TeX using the user's Emacs Org/ox-beamer.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v emacs >/dev/null || { echo 'Emacs missing.' >&2; exit 1; }
emacs --batch -Q \
  --eval "(require 'ox-beamer)" \
  --visit presentacion.org \
  --eval "(org-beamer-export-to-latex)"
if [[ -f presentacion.aux ]]; then
  rm -- presentacion.aux
  echo 'Removed stale presentacion.aux; it will be regenerated when compiling.'
fi
echo 'Exported presentacion.tex from presentacion.org; compile with scripts/build_pdf.sh.'
