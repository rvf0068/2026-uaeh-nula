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
echo 'Exported presentacion.tex from presentacion.org; compile with scripts/build_pdf.sh.'
