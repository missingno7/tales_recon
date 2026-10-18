extern int initialize_office_menu_scene();
extern int switch_display_buffer();
extern int play_sound();
extern int draw_masked_sprite();
extern int Delay();
extern int G_h01_511C;
extern int G_h01_5152;
extern char G_h01_5186;
extern int G_h01_5188;
extern char G_h01_51BC;

recovered()
{
    int i;

    initialize_office_menu_scene(0,0,0);
    switch_display_buffer();
    initialize_office_menu_scene(0,0,0);
    play_sound(4);
    i=15;
    do {
        draw_masked_sprite(&G_h01_511C);
        draw_masked_sprite(&G_h01_5188);
        G_h01_5186=i%3;
        draw_masked_sprite(&G_h01_5152);
        switch_display_buffer();
        Delay(5L);
        --i;
    } while (i>=3);
    draw_masked_sprite(&G_h01_511C);
    draw_masked_sprite(&G_h01_5152);
    G_h01_51BC=1;
    draw_masked_sprite(&G_h01_5188);
    play_sound(35);
    switch_display_buffer();
    Delay(5L);
    play_sound(34);
    initialize_office_menu_scene(0,0,0);
    draw_masked_sprite(&G_h01_511C);
    draw_masked_sprite(&G_h01_5152);
    G_h01_51BC=1;
    draw_masked_sprite(&G_h01_5188);
    switch_display_buffer();
    Delay(50L);
    i=1;
    do {
        initialize_office_menu_scene(i,0,0);
        switch_display_buffer();
        Delay(20L);
        ++i;
    } while (i<=3);
}
