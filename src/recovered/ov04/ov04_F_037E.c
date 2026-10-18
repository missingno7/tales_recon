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

extern long arc_file;
extern char G_h01_4705;
extern char G_h01_470A;
extern struct Loot G_h01_4732[35];
extern char G_h01_4C82;

extern int request_disk();
extern long Open();
extern int arc_read_index();
extern unsigned int F_h00_463E();
extern long F_h00_291E();
extern long F_h00_0976();
extern int sscanf();
extern int F_h00_3C0E();
extern int Close();

recovered()
{
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
    saved = arc_file;
    request_disk(1);
    arc_file = Open("DT1:loot.arc", 0x3edL);
    arc_read_index(arc_file);
    slot = (struct Slot *)&G_h01_4C82;
    slot->value = 0;
    for (i = 1; i < 35; ++i) {
        loot = (struct Loot *)((char *)&G_h01_470A + (long)i * 40);
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
                loot = (struct Loot *)((char *)&G_h01_470A + (long)i * 40);
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
        slot = (struct Slot *)((char *)&G_h01_4C82 + (long)i * 6);
        if (value == 9)
            G_h01_4705 = ((char *)&i)[1];
        --value;
        result = 0;
        result = F_h00_291E(value, result);
        name = ((struct Object *)result)->name;
        name = F_h00_0976(name, buffer);
        sscanf(buffer, "%d", slot->text);
        slot->value = value;
        F_h00_3C0E(result);
    }
    Close(arc_file);
    arc_file = saved;
    arc_read_index(arc_file);
}
