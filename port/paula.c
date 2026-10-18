/* paula.c - the custom chip registers the translated driver writes (DMACON, INTENA, INTREQ,
   ADKCON, AUD0-3) and Paula's four DMA sound channels, mixed into an SDL3 audio stream.

   Paula, as far as the game uses it: a channel whose DMA is switched on copies its
   location and length registers (LC, LEN in words) and requests its audio interrupt
   (INTREQ bit 7 + n); the handler then writes LC/LEN for the next block. When a block's
   last word has played, the channel reloads from LC/LEN and requests the interrupt again.
   Each byte is a signed 8-bit sample, played for PER ticks of the 3546895 Hz PAL clock at
   VOL/64; channels 0 and 3 are the left output, 1 and 2 the right. */
#include <SDL3/SDL.h>

#include "m68k.h"
#include "amiga.h"
#include "os.h"
#include <stdlib.h>

#define PAL_CLOCK 3546895.0
#define RATE 48000

/* As the OS leaves them: DMA master (DMAEN) and interrupt master (INTEN) on. */
static uint16_t dmacon = 0x0200, intena = 0x4000, intreq, adkcon;
static struct channel {
    uint32_t lc;                                  /* latched by the CPU */
    uint16_t len, per, vol;
    int playing;                                  /* DMA running */
    const int8_t *ptr;
    uint32_t remaining;                           /* bytes of the current block */
    double phase;
    int8_t sample;
} channels[4];
static int in_interrupt;

static void dispatch(void)
{
    if (in_interrupt) return;                     /* level 4 is masked while a handler runs */
    for (int pass = 0; pass < 8; pass++) {
        int ran = 0;
        for (int n = 0; n < 4; n++) {
            uint16_t bit = (uint16_t)(0x80 << n);
            struct Interrupt *handler;
            if (!(intena & 0x4000) || !(intena & bit) || !(intreq & bit)) continue;
            handler = (struct Interrupt *)platform_vector(7 + n);
            if (!handler || !handler->is_Code) { intreq &= (uint16_t)~bit; continue; }
            in_interrupt = 1;
            m68k_interrupt((uint32_t)(uintptr_t)handler->is_Code, (uint32_t)(uintptr_t)handler->is_Data, 0xDFF000u);
            in_interrupt = 0;
            ran = 1;
        }
        if (!ran) return;
    }
}

static void start_block(struct channel *c, int n)
{
    c->ptr = (const int8_t *)(uintptr_t)c->lc;
    c->remaining = (c->len ? c->len : 0x10000u) * 2u;
    intreq |= (uint16_t)(0x80 << n);
}

static void update_dma(void)
{
    for (int n = 0; n < 4; n++) {
        struct channel *c = &channels[n];
        int on = (dmacon & 0x200) && (dmacon & (1 << n));
        if (on && !c->playing) { c->playing = 1; c->phase = 0; start_block(c, n); }
        else if (!on && c->playing) { c->playing = 0; c->sample = 0; }
    }
}

static uint16_t set_clear(uint16_t reg, uint32_t value)
{
    return value & 0x8000 ? (uint16_t)(reg | (value & 0x7FFF)) : (uint16_t)(reg & ~value);
}

uint32_t custom_read16(uint32_t offset)
{
    switch (offset) {
    case 0x002: return dmacon;
    case 0x010: return adkcon;
    case 0x01C: return intena;
    case 0x01E: return intreq;
    default: platform_log("custom read %03X", offset); return 0;
    }
}

