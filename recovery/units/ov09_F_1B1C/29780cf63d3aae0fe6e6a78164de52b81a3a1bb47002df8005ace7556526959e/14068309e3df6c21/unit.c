/* ov09_F_1B1C v1: plain structured C, canonical declaration views where they exist. */
extern long F_h00_463E();
extern int F_h09_298E();
extern int F_h09_26C6();
extern int F_h09_28A0();
extern char G_h01_4332;
extern char G_h01_7192;
extern char G_h01_46E0;
extern unsigned char G_h01_41F4;
extern char G_h01_3D88;
extern char G_h01_3DBE;
extern char G_h01_3DF4;
extern char G_h01_3E2A;
extern char G_h01_3E60;
extern char G_h01_3E96;
extern char G_h01_3ECC;
extern char G_h01_3F02;
extern char G_h01_3F38;
extern char G_h01_3F6E;
extern char G_h01_3FA4;
extern char G_h01_3FDA;
extern char G_h01_4010;
extern char G_h01_4046;
extern char G_h01_407C;
extern char G_h01_40B2;
extern char G_h01_40E8;

struct State {
    unsigned char kind;
    char pad1;
    unsigned int type;
    unsigned char mode;
    unsigned char step;
    char ticks;
    char pad7;
    int first;
    int second;
};

