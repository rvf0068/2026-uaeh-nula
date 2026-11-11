#!/usr/bin/env bash
# Render EVERY Manim Community scene and replace the preview MP4s/posters.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if ! command -v manim >/dev/null 2>&1; then
  echo "ERROR: 'manim' not found. Activate your Python venv first." >&2
  exit 1
fi
mkdir -p videos posters
quality="${MANIM_QUALITY:--ql}" # -ql for quick preview, -qh for high quality
scenes=(
  'Intro:intro' 'Graficas:graficas' 'Completas:completas' 'Clanes:clanes'
  'GraficaDeClanes:grafica_clanes' 'Ejemplo:ejemplo' 'Iteradas:iteradas'
  'Prisma:prisma' 'SuspensionC5:suspension_c5' 'Comportamiento:comportamiento'
  'IteradasOctaedro:iteradas_octaedro' 'Helly:helly' 'Piramide:piramide'
  'Escalante:escalante' 'Desmantelables:desmantelables' 'Dominados:dominados'
)
for item in "${scenes[@]}"; do
  scene="${item%%:*}"
  slug="${item#*:}"
  echo "==> Manim: $scene -> videos/$slug.mp4"
  # -o receives only the basename, output location is found under --media_dir.
  manim "$quality" --format=mp4 --media_dir "$ROOT/.manim_media" \
     --output_file "$slug" "$ROOT/source/manim_scenes.py" "$scene"
  found="$(find "$ROOT/.manim_media/videos" -type f -name "$slug.mp4" | head -n 1)"
  if [[ -z "$found" ]]; then
    echo "ERROR: Could not locate rendered MP4 for $scene" >&2
    exit 1
  fi
  cp "$found" "$ROOT/videos/$slug.mp4"
  ffmpeg -hide_banner -loglevel error -y \
    -i "$ROOT/videos/$slug.mp4" -frames:v 1 "$ROOT/posters/$slug.png"
done
echo 'All 16 Manim scenes rendered; use scripts/build_pdf.sh now.'
