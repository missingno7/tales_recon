/* Direct recovery candidate for ov04_F_0104. */
struct Location {
    char pad[30];
    int selected;
    int a;
    int b;
    int c;
    int d;
};

extern long arc_file;
extern char location_records;
extern int request_disk();
extern long Open();
extern int arc_read_index();
extern long load_arc_record();
extern long F_h00_0976();
extern int sscanf();
extern int strcpy();
extern int free_text_block();
extern unsigned int F_h00_463E();
extern int Close();
extern int location_index_is_available();
extern int wrap_location_index();
extern int next_non_office_location_index();

recovered()
{
    int count;
    struct Location *location;
    long state;
    long page;
    long saved;
    int choices[35];
    char text[81];
    int row;
    int picked;

    page = 0;
    row = 0;
    picked = 0;
    for (count = 1; count < 35; ++count)
        choices[count] = 36;
    saved = arc_file;
    request_disk(1);
    arc_file = Open("DT1:loc.arc", 1005L);
    arc_read_index(arc_file);
    page = 0;
    page = load_arc_record(0, page);
    choices[0] = 0;
    location = (struct Location *)&location_records;
    state = *(long *)((char *)page + 2);
    state = F_h00_0976(state, text);
    sscanf(text, "%d %d %d %d", &location->a, &location->b,
        &location->c, &location->d);
    location->selected = 0;
    state = F_h00_0976(state, text);
    strcpy(location, text);
    free_text_block(page);
    row = F_h00_463E();
    row = (unsigned)row % 30;
    picked = F_h00_463E();
    picked = (unsigned)picked % 5;
    for (count = 1; count < 35; ++count) {
        while (!location_index_is_available(row, choices))
            row = next_non_office_location_index(row);
        choices[(unsigned)row] = row;
        location = (struct Location *)(&location_records + (long)count * 40);
        page = 0;
        page = load_arc_record(row, page);
        state = *(long *)((char *)page + 2);
        state = F_h00_0976(state, text);
        sscanf(text, "%d %d %d %d", &location->a, &location->b,
            &location->c, &location->d);
        state = F_h00_0976(state, text);
        strcpy(location, text);
        location->selected = row;
        free_text_block(page);
        row = wrap_location_index(row, picked);
    }
    Close(arc_file);
    arc_file = saved;
    arc_read_index(arc_file);
}
