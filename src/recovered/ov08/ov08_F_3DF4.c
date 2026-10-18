extern char G_h01_6F40[1];
extern int request_disk();
extern int load_arc_record();

recovered()
{
    int i;

    request_disk(2);
    for (i = 1; i < 11; ++i) {
        switch (i) {
        case 1: load_arc_record(5, G_h01_6F40 + (long)i * 54); break;
        case 2: load_arc_record(6, G_h01_6F40 + (long)i * 54); break;
        case 3: load_arc_record(7, G_h01_6F40 + (long)i * 54); break;
        case 4: load_arc_record(8, G_h01_6F40 + (long)i * 54); break;
        case 5: load_arc_record(9, G_h01_6F40 + (long)i * 54); break;
        case 6: load_arc_record(10, G_h01_6F40 + (long)i * 54); break;
        case 7: load_arc_record(11, G_h01_6F40 + (long)i * 54); break;
        case 8: load_arc_record(13, G_h01_6F40 + (long)i * 54); break;
        case 9: load_arc_record(14, G_h01_6F40 + (long)i * 54); break;
        case 10: load_arc_record(15, G_h01_6F40 + (long)i * 54); break;
        }
    }
}