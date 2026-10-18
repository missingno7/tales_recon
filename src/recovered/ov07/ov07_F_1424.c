struct Record {
    int amount;
    int flag;
    unsigned char state;
    char pad;
    int category;
    int f8;
    int f10;
    int f12;
    char rest[32];
};

struct Input {
    char pad[2];
    long text;
};

extern struct Record investment_market_state[16];
extern int invest_office_palette;
extern char *palette_fade_target;
extern long arc_file;
extern long G_h01_6EAC;
extern struct Input *G_h01_6EA8;
extern int request_disk();
extern long Open();
extern int arc_read_index();
extern long load_arc_record();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int poll_controller_and_keyboard_input();
extern int Delay();
extern int free_text_block();
extern int Close();
extern int draw_text();
extern int strcat();
extern int invest_draw_news_bulletin();
extern int invest_draw_record_text_lines();
char *invest_format_unsigned_decimal();

recovered(x, y)
long x;
long y;
{
    long l1;
    int i1;
    int i;
    char *q;
    char *p;
    char buf1[32];
    char buf2[40];
    int r;

    for (i = 0; i < 15; i++) {
        if (investment_market_state[i].state == 0)
            continue;
        G_h01_6EAC = arc_file;
        request_disk(1);
        arc_file = Open("DT1:invest.arc", 1005L);
        arc_read_index(arc_file);
        G_h01_6EA8 = 0;
        G_h01_6EA8 = load_arc_record(i, G_h01_6EA8);
        switch (investment_market_state[i].state) {
        case 1:
            invest_draw_news_bulletin(i, x, y);
            invest_draw_record_text_lines(i, 2, 32, 35);
            buf1[0] = 0;
            p = invest_format_unsigned_decimal((long)investment_market_state[i].f12);
            strcat(buf1, "STOCK IS UP BY ");
            strcat(buf1, p);
            strcat(buf1, "%");
            draw_text(80, 100, buf1, 14, 0);
            investment_market_state[i].state = 5;
            switch_display_buffer();
            palette_fade_target = (char *)&invest_office_palette;
            fade_palette_to_target(&invest_office_palette);
            do {
                r = poll_controller_and_keyboard_input();
                Delay(5L);
            } while ((r & 0x80) == 0);
            break;
        case 2:
            invest_draw_news_bulletin(i, x, y);
            invest_draw_record_text_lines(i, 3, 32, 35);
            buf1[0] = 0;
            p = invest_format_unsigned_decimal((long)investment_market_state[i].f12);
            strcat(buf1, "STOCK IS DOWN BY ");
            strcat(buf1, p);
            strcat(buf1, "%");
            draw_text(80, 100, buf1, 14, 0);
            investment_market_state[i].state = 5;
            switch_display_buffer();
            palette_fade_target = (char *)&invest_office_palette;
            fade_palette_to_target(&invest_office_palette);
            do {
                r = poll_controller_and_keyboard_input();
                Delay(5L);
            } while ((r & 0x80) == 0);
            break;
        case 3:
            invest_draw_news_bulletin(i, x, y);
            invest_draw_record_text_lines(i, 2, 32, 35);
            draw_text(48, 100, "MAJOR PRICE CHANGE EXPECTED", 14, 0);
            buf2[0] = 0;
            q = invest_format_unsigned_decimal((long)investment_market_state[i].f10);
            strcat(buf2, "ON OR AROUND DAY ");
            strcat(buf2, q);
            draw_text(56, 110, buf2, 14, 0);
            investment_market_state[i].state = 0x83;
            switch_display_buffer();
            palette_fade_target = (char *)&invest_office_palette;
            fade_palette_to_target(&invest_office_palette);
            do {
                r = poll_controller_and_keyboard_input();
                Delay(5L);
            } while ((r & 0x80) == 0);
            break;
        case 4:
            invest_draw_news_bulletin(i, x, y);
            invest_draw_record_text_lines(i, 3, 32, 35);
            draw_text(48, 100, "MAJOR PRICE CHANGE EXPECTED", 14, 0);
            buf2[0] = 0;
            q = invest_format_unsigned_decimal((long)investment_market_state[i].f10);
            strcat(buf2, "ON OR AROUND DAY ");
            strcat(buf2, q);
            draw_text(56, 110, buf2, 14, 0);
            investment_market_state[i].state = 0x84;
            switch_display_buffer();
            palette_fade_target = (char *)&invest_office_palette;
            fade_palette_to_target(&invest_office_palette);
            do {
                r = poll_controller_and_keyboard_input();
                Delay(5L);
            } while ((r & 0x80) == 0);
            break;
        default:
            break;
        }
        free_text_block(G_h01_6EA8);
        Close(arc_file);
        arc_file = G_h01_6EAC;
        request_disk(1);
        arc_read_index(arc_file);
    }
}
