/* main.c - the SDL3 side of the port: window, presentation, input, the 50 Hz VBlank,
   the game thread and the OS state the emulation keeps (interrupt servers, Forbid).

   ducktales [--data DIR] [--log]
   DIR holds the two original disk images (any *.adf; mounted under their volume names,
   DT1 and DT2). docs/sdl3-port.md describes the design. */
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>

#include "amiga.h"
#include "os.h"

#include <setjmp.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#define WIDTH 320
#define HEIGHT 200

static FILE *log_file;
static SDL_Mutex *state_lock;
static SDL_Condition *tick_signal;
static volatile uint32_t vblank_count;
static volatile int forbidden, quitting, game_done;
static const struct View *current_view;
static void *servers[8][4];                         /* AddIntServer chains, per number */
static void *vectors[16];                           /* SetIntVector */
static void *input_handler;
static volatile uint16_t joy1dat;
static volatile int fire_down;
static jmp_buf game_exit;
static struct { char path[512]; Uint64 at_ms; int done; } shots[32];
static int shot_count;

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
void platform_input_handler(void *interrupt) { input_handler = interrupt; }

/* Delay(ticks) and WaitBOVP: wait for ticks (at least one) VBlanks. */
void platform_wait_ticks(int ticks)
{
    uint32_t target;
    SDL_LockMutex(state_lock);
    target = vblank_count + (uint32_t)(ticks > 0 ? ticks : 1);
    while ((int32_t)(vblank_count - target) < 0 && !quitting)
        SDL_WaitCondition(tick_signal, state_lock);
    SDL_UnlockMutex(state_lock);
    if (quitting) longjmp(game_exit, 1);
}

uint16_t platform_joystick(void) { return joy1dat; }
int platform_fire(void) { return fire_down; }

/* VPOSR as the game samples it for its RNG seed: the beam position at the moment of the
   call. Here: where a 50 Hz frame would be, from the host clock (replay records it). */
uint16_t platform_beam(void)
{
    uint64_t ns = SDL_GetTicksNS() % 20000000u;           /* within the 20 ms frame */
    return (uint16_t)(ns * 313u / 20000000u);
}

void platform_exit(int code)
{
    platform_log("game exit %d", code);
    longjmp(game_exit, 1);
}

/* ---- the 50 Hz VBlank: interrupt servers run on this thread, as on the Amiga ---- */
static Uint64 SDLCALL vblank(void *user, SDL_TimerID id, Uint64 interval)
{
    (void)user; (void)id;
    if (!forbidden)
        for (int i = 0; i < 4; i++) {
            struct Interrupt *server = servers[5][i];
            if (server && server->is_Code) ((int32_t (*)(void))server->is_Code)();
        }
    SDL_LockMutex(state_lock);
    vblank_count++;
    SDL_BroadcastCondition(tick_signal);
    SDL_UnlockMutex(state_lock);
    return interval;
}

/* ---- the game thread ---- */
extern int16_t _main(int32_t alen, char *aptr);

static int SDLCALL game_thread(void *user)
{
    (void)user;
    if (!setjmp(game_exit))
        _main(0, "");
    game_done = 1;
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
    joy1dat = v;
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

int main(int argc, char **argv)
{
    const char *data = ".";
    SDL_Window *window;
    SDL_Renderer *renderer;
    SDL_Texture *screen;
    static uint32_t pixels[WIDTH * HEIGHT];
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--data") && i + 1 < argc) data = argv[++i];
        else if (!strcmp(argv[i], "--log")) log_file = stderr;
        else if (!strcmp(argv[i], "--shot") && i + 1 < argc && shot_count < 32) {
            /* --shot FILE.bmp:MS saves the exact 320x200 picture MS milliseconds after start */
            const char *colon = strrchr(argv[++i], ':');
            if (colon) {
                snprintf(shots[shot_count].path, sizeof shots[0].path, "%.*s", (int)(colon - argv[i]), argv[i]);
                shots[shot_count++].at_ms = (Uint64)SDL_strtoull(colon + 1, NULL, 10);
            }
        }
    }
    if (!log_file) log_file = fopen("ducktales.log", "w");
    if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS)) { platform_log("SDL_Init: %s", SDL_GetError()); return 1; }
    if (mount_disks(data) < 2) {
        SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR, "DuckTales",
            "Put the two DuckTales disk images (*.adf) next to the program, or use --data DIR.", NULL);
        return 1;
    }
    dos_init();
    window = SDL_CreateWindow("DuckTales: The Quest for Gold", WIDTH * 3, HEIGHT * 3 * 6 / 5, SDL_WINDOW_RESIZABLE);
    renderer = SDL_CreateRenderer(window, NULL);
    SDL_SetRenderLogicalPresentation(renderer, WIDTH, HEIGHT * 6 / 5, SDL_LOGICAL_PRESENTATION_LETTERBOX);
    build_font(renderer);
    screen = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, WIDTH, HEIGHT);
    SDL_SetTextureScaleMode(screen, SDL_SCALEMODE_NEAREST);
    state_lock = SDL_CreateMutex();
    tick_signal = SDL_CreateCondition();
    SDL_AddTimerNS(20000000u, vblank, NULL);
    SDL_DetachThread(SDL_CreateThread(game_thread, "game", NULL));

    while (!game_done) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_EVENT_QUIT) { quitting = 1; game_done = 1; }
            if (event.type == SDL_EVENT_KEY_DOWN || event.type == SDL_EVENT_KEY_UP) {
                int down = event.type == SDL_EVENT_KEY_DOWN;
                switch (event.key.key) {
                case SDLK_UP: key_up = down; break;
                case SDLK_DOWN: key_down = down; break;
                case SDLK_LEFT: key_left = down; break;
                case SDLK_RIGHT: key_right = down; break;
                case SDLK_SPACE: case SDLK_LCTRL: case SDLK_RETURN: fire_down = down; break;
                default: break;
                }
                update_joystick();
            }
        }
        render(pixels);
        for (int i = 0; i < shot_count; i++)
            if (!shots[i].done && SDL_GetTicks() >= shots[i].at_ms) {
                SDL_Surface *picture = SDL_CreateSurfaceFrom(WIDTH, HEIGHT, SDL_PIXELFORMAT_ARGB8888, pixels, WIDTH * 4);
                SDL_SaveBMP(picture, shots[i].path);
                SDL_DestroySurface(picture);
                shots[i].done = 1;
                if (i == shot_count - 1) game_done = 1;      /* the last shot ends the run */
            }
        SDL_UpdateTexture(screen, NULL, pixels, WIDTH * 4);
        SDL_RenderClear(renderer);
        {
            SDL_FRect dst = { 0, 0, WIDTH, HEIGHT * 6 / 5 };
            SDL_RenderTexture(renderer, screen, NULL, &dst);
        }
        SDL_RenderPresent(renderer);
        SDL_Delay(16);
    }
    quitting = 1;
    SDL_BroadcastCondition(tick_signal);
    SDL_Quit();
    return 0;
}
