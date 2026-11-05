#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
toolchain="$(cd "$root/../company-polka-20261022/.toolchain/msys64/mingw64" && pwd)"
"$toolchain/bin/python.exe" -X utf8 "$root/scripts/generate-god-structure.py"
cd "$root/engine/upstream/crawl-ref/source"
make -j6 TILES=y DEBUG=1 CFOPTIMIZE=-O1 EXTERNAL_DEFINES=-DVERSIONED_CACHE_DIR \
 BUILD_SDL2= BUILD_SDL2IMAGE= BUILD_SDL2MIXER= BUILD_FREETYPE= BUILD_LIBPNG= \
 COPY_FONTS= NO_PKGCONFIG=1 \
 FREETYPE_INCLUDE="-I$toolchain/include/freetype2" \
 SDL2_INCLUDE="-I$toolchain/include/SDL2" PNG_LIB='-lpng -lz' \
 MONOSPACED_FONT='C:/Windows/Fonts/consola.ttf' PROPORTIONAL_FONT='C:/Windows/Fonts/segoeui.ttf' \
 EXTRA_LIBS='-lmingw32 -lgdi32 -lwinmm -limm32 -lole32 -loleaut32 -lversion -lSDL2main -lSDL2_image -lSDL2 -lfreetype -lpng -lz -mwindows' crawl.exe
mkdir -p "$root/runtime/street01"
strip -o "$root/runtime/street01/HoloCrawl-0341-street.exe" crawl.exe


