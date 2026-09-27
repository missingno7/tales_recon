extern int F_h00_0976();
extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_291E();
extern int F_h00_3C0E();
extern int F_h00_463E();
extern int F_h00_704E();
extern int F_h00_868C();
extern int F_h00_86DC();
extern long G_h01_0012;
extern long G_h01_001E;
extern long G_h01_002A;
extern long G_h01_0030;
extern long G_h01_0096;
extern long G_h01_00A8;
extern long G_h01_00D2;
extern long G_h01_0114;
extern long G_h01_0120;
extern long G_h01_46DA;
extern long G_h01_4D60;
extern long G_h01_4D62;
extern long G_h01_4D82;
extern long G_h01_4D84;
extern long G_h01_4D86;
extern long G_h01_4D88;
extern long G_h01_5014;
recovered()
{
    short samples[15];
    char line[145];
    long handle, item;
    int row, col;
    handle = F_h00_86DC("DT1:invest.arc", 1005);
    F_h00_2816(8);
    G_h01_46DA = handle;
    F_h00_291E(handle);
    for (row=0; row<15; row++) {
        samples[row] = -1;
        item = F_h00_0976(handle, row);
        if (item) {
            F_h00_0976(item, &samples[row]);
            for (col=0; col<5; col++) {
                F_h00_463E(row, col, item);
                F_h00_704E("%d %d", line, row, col);
            }
        }
    }
    handle = F_h00_86DC("DT1:chart.arc", 1005);
    F_h00_2816(8);
    F_h00_291E(handle);
    for (row=0; row<15; row++) {
        for (col=0; col<30; col++) {
            F_h00_463E(row, col, handle);
            F_h00_704E("%d", line, col);
        }
    }
    F_h00_0FDE(1);
}
