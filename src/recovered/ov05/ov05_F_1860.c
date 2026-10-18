/* ov05_F_1860: per-frame float state machine over G_h01_5E34/5E38 and the 0A7E gain; returns one of two record pointers. */
struct Blob {
    int w0;
    int w2;
    char f4[48];
    char b52;
};
extern struct Blob G_h01_5B5A;
extern struct Blob G_h01_544E;
extern float G_h01_09B2[32];
extern float G_h01_5DAC[32];
extern char G_h01_0A3A[16];
extern char G_h01_0A4A[16];
extern char G_h01_0A5A[16];
extern char G_h01_0A6A[16];
extern float G_h01_0A7E;
extern char G_h01_0A89;
extern int G_h01_0A82;
extern int G_h01_0A84;
extern int G_h01_2F10;
extern int G_h01_2F12;
extern int G_h01_2F14;
extern int G_h01_2F16;
extern int G_h01_5C32;
extern int G_h01_5C34;
extern int G_h01_5C38;
extern float G_h01_5E34;
extern float G_h01_5E38;
extern int G_h01_5E3C;
extern int G_h01_5E3E;
extern int G_h01_5E40;
extern char G_h01_5E41;
extern int G_h01_5E42;
extern int G_h01_5E4C;
extern int G_h01_5E64[1][2];
extern int F_h00_307C();
extern int play_sound();
extern int F_h05_131C();
extern int F_h05_3A9E();

struct Blob *recovered()
{
    struct Blob *p;
    int t;
    float fa;
    float fb;
    int i;
    int flag;

    fa = G_h01_5E34;
    if (G_h01_0A7E != 0) {
        G_h01_5E34 += G_h01_09B2[G_h01_5E40 * 2] * G_h01_0A7E;
        G_h01_5E38 -= G_h01_09B2[G_h01_5E40 * 2 + 1] * G_h01_0A7E;
    }
    if (G_h01_5E40 > 8 && G_h01_5E40 < 16) {
        G_h01_5E34 += G_h01_5DAC[G_h01_5E40 * 2];
        G_h01_5E38 -= G_h01_5DAC[G_h01_5E40 * 2 + 1];
        if (G_h01_5E40 == 12)
            G_h01_0A7E = G_h01_0A7E + 0.6;
        else
            G_h01_0A7E = G_h01_0A7E + 0.4;
    }
    if (G_h01_5E40 > 0 && G_h01_5E40 < 8) {
        G_h01_5E34 -= G_h01_5DAC[G_h01_5E40 * 2];
        G_h01_5E38 += G_h01_5DAC[G_h01_5E40 * 2 + 1];
        if (G_h01_5E40 == 4)
            G_h01_0A7E = G_h01_0A7E + -0.4;
        else
            G_h01_0A7E = G_h01_0A7E + -0.17;
    }
    if (G_h01_5E40 >= 4 && G_h01_5E40 <= 12) {
        if (G_h01_5E3C > 0 && G_h01_0A7E > 0) {
            G_h01_5E40++;
            if (G_h01_5E40 > 15)
                G_h01_5E40 = 0;
        } else if (G_h01_5E3E > 0 && G_h01_0A7E > 2) {
            G_h01_5E40--;
            if (G_h01_5E40 < 0)
                G_h01_5E40 += 16;
        }
    } else {
        if (G_h01_5E3C > 0 && G_h01_0A7E > 2) {
            G_h01_5E40++;
            if (G_h01_5E40 > 15)
                G_h01_5E40 = 0;
        } else if (G_h01_5E3E > 0 && G_h01_0A7E > 0) {
            G_h01_5E40--;
            if (G_h01_5E40 < 0)
                G_h01_5E40 += 16;
        }
    }

    if (G_h01_0A84 < 2 || G_h01_0A84 > G_h01_5E42 - 2)
        t = 0x8b;
    else
        t = 0x90;
    fb = G_h01_5E34 - fa;
    G_h01_5E4C = (int)((float)G_h01_5E4C + fb);
    if (G_h01_5E40 > 4 && G_h01_5E40 < 12)
        flag = 0;
    else
        flag = 1;

