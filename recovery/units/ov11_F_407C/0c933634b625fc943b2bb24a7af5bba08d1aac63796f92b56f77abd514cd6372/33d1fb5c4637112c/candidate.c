/* Direct reconstruction candidate for ov11_F_407C. */
struct Record407C {
    char f407_pad0[12];
    int f407_value12;
    int f407_value14;
    char f407_pad1[16];
};

extern struct Record407C G_h01_A15E[1];
extern int F_h11_40E0();

recovered(index)
int index;
{
    G_h01_A15E[index].f407_value12 = G_h01_A15E[index].f407_value14;
    F_h11_40E0(index, 6);
}