recovered()
{
    int i;
    int f0;
    int f1;
    int f2;
    int thr;
    register struct State *p;

    f0 = 0;
    f1 = 0;
    f2 = 0;
    for (i = 0; i < 3; i++) {
        if (((struct State *)&G_h01_4332)[i].kind) {
            if (i == 0)
                f0 = 1;
            else if (i == 1)
                f1 = 1;
            else
                f2 = 1;
        }
    }

    if (G_h01_41F4 > 8) {
        if (G_h01_46E0 < 2) {
            G_h01_7192 = 25;
            thr = 90;
        } else {
            G_h01_7192 = 15;
            thr = 80;
        }
    } else if (G_h01_41F4 > 2) {
        if (G_h01_46E0 < 2) {
            G_h01_7192 = 40;
            thr = 35;
        } else {
            G_h01_7192 = 20;
            thr = 20;
        }
    } else {
        if (G_h01_46E0 < 2) {
            G_h01_7192 = 50;
            thr = 15;
        } else {
            G_h01_7192 = 25;
            thr = 8;
        }
    }

    if (!f0 && (unsigned)F_h00_463E() % 100 < thr)
        F_h09_298E(0);
    if (!f2 && (unsigned)F_h00_463E() % 100 < thr)
        F_h09_298E(2);
    if (!f1 && (unsigned)F_h00_463E() % 100 < thr)
        F_h09_298E(1);

    p = (struct State *)&G_h01_4332;
    for (i = 0; i < 3; i++, p++) {
        if (!p->kind)
            continue;
        switch (p->type) {
        case 14:
        case 30:
            if (p->type == 14)
                F_h09_26C6(p, &G_h01_3D88);
            else
                F_h09_26C6(p, &G_h01_40E8);
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step > 0)
                        p->mode = 1;
                    else
                        p->kind = 0;
                }
                break;
            case 1:
                if (--p->ticks == 0) {
                    p->ticks = 1;
                    if (p->step == 2 && G_h01_41F4 > 5)
                        p->kind = 0;
                    else if (p->step == 2) {
                        p->step = 0;
                        p->mode = 0;
                    } else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step = 2;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 15:
        case 31:
            F_h09_26C6(p, &G_h01_3DBE);
            if (p->type == 31)
                F_h09_26C6(p, &G_h01_40E8);
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 2)
                        p->kind = 0;
                    else
                        p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 0;
                    p->step = 2;
                }
                break;
            case 2:
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 7;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 16:
        case 32:
            F_h09_26C6(p, &G_h01_3DF4);
            if (p->type == 32)
                F_h09_26C6(p, &G_h01_40E8);
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 2 && G_h01_41F4 > 5)
                        p->kind = 0;
                    else if (p->step == 2)
                        p->mode = 3;
                    else if (p->step == 3) {
                        p->mode = 2;
                        p->step = 4;
                    } else if (p->step == 5)
                        p->kind = 0;
                    else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 1) {
                        p->step = 2;
                        p->mode = 1;
                    } else if (p->step == 4) {
                        p->step = 5;
                        p->mode = 1;
                    }
                }
                break;
            case 3:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step = 3;
                }
                break;
            case 4:
            case 5:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 5)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 17:
        case 18:
        case 33:
        case 34:
            if (p->type == 18)
                F_h09_26C6(p, &G_h01_3E60);
            else if (p->type == 34)
                F_h09_26C6(p, &G_h01_40E8);
            else if (p->type == 17)
                F_h09_26C6(p, &G_h01_3E2A);
            else
                F_h09_26C6(p, &G_h01_40E8);
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 1) {
                        p->mode = 1;
                        p->step = 2;
                        if (G_h01_41F4 > 5)
                            p->kind = 0;
                    } else
                        p->kind = 0;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 19:
        case 35:
            if (p->type == 19)
                F_h09_26C6(p, &G_h01_3E96);
            else
                F_h09_26C6(p, &G_h01_40E8);
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 2)
                        p->mode = 2;
                    else
                        p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 1) {
                        p->mode = 0;
                        p->step = 2;
                    } else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0)
                    p->kind = 0;
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 0;
                    if (++p->mode > 4) {
                        p->mode = 3;
                        if (++p->step > 7)
                            p->kind = 0;
                    }
                }
                break;
            }
            break;
        case 20:
        case 21:
        case 36:
        case 37:
            if (p->type == 20 || p->type == 36) {
                F_h09_26C6(p, &G_h01_3ECC);
                if (p->type == 36)
                    F_h09_26C6(p, &G_h01_40E8);
            } else {
                F_h09_26C6(p, &G_h01_3F02);
                if (p->type == 37)
                    F_h09_26C6(p, &G_h01_40E8);
            }
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 4)
                        p->step = 5;
                    p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step > 1 && G_h01_41F4 > 5)
                        p->kind = 0;
                    else if (p->step == 3) {
                        p->mode = 0;
                        p->step = 4;
                    } else if (p->step == 5)
                        p->kind = 0;
                    else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step++;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 22:
        case 23:
        case 38:
        case 39:
            if (p->type == 22 || p->type == 38) {
                F_h09_26C6(p, &G_h01_3F38);
                if (p->type == 38)
                    F_h09_26C6(p, &G_h01_40E8);
            } else {
                F_h09_26C6(p, &G_h01_3F6E);
                if (p->type == 39)
                    F_h09_26C6(p, &G_h01_40E8);
            }
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step > 0)
                        p->mode = 1;
                    else
                        p->kind = 0;
                }
                break;
            case 1:
                if (--p->ticks == 0) {
                    p->ticks = 1;
                    if (p->step > 1 && G_h01_41F4 > 5)
                        p->kind = 0;
                    else if (p->step == 2) {
                        p->step = 0;
                        p->mode = 0;
                    } else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step = 2;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 24:
        case 25:
        case 28:
        case 29:
        case 40:
        case 41:
        case 44:
        case 45:
            if (p->type == 25)
                F_h09_26C6(p, &G_h01_3FDA);
            else if (p->type == 41)
                F_h09_26C6(p, &G_h01_40E8);
            else if (p->type == 24)
                F_h09_26C6(p, &G_h01_3FA4);
            else if (p->type == 40)
                F_h09_26C6(p, &G_h01_40E8);
            else if (p->type == 28)
                F_h09_26C6(p, &G_h01_407C);
            else if (p->type == 44)
                F_h09_26C6(p, &G_h01_40E8);
            else if (p->type == 29)
                F_h09_26C6(p, &G_h01_40B2);
            else
                F_h09_26C6(p, &G_h01_40E8);
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 2)
                        p->kind = 0;
                    else
                        p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks == 0) {
                    p->ticks = 1;
                    if (p->step > 1 && G_h01_41F4 > 5)
                        p->kind = 0;
                    else if (p->step == 2)
                        p->mode = 0;
                    else
                        p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                    p->step = 2;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        case 26:
        case 27:
        case 42:
        case 43:
            if (p->type == 27)
                F_h09_26C6(p, &G_h01_4046);
            else if (p->type == 43)
                F_h09_26C6(p, &G_h01_40E8);
            else if (p->type == 26)
                F_h09_26C6(p, &G_h01_4010);
            else
                F_h09_26C6(p, &G_h01_40E8);
            F_h09_28A0(p->kind);
            switch (p->mode) {
            case 0:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    p->mode = 1;
                }
                break;
            case 1:
                if (--p->ticks == 0) {
                    if (p->step == 2 && G_h01_41F4 > 5)
                        p->kind = 0;
                    p->ticks = 1;
                    p->mode = 2;
                }
                break;
            case 2:
                if (--p->ticks < 0) {
                    p->ticks = 1;
                    if (p->step == 1) {
                        p->mode = 1;
                        p->step = 2;
                    } else
                        p->kind = 0;
                }
                break;
            case 3:
            case 4:
                if (--p->ticks < 0) {
                    p->ticks = 3;
                    if (++p->mode > 4)
                        p->kind = 0;
                }
                break;
            }
            break;
        default:
            break;
        }
    }
}

