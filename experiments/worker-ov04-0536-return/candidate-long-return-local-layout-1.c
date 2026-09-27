extern int F_h00_0976();
extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_291E();
extern int F_h00_3C0E();
extern int F_h00_463E();
extern int F_h00_704E();
extern int F_h00_868C();
extern long F_h00_86DC();
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
extern char G_h01_4D60;
extern char G_h01_5014[30][31];
extern char G_h01_4D62[15][46];
extern short G_h01_4D82[15][23];
extern short G_h01_4D84[15][23];
extern short G_h01_4D86[15][23];
extern short G_h01_4D88[15][23];
struct Row {
    char prefix[32];
    short first;
    short second;
    short third;
    short fourth;
    char tail[6];
};
recovered()
{
    long file, rowptr, data;
    int i, j, k;
    short local_a, local_b;
    short status[15];
    long local_c;
    long previous;
    long local_pad[2];
    char line[77];
    previous = G_h01_46DA;
    G_h01_4D60 = 0;
    F_h00_0FDE(1);
    file = F_h00_86DC("DT1:invest.arc", 1005L);
    G_h01_46DA = file;
    F_h00_2816(file);
    for (i=0; i<15; ++i) status[i] = -1;
    for (i=0; i<15; ++i) {
        rowptr = F_h00_0976(file, i);
        if (rowptr) {
            data = F_h00_0976(rowptr, &status[i]);
            G_h01_4D62[i][0] = 0;
            F_h00_463E(i, rowptr);
            F_h00_463E(i, &status[i]);
            for (j=0; j<15; ++j) {
                G_h01_4D82[i][j] = F_h00_0976(data, j);
                G_h01_4D84[i][j] = G_h01_4D82[i][j];
                G_h01_4D86[i][j] = G_h01_4D84[i][j];
                G_h01_4D88[i][j] = G_h01_4D86[i][j];
            }
            F_h00_704E("%d %d", line, rowptr, i, status[i]);
        }
    }
    file = F_h00_86DC("DT1:chart.arc", 1005L);
    F_h00_2816(8);
    F_h00_291E(file);
    for (i=0; i<15; ++i) {
        for (j=0; j<30; ++j) {
            rowptr = F_h00_0976(file, i);
            k = F_h00_0976(rowptr, j);
            G_h01_5014[j][i] = k;
        }
        F_h00_704E("%d", line, file, i);
        F_h00_463E(line, i);
    }
}