void custom_write16(uint32_t offset, uint32_t value)
{
    static int trace = -1;                        /* PAULA_TRACE=1: log every register write */
    if (trace < 0) trace = getenv("PAULA_TRACE") != NULL;
    if (trace) platform_log("custom %03X = %04X", offset, value);
    if (offset >= 0x0A0 && offset < 0x0E0) {
        struct channel *c = &channels[(offset - 0x0A0) >> 4];
        switch (offset & 0xF) {
        case 0x0: c->lc = (c->lc & 0xFFFF) | value << 16; break;
        case 0x2: c->lc = (c->lc & 0xFFFF0000u) | (value & 0xFFFF); break;
        case 0x4: c->len = (uint16_t)value; break;
        case 0x6: c->per = (uint16_t)value; break;
        case 0x8: c->vol = (uint16_t)(value & 0x7F); break;
        default: break;                           /* AUDxDAT: the game does not write it */
        }
        return;
    }
    switch (offset) {
    case 0x096: dmacon = set_clear(dmacon, value); update_dma(); break;
    case 0x09A: intena = set_clear(intena, value); break;
    case 0x09C: intreq = set_clear(intreq, value); break;
    case 0x09E: adkcon = set_clear(adkcon, value); break;
    default: platform_log("custom write %03X = %04X", offset, value); return;
    }
    dispatch();
}

/* ---- mixing ---- */
static void render(float *out, int frames)
{
    for (int i = 0; i < frames; i++) {
        float left = 0, right = 0;
        for (int n = 0; n < 4; n++) {
            struct channel *c = &channels[n];
            if (!c->playing || c->per == 0) continue;
            c->phase += PAL_CLOCK / (c->per < 124 ? 124 : c->per) / RATE;
            while (c->phase >= 1.0) {
                c->phase -= 1.0;
                if (c->remaining == 0) { start_block(c, n); dispatch(); }
                if (!c->playing) break;
                c->sample = c->ptr ? *c->ptr++ : 0;
                c->remaining--;
            }
            {
                float s = c->sample * (float)(c->vol > 64 ? 64 : c->vol) / (128.0f * 64.0f);
                if (n == 0 || n == 3) left += s; else right += s;
            }
        }
        out[2 * i] = left * 0.5f;
        out[2 * i + 1] = right * 0.5f;
    }
}

/* --wav FILE: the mixed output is also written to a 48 kHz stereo float WAV file. */
static SDL_IOStream *wav;
static Uint32 wav_bytes;
static SDL_AudioStream *stream;

static void wav_header(void)
{
    Uint8 h[44] = { 'R','I','F','F', 0,0,0,0, 'W','A','V','E', 'f','m','t',' ', 16,0,0,0, 3,0, 2,0,
                    0,0,0,0, 0,0,0,0, 8,0, 32,0, 'd','a','t','a', 0,0,0,0 };
    Uint32 riff = 36 + wav_bytes, rate = RATE, bps = RATE * 8;
    memcpy(h + 4, &riff, 4); memcpy(h + 24, &rate, 4); memcpy(h + 28, &bps, 4); memcpy(h + 40, &wav_bytes, 4);
    SDL_SeekIO(wav, 0, SDL_IO_SEEK_SET);
    SDL_WriteIO(wav, h, sizeof h);
    SDL_SeekIO(wav, 0, SDL_IO_SEEK_END);
}

void paula_record(const char *path)
{
    wav = SDL_IOFromFile(path, "wb");
    if (wav) wav_header();
}

void paula_stop(void)
{
    if (!wav) return;
    wav_header();
    SDL_CloseIO(wav);
    wav = NULL;
}

/* One PAL frame of sound (71051 colour clocks), on the game thread's clock (main.c): the
   channels play, their block interrupts run, and the samples go to the audio device. */
void paula_frame(void)
{
    static double owed;
    float buffer[2 * 1024];
    int frames;
    owed += RATE * 71051.0 / PAL_CLOCK;
    frames = (int)owed;
    owed -= frames;
    render(buffer, frames);
    if (wav) { SDL_WriteIO(wav, buffer, (size_t)frames * 8); wav_bytes += (Uint32)frames * 8; }
    if (stream) SDL_PutAudioStreamData(stream, buffer, frames * 8);
}

void paula_start(int device)
{
    SDL_AudioSpec spec = { SDL_AUDIO_F32, 2, RATE };
    if (!device) return;
    stream = SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &spec, NULL, NULL);
    if (!stream) { platform_log("audio: %s", SDL_GetError()); return; }
    SDL_ResumeAudioStreamDevice(stream);
}