/* Direct recovery candidate for ov09_F_26C6 (plain structured C, h1 baseline). */
extern int F_h00_34E0();

struct ov09_a {
    unsigned char f0;
    char f1_3[3];
    unsigned char f4;
    char f5_7[3];
    int f8;
    int f10;
};

struct ov09_b {
    int x;
    int y;
    char f4_33[48];
    unsigned char flag34;
};

F_h09_26C6(a, b)
struct ov09_a *a;
struct ov09_b *b;
{
    int x;
    int y;

    switch (a->f0) {
    case 1:
        x = 8;
        y = 80 - a->f10;
        break;
    case 2:
        x = 14;
        y = 108 - a->f10;
        break;
    case 3:
        x = 44;
        y = 124 - a->f10;
        break;
    case 4:
        x = 78 - a->f8;
        y = 124 - a->f10;
        break;
    case 5:
        x = 140;
        y = 106 - a->f10;
        break;
    case 6:
        x = 146;
        y = 64 - a->f10;
        break;
    case 7:
        x = 144;
        y = 106 - a->f10;
        break;
    case 8:
        x = 206 - a->f8;
        y = 106 - a->f10;
        break;
    case 9:
        x = 271 - a->f8;
        y = 121 - a->f10;
        break;
    case 10:
        x = 272;
        y = 70 - a->f10;
        break;
    case 11:
        x = 232;
        y = 121 - a->f10;
        break;
    case 12:
        x = 217;
        y = 151 - a->f10;
        break;
    case 13:
        x = 240;
        y = 36;
        break;
    case 14:
        x = 0;
        y = 176 - a->f10;
        break;
    default:
        x = 100;
        y = 100;
        break;
    }
    b->flag34 = a->f4;
    b->x = x;
    b->y = y;
    F_h00_34E0(b);
}

/* ov09_F_28A0 (fleet v3; two locals without references occupy the original frame). */
extern int F_h00_34E0();
extern int G_h01_3ACA; extern int G_h01_3B00; extern int G_h01_3B36;
extern int G_h01_3B6C; extern int G_h01_3BA2; extern int G_h01_3BD8;
extern int G_h01_3C0E; extern int G_h01_3C44; extern int G_h01_3C7A;
extern int G_h01_3CB0; extern int G_h01_3CE6; extern int G_h01_3D1C;
extern int G_h01_3D52;

