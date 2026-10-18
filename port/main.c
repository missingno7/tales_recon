/* main.c - the SDL3 side of the port: window, presentation, input, the game's clock (one
   tick per PAL frame), record/replay, the game thread and the OS state the emulation keeps
   (interrupt servers, Forbid).

   ducktales [--data DIR] [--log] [--wav FILE] [--headless] [--strict] [--ticks N]
             [--record FILE] [--replay FILE] [--dump DIR:FROM:EVERY] [--shot FILE.bmp:TICK ...]
   Exit status 3: a verification fault (platform_fault) happened; --strict stops at the first.
   DIR holds the two original disk images (any *.adf; mounted under their volume names,
   DT1 and DT2). docs/sdl3-port.md describes the design. */
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>

#include "amiga.h"
#include "os.h"
#include "m68k.h"

#include <setjmp.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WIDTH 320
#define HEIGHT 200
#define FRAME_NS 20031800u                          /* a PAL frame: 71051 / 3546895 Hz */

static FILE *log_file;
static volatile int forbidden, quitting, game_done;
static const struct View *current_view;
static void *servers[8][4];                         /* AddIntServer chains, per number */
static void *vectors[16];                           /* SetIntVector */
static void *input_handler;
static uint16_t joy1dat;                            /* what the game reads, per tick */
static int fire_down;
static jmp_buf game_exit;
static struct { char path[512]; uint32_t tick; } shots[32];
static int shot_count, headless, strict, failed;
static uint32_t tick, end_tick;                     /* frames since start; 0: no end */
/* Poll frames: the steps of the game's input reading. A poll starts a new one when the game
   has waited for time (Delay, WaitBOVP) since the current one began, or when it polled in the
   frame just before (a loop polling every frame while it waits for a sound). Work that spans
   frames on the 68000 - drawing, decompressing, loading - takes the port no frames, and on
   neither machine does it start a poll frame, so inputs, dumps and the end of a replay timed
   in poll frames mean the same game step on the original and on the port (docs/sdl3-port.md;
   tools/game_boot.py counts them the same way). */
static uint32_t poll_frames, polled_tick = UINT32_MAX;
static int waited;                                  /* a Delay or WaitBOVP since the last poll frame */
static uint32_t replay_end;                         /* poll frame at which a replay ends */
static Uint64 start_ns;

/* Live input, written by the main thread and taken by the game thread once per tick. */
static SDL_Mutex *input_lock;
static uint16_t live_joy;
static int live_fire;
static uint8_t key_queue[64];
static int key_head, key_tail;

/* Record/replay: every external input the game receives, in order (docs/sdl3-port.md). */
static FILE *record_file;
static struct input { uint32_t tick; char kind; uint16_t value; } *replay;   /* kind j f k */
static size_t replay_count, replay_next;
static uint16_t *seeds;
static size_t seed_count, seed_next;
static int replaying;

/* State dumps: the DATA/BSS hunk (host order, original offsets) at the first poll of every
   EVERY-th poll frame from FROM. */
static char dump_dir[512];
static uint32_t dump_from, dump_every;
extern char amiga_data_hunk[];
extern const uint32_t amiga_data_hunk_size;

uint8_t platform_font8x8[256][8];

void platform_log(const char *format, ...)
{
    va_list args;
    va_start(args, format);
    if (log_file) { vfprintf(log_file, format, args); fputc('\n', log_file); fflush(log_file); }
    va_end(args);
}

void platform_unimplemented(const char *name)
{
    static const char *seen[256];
    for (int i = 0; i < 256; i++) {
        if (seen[i] == name) return;
        if (!seen[i]) { seen[i] = name; platform_log("not implemented yet: %s", name); return; }
    }
}

const struct View *platform_view(void) { return current_view; }
void platform_set_view(const struct View *view) { current_view = view; }
void platform_forbid(int on) { forbidden = on; }

void platform_add_server(int number, void *interrupt)
{
    for (int i = 0; i < 4; i++) if (!servers[number & 7][i]) { servers[number & 7][i] = interrupt; break; }
    platform_log("AddIntServer %d", number);
}
void platform_remove_server(int number, void *interrupt)
{
    for (int i = 0; i < 4; i++) if (servers[number & 7][i] == interrupt) servers[number & 7][i] = NULL;
}
void *platform_set_vector(int number, void *interrupt)
{
    void *previous = vectors[number & 15];
    vectors[number & 15] = interrupt;
    return previous;
}
void *platform_vector(int number) { return vectors[number & 15]; }
void platform_input_handler(void *interrupt) { input_handler = interrupt; }

