#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p runtime/logs
cd engine/crawl/crawl-ref/source
make -j"${HOLOCRAWL_BUILD_JOBS:-8}" DEBUG=1 EXTERNAL_DEFINES=-DDEBUG_TESTS \
    CFOPTIMIZE=-O1 NO_PKGCONFIG=1 crawl.exe 2>&1 | tee ../../../../runtime/logs/build.log
