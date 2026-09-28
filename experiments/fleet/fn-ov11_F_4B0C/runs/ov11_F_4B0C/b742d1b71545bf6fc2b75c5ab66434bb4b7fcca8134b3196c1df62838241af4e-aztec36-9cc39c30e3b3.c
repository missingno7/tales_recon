/* Isolated source-shape probe for ov11_F_4B0C; no source ownership claimed. */
struct Descriptor { long object; char pad4; char state; int type; char pad8[4]; int dy; int dx; };
struct Object { char pad[52]; char state; };
extern int G_h01_94B0; extern int G_h01_94B2; extern int G_h01_94B4; extern int G_h01_94B6; extern int G_h01_94B8;
extern int G_h01_94BE; extern int G_h01_94C0; extern int G_h01_94C2; extern int G_h01_94D8;
extern struct Object *G_h01_94DA; extern int G_h01_94DE; extern int G_h01_94E0; extern int G_h01_94E2;
extern int G_h01_94E4; extern int G_h01_94E6; extern struct Descriptor *G_h01_94E8;
extern struct Object *G_h01_9F4E; extern struct Object *G_h01_9F52;
extern struct Descriptor G_h01_94EE[1]; extern struct Descriptor G_h01_958E[1];
extern struct Descriptor G_h01_962E[1]; extern struct Descriptor G_h01_96AE[1];
extern struct Descriptor G_h01_972E[1]; extern struct Descriptor G_h01_978E[1];
extern struct Descriptor G_h01_975E[1]; extern struct Descriptor G_h01_97FE[1];
extern struct Descriptor G_h01_986E[1]; extern struct Descriptor G_h01_987E[1];
extern struct Descriptor G_h01_98BE[1]; extern struct Descriptor G_h01_994E[1];
extern struct Descriptor G_h01_99DE[1]; extern struct Descriptor G_h01_99FE[1];
extern struct Descriptor G_h01_9A1E[1]; extern struct Descriptor G_h01_9A6E[1];
extern struct Descriptor G_h01_9ABE[1]; extern struct Descriptor G_h01_9AEE[1];
extern struct Descriptor G_h01_9AFE[1]; extern struct Descriptor G_h01_9B4E[1];
extern struct Descriptor G_h01_9BBE[1]; extern struct Object *G_h01_9F52; extern struct Object *G_h01_9F4E;
extern int F_h00_57D2(); extern int F_h11_6ED6();

recovered(mode)
int mode;
{
    int x;
    int y;
    G_h01_94DE = 0;
    G_h01_94E4 = 0;
    G_h01_94E6 = 1;
    G_h01_94E8 = 0;
    switch (mode) {
    case 20: G_h01_94E2 = 7; G_h01_94E8 = G_h01_9B4E; break;
    case 21: G_h01_94E2 = 7; G_h01_94E8 = G_h01_9BBE; break;
    case 6: F_h00_57D2(0x58); G_h01_94E2 = 5; G_h01_94E8 = G_h01_9AFE; break;
    case 19: G_h01_94E2 = 3; G_h01_94E8 = G_h01_9ABE; break;
    case 18: G_h01_94E2 = 5; if (G_h01_94B2 == 0) G_h01_94E8 = G_h01_9A1E; else G_h01_94E8 = G_h01_9A6E; F_h00_57D2(0x64); break;
    case 17: G_h01_94E2 = 2; G_h01_94E8 = G_h01_99DE; break;
    case 16: G_h01_94E2 = 2; G_h01_94E8 = G_h01_99FE; break;
    case 14: G_h01_94E2 = 1; G_h01_94E8 = G_h01_9AEE; break;
    case 5: G_h01_94E2 = 0; if (G_h01_94B2 == 0) G_h01_94E8 = G_h01_987E; else G_h01_94E8 = G_h01_986E; break;
    case 13: G_h01_94E2 = 7; G_h01_94E8 = G_h01_97FE; break;
    case 12: G_h01_94E2 = 7; G_h01_94E8 = G_h01_978E; break;
    case 3: G_h01_94E2 = 9; if (G_h01_94B2 == 1) G_h01_94E8 = G_h01_98BE; else G_h01_94E8 = G_h01_994E; break;
    case 10: G_h01_94E2 = 3; if (G_h01_94B2 == 1) G_h01_94E8 = G_h01_972E; else G_h01_94E8 = G_h01_975E; break;
    case 4: G_h01_94E2 = 8; if (G_h01_94B2 == 1) G_h01_94E8 = G_h01_962E; else G_h01_94E8 = G_h01_96AE; break;
    case 1:
        if (G_h01_94B4 != 0) { G_h01_94DE = 0; G_h01_94E2 = 5; }
        else { G_h01_94DE = 5; G_h01_94E2 = 10; }
        if (G_h01_94B2 == 1) G_h01_94E8 = &G_h01_94EE[G_h01_94DE];
        else G_h01_94E8 = &G_h01_958E[G_h01_94DE];
        break;
    case 2:
        G_h01_94B8 = 0; G_h01_94B6 = 0; G_h01_94E2 = 0; G_h01_94DA = G_h01_9F52;
        if (G_h01_94B2 == 1) G_h01_94DA->state = 1; else G_h01_94DA->state = 3;
        F_h00_57D2(0xf); break;
    case 8:
        G_h01_94E2 = 1; G_h01_94DA = G_h01_9F4E;
        F_h11_6ED6(G_h01_94D8, &x, &y, &G_h01_94BE, &G_h01_94C0);
        if (G_h01_94C0 < x) {
            if (G_h01_94B2 == 1) G_h01_94DA->state = 0x1c; else G_h01_94DA->state = 0x1e;
            if (G_h01_94B2 == 1) { G_h01_94C0 -= 12; G_h01_94C2 += 8; }
            else { G_h01_94C0 -= 3; G_h01_94C2 += 9; }
        } else if (G_h01_94C0 > x) {
            if (G_h01_94B2 == 1) G_h01_94DA->state = 0x1d; else G_h01_94DA->state = 0x1f;
            if (G_h01_94B2 == 1) { G_h01_94C0 += 0; G_h01_94C2 += 10; }
            else { G_h01_94C0 += 10; G_h01_94C2 += 17; }
        } else {
            if (G_h01_94B2 == 1) G_h01_94DA->state = 0x17; else G_h01_94DA->state = 0x1b;
            if (G_h01_94B2 == 1) { G_h01_94C0 -= 6; G_h01_94C2 += 22; }
            else { G_h01_94C0 += 1; G_h01_94C2 += 22; }
        }
        G_h01_94C0 -= 6; G_h01_94C2 -= 21; break;
    case 45: G_h01_94E2 = 0; break;
    }
    if (G_h01_94E8 != 0) {
        G_h01_94DA = G_h01_94E8->object;
        G_h01_94C0 += G_h01_94E8->dy;
        G_h01_94C2 += G_h01_94E8->dx;
        G_h01_94DA->state = G_h01_94E8->state;
        G_h01_94E4 = G_h01_94E8->type;
    }
}
