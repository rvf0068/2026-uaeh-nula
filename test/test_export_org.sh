#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="$(mktemp -d)"
trap 'rm -rf -- "$WORKDIR"' EXIT

mkdir "$WORKDIR/scripts"
cp "$ROOT/scripts/export_org.sh" "$ROOT/scripts/build_pdf.sh" "$WORKDIR/scripts/"
cat > "$WORKDIR/presentacion.org" <<'EOF'
#+TITLE: Export test
#+LATEX_CLASS: beamer
#+OPTIONS: H:2 toc:nil

** Test frame
Hello.
EOF
printf '\\relax\n\\abx@aux@refcontext{nty/global//global/global/global}\n' > "$WORKDIR/presentacion.aux"

bash "$WORKDIR/scripts/export_org.sh"
test ! -e "$WORKDIR/presentacion.aux"
if ! bash "$WORKDIR/scripts/build_pdf.sh" > "$WORKDIR/build.log" 2>&1; then
  cat "$WORKDIR/build.log" >&2
  exit 1
fi
test -s "$WORKDIR/presentacion.pdf"
