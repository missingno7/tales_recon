struct Loot {
    char padding[38];
    int value;
};

struct Slot {
    int value;
    char text[4];
};

struct Object {
    char padding[2];
    long name;
};

extern long G_h01_46DA;
extern char G_h01_4705;
extern struct Loot G_h01_470A[36];
extern struct Loot G_h01_4732[35];
extern struct Slot G_h01_4C82[36];

extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_463E();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern int F_h00_3C0E();
extern int F_h00_868C();

recovered()
{
    char selected;
    int i;
    int probe;
    struct Slot *slot;
    struct Loot *loot;
    long unused;
    long name;
    long result;
    long saved;
    char buffer[81];
    int value;

    result = 0;
    value = 0;
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loot.arc", 0x3edL);
    F_h00_2816(G_h01_46DA);
    slot = G_h01_4C82;
    slot->value = 0;
    for (i = 1; i < 36; ++i) {
        loot = G_h01_470A + i;
        if (loot->value)
            value = loot->value;
        else {
            value = (unsigned)F_h00_463E() % 37 + 1;
again:
            loot = G_h01_4732;
            probe = 1;
            do {
                if (loot->value == value)
                    break;
                ++probe;
                ++loot;
            } while (probe < 35);
            if (probe >= 35) {
                loot = G_h01_470A + i;
                loot->value = value;
            }
            else {
                if ((unsigned)(value + 1) >= 37)
                    value = 1;
                else
                    ++value;
                goto again;
            }
        }
        slot = G_h01_4C82 + i;
        if (value == 9)
            G_h01_4705 = selected;
        --value;
        result = 0;
        result = F_h00_291E(value, result);
        name = ((struct Object *)result)->name;
        name = F_h00_0976(name, buffer);
        F_h00_704E(buffer, "%d", slot->text);
        slot->value = value;
        F_h00_3C0E(result);
    }
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}
