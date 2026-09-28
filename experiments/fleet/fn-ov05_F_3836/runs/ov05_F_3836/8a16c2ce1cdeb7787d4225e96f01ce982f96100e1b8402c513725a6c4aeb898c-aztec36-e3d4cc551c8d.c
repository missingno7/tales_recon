extern int G_h01_0A84;
extern long G_h01_46CA;
extern char G_h01_46E1;
extern int G_h01_5E42;
extern int G_h01_5E52;
extern int G_h01_5E56;
extern char G_h01_5E58;
extern char *G_h01_5370;
extern int G_h01_593E[1];
extern int G_h01_5974[1];
extern int G_h01_59AA[2];
extern int G_h01_5C9E[2];
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
extern int F_h00_34E0();
extern int F_h00_09C0();
extern long F_h00_8D1E();
extern long F_h00_8D14();
extern long F_h00_8D28();
extern long F_h00_8CD8();
extern int F_h00_8D00();
#pragma regcall(F_h00_8D1E(d0))
#pragma regcall(F_h00_8D14(d0,d1))
#pragma regcall(F_h00_8D28(d0,d1))
#pragma regcall(F_h00_8CD8(d0,d1))
#pragma regcall(F_h00_8D00(d0))

recovered()
{
    long first, second;

    first = F_h00_8D1E((long)G_h01_0A84);
    second = F_h00_8D1E((long)G_h01_5E42);
    *G_h01_5370 = 4;

    F_h00_8B88((long)G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C((long)G_h01_46CA, 0L, 176L);
    F_h00_8AA8((long)G_h01_46CA, 319L, 176L);

    F_h00_8B88((long)G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C((long)G_h01_46CA, 0L, 199L);
    F_h00_8AA8((long)G_h01_46CA, 319L, 199L);

    F_h00_8B88((long)G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C((long)G_h01_46CA, 0L, 177L);
    F_h00_8AA8((long)G_h01_46CA, 0L, 199L);

    F_h00_8B88((long)G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C((long)G_h01_46CA, 319L, 177L);
    F_h00_8AA8((long)G_h01_46CA, 319L, 199L);

    F_h00_34E0(G_h01_593E);

    if (G_h01_5E56 + 42 <= G_h01_0A84) {
        G_h01_46E1++;
        G_h01_5E56 += 42;
    }

    if (G_h01_46E1 < 10)
        F_h00_09C0(18, 184, (long)(G_h01_46E1 > 30 ? 30 : G_h01_46E1), 7, 1, 0);
    else
        F_h00_09C0(14, 184, (long)(G_h01_46E1 > 30 ? 30 : G_h01_46E1), 7, 1, 0);

    F_h00_34E0(G_h01_5974);

    if (G_h01_5E58) {
        G_h01_59AA[0] = (int)F_h00_8D00(F_h00_8CD8(F_h00_8D28(F_h00_8D14(first, second), 0xd0000048L), 0x90000047L));
        G_h01_59AA[1] = 0xb1;
        F_h00_34E0(G_h01_59AA);
        G_h01_5C9E[0] = (int)F_h00_8D00(F_h00_8CD8(F_h00_8D28(F_h00_8D14(F_h00_8D1E((long)G_h01_5E52), second), 0xd0000048L), 0x90000047L));
        G_h01_5C9E[1] = 0xba;
        F_h00_34E0(G_h01_5C9E);
    } else {
        G_h01_59AA[0] = (int)F_h00_8D00(F_h00_8CD8(F_h00_8D28(F_h00_8D14(first, second), 0xd0000048L), 0x90000047L));
        G_h01_59AA[1] = 0xb6;
        F_h00_34E0(G_h01_59AA);
    }
}
