#ifndef __included_crawl_compile_flags_h
#define __included_crawl_compile_flags_h

#define CRAWL_CFLAGS "-O1 -ggdb -pipe -DWINMM_PLAY_SOUNDS -D__USE_MINGW_ANSI_STDIO -DUSE_TILE -DUSE_TILE_LOCAL -DUSE_SDL -DUSE_GL -DUSE_FT -DUSE_SOUND -Wall -Wformat-security -Wundef -Wno-array-bounds -Wmissing-declarations -Wredundant-decls -Wno-parentheses -Wwrite-strings -Wshadow -pedantic -Wuninitialized -Iutil -I. -Irltiles -I../../../../.toolchain/msys64/mingw64/include/freetype2 -I../../../../.toolchain/msys64/mingw64/include/SDL2 -isystem contrib/install/x86_64-w64-mingw32/include -DDEBUG_TESTS -DDEBUG -DWIZARD -DASSERTS -DPROPORTIONAL_FONT=\"C:/Windows/Fonts/segoeui.ttf\" -DMONOSPACED_FONT=\"C:/Windows/Fonts/consola.ttf\" -DREGEX_PCRE -DCLUA_BINDINGS"
#define CRAWL_LDFLAGS "-O1"
#define CRAWL_HOST "x86_64-w64-mingw32"
#define CRAWL_ARCH "x86_64-w64-mingw32"

#endif