F_h09_28A0(a) char a;
{
    long la;
    long lb;
    switch (a) {
    case 1:
        F_h00_34E0(&G_h01_3ACA);
        break;
    case 2:
        F_h00_34E0(&G_h01_3B00);
        break;
    case 4:
        F_h00_34E0(&G_h01_3B6C);
    case 3:
        F_h00_34E0(&G_h01_3B36);
        break;
    case 5:
        F_h00_34E0(&G_h01_3BA2);
    case 7:
        F_h00_34E0(&G_h01_3C0E);
        break;
    case 6:
        F_h00_34E0(&G_h01_3BD8);
        break;
    case 8:
        F_h00_34E0(&G_h01_3C44);
        F_h00_34E0(&G_h01_3C0E);
        break;
    case 9:
        F_h00_34E0(&G_h01_3C7A);
    case 11:
        F_h00_34E0(&G_h01_3CE6);
        break;
    case 10:
        F_h00_34E0(&G_h01_3CB0);
        break;
    case 12:
        F_h00_34E0(&G_h01_3D1C);
        break;
    case 13:
        F_h00_34E0(&G_h01_3D52);
        break;
    default:
        break;
    }
}

struct Table {
    int first;
    int second;
    char pad[2];
};

extern long F_h00_463E();
extern int F_h00_57D2();
extern char G_h01_7192;
extern int G_h01_4262;
extern int G_h01_4264[6];
extern unsigned char G_h01_4272[96];
extern char G_h01_0468[16];
extern char G_h01_4332;
extern char G_h01_433E;
extern char G_h01_434A;
extern char G_h01_46E0;
extern char G_h01_4188;
extern struct Table G_h01_4274[64];

F_h09_298E(mode)
char mode;
{
    unsigned row;
    int value;
    register char *event;

again:
    if ((unsigned)F_h00_463E()%100 < G_h01_7192)
        row=G_h01_4262;
    else
        row=G_h01_4264[(unsigned)F_h00_463E()%6];

    if (!mode) {
        value=(unsigned)F_h00_463E()%5;
        if (!(*((unsigned char *)G_h01_4272+(long)(row-14)*6) & G_h01_0468[value]))
            goto mode0_done;
        if (value==4)
            value=13;
        event=&G_h01_4332;
        event[0]=value+1;
        *(int *)(event+2)=row;
        event[4]=0;
        event[5]=1;
        if (!G_h01_46E0 && G_h01_4188)
            event[6]=2;
        else
            event[6]=1;
        *(int *)(event+8)=G_h01_4274[row-14].first;
        *(int *)(event+10)=G_h01_4274[row-14].second;
        F_h00_57D2(103);
        goto done;
mode0_done:
        goto done;
    }
    if (mode==1) {
        value=(int)F_h00_463E()&3;
        if (!(*((unsigned char *)G_h01_4272+(long)(row-14)*6) & G_h01_0468[value+5]))
            goto mode1_done;
        event=&G_h01_433E;
        event[0]=value+5;
        *(int *)(event+2)=row;
        event[4]=0;
        event[5]=1;
        if (!G_h01_46E0 && G_h01_4188!=1)
            event[6]=2;
        else
            event[6]=1;
        *(int *)(event+8)=G_h01_4274[row-14].first;
        *(int *)(event+10)=G_h01_4274[row-14].second;
        F_h00_57D2(105);
        goto done;
mode1_done:
        goto done;
    }
    if (mode==2) {
        value=(unsigned)F_h00_463E()%5;
        if (!(*((unsigned char *)G_h01_4272+(long)(row-14)*6) & G_h01_0468[value+9]))
            goto mode2_done;
        event=&G_h01_434A;
        event[0]=value+9;
        *(int *)(event+2)=row;
        event[4]=0;
        event[5]=1;
        if (!G_h01_46E0 && G_h01_4188!=2)
            event[6]=2;
        else
            event[6]=1;
        *(int *)(event+8)=G_h01_4274[row-14].first;
        *(int *)(event+10)=G_h01_4274[row-14].second;
        F_h00_57D2(104);
        goto done;
mode2_done:
        goto done;
    }
    goto again;

done:
    ;
}

