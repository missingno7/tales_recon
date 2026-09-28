extern short G_h01_94AE;
extern short G_h01_94B0;
extern short G_h01_94B4;
extern short G_h01_94BA;
extern short G_h01_94BC;
extern short G_h01_94BE;
extern short G_h01_94C0;
extern short G_h01_8A3C;
extern short G_h01_8B1C[40][4];
extern short G_h01_940C[1];
extern long G_h01_46E6;
extern int F_h11_25D6();
extern int F_h00_57D2();
extern int F_h11_5A12();
extern int F_h11_5A62();
extern int F_h11_4B0C();

recovered()
{
    int tile, xpos, offset, ypos;

    offset = (8 >> G_h01_94B0) + G_h01_94BE;
    if (((G_h01_94C0 + 14) >> 5) < 3) {
        if ((tile = G_h01_8B1C[G_h01_94BA][((G_h01_94C0 + 14) >> 5)]) != 0 &&
            G_h01_940C[tile] != 0) {
            xpos = G_h01_94BA * 53;
            ypos = (((G_h01_94C0 + 14) >> 5) << 5) + 0x30;
            if (F_h11_25D6(xpos + 0x0f, offset, xpos + 0x21) &&
                F_h11_25D6(ypos - 0x0f, G_h01_94C0 + 0x12, ypos)) {
                F_h00_57D2(0x20);
                G_h01_940C[tile] = 0;
                G_h01_46E6 += 0x32;
                G_h01_8A3C = 3;
            }
        }
    }

    switch (G_h01_94AE) {
    case 1:
    case 5:
        if (G_h01_94B4 == 0)
            goto ov11_mode_ok;
        break;
ov11_mode_ok:
        if (G_h01_8B1C[G_h01_94BA][((G_h01_94C0 + 14) >> 5)] != 0)
            break;
        if (G_h01_94BC >= 3)
            break;
        if (G_h01_8B1C[G_h01_94BA - 1][((G_h01_94C0 + 14) >> 5)] != 0) {
            if (offset + 1 >= F_h11_5A12(0, G_h01_94BA - 1))
                goto ov11_left_ok;
            break;
        }
ov11_left_ok:
        if (G_h01_8B1C[G_h01_94BA + 1][((G_h01_94C0 + 14) >> 5)] != 0) {
            if (offset + 4 <= F_h11_5A62(0, G_h01_94BA + 1))
                goto ov11_right_ok;
            break;
        }
ov11_right_ok:
        G_h01_94AE = 2;
        F_h11_4B0C(2);
        break;
    }
}






