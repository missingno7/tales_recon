/* Candidate v2 (v1 with the leading space of the third string restored) for ov07_F_0000: setup calls, 3+5 table-driven calls, key state machine, closing screen. */
struct Rec54 { char b[54]; };

extern char G_h01_33E2;
extern int invest_office_asset_record_indices[8];
extern char G_h01_3232;
extern char G_h01_323A;
extern char G_h01_323C;
extern char G_h01_3242;
extern char G_h01_329E;
extern int invest_office_palette;
extern char invest_trade_confirmation_palette[1];
extern char *palette_fade_target;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern long arc_file;
extern int clear_input_direction_and_fire_state();
extern int play_sound();
extern int request_disk();
extern int load_arc_record();
extern int BltBitMap();
extern long Open();
extern int arc_read_index();
extern int Close();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int poll_controller_and_keyboard_input();
extern int fade_palette_to_black();
extern int load_scene_graphic();
extern int draw_text();
extern int wait_for_fire_input();
extern int free_bitmap_planes();
extern int Delay();
extern int invest_show_stock_change();
extern int invest_draw_portfolio_header();
extern int invest_draw_portfolio_rows();
extern int invest_trade_company_shares();

recovered()
{
    unsigned char key;
    int flag;
    int i;
    int cnt;
    int y;
    int x;
    int u0e;
    long saved;
    int u14;

    u14 = 0;
    G_h01_33E2 = 0;
    clear_input_direction_and_fire_state();
    play_sound(0);
    request_disk(1);
    load_arc_record(0x14, archive_image_bitmap);
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    for (i = 0; i < 3; i++)
        load_arc_record(invest_office_asset_record_indices[i], (char *)((struct Rec54 *)&G_h01_3232 + i));
    saved = arc_file;
    request_disk(1);
    arc_file = Open("DT1:invart.arc", 1005L);
    arc_read_index(arc_file);
    for (i = 3; i < 8; i++)
        load_arc_record(invest_office_asset_record_indices[i], (char *)((struct Rec54 *)&G_h01_3232 + i));
    Close(arc_file);
    arc_file = saved;
    arc_read_index(arc_file);
    play_sound(30);
    invest_show_stock_change(&G_h01_3232, &G_h01_329E);
    cnt = 0;
    x = 10;
    y = 10;
    invest_draw_portfolio_header();
    invest_draw_portfolio_rows(y, x);
    switch_display_buffer();
    palette_fade_target = (char *)&invest_office_palette;
    fade_palette_to_target((char *)&invest_office_palette);
    flag = 0;
    while (flag == 0) {
        key = poll_controller_and_keyboard_input();
        if (key & 0x80) {
            play_sound(36);
            if (x == 15)
                flag = 1;
            else
                flag = invest_trade_company_shares(x, &G_h01_3232);
            invest_draw_portfolio_header();
            invest_draw_portfolio_rows(y, x);
            switch_display_buffer();
        } else {
            key &= 0x3f;
            switch (key) {
            case 1:
                play_sound(36);
                x--;
                x &= 15;
                cnt--;
                if (cnt < 0) {
                    y--;
                    y &= 15;
                    cnt = 0;
                }
                invest_draw_portfolio_header();
                invest_draw_portfolio_rows(y, x);
                switch_display_buffer();
                Delay(10L);
                break;
            case 5:
                play_sound(36);
                x++;
                x &= 15;
                cnt++;
                if (cnt > 5) {
                    y++;
                    y &= 15;
                    cnt = 5;
                }
                invest_draw_portfolio_header();
                invest_draw_portfolio_rows(y, x);
                switch_display_buffer();
                Delay(10L);
                break;
            default:
                u14 = 0;
                break;
            }
        }
    }
    fade_palette_to_black();
    if (G_h01_33E2) {
        load_scene_graphic(1);
        draw_text(176, 60, "I'll put that", 1, 0);
        draw_text(176, 76, "order through", 1, 0);
        draw_text(176, 92, " right away,  ", 1, 0);
        draw_text(176, 108, " Mr. McDuck!", 1, 0);
        fade_palette_to_black();
        switch_display_buffer();
        palette_fade_target = invest_trade_confirmation_palette;
        fade_palette_to_target(invest_trade_confirmation_palette);
        if (wait_for_fire_input(50))
            play_sound(36);
    }
    for (i = 0; i < 8; i++)
        free_bitmap_planes((char *)((struct Rec54 *)&G_h01_3242 + i),
                   *(short *)((struct Rec54 *)&G_h01_323A + i),
                   *(short *)((struct Rec54 *)&G_h01_323C + i));
}
