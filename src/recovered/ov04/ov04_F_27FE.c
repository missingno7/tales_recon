extern long graphics_library_base;
extern long intuition_library_base;
extern long layers_library_base;
extern long G_h01_5380;
extern long G_h01_5384;
extern long G_h01_53B4;
extern long G_h01_53E0;
extern long G_h01_53E4;
extern long G_h01_53E8;
extern long G_h01_53F0;
extern long G_h01_53F4;
extern char G_h01_53F8;
extern long G_h01_5422;
extern long G_h01_5426;
extern long G_h01_542A;
extern long arc_file;
extern long G_h01_46F8;

struct InitBlock { char pad[12]; long field_c; long field_10; };
struct S3 { char pad[8]; long field_8; long field_c; };
struct S2 { char pad[4]; struct S3 *field_4; };
struct S1 { char pad[36]; struct S2 *field_24; };
struct S0 { struct S1 *field_0; };
extern struct InitBlock *G_h01_53EC;
extern struct S0 *G_h01_53DC;

extern int F_h00_4EC6();
extern int shutdown_audio_and_input();
extern int F_h00_330E();
extern long F_h00_89D0();
extern long allocate_memory_or_report();
extern int GetPrefs();
extern int SetPrefs();
extern int free_memory_checked();
extern int F_h00_3850();
extern int F_h00_897C();
extern int BltClear();
extern int Close();
extern int CloseFont();
extern int DeleteLayer();
extern int DisposeLayer();
extern int LoadView();
extern int FreeColorMap();
extern int FreeVPort();
extern int FreeCprList();
extern int CloseWorkBench();
extern int OpenWorkBench();
extern int CloseLibrary();
extern int F_h00_8534();

recovered()
{
    int unused;

    F_h00_4EC6();
    shutdown_audio_and_input();
    F_h00_330E();
    intuition_library_base = F_h00_89D0("intuition.library", 0L);
    if (!intuition_library_base)
        recovered("InitAV:\tcannot open intuition library\n");
    G_h01_53EC = allocate_memory_or_report(&G_h01_542A, 0xe8L);
    GetPrefs(G_h01_53EC, 0xe8L);
    G_h01_53EC->field_c = G_h01_53F0;
    G_h01_53EC->field_10 = G_h01_53F4;
    SetPrefs(G_h01_53EC, 0xe8L, 1L);
    free_memory_checked(&G_h01_542A, G_h01_53EC, 0xe8L);
    F_h00_3850(0x40f10L);
    if (G_h01_53F8) {
        if (G_h01_5422)
            F_h00_897C(G_h01_5422, 0x3e80L);
        if (G_h01_5426)
            F_h00_897C(G_h01_5426, 0x3e80L);
    } else {
        BltClear(G_h01_53DC->field_0->field_24->field_4->field_8, 0x3e80L, 0L);
        BltClear(G_h01_53DC->field_0->field_24->field_4->field_c, 0x3e80L, 0L);
    }
    Close(arc_file);
    CloseFont(G_h01_46F8);
    DeleteLayer(G_h01_5380, G_h01_5384);
    DisposeLayer(G_h01_5380);
    LoadView(G_h01_53DC);
    FreeColorMap(G_h01_53E8);
    FreeVPort(&G_h01_53B4);
    FreeCprList(G_h01_53E0);
    FreeCprList(G_h01_53E4);
    CloseWorkBench();
    OpenWorkBench();
    CloseLibrary(layers_library_base);
    CloseLibrary(intuition_library_base);
    CloseLibrary(graphics_library_base);
    F_h00_8534(0);
}
