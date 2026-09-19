/* Direct reconstruction candidate for ov11_F_407C. */
struct Record {
    char pad0[12];
    int value12;
    int value14;
    char pad1[16];
};

extern struct Record G_h01_A15E[1];
extern int F_h11_40E0();

recovered(index)
int index;
{
    G_h01_A15E[index].value12 = G_h01_A15E[index].value14;
    F_h11_40E0(index, 6);
}