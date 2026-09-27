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
    short price[15];
    char text[145];
    long file, chart, record;
    int i;
    G_h01_4D60 = 0;
    file = F_h00_86DC("DT1:invest.arc", 1005);
    F_h00_2816(8);
    G_h01_46DA = file;
    F_h00_291E(file);
    for (i=0; i<15; ++i) price[i] = -1;
    for (i=0; i<15; ++i) {
        record = F_h00_0976(file, i);
        if (record) {
            F_h00_0976(record, &price[i]);
            F_h00_463E(i, record);
            F_h00_463E(i, &price[i]);
            F_h00_704E("%d %d", text, record, i, price[i]);
        }
    }
    chart = F_h00_86DC("DT1:chart.arc", 1005);
    F_h00_2816(8);
    F_h00_291E(chart);
    for (i=0; i<5; ++i) {
        F_h00_704E("%d", text, chart, i);
        F_h00_463E(text, i);
    }
    F_h00_0FDE(1);
}
