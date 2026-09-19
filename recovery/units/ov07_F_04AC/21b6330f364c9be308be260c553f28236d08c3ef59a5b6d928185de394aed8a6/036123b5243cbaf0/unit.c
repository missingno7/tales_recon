struct PortfolioRow {
    char name[34];
    int value;
    char rest[10];
};

extern int F_h00_35DC();
extern int F_h00_09C0();
extern int F_h07_0EC0();
extern struct PortfolioRow G_h01_4D62[16];

recovered(start, selected)
int start;
int selected;
{
    int i;
    int slot;
    int value;
    char scratch[16];
    int y;
    unsigned char color;

    y = 40;
    for (i = start; i < start + 6; i++) {
        slot = i & 15;
        color = 0;
        if (slot == selected)
            color = 9;
        F_h00_35DC(32, y, "                                ", 1, color);
        if (slot == 15)
            F_h00_35DC(32, y, "RETURN TO OFFICE", 15, color);
        else {
            value = F_h07_0EC0(slot);
            F_h00_09C0(248, y, (long)value, 1, color, 1);
            F_h00_35DC(32, y, G_h01_4D62[slot].name, 1, color);
            F_h00_09C0(280, y, (long)G_h01_4D62[slot].value, 1, color, 1);
        }
        y += 20;
    }
}

struct Record { int amount; char reserved[4]; int category; char rest[38]; };
extern struct Record G_h01_4D82[16];
extern unsigned char G_h01_5014[16][31];
extern char G_h01_46E1;
F_h07_0EC0(n) int n;
{
    int result, amount, percent;
    amount = G_h01_4D82[n].amount;
    percent = G_h01_5014[G_h01_4D82[n].category][G_h01_46E1-1];
    result = amount * percent / 100;
    if (result <= 0 && percent > 0) result = 1;
    return result;
}

