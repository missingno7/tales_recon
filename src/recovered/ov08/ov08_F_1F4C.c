struct Entry { unsigned char kind; unsigned char active; int pos; int t; };
struct Slot { int x; int y; int t; char pad[46]; char st; char tail; };
extern struct Entry *G_h01_6F3C;
extern struct Entry G_h01_12B4;
extern struct Entry G_h01_12BA;
extern struct Slot G_h01_6F76[10];
extern char G_h01_6EEE[54];
extern char *G_h01_6EB0;
extern char *G_h01_6EB4;
extern int G_h01_34E2;
extern int G_h01_34E4;
extern int G_h01_6F24;
extern int G_h01_6F28;
extern int G_h01_6F2A;
extern int G_h01_6F2C;
extern int G_h01_6F2E;
extern int G_h01_6F30;
extern int G_h01_6F32;
extern int G_h01_6F34;
extern char G_h01_6F36;
extern char G_h01_6F37;
extern int G_h01_6F38;
extern char G_h01_6F3A;
extern unsigned char G_h01_10ED;
extern char difficulty_level;
extern long total_money;
extern int play_sound();
extern int F_h00_34E0();
extern unsigned int F_h00_463E();
extern int F_h08_1D42();

recovered(P, Q)
int P;
int Q;
{
    int i;
    int unused;
    int k;
    struct Slot *sl;
    struct Entry *e;
    unsigned char n;
    int x;
    int base;

    G_h01_6F37 = 0;
    base = Q < 0 ? 1 : 0;
    for (i = P - base; i < P - base + 5 && i < 25; i++) {
        if (i > 0) {
            e = G_h01_6F3C + i;
            switch (e->kind) {
            case 4:
                sl = &G_h01_6F76[3];
                sl->y = 160 - (i - P) * 40 + Q - 20;
                G_h01_6F76[4].y = 160 - (i - P) * 40 + Q - 16;
                G_h01_6F76[4].st = 0;
                switch (e->active) {
                case 0:
                    x = e->pos;
                    sl->x = x;
                    sl->st = 0;
                    e->active = 1;
                    e->t = 8 + ((2 - difficulty_level) << 3);
                    break;
                case 1:
                    if (--e->t <= 0) {
                        e->active = 2;
                        G_h01_6F76[4].x = e->pos + 16;
                    }
                    sl->st = 0;
                    break;
                case 2:
                    if (--e->t <= 0) {
                        e->active = 3;
                        sl->st = 2;
                        G_h01_6F76[4].x = e->pos + 16;
                        play_sound(21);
                    } else {
                        sl->st = 1;
                    }
                    break;
                case 3:
                    sl->st = 0;
                    G_h01_6F76[4].x -= 16;
                    if (G_h01_6F76[4].x < 0) {
                        e->active = 0;
                    } else if (i == G_h01_6F2A && (G_h01_6F76[4].x >> 4) == G_h01_6F2C && G_h01_6F28 != 22 && G_h01_6F28 != 28 && G_h01_6F2E != 10) {
                        G_h01_6F32 = 2;
                        e->active = 0;
                        G_h01_6F36 = 0;
                        G_h01_6F2E = 8;
                        play_sound(24);
                        play_sound(15);
                    } else {
                        F_h00_34E0(&G_h01_6F76[4]);
                    }
                    break;
                }
                F_h00_34E0(sl);
                break;
            case 2:
                sl = &G_h01_6F76[0];
                sl->y = 160 - (i - P) * 40 + Q - 32;
                x = e->pos;
                sl->x = x;
                sl->st = e->active < 10 ? 0 : 1;
                F_h00_34E0(sl);
                sl = &G_h01_6F76[1];
                sl->y = 160 - (i - P) * 40 + Q - 30;
                x = e->active < 10 ? e->pos + 14 : e->pos - 20;
                sl->x = x;
                switch (e->active) {
                case 0:
                    sl->st = 0;
                    if (i == G_h01_6F2A && G_h01_6F2E != 10) {
                        x = x >> 4;
                        if (G_h01_6F2C >= x && G_h01_6F2C <= x + 3) {
                            if (++e->t >= 20) {
                                e->active = 1;
                                e->t = 0;
                                play_sound(14);
                            }
                        }
                    }
                    break;
                case 1:
                case 2:
                case 3:
                    if (--e->t <= 0) {
                        sl->st = e->active++;
                        e->t = 2;
                    } else {
                        sl->st = e->active - 1;
                    }
                    break;
                case 4:
                    if (--e->t <= 0) {
                        sl->st = 4;
                        e->active = 5;
                        e->t = 3;
                        if (i == G_h01_6F2A) {
                            x = x >> 4;
                            if (G_h01_6F2C >= x && G_h01_6F2C <= x + 3) {
                                G_h01_6F28 = 10;
                                G_h01_6F2E = 9;
                                G_h01_6F32 = 2;
                                G_h01_6F24 += 32;
                            }
                        }
                    } else {
                        sl->st = 3;
                    }
                    break;
                case 5:
                    if (--e->t <= 0) {
                        sl->st = 3;
                        e->active++;
                        e->t = 2;
                    } else {
                        sl->st = 4;
                    }
                    break;
                case 6:
                    if (--e->t <= 0) {
                        sl->st = 2;
                        e->active++;
                        e->t = 2;
                    } else {
                        sl->st = 3;
                    }
                    break;
                case 7:
                    if (--e->t <= 0) {
                        sl->st = 1;
                        e->active++;
                        e->t = 2;
                    } else {
                        sl->st = 2;
                    }
                    break;
                case 8:
                    e->active = 0;
                    sl->st = 1;
                    break;
                case 10:
                    sl->st = 5;
                    if (i == G_h01_6F2A && G_h01_6F2E != 10) {
                        x = x >> 4;
                        if (G_h01_6F2C >= x && G_h01_6F2C <= x + 2) {
                            if (++e->t >= 10) {
                                e->active = 11;
                                e->t = 0;
                                play_sound(14);
                            }
                        }
                    }
                    break;
                case 11:
                case 12:
                case 13:
                    if (--e->t <= 0) {
                        sl->st = e->active++ - 5;
                        e->t = 2;
                    } else {
                        sl->st = e->active - 6;
                    }
                    break;
                case 14:
                    if (--e->t == 0) {
                        sl->st = 9;
                        e->active = 15;
                        e->t = 3;
                        if (i == G_h01_6F2A) {
                            x = x >> 4;
                            if (G_h01_6F2C > x - 1 && G_h01_6F2C < x + 3) {
                                G_h01_6F28 = 4;
                                G_h01_6F2E = 9;
                                G_h01_6EB4 = G_h01_6EEE;
                                G_h01_6F24 -= 32;
                                G_h01_6F32 = 2;
                            }
                        }
                    } else {
                        sl->st = 8;
                    }
                    break;
                case 15:
                    if (--e->t == 0) {
                        sl->st = 8;
                        e->active++;
                        e->t = 2;
                    } else {
                        sl->st = 9;
                    }
                    break;
                case 16:
                    if (--e->t == 0) {
                        sl->st = 7;
                        e->active++;
                        e->t = 2;
                    } else {
                        sl->st = 8;
                    }
                    break;
                case 17:
                    if (--e->t == 0) {
                        sl->st = 6;
                        e->active++;
                        e->t = 2;
                    } else {
                        sl->st = 7;
                    }
                    break;
                case 18:
                    e->active = 10;
                    sl->st = 6;
                    break;
                }
                F_h00_34E0(sl);
                break;
            case 3:
                sl = &G_h01_6F76[2];
                sl->y = 160 - (i - P) * 40 + Q - 36;
                x = e->pos;
                sl->x = x;
                switch (e->active) {
                case 0:
                    sl->st = 0;
                    if (i == G_h01_6F2A) {
                        x = x >> 4;
                        if (G_h01_6F2C >= x && G_h01_6F2C <= x + 2) {
                            if (++e->t >= 10) {
                                e->active = 1;
                                e->t = 0;
                                play_sound(91);
                            }
                        }
                    }
                    break;
                case 1:
                    sl->st = 1;
                    e->t = 5;
                    e->active = 2;
                    break;
                case 2:
                    if (--e->t <= 0) {
                        sl->st = 2;
                        e->t = 5;
                        e->active = 3;
                        G_h01_6F24 += 32;
                        G_h01_6F2E = 9;
                        G_h01_6F28 = 10;
                        G_h01_6EB4 = G_h01_6EEE;
                        G_h01_6F32 = 2;
                    } else {
                        sl->st = 1;
                    }
                    break;
                case 3:
                    if (--e->t <= 0) {
                        sl->st = 3;
                        e->active = 0;
                    } else {
                        sl->st = 2;
                    }
                    break;
                }
                F_h00_34E0(sl);
                break;
            case 6:
                sl = &G_h01_6F76[0];
                sl->y = 160 - (i - P) * 40 + Q - 30;
                x = e->pos;
                sl->x = x;
                sl->st = 0;
                F_h00_34E0(sl);
                sl = &G_h01_6F76[5];
                sl->y = 160 - (i - P) * 40 + Q - 36;
                switch (e->active) {
                case 0:
                    if (i == G_h01_6F2A && G_h01_6F2E != 10) {
                        if (++e->t >= 40) {
                            e->active = 1;
                            e->t = 20;
                            play_sound(18);
                        }
                    }
                    break;
                case 1:
                    e->active = 2;
                    sl->st = 0;
                    F_h00_34E0(sl);
                    G_h01_6F28 = 10;
                    G_h01_6F2E = 9;
                    G_h01_6F32 = 2;
                    G_h01_6EB4 = G_h01_6EEE;
                    if (--e->t <= 0) {
                        e->active = 3;
                    }
                    break;
                case 2:
                    e->active = 1;
                    sl->st = 1;
                    F_h00_34E0(sl);
                    G_h01_6F28 = 11;
                    G_h01_6F2E = 9;
                    G_h01_6F32 = 2;
                    G_h01_6EB4 = G_h01_6EEE;
                    if (--e->t <= 0) {
                        e->active = 3;
                    }
                    break;
                case 3:
                    e->t = 0;
                    e->active = 0;
                    G_h01_6F28 = 10;
                    G_h01_6EB4 = G_h01_6EEE;
                    G_h01_6F2E = 9;
                    G_h01_6F32 = 2;
                    G_h01_6F34 = 0;
                    F_h00_34E0(sl);
                    break;
                }
                break;
            case 1:
                sl = &G_h01_6F76[0];
                sl->y = 160 - (i - P) * 40 + Q - 30;
                x = e->pos;
                sl->x = x;
                sl->st = 0;
                F_h00_34E0(sl);
                if (i == G_h01_6F2A) {
                    x = x >> 4;
                    if (G_h01_6F2C >= x && G_h01_6F2C <= x + 1 && G_h01_6F2E != 10) {
                        G_h01_6F37 = 1;
                        if (e->active == 1) {
                            for (k = i + 1; k < 25; k++) {
                                if (G_h01_6F3C[k].kind == 1) {
                                    G_h01_6F3A = k;
                                    G_h01_6F38 = G_h01_6F3C[k].pos & 0xfff0;
                                    break;
                                }
                            }
                        } else {
                            for (k = i - 1; k > 0; k--) {
                                if (G_h01_6F3C[k].kind == 1) {
                                    G_h01_6F3A = k;
                                    G_h01_6F38 = G_h01_6F3C[k].pos & 0xfff0;
                                    break;
                                }
                            }
                        }
                    }
                }
                break;
            case 8:
                sl = &G_h01_6F76[7];
                sl->y = 160 - (i - P) * 40 + Q - 29;
                x = e->pos;
                sl->x = x;
                sl->st = 0;
                F_h00_34E0(sl);
                break;
            case 9:
                sl = &G_h01_6F76[8];
                sl->y = 160 - (i - P) * 40 + Q - 12;
                x = e->pos;
                sl->x = x;
                sl->st = 0;
                if (e->active == 0) {
                    F_h00_34E0(sl);
                    if (i == G_h01_6F2A && G_h01_6F2E != 10) {
                        x = x >> 4;
                        if (G_h01_6F2C >= x && G_h01_6F2C <= x + 1) {
                            e->active = 1;
                            play_sound(32);
                            total_money += 50;
                            F_h08_1D42();
                        }
                    }
                }
                break;
            default:
                break;
            }
        }
    }

    e = &G_h01_12B4;
    sl = &G_h01_6F76[6];
    switch (e->active) {
    case 0:
        if ((unsigned char)G_h01_10ED > 100 - (20 << difficulty_level)) {
            x = G_h01_6F30 == 0 ? G_h01_6F24 : G_h01_6F24 - 16;
            if (x < 0) {
                x = 0;
            } else if (x >= 320 - sl->t) {
                x = 320 - (sl->t << 3);
            }
            e->active = 1;
            G_h01_10ED = 0;
            sl->y = -30;
        }
        break;
    case 1:
        x = e->pos;
        e->pos = x;
        sl->x = x;
        sl->st = 0;
        sl->y += 2;
        F_h00_34E0(sl);
        if (e->t & 1)
            sl->st = 2;
        else
            sl->st = 3;
        F_h00_34E0(sl);
        if (sl->y >= 0) {
            sl->y = 0;
            e->active = 2;
            e->t = 40;
            play_sound(13);
        }
        break;
    case 2:
        x = e->pos;
        if (G_h01_6F30 == 0) {
            if (x < G_h01_6F24) {
                x += 8;
            } else if (x > G_h01_6F24) {
                x -= 8;
            }
        } else {
            if (x < G_h01_6F24 - 16) {
                x += 8;
            } else if (x > G_h01_6F24 - 16) {
                x -= 8;
            }
        }
        if (x < 0) {
            x = 0;
        } else if (x > 320 - sl->t) {
            x = 320 - (sl->t << 3);
        }
        e->pos = x;
        sl->x = x;
        sl->st = 0;
        F_h00_34E0(sl);
        if (e->t & 1)
            sl->st = 2;
        else
            sl->st = 3;
        F_h00_34E0(sl);
        if (--e->t <= 0 && G_h01_6F2E != 7) {
            e->active = 4;
            e->t = 0;
        }
        break;
    case 4:
        sl->x = e->pos;
        sl->st = 1;
        F_h00_34E0(sl);
        if (e->t & 1)
            sl->st = 2;
        else
            sl->st = 3;
        F_h00_34E0(sl);
        sl = &G_h01_6F76[4];
        sl->st = 1;
        sl->x = e->pos + 18;
        sl->y = 40;
        F_h00_34E0(sl);
        e->t = 5;
        e->active = 5;
        play_sound(11);
        break;
    case 5:
        sl->x = e->pos;
        sl->st = 1;
        F_h00_34E0(sl);
        if (e->t & 1)
            sl->st = 2;
        else
            sl->st = 3;
        F_h00_34E0(sl);
        sl = &G_h01_6F76[4];
        sl->st = 1;
        sl->x = e->pos + 18;
        sl->y = e->t++ << 3;
        if (sl->y + 16 > 168) {
            sl->y = 152;
            e->active = 0;
            play_sound(0);
        }
        F_h00_34E0(sl);
        if ((160 - sl->y) / 40 + P == G_h01_6F2A) {
            x = sl->x >> 4;
            if ((G_h01_6F2C == x && G_h01_6F2E != 10) || (G_h01_6F28 == 22 && G_h01_6F2C + 1 == x) || (G_h01_6F28 == 28 && G_h01_6F2C - 1 == x)) {
                G_h01_6EB4 = G_h01_6EEE;
                G_h01_6F28 = G_h01_6F30 == 0 ? 5 : 11;
                G_h01_6F2E = 8;
                G_h01_6F32 = 2;
                play_sound(56);
                play_sound(15);
                e->active = 0;
            }
        }
        G_h01_10ED = 0;
        break;
    }

    e = &G_h01_12BA;
    sl = &G_h01_6F76[9];
    x = e->pos;
    switch (e->active) {
    case 0:
        if (--e->t <= 0) {
            G_h01_34E2 = 24;
            G_h01_34E4 = 40;
            sl->st = 0;
            e->pos = F_h00_463E() % 320 & 0xfff0;
            e->active = 1;
            if ((G_h01_34E2 - G_h01_6F2A < 0 ? -(G_h01_34E2 - G_h01_6F2A) : G_h01_34E2 - G_h01_6F2A) < 4) {
                play_sound(11);
            }
        }
        break;
    case 1:
        G_h01_34E4 -= 8;
        if (G_h01_34E4 < 0) {
            x = e->pos;
            if (G_h01_6EB0[(long)G_h01_34E2 * 21 + (x >> 4)] != 0x46) {
                if (x > 160)
                    e->active = 3;
                else
                    e->active = 2;
                if ((G_h01_34E2 - G_h01_6F2A < 0 ? -(G_h01_34E2 - G_h01_6F2A) : G_h01_34E2 - G_h01_6F2A) < 6) {
                    play_sound(28);
                }
                if (G_h01_34E2 - P == 0) {
                    G_h01_34E4 = 0;
                }
            } else {
                G_h01_34E2--;
                G_h01_34E4 = 40;
            }
        }
        break;
    case 2:
        e->pos += 2;
        x = e->pos;
        G_h01_34E4 = -2;
        sl->st++;
        if ((unsigned char)sl->st > 2) {
            sl->st = 0;
        }
        if (x <= 0) {
            e->pos = 0;
            e->active = 0;
            e->t = 5;
            break;
        }
        if (x + 16 >= 320) {
            e->pos = 303;
            e->active = 0;
            e->t = 5;
        }
        if (G_h01_6EB0[(long)G_h01_34E2 * 21 + (x >> 4)] == 0x46) {
            G_h01_34E2--;
            G_h01_34E4 = 40;
            e->active = 1;
            if ((G_h01_34E2 - G_h01_6F2A < 0 ? -(G_h01_34E2 - G_h01_6F2A) : G_h01_34E2 - G_h01_6F2A) < 4) {
                play_sound(11);
            }
        } else if (G_h01_6F2A == G_h01_34E2) {
            if (((G_h01_6F2C << 4) - x < 0 ? -((G_h01_6F2C << 4) - x) : (G_h01_6F2C << 4) - x) < 8 && G_h01_6F2E != 2 && G_h01_6F2E != 3) {
                G_h01_6EB4 = G_h01_6EEE;
                G_h01_6F28 = G_h01_6F30 == 0 ? 5 : 11;
                G_h01_6F2E = 8;
                G_h01_6F32 = 2;
                play_sound(56);
                play_sound(15);
            }
        }
        break;
    case 3:
        e->pos -= 2;
        G_h01_34E4 = -2;
        sl->st--;
        if (sl->st < 0) {
            sl->st = 2;
        }
        x = e->pos;
        if (x <= 0) {
            e->pos = 0;
            e->active = 0;
            e->t = 5;
            break;
        }
        if (x + 16 >= 320) {
            e->pos = 303;
            e->active = 0;
            e->t = 5;
        }
        if (G_h01_6EB0[(long)G_h01_34E2 * 21 + (x >> 4)] == 0x46) {
            G_h01_34E2--;
            G_h01_34E4 = 40;
            e->active = 1;
            if ((G_h01_34E2 - G_h01_6F2A < 0 ? -(G_h01_34E2 - G_h01_6F2A) : G_h01_34E2 - G_h01_6F2A) < 4) {
                play_sound(11);
            }
        } else if (G_h01_6F2A == G_h01_34E2) {
            if (((G_h01_6F2C << 4) - x < 0 ? -((G_h01_6F2C << 4) - x) : (G_h01_6F2C << 4) - x) < 8 && G_h01_6F2E != 2 && G_h01_6F2E != 3) {
                G_h01_6EB4 = G_h01_6EEE;
                G_h01_6F28 = G_h01_6F30 == 0 ? 5 : 11;
                G_h01_6F2E = 8;
                G_h01_6F32 = 2;
                play_sound(56);
                play_sound(15);
            }
        }
        break;
    }

    if (e - n) {
        if (G_h01_34E2 < P + 5 && G_h01_34E2 >= P) {
            sl->x = e->pos;
            sl->y = 160 - (G_h01_34E2 - P) * 40 + Q - G_h01_34E4 - 14;
            if (sl->x >= 0 && sl->x < 304) {
                F_h00_34E0(sl);
            }
        }
    }
}