/* Call an interrupt's code: translated 68000 code (a code key, m68k.h) with a1 = is_Data,
   or a C function of the port. Returns d0. */
static uint32_t call_interrupt(const struct Interrupt *is, uint32_t a0)
{
    uint32_t code = (uint32_t)(uintptr_t)is->is_Code;
    if (m68k_is_code(code)) return m68k_interrupt(code, (uint32_t)(uintptr_t)is->is_Data, a0);
    return (uint32_t)((int32_t (*)(void))is->is_Code)();
}

/* Keys to the game's input handler (input.device, IND_ADDHANDLER): one InputEvent per key,
   class IECLASS_RAWKEY, the Amiga raw key code (bit 7 set on release) in ie_Code. The game
   reads ie_Code's low byte at offset 7 - the 68000's byte order - so the event is laid out
   in that view: next pointer, class, subclass, then the code's high and low byte. */
static uint8_t amiga_key(SDL_Scancode s)
{
    static const struct { SDL_Scancode s; uint8_t code; } map[] = {
        { SDL_SCANCODE_GRAVE, 0x00 }, { SDL_SCANCODE_MINUS, 0x0B }, { SDL_SCANCODE_EQUALS, 0x0C },
        { SDL_SCANCODE_BACKSLASH, 0x0D }, { SDL_SCANCODE_LEFTBRACKET, 0x1A }, { SDL_SCANCODE_RIGHTBRACKET, 0x1B },
        { SDL_SCANCODE_SEMICOLON, 0x29 }, { SDL_SCANCODE_APOSTROPHE, 0x2A }, { SDL_SCANCODE_COMMA, 0x38 },
        { SDL_SCANCODE_PERIOD, 0x39 }, { SDL_SCANCODE_SLASH, 0x3A }, { SDL_SCANCODE_SPACE, 0x40 },
        { SDL_SCANCODE_BACKSPACE, 0x41 }, { SDL_SCANCODE_TAB, 0x42 }, { SDL_SCANCODE_KP_ENTER, 0x43 },
        { SDL_SCANCODE_RETURN, 0x44 }, { SDL_SCANCODE_ESCAPE, 0x45 }, { SDL_SCANCODE_DELETE, 0x46 },
        { SDL_SCANCODE_UP, 0x4C }, { SDL_SCANCODE_DOWN, 0x4D }, { SDL_SCANCODE_RIGHT, 0x4E }, { SDL_SCANCODE_LEFT, 0x4F },
        { SDL_SCANCODE_LSHIFT, 0x60 }, { SDL_SCANCODE_RSHIFT, 0x61 }, { SDL_SCANCODE_CAPSLOCK, 0x62 },
        { SDL_SCANCODE_LCTRL, 0x63 }, { SDL_SCANCODE_LALT, 0x64 }, { SDL_SCANCODE_RALT, 0x65 },
        { SDL_SCANCODE_KP_0, 0x0F }, { SDL_SCANCODE_KP_1, 0x1D }, { SDL_SCANCODE_KP_2, 0x1E }, { SDL_SCANCODE_KP_3, 0x1F },
        { SDL_SCANCODE_KP_4, 0x2D }, { SDL_SCANCODE_KP_5, 0x2E }, { SDL_SCANCODE_KP_6, 0x2F },
        { SDL_SCANCODE_KP_7, 0x3D }, { SDL_SCANCODE_KP_8, 0x3E }, { SDL_SCANCODE_KP_9, 0x3F },
        { SDL_SCANCODE_KP_PERIOD, 0x3C }, { SDL_SCANCODE_KP_MINUS, 0x4A },
    };
    static const char rows[4][13] = { "1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm" };
    static const uint8_t row_start[4] = { 0x01, 0x10, 0x20, 0x31 };
    SDL_Keycode key = SDL_GetKeyFromScancode(s, SDL_KMOD_NONE, false);
    for (size_t i = 0; i < sizeof map / sizeof map[0]; i++) if (map[i].s == s) return map[i].code;
    if (s >= SDL_SCANCODE_F1 && s <= SDL_SCANCODE_F10) return (uint8_t)(0x50 + (s - SDL_SCANCODE_F1));
    for (int r = 0; r < 4; r++) {
        const char *at = strchr(rows[r], (int)key);
        if (key && key < 128 && at) return (uint8_t)(row_start[r] + (at - rows[r]));
    }
    return 0xFF;
}

