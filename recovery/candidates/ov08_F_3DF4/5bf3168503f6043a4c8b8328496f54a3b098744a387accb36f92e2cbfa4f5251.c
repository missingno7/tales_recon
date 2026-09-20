extern char G_h01_6F40[1];
extern int F_h00_0FDE();
extern int F_h00_291E();

recovered()
{
    int i;

    F_h00_0FDE(2);
    for (i = 1; i < 11; ++i) {
        switch (i) {
        case 1: F_h00_291E(5, G_h01_6F40 + (long)i * 54); break;
        case 2: F_h00_291E(6, G_h01_6F40 + (long)i * 54); break;
        case 3: F_h00_291E(7, G_h01_6F40 + (long)i * 54); break;
        case 4: F_h00_291E(8, G_h01_6F40 + (long)i * 54); break;
        case 5: F_h00_291E(9, G_h01_6F40 + (long)i * 54); break;
        case 6: F_h00_291E(10, G_h01_6F40 + (long)i * 54); break;
        case 7: F_h00_291E(11, G_h01_6F40 + (long)i * 54); break;
        case 8: F_h00_291E(13, G_h01_6F40 + (long)i * 54); break;
        case 9: F_h00_291E(14, G_h01_6F40 + (long)i * 54); break;
        case 10: F_h00_291E(15, G_h01_6F40 + (long)i * 54); break;
        }
    }
}