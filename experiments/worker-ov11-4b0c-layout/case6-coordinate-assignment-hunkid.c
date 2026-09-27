/* Isolated source-shape probe for ov11_F_4B0C; no source ownership claimed. */
struct Descriptor { long object; char pad4; char state; int type; char pad8[4]; int dy; int dx; };
struct Object { char pad[52]; char state; };
extern struct Descriptor G_h01_94EC[110];
extern int G_h01_94B0; extern int G_h01_94B2; extern int G_h01_94B4; extern int G_h01_94B6; extern int G_h01_94B8;
extern int G_h01_94BE; extern int G_h01_94C0; extern int G_h01_94C2; extern int G_h01_94D8;
extern struct Object *G_h01_94DA; extern int G_h01_94DE; extern int G_h01_94E0; extern int G_h01_94E2;
extern int G_h01_94E4; extern int G_h01_94E6; extern struct Descriptor *G_h01_94E8;
extern struct Object *G_h01_9F4E; extern struct Object *G_h01_9F52;
extern struct Object *G_h01_9F52; extern struct Object *G_h01_9F4E;
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
    case 20: G_h01_94E2 = 7; G_h01_94E8 = (&G_h01_94EC[102]); break;
    case 21: G_h01_94E2 = 7; G_h01_94E8 = (&G_h01_94EC[109]); break;
    case 6: F_h00_57D2(0x58); G_h01_94C0 = 0x8e; G_h01_94E2 = 5; G_h01_94E8 = (&G_h01_94EC[97]); break;
    case 19: G_h01_94E2 = 3; G_h01_94E8 = (&G_h01_94EC[93]); break;
    case 18: G_h01_94E2 = 5; if (G_h01_94B2 == 0) G_h01_94E8 = (&G_h01_94EC[83]); else G_h01_94E8 = (&G_h01_94EC[88]); F_h00_57D2(0x64); break;
    case 17: G_h01_94E2 = 2; G_h01_94E8 = (&G_h01_94EC[79]); break;
    case 16: G_h01_94E2 = 2; G_h01_94E8 = (&G_h01_94EC[81]); break;
    case 14: G_h01_94E2 = 1; G_h01_94E8 = (&G_h01_94EC[96]); break;
    case 13: G_h01_94E2 = 7; G_h01_94E8 = (&G_h01_94EC[49]); break;
    case 12: G_h01_94E2 = 7; G_h01_94E8 = (&G_h01_94EC[42]); break;
    case 5: G_h01_94E2 = 0; if (G_h01_94B2 == 0) G_h01_94E8 = (&G_h01_94EC[58]); else G_h01_94E8 = (&G_h01_94EC[57]); break;
    case 4: G_h01_94E2 = 8; if (G_h01_94B2 == 1) G_h01_94E8 = (&G_h01_94EC[25]); else G_h01_94E8 = (&G_h01_94EC[33]); break;
    case 3: G_h01_94E2 = 9; if (G_h01_94B2 == 1) G_h01_94E8 = (&G_h01_94EC[61]); else G_h01_94E8 = (&G_h01_94EC[73]); break;
    case 10: G_h01_94E2 = 3; if (G_h01_94B2 == 1) G_h01_94E8 = (&G_h01_94EC[40]); else G_h01_94E8 = (&G_h01_94EC[43]); break;
    case 1:
        if (G_h01_94B4 != 0) { G_h01_94DE = 0; G_h01_94E2 = 5; }
        else { G_h01_94DE = 5; G_h01_94E2 = 10; }
        if (G_h01_94B2 == 1) G_h01_94E8 = &G_h01_94EC[G_h01_94DE];
        else G_h01_94E8 = &G_h01_94EC[11+G_h01_94DE];
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