    if (G_h01_5E34 > 90 && flag != 0 && G_h01_0A84 < G_h01_5E42 - 2) {
        G_h01_5E4C = (int)((float)G_h01_5E4C + fb);
        G_h01_5E34 = 90.0;
    } else if (G_h01_5E34 < 80 && flag == 0 && G_h01_0A82 != 0) {
        G_h01_5E4C = (int)((float)G_h01_5E4C + fb);
        G_h01_5E34 = 80.0;
    } else if (G_h01_0A84 == G_h01_5E42 && G_h01_5E34 > 288 && G_h01_0A82 + 3 == G_h01_5E42) {
        G_h01_5E4C = 0;
        G_h01_5E34 = 288.0;
        G_h01_5E40 = 8;
    } else if (G_h01_0A84 == 0 && flag == 0 && G_h01_5E34 < 0.0) {
        G_h01_5E34 = 0.0;
        G_h01_5E40 = 0;
        G_h01_5E4C = 0;
    }

    if (G_h01_5E4C > 79) {
        if (G_h01_0A82 + 3 < G_h01_5E42)
            G_h01_0A82++;
        G_h01_5E4C -= 80;
    } else if (G_h01_5E4C < -79) {
        G_h01_5E4C += 80;
        if (G_h01_0A82 > 0)
            G_h01_0A82--;
    }

    if ((G_h01_0A82 + 3 >= G_h01_5E42 && G_h01_5E34 > 80) || (G_h01_0A82 == 0 && G_h01_0A84 < 2 && flag == 0))
        G_h01_5E4C = 0;

    if (G_h01_0A7E < 3 && G_h01_5E38 < (float)t)
        G_h01_5E40 = F_h05_3A9E(G_h01_5E40);
    if (G_h01_5E38 < 0.0) {
        G_h01_5E40 = F_h05_3A9E(G_h01_5E40);
        G_h01_5E38 = 0.0;
    } else if (G_h01_5E38 > (float)t) {
        if (G_h01_0A84 >= G_h01_5E42 - 1 && (G_h01_5E40 > 12 || G_h01_5E40 == 0)) {
            G_h01_5E40 = 0;
            G_h01_5E38 = (float)t;
        } else if (G_h01_0A89 > 1) {
            G_h01_0A7E = 0.0;
            G_h01_5E40 = 0;
            G_h01_5E38 = (float)t;
            p = &G_h01_5B5A;
            p->b52 = 0;
            p->w0 = (int)(G_h01_5E34 + 8);
            p->w2 = (int)(G_h01_5E38 + -14);
            if (G_h01_5E64[G_h01_0A84][0] == 12) {
                play_sound(0x3a);
                G_h01_5C32 = (int)(G_h01_5E34 + -24);
                G_h01_5C34 = 0xb0 - G_h01_5C38 - 8;
                for (i = 1; i < 4; i++) {
                    F_h05_131C(&G_h01_5C32);
                    F_h00_307C();
                }
                return p;
            } else {
                play_sound(0x2b);
                return p;
            }
        } else {
            G_h01_0A89++;
            G_h01_5E38 = (float)(t - 4);
            if (G_h01_5E40 > 11) {
                G_h01_5E40 = 1;
                if (G_h01_0A7E < 4)
                    G_h01_0A7E = 4.0;
            } else if (G_h01_5E40 > 7) {
                G_h01_5E40 = 7;
                if (G_h01_0A7E < 4)
                    G_h01_0A7E = 4.0;
            } else {
                G_h01_5E40 = 5;
                G_h01_0A7E = 5.0;
            }
            play_sound(0x42);
        }
    }

    p = &G_h01_544E;
    p->b52 = G_h01_5E41;
    p->w0 = (int)G_h01_5E34;
    p->w2 = (int)G_h01_5E38;
    G_h01_2F10 = (int)((float)G_h01_0A4A[G_h01_5E40] + G_h01_5E38);
    G_h01_2F12 = (int)((float)G_h01_0A6A[G_h01_5E40] + G_h01_5E38);
    G_h01_2F14 = (int)((float)G_h01_0A3A[G_h01_5E40] + G_h01_5E34);
    G_h01_2F16 = (int)((float)G_h01_0A5A[G_h01_5E40] + G_h01_5E34);
    G_h01_5E3E = 0;
    G_h01_5E3C = 0;
    return p;
}
