struct RootBitMapView { unsigned short BytesPerRow; unsigned short Rows; unsigned char Flags; unsigned char Depth; unsigned short pad; unsigned char *Planes[8]; };
struct RootRasInfoView { struct RootRasInfoView *Next; struct RootBitMapView *BitMap; short RxOffset; short RyOffset; };
struct BitmapScreenRecord { char pad0[4]; long field_4; char pad8[16]; char field_18; char field_19; char field_1a; char field_1b; char field_1c; char pad1d[5]; short field_22; };
struct BitmapLayout { char pad0[8]; long planes[8]; };
struct ScreenInfo { char pad0[12]; struct BitmapScreenRecord *field_c; };
struct S53B8 { long field_0; long field_4; };

extern long G_h01_0036;
extern long G_h01_004E;
extern long G_h01_0066;
extern long G_h01_0072;
extern long G_h01_0078;
extern long G_h01_00AE;
extern long G_h01_00C0;
extern long G_h01_010E;
extern long G_h01_0126;
extern long G_h01_012C;
extern long G_h01_0132;
extern long G_h01_0138;
extern long G_h01_013E;
extern long G_h01_0144;
extern long G_h01_0174;
extern long G_h01_0180;
extern long G_h01_0186;
extern long G_h01_018C;
extern long G_h01_0192;
extern long G_h01_0198;
extern long G_h01_019E;
extern long G_h01_01AA;
extern long G_h01_01B0;
extern long G_h01_01BC;
extern long G_h01_01C2;
extern long G_h01_01C8;
extern long G_h01_01CE;
extern long G_h01_01E0;
extern long G_h01_01E6;
extern long G_h01_01F2;
extern long G_h01_01F8;
extern long G_h01_020A;

extern short G_h01_0970;
extern struct RootRasInfoView G_h01_2EB4;
extern struct RootBitMapView G_h01_2EC0;
extern struct RootBitMapView G_h01_2EE8;
extern struct BitmapScreenRecord *screen_rast_port;
extern struct BitmapLayout *G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46F8;
extern long G_h01_5370;
extern long graphics_library_base;
extern long intuition_library_base;
extern long layers_library_base;
extern long G_h01_5380;
extern struct ScreenInfo *G_h01_5384;
extern long G_h01_5388;
extern long G_h01_538C;
extern unsigned char G_h01_5390;
extern long G_h01_5392;
extern long G_h01_5396;
extern short G_h01_539A;
extern char G_h01_539C;
extern char G_h01_539D;
extern long G_h01_53A2;
extern long G_h01_53A6;
extern long G_h01_53B4;
extern long G_h01_53B8;
extern short G_h01_53CC;
extern short G_h01_53CE;
extern long G_h01_53D8;
extern long G_h01_53DC;
extern long G_h01_53E0;
extern long G_h01_53E4;
extern long G_h01_53E8;
extern long G_h01_53EC;
extern long G_h01_53F0;
extern long G_h01_53F4;
extern char G_h01_53F8;
extern long G_h01_5422;
extern long G_h01_5426;
extern long G_h01_542A;
extern long G_h01_544A;

struct GraphicsBaseView { char pad[34]; long view; };
struct S3 { char pad[8]; long field_8; long field_c; };
struct S2 { char pad[4]; struct S3 *field_4; };
struct S1 { char pad[36]; struct S2 *field_24; };
struct S0 { struct S1 *field_0; };
struct InitBlock { char first; char pad[11]; long field_c; long field_10; };
struct Layer { char pad[0xb8]; long field_b8; };

extern long F_h00_89D0();
extern int shutdown_av();
extern long AvailMem();
extern int show_system_request();
extern int F_h00_37C8();
extern int CloseWorkBench();
extern long AllocMem();
extern long NewLayer();
extern long CreateUpfrontLayer();
extern long FindTask();
extern long allocate_memory_or_report();
extern int GetPrefs();
extern int SetPrefs();
extern int free_memory_checked();
extern int InitBitMap();
extern int F_h00_8534();
extern int InitView();
extern int InitVPort();
extern long GetColorMap();
extern int MakeVPort();
extern int MrgCop();
extern int LoadView();
extern long OpenFont();
extern int SetFont();
extern int SetDrMd();
extern int SetAPen();
extern int SetRast();
extern int F_h00_307C();
extern int F_h00_330E();
extern int FreeSprite();
extern int seed_random();
extern int initialize_audio_and_input();
extern int F_h00_897C();
extern int CloseLibrary();