/* Raw key code to the game's input handler: one InputEvent of class IECLASS_RAWKEY. */
static void deliver_key(uint8_t code)
{
    static uint8_t event[22];                          /* struct InputEvent, guest memory */
    static int registered;
    if (!input_handler) return;
    if (!registered) { registered = 1; m68k_memory(event, sizeof event, 0); }
    memset(event, 0, sizeof event);
    event[4] = 1;                                      /* ie_Class = IECLASS_RAWKEY */
    event[7] = code;                                   /* ie_Code, low byte (bit 7: release) */
    call_interrupt((const struct Interrupt *)input_handler, (uint32_t)(uintptr_t)event);
}

uint16_t platform_joystick(void) { return joy1dat; }
int platform_fire(void) { return fire_down; }

/* VPOSR, read only by seed_random (resident_F_4676), which stores VPOSR + game_frame_tick as
   the RNG state: bit 15 LOF (set: PAL non-interlaced frames are long frames), bit 0 V8 (the
   beam is on line 256-312), the OCS Agnus ID bits 0. The seed is therefore 0x8000 +
   game_frame_tick, plus one bit of beam position; the original's recorded seeds fit this
   (docs/sdl3-port.md). It is the one input that depends on the machine's timing, so the log
   holds the seed itself: replay returns the seed minus the game clock, record writes the sum.
   Live: V8 from where a PAL frame would be on the host clock. */
#define GAME_FRAME_TICK (*(uint32_t *)(amiga_data_hunk + 0xB1EC))   /* G_h01_B1EC */

uint16_t platform_vposr(void)
{
    uint16_t vposr = (uint16_t)(0x8000 | (SDL_GetTicksNS() % FRAME_NS * 313u / FRAME_NS >= 256));
    if (replaying) {
        if (seed_next < seed_count) vposr = (uint16_t)(seeds[seed_next++] - GAME_FRAME_TICK);
        else platform_log("replay: no seed left at poll frame %u", poll_frames);
    }
    if (record_file) fprintf(record_file, "%u seed %04x\n", poll_frames, (uint16_t)(vposr + GAME_FRAME_TICK));
    return vposr;
}

/* A verification failure (an access outside guest memory ...): logged always; with --strict
   the run ends and the program exits with status 3, so a replay test cannot pass over it. */
void platform_fault(const char *what)
{
    platform_log("FAULT at tick %u, poll frame %u: %s", tick, poll_frames, what);
    failed = 1;
    if (strict) longjmp(game_exit, 1);
}

/* Game events worth comparing with the original - the sound commands the game issues - go
   into the record log as "POLL sound HEX" lines; replay ignores them. */
void platform_event(const char *what, uint32_t value)
{
    if (record_file) fprintf(record_file, "%u %s %04x\n", poll_frames, what, value);
}

void platform_exit(int code)
{
    platform_log("game exit %d", code);
    longjmp(game_exit, 1);
}

static void apply_input(char kind, uint16_t value)
{
    if (kind == 'j' && value == joy1dat) return;
    if (kind == 'f' && (int)value == fire_down) return;
    if (record_file)
        fprintf(record_file, "%u %s %04x\n", poll_frames, kind == 'j' ? "joy" : kind == 'f' ? "fire" : "key", value);
    if (kind == 'j') joy1dat = value;
    else if (kind == 'f') fire_down = value;
    else deliver_key((uint8_t)value);
}

/* The inputs of this poll frame: the replay log, or what the main thread collected. */
static void sample_inputs(void)
{
    uint8_t keys[64];
    int count = 0;
    uint16_t joy;
    int fire;
    if (replaying) {
        while (replay_next < replay_count && replay[replay_next].tick <= poll_frames) {
            apply_input(replay[replay_next].kind, replay[replay_next].value);
            replay_next++;
        }
        return;
    }
    SDL_LockMutex(input_lock);
    joy = live_joy; fire = live_fire;
    while (key_tail != key_head) { keys[count++] = key_queue[key_tail]; key_tail = (key_tail + 1) & 63; }
    SDL_UnlockMutex(input_lock);
    apply_input('j', joy);
    apply_input('f', (uint16_t)fire);
    for (int i = 0; i < count; i++) apply_input('k', keys[i]);
}

