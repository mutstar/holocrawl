$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot
$engine = Join-Path $root 'engine/upstream/crawl-ref/source'
$run = Join-Path $root 'analysis/native-facilities94'
New-Item -ItemType Directory -Path $run -ErrorAction Stop | Out-Null
$sourceFile = Join-Path $engine 'holo34-city.cc'
$original = Join-Path $run 'holo34-city.original.cc'
$candidate = Join-Path $run 'holo34-city.review94.cc'
Copy-Item -LiteralPath $sourceFile -Destination $original
$code = Get-Content -LiteralPath $sourceFile -Raw
$anchor = '    int rolls = 0, placements = 0, first_floor_placements = 0;'
if ($code.IndexOf($anchor) -lt 0) { throw 'Exporter insertion point missing' }
$branch = @'
    // Isolated94 artwork export only. Ordinary play and its50% schedule are
    // untouched; the review process explicitly chooses one facility per map.
    if (const char *name = std::getenv("HOLOCRAWL_CITY_FACILITY_REVIEW94")) {
        const char *seed_text = std::getenv("HOLOCRAWL_CITY_FACILITY_SEED94");
        check(seed_text && *seed_text, "Facility review needs a seed");
        const std::string seed_string(seed_text);
        check(seed_string.find_first_not_of("0123456789") == std::string::npos,
              "Invalid facility review seed");
        int chosen = -1;
        for (int i = 0; i < facility_count; ++i)
            if (std::string(name) == facilities[i].id) chosen = i;
        check(chosen >= 0, "Unknown review facility");
        const uint64_t seed = std::stoull(seed_string);
        rng::seed(seed);
        init_level_connectivity();
        you.game_seed = seed;
        you.where_are_you = BRANCH_DUNGEON;
        you.depth = 1;
        std::string review_plan(city_floors, '-');
        review_plan[0] = 'A' + chosen;
        you.props[plan_key] = review_plan;
        check(builder(true), "Facility review generation failed");
        check(env.properties[facility_key].get_int() == chosen,
              "Review facility mismatch");
        check(dgn_count_disconnected_zones(false) == 1,
              "Facility review floor disconnected");
        export_native_floor(output_directory, seed, 1);
        std::ostringstream report;
        report << "{\"status\":\"passed\",\"seed\":" << seed
               << ",\"nativeFloors\":1,\"depth\":1,\"connected\":true,\"facility\":\""
               << facilities[chosen].id << "\",\"forcedArtReview\":true}";
        std::ofstream file(output_directory + "/validation.json");
        check(bool(file), "Cannot write facility review report");
        file << report.str() << '\n';
        return report.str();
    }
'@
$code = $code.Replace($anchor, $branch + "`n" + $anchor)
[IO.File]::WriteAllText($candidate, $code)
$exe = Join-Path $engine 'crawl.exe'
$backupExe = Join-Path $run 'crawl-art84.original.exe'
$hash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
$compiler = 'C:/Users/IN/Documents/ChatGPT/Game/company-checkpoint-20261019/.toolchain/msys64/usr/bin/bash.exe'
try {
    Copy-Item -LiteralPath $candidate -Destination $sourceFile
    Move-Item -LiteralPath $exe -Destination $backupExe
    $env:MSYSTEM='MINGW64'; $env:CHERE_INVOKING='1'; $env:HOLOCRAWL_CITY_SOURCE=$engine
    & $compiler -lc 'cd "$(cygpath -u "$HOLOCRAWL_CITY_SOURCE")" && make -j8 TILES=1 DEBUG=1 CFOPTIMIZE=-O1 NO_PKGCONFIG=1 EXTERNAL_DEFINES=-DDEBUG_TESTS crawl.exe' *> (Join-Path $run 'build.log')
    if ($LASTEXITCODE -ne 0) { throw "Facility preview build failed: $LASTEXITCODE" }
    Move-Item -LiteralPath $exe -Destination (Join-Path $run 'crawl-facilities94.exe')
} finally {
    Copy-Item -LiteralPath $original -Destination $sourceFile
    (Get-Item -LiteralPath $sourceFile).LastWriteTime=Get-Date
    if (Test-Path -LiteralPath $backupExe) {
        if (Test-Path -LiteralPath $exe) { Move-Item -LiteralPath $exe -Destination (Join-Path $run 'failed-build.exe') }
        Move-Item -LiteralPath $backupExe -Destination $exe
    }
    if ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -ne $hash) { throw 'Original executable restoration mismatch' }
}
Write-Output 'Built isolated facility-art exporter; original engine source and executable restored.'
