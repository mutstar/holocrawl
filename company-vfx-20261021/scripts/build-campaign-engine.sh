#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../engine/campaign-crawl/crawl-ref/source"
make -j8 DEBUG=1 EXTERNAL_DEFINES=-DDEBUG_TESTS CFOPTIMIZE=-O1 NO_PKGCONFIG=1 crawl.exe