static void render(uint32_t *pixels);

static void save_shot(const char *path)
{
    static uint32_t pixels[WIDTH * HEIGHT];
    SDL_Surface *picture;
    render(pixels);
    picture = SDL_CreateSurfaceFrom(WIDTH, HEIGHT, SDL_PIXELFORMAT_ARGB8888, pixels, WIDTH * 4);
    SDL_SaveBMP(picture, path);
    SDL_DestroySurface(picture);
}

static void dump_state(void)
{
    static int layout_written;
    if (!layout_written) {
        /* Where the guest memory lies, so pointers in the dumps can be compared through what
           they point at (an offset in the DATA hunk) instead of their host addresses. */
        char path[600];
        uint32_t arena_size;
        const void *arena = amiga_arena(&arena_size);
        FILE *layout;
        snprintf(path, sizeof path, "%s/state-layout.json", dump_dir);
        if ((layout = fopen(path, "w"))) {
            uint32_t start, size;
            fprintf(layout, "{\"data_base\": %u, \"data_size\": %u, \"arena_base\": %u, \"arena_size\": %u, \"regions\": [",
                    (uint32_t)(uintptr_t)amiga_data_hunk, amiga_data_hunk_size,
                    (uint32_t)(uintptr_t)arena, arena_size);
            for (int i = 0; m68k_region_info(i, &start, &size); i++)
                fprintf(layout, "%s[%u, %u]", i ? ", " : "", start, size);
            fputs("]}\n", layout);
            fclose(layout);
        }
        layout_written = 1;
    }
    {
        char path[600];
        FILE *data, *index;
        snprintf(path, sizeof path, "%s/state.bin", dump_dir);
        data = fopen(path, "ab");
        snprintf(path, sizeof path, "%s/state-index.jsonl", dump_dir);
        index = fopen(path, "ab");
        if (data && index) {
            long offset;
            fseek(data, 0, SEEK_END);
            offset = ftell(data);
            fwrite(amiga_data_hunk, 1, amiga_data_hunk_size, data);
            fprintf(index, "{\"poll\": %u, \"frame\": %u, \"offset\": %ld, \"size\": %u}\n",
                    poll_frames, tick, offset, amiga_data_hunk_size);
        }
        if (data) fclose(data);
        if (index) fclose(index);
    }
}

/* Called by the game's input poll (port/override/resident_F_4376.c) before it reads the
   joystick: the first poll of a frame starts a poll frame, which takes that frame's inputs and
   is a checkpoint - the state as the game is about to read its input. */
void platform_poll(void)
{
    int fresh;
    if (polled_tick == tick) return;
    fresh = waited || polled_tick + 1 == tick || poll_frames == 0;
    polled_tick = tick;
    if (!fresh) return;                             /* the same poll frame continues */
    waited = 0;
    poll_frames++;
    if (replay_end && poll_frames > replay_end) longjmp(game_exit, 1);
    sample_inputs();
    if (dump_every && poll_frames >= dump_from && (poll_frames - dump_from) % dump_every == 0) dump_state();
}

/* Screenshots and the end of the run, at tick boundaries. */
static void checkpoint(void)
{
    for (int i = 0; i < shot_count; i++)
        if (shots[i].tick == tick) save_shot(shots[i].path);
    if (end_tick && tick >= end_tick) quitting = 1;
}

/* ---- the game's clock: one tick per PAL frame (313 lines of 227 colour clocks), run on
   the game thread whenever the game waits for time (Delay, WaitBOVP). A tick runs, in
   order, what the Amiga did around a frame: Paula plays one frame of sound (its block
   interrupts run the audio driver), the VBlank servers run (game_frame_tick, colour
   cycling, the driver's channel update), and the inputs of the new frame are taken. One
   thread does all of it, so a run is a function of its recorded inputs. ---- */
