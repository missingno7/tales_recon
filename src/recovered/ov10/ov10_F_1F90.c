extern int play_sound();

recovered(a)
int a;
{
    if (a < 2)
        play_sound(0x51);
    else if (a < 4)
        play_sound(0x50);
    else if (a < 6)
        play_sound(0x4f);
    else
        play_sound(0x4e);
}
