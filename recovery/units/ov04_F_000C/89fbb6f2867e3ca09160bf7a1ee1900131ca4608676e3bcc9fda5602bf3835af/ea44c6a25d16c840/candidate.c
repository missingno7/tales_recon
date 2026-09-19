struct LinkEntry {
    char *target;
    char pad[8];
};

struct TargetEntry {
    char pad[40];
};

struct ShortTargetEntry {
    char pad[6];
};

struct FlagEntry {
    char value;
    char pad[11];
};

extern struct LinkEntry G_h01_4524[35];
extern struct LinkEntry G_h01_4528[35];
extern char G_h01_470A;
extern char G_h01_4C82;
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];
extern int F_h04_0104();
extern int F_h04_037E();

recovered()
{
    int i;

    for (i = 0; i < 35; i++) {
        G_h01_4524[i].target = (char *)&G_h01_470A + (long)i * 40;
        G_h01_4528[i].target = (char *)&G_h01_4C82 + (long)i * 6;
        G_h01_452E[i].value = 0;
        G_h01_452F[i].value = 0;
    }
    F_h04_0104();
    F_h04_037E();
}
