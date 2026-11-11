#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v pdflatex >/dev/null || { echo 'Install TeX Live first.' >&2; exit 1; }
pdflatex -interaction=nonstopmode -halt-on-error presentacion.tex
pdflatex -interaction=nonstopmode -halt-on-error presentacion.tex
printf '\nPDF ready: %s/presentacion.pdf\nOpen with: pdfpc -S presentacion.pdf\n' "$ROOT"
