#ifndef __included_crawl_compile_flags_h
#define __included_crawl_compile_flags_h

#define CRAWL_CFLAGS "-O1 -ggdb -pipe -DWINMM_PLAY_SOUNDS -D__USE_MINGW_ANSI_STDIO -DUSE_SOUND -Wall -Wformat-security -Wundef -Wno-array-bounds -Wmissing-declarations -Wredundant-decls -Wno-parentheses -Wwrite-strings -Wshadow -pedantic -Wuninitialized -Iutil -I. -Irltiles -isystem contrib/install/x86_64-w64-mingw32/include -DDEBUG_TESTS -DDEBUG -DWIZARD -DASSERTS -DREGEX_PCRE -DCLUA_BINDINGS"
#define CRAWL_LDFLAGS "-O1"
#define CRAWL_HOST "x86_64-w64-mingw32"
#define CRAWL_ARCH "x86_64-w64-mingw32"

#endif

