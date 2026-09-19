struct LinkEntry {
    char *target;
    char pad[8];
};

struct TargetEntry {
    char pad[40];
};

extern struct LinkEntry G_h01_4524[36];
extern struct TargetEntry G_h01_4528[36];
extern char G_h01_452E[432];
extern char G_h01_452F[432];
extern F_h04_0104();
extern F_h04_037E();

recovered()
{
    int i;

    for (i = 0; i < 36; i++) {
        G_h01_4524[i].target = (char *)&G_h01_4528[i];
        G_h01_452E[i * 12] = 0;
        G_h01_452F[i * 12] = 0;
    }
    F_h04_0104();
    F_h04_037E();
}
