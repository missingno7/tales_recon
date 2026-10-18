struct Entry { unsigned char kind; char active; char rest[4]; };
extern struct Entry *grid_entity_state_table;
extern char G_h01_12B5;
extern char G_h01_12BB;
recovered()
{
    int i, kind;
    i = 0;
    do {
        kind = grid_entity_state_table[i].kind;
        if (kind == 6 || kind == 4)
            grid_entity_state_table[i].active = 0;
        ++i;
    } while (i < 25);
    G_h01_12B5 = 0;
    G_h01_12BB = 0;
}
