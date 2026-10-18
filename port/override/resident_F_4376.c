/* Port version of src/recovered/resident/resident_F_4376.c (input poll).
   The original reads the joystick from JOY1DAT (0xdff00c) and the fire button from
   CIA-A PRA (word at 0xbfe0fe); here the platform supplies both, and the rest is the
   recovered function unchanged. */
#include "aztec.h"
#include "../amiga.h"

extern int32_t F_h00_4F62();
extern int16_t recon_h00_57D2();   /* F_h00_57D2: sound command entry */
extern int16_t F_h00_0A44();
extern int16_t F_h00_0D36();
extern unsigned char G_h01_1F14[32];
extern int16_t G_h01_1F34;
extern char G_h01_1F36;
extern char G_h01_4704;
extern char G_h01_536E;
extern char G_h01_A7CC;
extern char G_h01_A7CD;
extern char G_h01_B1EA;
extern char G_h01_B1EB;
extern int16_t G_h01_096E;

int16_t F_h00_4376(void)
{
    uint16_t s, joy = platform_joystick();
    uint16_t c;
    int16_t e;

    s = (uint16_t)((platform_fire() ? 0x80 : 0) >> 3);          /* PRA bit 7 is active low */
    s |= (joy & 0x2) << 2;
    s |= (joy & 0x200) >> 7;
    s |= ((joy & 0x1) << 1) ^ (joy & 0x2);
    s |= ((joy & 0x200) >> 9) ^ ((joy & 0x100) >> 8);
    e = G_h01_1F14[s];
    c = (uint16_t)F_h00_4F62();
    switch (c & 0x7f) {
    case 27:
    case 113:
        G_h01_B1EA = 1;
        if (G_h01_A7CC == 0 && G_h01_A7CD == 0) {
            F_h00_0A44();
            e = 0;
        } else {
            e = 0x71;
        }
        break;
    case 13:
    case 32:
        e = G_h01_1F34;
        break;
    case 1: e = 6; G_h01_1F34 = 6; break;
    case 2: case 109: e = 5; G_h01_1F34 = 5; break;
    case 3: e = 4; G_h01_1F34 = 4; break;
    case 4: case 106: e = 7; G_h01_1F34 = 7; break;
    case 5: e = 0; G_h01_1F34 = 0; break;
    case 6: case 107: e = 3; G_h01_1F34 = 3; break;
    case 7: e = 8; G_h01_1F34 = 8; break;
    case 8: case 105: e = 1; G_h01_1F34 = 1; break;
    case 9: e = 2; G_h01_1F34 = 2; break;
    case 112:
        if (G_h01_A7CD == 0 && G_h01_A7CC == 0) {
            F_h00_0D36();
            e = 0;
        } else {
            e = 0x70;
        }
        break;
    case 115:
        if (G_h01_096E == 0) {
            G_h01_096E = 1;
            recon_h00_57D2(0x7f);
        } else {
            G_h01_096E = 0;
            recon_h00_57D2(0x7e);
        }
        break;
    case 78: case 89: case 110: case 121:
        e = (int16_t)c;
        break;
    default:
        G_h01_1F34 = 0;
        break;
    }
    if (G_h01_1F36 == 0)
        G_h01_1F34 = 0;
    if (G_h01_B1EB)
        e |= 0x80;
    if (G_h01_4704 && (e & 0x80))
        G_h01_536E = 1;
    return e;
}