static void frame(void)
{
    if (quitting) longjmp(game_exit, 1);
    paula_frame();
    if (!forbidden)
        for (int i = 0; i < 4; i++) {
            struct Interrupt *server = servers[5][i];
            if (server && server->is_Code) call_interrupt(server, 0);
        }
    tick++;
    checkpoint();
    if (!headless) {
        Uint64 due = start_ns + (Uint64)tick * FRAME_NS, now = SDL_GetTicksNS();
        if (due > now) SDL_DelayPrecise(due - now);
    }
}

/* Delay(ticks) and WaitBOVP: wait for ticks (at least one) frames. */
void platform_wait_ticks(int ticks)
{
    for (int n = ticks > 0 ? ticks : 1; n > 0; n--) frame();
    waited = 1;
}

/* One pass of a busy-wait on interrupt state (port_gen spin_waits): a frame passes, but the
   game did not wait for time itself. */
void platform_spin_frame(void) { frame(); }

/* ---- the game thread ---- */
extern int16_t _main(int32_t alen, char *aptr);

static int SDLCALL game_thread(void *user)
{
    (void)user;
    start_ns = SDL_GetTicksNS();
    if (!setjmp(game_exit))
        _main(0, "");
    game_done = 1;
    return 0;
}

/* A replay log, timed in poll frames: "POLL joy|fire|key HEX" (JOY1DAT, fire 0/1, raw key
   with bit 7 on release; taken at the first poll of that poll frame), "POLL seed HEX" (RNG
   seeds, taken in order), "POLL end"; '#' starts a comment line. --record writes the same. */
static int load_replay(const char *path)
{
    FILE *f = fopen(path, "r");
    char line[128], word[16];
    size_t capacity = 0, seed_capacity = 0;
    if (!f) return -1;
    while (fgets(line, sizeof line, f)) {
        unsigned at, value;
        if (line[0] == '#') continue;
        if (sscanf(line, "%u %15s %x", &at, word, &value) == 3) {
            if (!strcmp(word, "seed")) {
                if (seed_count == seed_capacity) seeds = realloc(seeds, (seed_capacity = seed_capacity * 2 + 16) * sizeof *seeds);
                seeds[seed_count++] = (uint16_t)value;
                continue;
            }
            if (replay_count == capacity) replay = realloc(replay, (capacity = capacity * 2 + 64) * sizeof *replay);
            if (strcmp(word, "joy") && strcmp(word, "fire") && strcmp(word, "key")) continue;   /* events */
            replay[replay_count++] = (struct input){ at, word[0] == 'j' ? 'j' : word[0] == 'f' ? 'f' : 'k', (uint16_t)value };
        } else if (sscanf(line, "%u %15s", &at, word) == 2 && !strcmp(word, "end"))
            replay_end = at;
    }
    fclose(f);
    replaying = 1;
    return 0;
}

/* ---- presentation: the loaded View's bitplanes through the copper palette ---- */
int platform_palette(const struct View *view, uint16_t colours[32]);

static void render(uint32_t *pixels)
{
    const struct View *view = current_view;
    const struct BitMap *bm;
    uint16_t colours[32];
    uint32_t rgb[32];
    if (!view || !view->ViewPort || !view->ViewPort->RasInfo || !(bm = view->ViewPort->RasInfo->BitMap)) {
        memset(pixels, 0, WIDTH * HEIGHT * 4);
        return;
    }
    platform_palette(view, colours);
    for (int i = 0; i < 32; i++) {
        uint16_t c = colours[i];
        rgb[i] = 0xff000000u | (uint32_t)((c >> 8) & 15) * 0x110000u | (uint32_t)((c >> 4) & 15) * 0x1100u | (uint32_t)(c & 15) * 0x11u;
    }
    for (int y = 0; y < HEIGHT && y < bm->Rows; y++)
        for (int x = 0; x < WIDTH && x < bm->BytesPerRow * 8; x++) {
            int value = 0;
            for (int p = 0; p < bm->Depth && p < 5; p++)
                if (bm->Planes[p] && (bm->Planes[p][y * bm->BytesPerRow + (x >> 3)] & (0x80 >> (x & 7))))
                    value |= 1 << p;
            pixels[y * WIDTH + x] = rgb[value];
        }
}

