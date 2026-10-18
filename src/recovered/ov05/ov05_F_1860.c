/* ov05_F_1860: per-frame float state machine over G_h01_5E34/5E38 and the 0A7E gain; returns one of two record pointers. */
struct Blob {
    int w0;
    int w2;
    char f4[48];
    char b52;
};
extern struct Blob G_h01_5B5A;
extern struct Blob G_h01_544E;
extern float plane_heading_vectors[32];
extern float G_h01_5DAC[32];
extern char plane_heading_left_collision_offsets[16];
extern char plane_heading_top_collision_offsets[16];
extern char plane_heading_right_collision_offsets[16];
extern char plane_heading_bottom_collision_offsets[16];
extern float plane_speed;
extern char G_h01_0A89;
extern int plane_first_visible_segment;
extern int plane_current_segment;
extern int G_h01_2F10;
extern int G_h01_2F12;
extern int G_h01_2F14;
extern int G_h01_2F16;
extern int G_h01_5C32;
extern int G_h01_5C34;
extern int G_h01_5C38;
extern float G_h01_5E34;
extern float G_h01_5E38;
extern int G_h01_5E3C;
extern int G_h01_5E3E;
extern int G_h01_5E40;
extern char G_h01_5E41;
extern int G_h01_5E42;
extern int G_h01_5E4C;
extern int G_h01_5E64[1][2];
extern int switch_display_buffer();
extern int play_sound();
extern int plane_draw_scrolling_frame();
extern int F_h05_3A9E();

struct Blob *recovered()
{
    struct Blob *p;
    int t;
    float fa;
    float fb;
    int i;
    int flag;

    fa = G_h01_5E34;
    if (plane_speed != 0) {
        G_h01_5E34 += plane_heading_vectors[G_h01_5E40 * 2] * plane_speed;
        G_h01_5E38 -= plane_heading_vectors[G_h01_5E40 * 2 + 1] * plane_speed;
    }
    if (G_h01_5E40 > 8 && G_h01_5E40 < 16) {
        G_h01_5E34 += G_h01_5DAC[G_h01_5E40 * 2];
        G_h01_5E38 -= G_h01_5DAC[G_h01_5E40 * 2 + 1];
        if (G_h01_5E40 == 12)
            plane_speed = plane_speed + 0.6;
        else
            plane_speed = plane_speed + 0.4;
    }
    if (G_h01_5E40 > 0 && G_h01_5E40 < 8) {
        G_h01_5E34 -= G_h01_5DAC[G_h01_5E40 * 2];
        G_h01_5E38 += G_h01_5DAC[G_h01_5E40 * 2 + 1];
        if (G_h01_5E40 == 4)
            plane_speed = plane_speed + -0.4;
        else
            plane_speed = plane_speed + -0.17;
    }
    if (G_h01_5E40 >= 4 && G_h01_5E40 <= 12) {
        if (G_h01_5E3C > 0 && plane_speed > 0) {
            G_h01_5E40++;
            if (G_h01_5E40 > 15)
                G_h01_5E40 = 0;
        } else if (G_h01_5E3E > 0 && plane_speed > 2) {
            G_h01_5E40--;
            if (G_h01_5E40 < 0)
                G_h01_5E40 += 16;
        }
    } else {
        if (G_h01_5E3C > 0 && plane_speed > 2) {
            G_h01_5E40++;
            if (G_h01_5E40 > 15)
                G_h01_5E40 = 0;
        } else if (G_h01_5E3E > 0 && plane_speed > 0) {
            G_h01_5E40--;
            if (G_h01_5E40 < 0)
                G_h01_5E40 += 16;
        }
    }

    if (plane_current_segment < 2 || plane_current_segment > G_h01_5E42 - 2)
        t = 0x8b;
    else
        t = 0x90;
    fb = G_h01_5E34 - fa;
    G_h01_5E4C = (int)((float)G_h01_5E4C + fb);
    if (G_h01_5E40 > 4 && G_h01_5E40 < 12)
        flag = 0;
    else
        flag = 1;