recovered()
{
    unsigned int i;
    long memory;
    struct Layer *layer;
    long size;
    long unused_slot;
    long probe;

    graphics_library_base = F_h00_89D0("graphics.library", 0L);
    if (!graphics_library_base)
        shutdown_av("InitAV:\tcannot open graphics library\n");
    G_h01_53DC = ((struct GraphicsBaseView *)graphics_library_base)->view;
    intuition_library_base = F_h00_89D0("intuition.library", 0L);
    if (!intuition_library_base)
        shutdown_av("InitAV:\tcannot open intuition library\n");

    size = AvailMem(2L);
    if (size < 0x45948L)
        show_system_request("Insufficient Chip Memory!");
    i = F_h00_37C8(0x40f10L);
    if (i < 0)
        show_system_request("Memory Fragmentation:  Can't allocate enough contiguous chip memory.");

    i = CloseWorkBench();
    if (i)
        G_h01_53F8 = 1;
    else
        G_h01_53F8 = 0;
    if (G_h01_53F8) {
        G_h01_5422 = AllocMem(0x3e80L, 0x10002L);
        G_h01_5426 = AllocMem(0x3e80L, 0x10002L);
        if (!G_h01_5422 || !G_h01_5426)
            show_system_request("Insufficient Chip Memory!");
    } else {
        G_h01_5422 = ((struct S0 *)G_h01_53DC)->field_0->field_24->field_4->field_8;
        G_h01_5426 = ((struct S0 *)G_h01_53DC)->field_0->field_24->field_4->field_c;
    }

    size = AvailMem(2L);
    if (size < 0x4a38L) {
        show_system_request("Insufficient Chip Memory!");
    } else {
        size = 0x4a38L;
        do {
            probe = AllocMem(size, 2L);
            if (!probe)
                size -= 0x1f4L;
        } while (!probe);
        F_h00_897C(probe, size);
        if (size < 0x4a38L)
            show_system_request("Memory Fragmentation:  Can't allocate enough contiguous chip memory.");
    }

    layers_library_base = F_h00_89D0("layers.library", 0L);
    if (!layers_library_base)
        shutdown_av("InitAV:\tcannot open layers library\n");
    G_h01_5380 = NewLayer();
    if (!G_h01_5380)
        shutdown_av("InitAV:\tcannot allocate Layer_Info");

    G_h01_5384 = CreateUpfrontLayer(G_h01_5380, &G_h01_2EC0, 0L, 0L, 0x13fL, 0xc7L, 1L);
    layer = (struct Layer *)FindTask(0L);
    layer->field_b8 = 0xffffffffL;
    G_h01_53EC = allocate_memory_or_report(&G_h01_542A, 0xe8L);
    GetPrefs(G_h01_53EC, 0xe8L);
    ((struct InitBlock *)G_h01_53EC)->first = 8;
    G_h01_53F0 = ((struct InitBlock *)G_h01_53EC)->field_c;
    ((struct InitBlock *)G_h01_53EC)->field_c = 0L;
    G_h01_53F4 = ((struct InitBlock *)G_h01_53EC)->field_10;
    ((struct InitBlock *)G_h01_53EC)->field_10 = 10L;
    SetPrefs(G_h01_53EC, 0xe8L, 1L);
    free_memory_checked(&G_h01_542A, G_h01_53EC, 0xe8L);
    CloseLibrary(intuition_library_base);

    G_h01_544A = allocate_memory_or_report(&G_h01_542A, 0x4000L);
    if (!G_h01_544A)
        F_h00_8534(-1);
    InitView(&G_h01_53A2);
    InitVPort(&G_h01_53B4);
    G_h01_53A2 = &G_h01_53B4;

    InitBitMap(&G_h01_2EC0, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = allocate_memory_or_report(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        G_h01_2EC0.Planes[i] = (unsigned char *)memory + (long)i * 0x1f40L;

    InitBitMap(&G_h01_2EE8, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = allocate_memory_or_report(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        G_h01_2EE8.Planes[i] = (unsigned char *)memory + (long)i * 0x1f40L;

    G_h01_46CE = allocate_memory_or_report(&G_h01_542A, 0x28L);
    InitBitMap(G_h01_46CE, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = allocate_memory_or_report(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        G_h01_46CE->planes[i] = memory + (long)i * 0x1f40L;

    G_h01_2EB4.BitMap = &G_h01_2EC0;
    G_h01_2EB4.RxOffset = 0;
    G_h01_2EB4.RyOffset = 0;
    G_h01_2EB4.Next = 0L;
    G_h01_53CC = 0x140;
    G_h01_53CE = 0xc8;
    G_h01_53D8 = &G_h01_2EB4;
    G_h01_53E8 = GetColorMap(0x20L);
    G_h01_53B8 = G_h01_53E8;
    G_h01_5392 = ((struct S53B8 *)G_h01_53B8)->field_4;
    MakeVPort(&G_h01_53A2, &G_h01_53B4);
    MrgCop(&G_h01_53A2);
    G_h01_53E0 = G_h01_53A6;
    G_h01_53A6 = 0L;
    G_h01_2EB4.BitMap = &G_h01_2EE8;
    G_h01_53B8 = G_h01_53E8;
    MakeVPort(&G_h01_53A2, &G_h01_53B4);
    MrgCop(&G_h01_53A2);
    G_h01_53E4 = G_h01_53A6;
    LoadView(&G_h01_53A2);

    screen_rast_port = G_h01_5384->field_c;
    screen_rast_port->field_4 = (long)&G_h01_2EC0;
    screen_rast_port->field_18 = 0xff;
    screen_rast_port->field_19 = 0x1f;
    screen_rast_port->field_1a = 2;
    screen_rast_port->field_1b = 1;
    screen_rast_port->field_1c = 0;
    screen_rast_port->field_22 = -1;

    G_h01_5396 = "topaz.font";
    G_h01_539A = 8;
    G_h01_539C = 0;
    G_h01_539D = 0;
    G_h01_46F8 = OpenFont(&G_h01_5396);
    if (!G_h01_46F8)
        shutdown_av("InitAV:\tcannot open font");
    SetFont(screen_rast_port, G_h01_46F8);
    SetDrMd(screen_rast_port, 0L);
    SetAPen(screen_rast_port, 0x1fL);
    G_h01_5370 = (long)((char *)screen_rast_port + 0x19L);
    G_h01_5388 = &G_h01_2EC0;
    G_h01_538C = &G_h01_2EE8;
    G_h01_5390 = 0;
    G_h01_46D2 = ((long *)&G_h01_5388)[G_h01_5390];
    SetRast(screen_rast_port, 0L);
    F_h00_307C();
    SetRast(screen_rast_port, 0L);
    F_h00_330E();
    for (i = 0; i < 8; ++i)
        FreeSprite((long)i);
    seed_random();
    initialize_audio_and_input();
}
