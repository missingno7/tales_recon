struct Record { int amount; char reserved[4]; int category; char rest[38]; };
extern struct Record G_h01_4D82[16];
extern unsigned char G_h01_5014[16][31];
extern char G_h01_46E1;
recovered(n) int n;
{
    int result, amount, percent;
    amount = G_h01_4D82[n].amount;
    percent = G_h01_5014[G_h01_4D82[n].category][G_h01_46E1-1];
    result = amount * percent / 100;
    if (result <= 0 && percent > 0) result = 1;
    return result;
}
