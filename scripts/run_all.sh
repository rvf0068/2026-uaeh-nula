#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$ROOT/scripts/render_manim.sh"
"$ROOT/scripts/build_pdf.sh"
echo 'Ready: pdfpc -S presentacion.pdf'