/* The 8x8 glyphs: SDL's built-in debug font, rendered once and read back. */
static void build_font(SDL_Renderer *renderer)
{
    SDL_Texture *target = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32, SDL_TEXTUREACCESS_TARGET, 8 * 96, 8);
    SDL_Surface *surface;
    SDL_SetRenderTarget(renderer, target);
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
    SDL_RenderClear(renderer);
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    for (int c = 32; c < 128; c++) {
        char text[2] = { (char)c, 0 };
        SDL_RenderDebugText(renderer, (float)((c - 32) * 8), 0, text);
    }
    surface = SDL_RenderReadPixels(renderer, NULL);
    if (surface) {
        SDL_Surface *rgba = SDL_ConvertSurface(surface, SDL_PIXELFORMAT_RGBA32);
        for (int c = 32; c < 128; c++)
            for (int y = 0; y < 8; y++) {
                uint8_t bits = 0;
                for (int x = 0; x < 8; x++) {
                    const uint8_t *px = (const uint8_t *)rgba->pixels + y * rgba->pitch + ((c - 32) * 8 + x) * 4;
                    if (px[0] > 127) bits |= (uint8_t)(0x80 >> x);
                }
                platform_font8x8[c][y] = bits;
            }
        SDL_DestroySurface(rgba);
        SDL_DestroySurface(surface);
    }
    SDL_SetRenderTarget(renderer, NULL);
    SDL_DestroyTexture(target);
}

/* Keys to the joystick on port 2: arrows move, Space/Ctrl/Enter fire. JOY1DAT encodes
   right in bit 1, left in bit 9, down as bit 0 ^ bit 1, up as bit 8 ^ bit 9. */
static int key_up, key_down, key_left, key_right;
static void update_joystick(void)
{
    uint16_t v = 0;
    if (key_right) v |= 0x0002;
    if (key_left) v |= 0x0200;
    if (key_down ^ key_right) v |= 0x0001;
    if (key_up ^ key_left) v |= 0x0100;
    live_joy = v;
}

static int mount_disks(const char *dir)
{
    int mounted = 0;
    int count = 0;
    char **names = SDL_GlobDirectory(dir, "*.adf", SDL_GLOB_CASEINSENSITIVE, &count);
    for (int i = 0; names && i < count; i++) {
        char path[1024];
        snprintf(path, sizeof path, "%s/%s", dir, names[i]);
        if (adf_mount(NULL, path) == 0) mounted++;
    }
    SDL_free(names);
    return mounted;
}

/* A key event from SDL: the joystick state and the raw key, taken by the game thread at
   its next tick. */
static void live_key(const SDL_KeyboardEvent *key, int down)
{
    uint8_t code = amiga_key(key->scancode);
    SDL_LockMutex(input_lock);
    switch (key->key) {
    case SDLK_UP: key_up = down; break;
    case SDLK_DOWN: key_down = down; break;
    case SDLK_LEFT: key_left = down; break;
    case SDLK_RIGHT: key_right = down; break;
    case SDLK_SPACE: case SDLK_LCTRL: case SDLK_RETURN: live_fire = down; break;
    default: break;
    }
    update_joystick();
    if (!key->repeat && code != 0xFF && ((key_head + 1) & 63) != key_tail) {
        key_queue[key_head] = (uint8_t)(code | (down ? 0 : 0x80));
        key_head = (key_head + 1) & 63;
    }
    SDL_UnlockMutex(input_lock);
}

