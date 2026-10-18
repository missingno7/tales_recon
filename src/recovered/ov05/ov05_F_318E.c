struct Lookup { int index; int f2; };
struct Obj14 {
    unsigned char id;
    char f1;
    int w2;
    int w4;
    char b6;
    char b7;
    int w8;
    int w10;
    char b12;
    char b13;
};
extern struct Lookup G_h01_5E66[16];
extern struct Obj14 G_h01_606C[16];
extern char G_h01_5E58;
extern int G_h01_5E52;
extern int G_h01_5E42;
extern int G_h01_5C68;
extern int plane_reward_contact_pending;
extern int plane_reward_already_collected;
extern int plane_current_segment;
extern int plane_contact_suppression_segment;
extern int plane_contact_suppression_kind;
extern int G_h01_0A90;
extern float plane_speed;
extern char plane_collision_recovery_pending;
extern char G_h01_0A87;
extern char G_h01_0A88;
extern int G_h01_2F10;
extern int G_h01_2F12;
extern int G_h01_2F14;
extern int G_h01_2F16;
extern long total_money;
extern float G_h01_5E34;
extern float G_h01_5E38;
extern int G_h01_5E3C;
extern int G_h01_5E3E;
extern int G_h01_5E40;
extern int G_h01_5E44;
extern int G_h01_5E46;
extern int G_h01_5E48;
extern int G_h01_5E4A;
extern char G_h01_5E5A;
extern int play_sound();
extern unsigned int F_h00_463E();
extern int clear_input_direction_and_fire_state();
extern int plane_play_heading_spin_effect();

