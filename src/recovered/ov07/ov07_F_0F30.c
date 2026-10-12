extern long G_h01_46CA;
extern char *G_h01_5370;
extern int F_h00_8AA8();
extern int F_h00_8B4C();
extern int F_h00_8B88();

recovered(arg)
int arg;
{
    *G_h01_5370 = 12;
    switch (arg) {
    case 0xc0:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 25), 0xaeL);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 25), 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(arg + 25), 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 25), 0xc2L);
        break;
    case 0xe0:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xaeL);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(arg + 24), 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc2L);
        break;
    case 0x100:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xaeL);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)arg, 0xc2L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(arg + 24), 0xaeL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc2L);
        break;
    case 0x120:
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xacL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xacL);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xc5L);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc5L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)arg, 0xacL);
        F_h00_8AA8(G_h01_46CA, (long)arg, 0xc5L);
        F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
        F_h00_8B4C(G_h01_46CA, (long)(arg + 24), 0xacL);
        F_h00_8AA8(G_h01_46CA, (long)(arg + 24), 0xc5L);
        break;
    default:
        break;
    }
}