int main(int argc, char **argv)
{
    const char *data = ".", *wav_path = NULL;
    SDL_Window *window = NULL;
    SDL_Renderer *renderer = NULL;
    SDL_Texture *screen = NULL;
    SDL_Thread *game;
    static uint32_t pixels[WIDTH * HEIGHT];
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--data") && i + 1 < argc) data = argv[++i];
        else if (!strcmp(argv[i], "--log")) log_file = stderr;
        else if (!strcmp(argv[i], "--wav") && i + 1 < argc) wav_path = argv[++i];
        else if (!strcmp(argv[i], "--headless")) headless = 1;
        else if (!strcmp(argv[i], "--strict")) strict = 1;
        else if (!strcmp(argv[i], "--ticks") && i + 1 < argc) end_tick = (uint32_t)strtoul(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--record") && i + 1 < argc) {
            record_file = fopen(argv[++i], "w");
            if (record_file) fputs("# ducktales replay log (poll frames): POLL joy|fire|key|seed HEX, POLL end\n", record_file);
        } else if (!strcmp(argv[i], "--replay") && i + 1 < argc) {
            if (load_replay(argv[++i])) { fprintf(stderr, "cannot read %s\n", argv[i]); return 1; }
        } else if (!strcmp(argv[i], "--dump") && i + 1 < argc) {
            /* --dump DIR:FROM:EVERY appends state.bin and state-index.jsonl in DIR (poll frames) */
            char *spec = argv[++i], *every = strrchr(spec, ':'), *from;
            if (every) { *every++ = 0; from = strrchr(spec, ':'); }
            if (!every || !from) { fprintf(stderr, "--dump DIR:FROM:EVERY\n"); return 1; }
            *from++ = 0;
            snprintf(dump_dir, sizeof dump_dir, "%s", spec);
            dump_from = (uint32_t)strtoul(from, NULL, 10);
            dump_every = (uint32_t)strtoul(every, NULL, 10);
        } else if (!strcmp(argv[i], "--shot") && i + 1 < argc && shot_count < 32) {
            /* --shot FILE.bmp:TICK saves the exact 320x200 picture at that tick */
            const char *colon = strrchr(argv[++i], ':');
            if (colon) {
                snprintf(shots[shot_count].path, sizeof shots[0].path, "%.*s", (int)(colon - argv[i]), argv[i]);
                shots[shot_count++].tick = (uint32_t)strtoul(colon + 1, NULL, 10);
            }
        }
    }
    if (!log_file) log_file = fopen("ducktales.log", "w");
    if (!SDL_Init(headless ? 0 : SDL_INIT_VIDEO | SDL_INIT_EVENTS | SDL_INIT_AUDIO)) { platform_log("SDL_Init: %s", SDL_GetError()); return 1; }
    m68k_memory(amiga_data_hunk, amiga_data_hunk_size, 0);
    asm_tables_init();
    if (wav_path) paula_record(wav_path);
    paula_start(!headless);
    if (mount_disks(data) < 2) {
        if (headless) fprintf(stderr, "no disk images in %s\n", data);
        else SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR, "DuckTales",
            "Put the two DuckTales disk images (*.adf) next to the program, or use --data DIR.", NULL);
        return 1;
    }
    dos_init();
    {
        /* the glyphs come from a software renderer: identical with and without a window */
        SDL_Surface *canvas = SDL_CreateSurface(8 * 96, 8, SDL_PIXELFORMAT_RGBA32);
        SDL_Renderer *software = SDL_CreateSoftwareRenderer(canvas);
        build_font(software);
        SDL_DestroyRenderer(software);
        SDL_DestroySurface(canvas);
    }
    input_lock = SDL_CreateMutex();
    if (!headless) {
        window = SDL_CreateWindow("DuckTales: The Quest for Gold", WIDTH * 3, HEIGHT * 3 * 6 / 5, SDL_WINDOW_RESIZABLE);
        renderer = SDL_CreateRenderer(window, NULL);
        SDL_SetRenderLogicalPresentation(renderer, WIDTH, HEIGHT * 6 / 5, SDL_LOGICAL_PRESENTATION_LETTERBOX);
        screen = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, WIDTH, HEIGHT);
        SDL_SetTextureScaleMode(screen, SDL_SCALEMODE_NEAREST);
    }
    game = SDL_CreateThread(game_thread, "game", NULL);

    while (!headless && !game_done) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_EVENT_QUIT) quitting = 1;
            if (event.type == SDL_EVENT_KEY_DOWN || event.type == SDL_EVENT_KEY_UP)
                live_key(&event.key, event.type == SDL_EVENT_KEY_DOWN);
        }
        render(pixels);
        SDL_UpdateTexture(screen, NULL, pixels, WIDTH * 4);
        SDL_RenderClear(renderer);
        {
            SDL_FRect dst = { 0, 0, WIDTH, HEIGHT * 6 / 5 };
            SDL_RenderTexture(renderer, screen, NULL, &dst);
        }
        SDL_RenderPresent(renderer);
        SDL_Delay(16);
    }
    SDL_WaitThread(game, NULL);
    if (record_file) { fprintf(record_file, "%u end\n", poll_frames); fclose(record_file); }
    paula_stop();
    SDL_Quit();
    return failed ? 3 : 0;
}
