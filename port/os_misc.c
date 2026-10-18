/* os_misc.c - intuition.library and icon.library as far as the game uses them: it closes
   the Workbench screen while it runs, reads and restores Preferences, may show an
   AutoRequest, and reads its icon's tool types at Workbench start. */
#include "amiga.h"
#include "os.h"

#include <string.h>

int16_t CloseWorkBench(void) { return 1; }               /* TRUE: closed */
int16_t OpenWorkBench(void) { return 1; }

/* Preferences: the game saves a copy and writes it back on exit; a zeroed block is a
   valid Preferences image for both. */
int16_t GetPrefs(void *prefs, int32_t size) { memset(prefs, 0, (size_t)size); return 0; }
int16_t SetPrefs(void *prefs, int32_t size, int32_t inform) { (void)prefs; (void)size; (void)inform; return 0; }

/* IntuiText: FrontPen, BackPen, DrawMode, pad, LeftEdge, TopEdge, ITextFont*, IText*, NextText* */
#pragma pack(push, 2)
struct IntuiText { uint8_t FrontPen, BackPen, DrawMode, pad; int16_t LeftEdge, TopEdge; void *Font; char *IText; struct IntuiText *Next; };
#pragma pack(pop)

int16_t AutoRequest(int32_t window, struct IntuiText *body, struct IntuiText *positive, struct IntuiText *negative,
                    int32_t pflags, int32_t nflags, int32_t width, int32_t height)
{
    (void)window; (void)negative; (void)pflags; (void)nflags; (void)width; (void)height;
    for (struct IntuiText *t = body; t; t = t->Next) platform_log("AutoRequest: %s", t->IText ? t->IText : "");
    if (positive && positive->IText) platform_log("AutoRequest button: %s", positive->IText);
    return 1;
}

/* icon.library: the game is started from the CLI here, so there is no icon. */
struct Library *IconBase;
int32_t GetDiskObject(const char *name) { (void)name; return 0; }
int16_t FreeDiskObject(int32_t object) { (void)object; return 0; }
int32_t FindToolType(int32_t types, const char *name) { (void)types; (void)name; return 0; }
