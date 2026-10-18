/* adf.c - read-only access to the game's two Amiga disk images (OFS, 880 KB).

   The game opens files by volume name ("DT1:main.arc", "dt2:dt2.as"). The player keeps
   the original disk images next to the program; each image is mounted under its own
   volume name and files are read whole through the OFS data-block chain. */
#include "amiga.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BLOCK 512
#define BLOCKS 1760
#define ROOT_BLOCK 880
#define HASH_SIZE 72

struct volume {
    char name[32];
    uint8_t *image;
    struct cached { char *path; uint8_t *data; uint32_t size; } *files;
    int file_count;
};

static struct volume volumes[4];
static int volume_count;

static uint32_t be32(const uint8_t *p) { return (uint32_t)p[0] << 24 | p[1] << 16 | p[2] << 8 | p[3]; }
static const uint8_t *block(struct volume *v, uint32_t n) { return n < BLOCKS ? v->image + n * BLOCK : NULL; }

static void bstr(const uint8_t *b, char *out, size_t size)
{
    size_t len = b[0] < size - 1 ? b[0] : size - 1;
    memcpy(out, b + 1, len); out[len] = 0;
}

static uint32_t name_hash(const char *name)
{
    uint32_t hash = (uint32_t)strlen(name);
    for (; *name; name++)
        hash = (hash * 13 + (uint32_t)toupper((unsigned char)*name)) & 0x7ff;
    return hash % HASH_SIZE;
}

/* The header block of `name` inside directory block `dir`, or 0. */
static uint32_t lookup(struct volume *v, uint32_t dir, const char *name)
{
    const uint8_t *d = block(v, dir);
    uint32_t key = d ? be32(d + 24 + 4 * name_hash(name)) : 0;
    while (key) {
        const uint8_t *h = block(v, key);
        char entry[32];
        if (!h) return 0;
        bstr(h + BLOCK - 80, entry, sizeof entry);
        if (strlen(entry) == strlen(name)) {
            size_t i = 0;
            while (entry[i] && toupper((unsigned char)entry[i]) == toupper((unsigned char)name[i])) i++;
            if (!entry[i]) return key;
        }
        key = be32(h + BLOCK - 16);    /* hash chain */
    }
    return 0;
}

int adf_mount(const char *volume, const char *image_path)
{
    FILE *f = fopen(image_path, "rb");
    struct volume *v;
    if (!f || volume_count == (int)(sizeof volumes / sizeof volumes[0])) { if (f) fclose(f); return -1; }
    v = &volumes[volume_count];
    memset(v, 0, sizeof *v);
    v->image = malloc(BLOCK * BLOCKS);
    if (!v->image || fread(v->image, 1, BLOCK * BLOCKS, f) != BLOCK * BLOCKS) { fclose(f); free(v->image); return -1; }
    fclose(f);
    if (volume && *volume)
        snprintf(v->name, sizeof v->name, "%s", volume);
    else
        bstr(v->image + ROOT_BLOCK * BLOCK + BLOCK - 80, v->name, sizeof v->name);
    volume_count++;
    platform_log("mounted %s: %s", v->name, image_path);
    return 0;
}

int adf_volume_count(void) { return volume_count; }
const char *adf_volume_name(int index) { return index >= 0 && index < volume_count ? volumes[index].name : NULL; }

static struct volume *find_volume(const char *name, size_t len)
{
    for (int i = 0; i < volume_count; i++)
        if (strlen(volumes[i].name) == len) {
            size_t j = 0;
            while (j < len && toupper((unsigned char)volumes[i].name[j]) == toupper((unsigned char)name[j])) j++;
            if (j == len) return &volumes[i];
        }
    return NULL;
}

const uint8_t *adf_file(const char *amiga_path, uint32_t *size)
{
    const char *colon = strchr(amiga_path, ':');
    struct volume *v = colon ? find_volume(amiga_path, (size_t)(colon - amiga_path)) : (volume_count ? &volumes[0] : NULL);
    const char *path = colon ? colon + 1 : amiga_path;
    uint32_t key = ROOT_BLOCK, total, done = 0, data;
    uint8_t *out;
    char part[32];
    if (!v) return NULL;
    for (int i = 0; i < v->file_count; i++)
        if (!strcmp(v->files[i].path, amiga_path)) { *size = v->files[i].size; return v->files[i].data; }
    while (*path) {                    /* walk directories: "a/b/c" */
        size_t n = strcspn(path, "/");
        if (n >= sizeof part) return NULL;
        memcpy(part, path, n); part[n] = 0;
        key = lookup(v, key, part);
        if (!key) return NULL;
        path += n + (path[n] == '/');
    }
    total = be32(block(v, key) + BLOCK - 188);
    out = malloc(total ? total : 1);
    for (data = be32(block(v, key) + 16); data && done < total; ) {
        const uint8_t *b = block(v, data);
        uint32_t chunk;
        if (!b) break;
        chunk = be32(b + 12);
        if (chunk > total - done) chunk = total - done;
        memcpy(out + done, b + 24, chunk);
        done += chunk;
        data = be32(b + 16);
    }
    v->files = realloc(v->files, sizeof *v->files * (size_t)(v->file_count + 1));
    v->files[v->file_count].path = strdup(amiga_path);
    v->files[v->file_count].data = out;
    v->files[v->file_count].size = done;
    v->file_count++;
    *size = done;
    return out;
}
