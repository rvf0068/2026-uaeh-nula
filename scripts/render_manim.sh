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
  'GraficaDeClanes:grafica_clanes' 'SuspensionC5:suspension_c5' 'Iteradas:iteradas'
  'PrismaClanes:prisma_clanes' 'PrismaK23:prisma_k23' 'Prisma:prisma'
  'Comportamiento:comportamiento'
  'IteradasOctaedro:iteradas_octaedro' 'RealizacionSimplicial:realizacion_simplicial'
  'TopologiaGraficas:topologia_graficas'
  'Piramide:piramide'
  'Desmantelables:desmantelables' 'Dominados:dominados'
)
second_part_scenes=(
  'BettiOctaedros:betti_octaedros' 'DiscoSuspension:disco_suspension'
  'RetractoOctaedro:retracto_octaedro' 'DosEjemplosS2:dos_ejemplos_s2'
  'ColapsosS2:colapsos_s2' 'IteradasNulas:iteradas_nulas'
)
render_scenes() {
  local source_file="$1"
  local item scene slug output_file found
  local -a fps_args
  shift
  for item in "$@"; do
    scene="${item%%:*}"
    slug="${item#*:}"
    output_file="$slug"
    # Optional comma-separated class names, e.g. MANIM_ONLY=DosEjemplosS2,ColapsosS2
    if [[ -n "${MANIM_ONLY:-}" && ",${MANIM_ONLY}," != *",$scene,"* ]]; then
      continue
    fi
    fps_args=()
    if [[ "$scene" == "SuspensionC5" || "$scene" == "PrismaClanes" || "$scene" == "PrismaK23" ]]; then
      fps_args=(--fps 30)
      output_file="${slug}_${quality#-}_fps30"
    fi
    echo "==> Manim: $scene -> videos/$slug.mp4"
    # -o receives only the basename, output location is found under --media_dir.
    manim "$quality" "${fps_args[@]}" --format=mp4 --media_dir "$ROOT/.manim_media" \
       --output_file "$output_file" "$ROOT/source/$source_file" "$scene"
    found="$(find "$ROOT/.manim_media/videos/${source_file%.py}" -type f -name "$output_file.mp4" | head -n 1)"
    if [[ -z "$found" ]]; then
      echo "ERROR: Could not locate rendered MP4 for $scene" >&2
      exit 1
    fi
    cp "$found" "$ROOT/videos/$slug.mp4"
    ffmpeg -hide_banner -loglevel error -y \
      -i "$ROOT/videos/$slug.mp4" -frames:v 1 "$ROOT/posters/$slug.png"
  done
}
render_scenes manim_scenes.py "${scenes[@]}"
render_scenes segunda_parte_manim.py "${second_part_scenes[@]}"
echo 'Manim render completed; use scripts/build_pdf.sh now.'
