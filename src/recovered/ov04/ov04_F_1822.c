/* Direct reconstruction candidate for ov04_F_1822. */
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern int BltBitMap();
extern int switch_display_buffer();
extern int poll_controller_and_keyboard_input();
extern int Delay();

recovered()
{
    int inset;

    inset = 80;
    do {
        BltBitMap(archive_image_bitmap, (long)inset, (long)inset,
            active_screen_bitmap, (long)inset, (long)inset,
            (long)(320 - inset - inset), (long)(200 - inset - inset),
            (long)192, (long)255, 0L);
        switch_display_buffer();
        poll_controller_and_keyboard_input();
        Delay(2L);
        inset -= 8;
    } while (inset >= 0);
}
