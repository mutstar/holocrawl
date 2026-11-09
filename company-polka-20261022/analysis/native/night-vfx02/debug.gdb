set pagination off
set confirm off
catch throw
set environment HOLOCRAWL_CAMPAIGN_TEST=1
set environment HOLOCRAWL_CAMPAIGN_OUTPUT=C:/Users/IN/Documents/ChatGPT/Game/HoloCrawl_HOME_2026-10-20/analysis/native/night-vfx02/debug
set environment HOLOCRAWL_INVOCATION_CAPTURE=C:/Users/IN/Documents/ChatGPT/Game/HoloCrawl_HOME_2026-10-20/analysis/native/night-vfx02/debug/shots
set environment HOLOCRAWL_NIGHT_REVIEW=C:/Users/IN/Documents/ChatGPT/Game/HoloCrawl_HOME_2026-10-20/analysis/native/night-vfx02/debug/shots
set args -dir C:/Users/IN/Documents/ChatGPT/Game/HoloCrawl_HOME_2026-10-20/engine/tiles-crawl/crawl-ref/source -rc C:/Users/IN/Documents/ChatGPT/Game/HoloCrawl_HOME_2026-10-20/analysis/native/night-vfx02/native/capture.rc -test holocrawl-campaign -no-throttle
run
bt
frame 1
info args
quit

