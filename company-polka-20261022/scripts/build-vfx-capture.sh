#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "$0")/.." && pwd)"
run="${1:-god-vfx-capture05}"
if [[ -e "$project_root/analysis/native/$run/capture-engine.exe" ]]; then
  echo "Capture executable exists; use a fresh run name" >&2; exit 1
fi
cd "$project_root"
"$project_root/.toolchain/msys64/mingw64/bin/python.exe" -X utf8 "$project_root/scripts/prepare-tiles-source.py"
cd "$project_root/engine/tiles-crawl/crawl-ref/source"
make -j6 TILES=y DEBUG=1 EXTERNAL_DEFINES=-DDEBUG_TESTS CFOPTIMIZE=-O1 \
  BUILD_SDL2= BUILD_SDL2IMAGE= BUILD_FREETYPE= BUILD_LIBPNG= COPY_FONTS= NO_PKGCONFIG=1 \
  FREETYPE_INCLUDE=-I../../../../.toolchain/msys64/mingw64/include/freetype2 \
  SDL2_INCLUDE=-I../../../../.toolchain/msys64/mingw64/include/SDL2 PNG_LIB="-lpng -lz" \
  MONOSPACED_FONT='C:/Windows/Fonts/consola.ttf' PROPORTIONAL_FONT='C:/Windows/Fonts/segoeui.ttf' \
  EXTRA_LIBS='-lmingw32 -lgdi32 -lwinmm -limm32 -lole32 -loleaut32 -lversion -lSDL2main -lSDL2_image -lSDL2 -lfreetype -lpng -lz -mwindows' crawl.exe

mkdir -p "$project_root/analysis/native/$run"
strip -o "$project_root/analysis/native/$run/capture-engine.exe" crawl.exe