recovered()
{
    int x0;
    int y0;
    int k;
    int unk8;
    struct Obj14 *p;
    int x_a;
    int x_b;
    int y_a;
    int y_b;

    if (G_h01_5E58 && G_h01_5E52 >= G_h01_5E42 && G_h01_5C68 > 288)
        return 2;
    if (plane_contact_suppression_segment != plane_current_segment)
        plane_contact_suppression_segment = 0;
    x0 = (int)(G_h01_5E34 + 16);
    y0 = (int)(G_h01_5E38 + 16);
    k = plane_current_segment;
    if (G_h01_5E66[k].index == -1)
        return 0;
    p = (struct Obj14 *)&G_h01_606C[G_h01_5E66[k].index];
    while (p->id == k) {
        if (plane_reward_contact_pending != 0) {
            if (G_h01_5E40 < 4 || G_h01_5E40 > 12)
                G_h01_5E40 = 0;
            else
                G_h01_5E40 = 8;
            if (plane_reward_already_collected == 0) {
                plane_reward_contact_pending = 0;
                play_sound(57);
                G_h01_5E5A = 1;
                total_money += 50;
                plane_reward_already_collected = 1;
            }
            return 0;
        }
        if (((p->b12 == 0x2a || p->b12 == 0x2b) && p->b13 == 0)
            || ((p - 2)->b12 == 0x11 && ((p - 2)->b13 < 1 || (p - 2)->b13 > 3))
            || p->b12 == 0x1a || p->b12 == 0x3a) {
            p++;
            continue;
        }
        if ((p->b12 == 0x2c && (p - 1)->b13 != 4) || (p->b12 == 0x2d && (p - 2)->b13 != 5)) {
            p++;
            continue;
        }
        if (p->b12 == 0x1f && p->b13 == 0) {
            p++;
            continue;
        }
        y_a = p->w4;
        y_b = p->w4 + p->w10;
        x_a = p->w2;
        x_b = p->w2 + p->w8;
        switch (p->b12) {
        case 0x11:
            y_a += 10;
            x_a += 4;
            break;
        case 0x28:
        case 0x29:
            y_b -= 5;
            y_a += 9;
            x_a += 20;
            x_b -= 20;
            break;
        case 0x21:
        case 0x22:
            y_a += 9;
            x_a += 20;
            x_b -= 20;
            y_b += 3;
            break;
        case 0x23:
        case 0x24:
            if (plane_speed > 7) {
                x_a = x_a + p->b6 + 24;
                x_b = x_b + p->b6 - 24;
            } else {
                x_a = x_a + p->b6 + 30;
                x_b = x_b + p->b6 - 30;
            }
            break;
        case 0x1c:
            if (plane_speed > 7) {
                x_a += 25;
                x_b -= 25;
            } else {
                x_a += 37;
                x_b -= 37;
            }
            break;
        case 0x20:
            x_a -= 4;
            x_b += 4;
            break;
        case 0x1f:
            x_a += 6;
            x_b -= 6;
            y_b -= 10;
            break;
        case 0x1b:
            x_a += 8;
            y_a += 10;
            break;
        case 0x34:
            x_a += 32;
            y_a += 6;
            break;
        case 0x31:
            y_a += 16;
            y_b = y_a + 20;
            x_b = x_a + 80;
            x_a += 6;
            break;
        default:
            break;
        }
        if ((p - 2)->b12 == 0x11 && p->b13 != 0x14) {
            x_a -= 8;
            x_b += 8;
            y_a -= 8;
            y_b += 8;
        }
        if (G_h01_2F12 > y_a && G_h01_2F10 < y_b && G_h01_2F16 > x_a && G_h01_2F14 < x_b) {
            if (plane_contact_suppression_segment == plane_current_segment && p->b12 == plane_contact_suppression_kind)
                return 0;
        switch (p->b12) {
        case 0x2a:
        case 0x2b:
            G_h01_5E38 = 136.0;
            G_h01_5E40 = (F_h00_463E() & 1) ? 8 : 0;
            G_h01_0A90 = 1;
            plane_contact_suppression_segment = k;
            plane_contact_suppression_kind = p->b12;
            clear_input_direction_and_fire_state();
            G_h01_5E3E = 0;
            G_h01_5E3C = 0;
            return 0;
        case 0x2c:
            G_h01_0A88 = 1;
            break;
        case 0x34:
            G_h01_5E44 = p->w2 + 0x40;
            G_h01_5E46 = p->w4 + 8;
            G_h01_5E48 = p->w2 + 0x30;
            G_h01_5E4A = p->w4 + 0x23;
            G_h01_0A90 = 1;
            G_h01_0A87 = 1;
            return 0;
        case 0x2d:
            G_h01_0A88 = 2;
            break;
        case 0x1f:
            plane_collision_recovery_pending = 1;
            break;
        case 0x1b:
            G_h01_5E34 = 288.0;
            return 1;
        case 0x21:
        case 0x22:
        case 0x28:
        case 0x29:
            plane_play_heading_spin_effect();
            if (G_h01_5E40 > 8 && G_h01_5E40 < 16)
                plane_speed = 1.0;
            G_h01_0A90 = 1;
            plane_contact_suppression_segment = k;
            plane_contact_suppression_kind = p->b12;
            return 0;
        case 0x1c:
            G_h01_5E40 = (G_h01_5E40 + 8) & 15;
            play_sound(53);
            return 0;
        case 0x23:
        case 0x24:
            G_h01_5E40 = (G_h01_5E40 + 8) & 15;
            play_sound(50);
            return 0;
        case 0x31:
            if (G_h01_2F14 > x_a && G_h01_2F16 < x_b) {
                if (G_h01_2F10 < y_a) {
                    if (G_h01_5E40 > 8)
                        G_h01_5E40 = 16 - G_h01_5E40;
                    else if (G_h01_5E40 == 0)
                        G_h01_5E40 = 2;
                    else if (G_h01_5E40 == 8)
                        G_h01_5E40 = 6;
                } else {
                    if (G_h01_5E40 < 4 || G_h01_5E40 > 12)
                        G_h01_5E40 = 0;
                    else
                        G_h01_5E40 = 8;
                }
            } else {
                G_h01_5E40 = (G_h01_5E40 + 8) & 15;
            }
            G_h01_0A90 = 1;
            play_sound(50);
            return 0;
        default:
            play_sound(66);
            break;
        }
        G_h01_5E40 = F_h00_463E() & 15;
        plane_contact_suppression_segment = k;
        plane_contact_suppression_kind = p->b12;
        G_h01_0A90 = 1;
        if (G_h01_5E40 > 8 && G_h01_5E40 < 16)
            plane_speed = 1.0;
        if (G_h01_5E38 >= 144)
            G_h01_5E40 = 0;
        }
        p++;
    }
    return 0;
}
