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
extern char bombastium_location_index;
extern char location_records;
extern struct Loot G_h01_4732[35];
extern char location_treasure_slots;

extern int request_disk();
extern long Open();
extern int arc_read_index();
extern unsigned int F_h00_463E();
extern long load_arc_record();
extern long F_h00_0976();
extern int sscanf();
extern int free_text_block();
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
    slot = (struct Slot *)&location_treasure_slots;
    slot->value = 0;
    for (i = 1; i < 35; ++i) {
        loot = (struct Loot *)((char *)&location_records + (long)i * 40);
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
                loot = (struct Loot *)((char *)&location_records + (long)i * 40);
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
        slot = (struct Slot *)((char *)&location_treasure_slots + (long)i * 6);
        if (value == 9)
            bombastium_location_index = ((char *)&i)[1];
        --value;
        result = 0;
        result = load_arc_record(value, result);
        name = ((struct Object *)result)->name;
        name = F_h00_0976(name, buffer);
        sscanf(buffer, "%d", slot->text);
        slot->value = value;
        free_text_block(result);
    }
    Close(arc_file);
    arc_file = saved;
    arc_read_index(arc_file);
}