    if (G_h01_5E34 > 90 && flag != 0 && plane_current_segment < G_h01_5E42 - 2) {
        G_h01_5E4C = (int)((float)G_h01_5E4C + fb);
        G_h01_5E34 = 90.0;
    } else if (G_h01_5E34 < 80 && flag == 0 && plane_first_visible_segment != 0) {
        G_h01_5E4C = (int)((float)G_h01_5E4C + fb);
        G_h01_5E34 = 80.0;
    } else if (plane_current_segment == G_h01_5E42 && G_h01_5E34 > 288 && plane_first_visible_segment + 3 == G_h01_5E42) {
        G_h01_5E4C = 0;
        G_h01_5E34 = 288.0;
        G_h01_5E40 = 8;
    } else if (plane_current_segment == 0 && flag == 0 && G_h01_5E34 < 0.0) {
        G_h01_5E34 = 0.0;
        G_h01_5E40 = 0;
        G_h01_5E4C = 0;
    }

    if (G_h01_5E4C > 79) {
        if (plane_first_visible_segment + 3 < G_h01_5E42)
            plane_first_visible_segment++;
        G_h01_5E4C -= 80;
    } else if (G_h01_5E4C < -79) {
        G_h01_5E4C += 80;
        if (plane_first_visible_segment > 0)
            plane_first_visible_segment--;
    }

    if ((plane_first_visible_segment + 3 >= G_h01_5E42 && G_h01_5E34 > 80) || (plane_first_visible_segment == 0 && plane_current_segment < 2 && flag == 0))
        G_h01_5E4C = 0;

    if (plane_speed < 3 && G_h01_5E38 < (float)t)
        G_h01_5E40 = F_h05_3A9E(G_h01_5E40);
    if (G_h01_5E38 < 0.0) {
        G_h01_5E40 = F_h05_3A9E(G_h01_5E40);
        G_h01_5E38 = 0.0;
    } else if (G_h01_5E38 > (float)t) {
        if (plane_current_segment >= G_h01_5E42 - 1 && (G_h01_5E40 > 12 || G_h01_5E40 == 0)) {
            G_h01_5E40 = 0;
            G_h01_5E38 = (float)t;
        } else if (G_h01_0A89 > 1) {
            plane_speed = 0.0;
            G_h01_5E40 = 0;
            G_h01_5E38 = (float)t;
            p = &G_h01_5B5A;
            p->b52 = 0;
            p->w0 = (int)(G_h01_5E34 + 8);
            p->w2 = (int)(G_h01_5E38 + -14);
            if (G_h01_5E64[plane_current_segment][0] == 12) {
                play_sound(0x3a);
                G_h01_5C32 = (int)(G_h01_5E34 + -24);
                G_h01_5C34 = 0xb0 - G_h01_5C38 - 8;
                for (i = 1; i < 4; i++) {
                    plane_draw_scrolling_frame(&G_h01_5C32);
                    switch_display_buffer();
                }
                return p;
            } else {
                play_sound(0x2b);
                return p;
            }
        } else {
            G_h01_0A89++;
            G_h01_5E38 = (float)(t - 4);
            if (G_h01_5E40 > 11) {
                G_h01_5E40 = 1;
                if (plane_speed < 4)
                    plane_speed = 4.0;
            } else if (G_h01_5E40 > 7) {
                G_h01_5E40 = 7;
                if (plane_speed < 4)
                    plane_speed = 4.0;
            } else {
                G_h01_5E40 = 5;
                plane_speed = 5.0;
            }
            play_sound(0x42);
        }
    }

    p = &G_h01_544E;
    p->b52 = G_h01_5E41;
    p->w0 = (int)G_h01_5E34;
    p->w2 = (int)G_h01_5E38;
    G_h01_2F10 = (int)((float)plane_heading_top_collision_offsets[G_h01_5E40] + G_h01_5E38);
    G_h01_2F12 = (int)((float)plane_heading_bottom_collision_offsets[G_h01_5E40] + G_h01_5E38);
    G_h01_2F14 = (int)((float)plane_heading_left_collision_offsets[G_h01_5E40] + G_h01_5E34);
    G_h01_2F16 = (int)((float)plane_heading_right_collision_offsets[G_h01_5E40] + G_h01_5E34);
    G_h01_5E3E = 0;
    G_h01_5E3C = 0;
    return p;
}
