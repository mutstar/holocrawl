#!/usr/bin/env bash
set -euo pipefail
pacman -Sy --needed --noconfirm mingw-w64-x86_64-SDL2 mingw-w64-x86_64-SDL2_image mingw-w64-x86_64-freetype mingw-w64-x86_64-libpng mingw-w64-x86_64-pkgconf
