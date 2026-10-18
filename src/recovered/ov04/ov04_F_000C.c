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

extern struct LinkEntry map_location_table[35];
extern struct LinkEntry G_h01_4528[35];
extern char location_records;
extern char location_treasure_slots;
extern struct FlagEntry player_treasure_collected[35];
extern struct FlagEntry rival_treasure_collected[35];
extern int arc_load_locations();
extern int arc_load_treasures();

recovered()
{
    int i;

    for (i = 0; i < 35; i++) {
        map_location_table[i].target = (char *)&location_records + (long)i * 40;
        G_h01_4528[i].target = (char *)&location_treasure_slots + (long)i * 6;
        player_treasure_collected[i].value = 0;
        rival_treasure_collected[i].value = 0;
    }
    arc_load_locations();
    arc_load_treasures();
}
