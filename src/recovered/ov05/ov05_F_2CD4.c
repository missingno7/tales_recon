/* Worker haiku-fn-ov05_F_2CD4: structured candidate for ov05_F_2CD4 (v8). */
struct Lookup { int index; int f2; };
struct Rec { unsigned char id; char a1; int x; int y; char b6; char b7; int w8; char b10; char b11; char type; char d; };
struct Pos { int x; int y; };
struct Ent { int x; int y; char rest[50]; };
extern struct Lookup G_h01_5E66[16];
extern struct Rec G_h01_606C[16];
extern struct Pos G_h01_54C8;
extern struct Pos G_h01_54FE;
extern struct Ent G_h01_5534[2];
extern struct Ent G_h01_57C0[2];
extern struct Pos G_h01_582C;
extern struct Pos G_h01_5862;
extern struct Pos G_h01_5AEE;
extern struct Pos G_h01_5D40;
extern char G_h01_5D74;
extern float G_h01_5E34;
extern int G_h01_2F10;
extern int G_h01_2F14;
extern int G_h01_2F16;
extern int G_h01_2F18;
extern int G_h01_2F1A;
extern int G_h01_2F1C;
extern int plane_reward_contact_pending;
extern int plane_reward_already_collected;
extern int draw_masked_sprite();
extern int play_sound();
extern unsigned int F_h00_463E();

recovered(arg)
int arg;
{
    int aux;
    char idx;
    int dxv;
    unsigned int r;
    struct Rec *p;

    if (G_h01_5E66[arg].index == -1)
        return;
    p = &G_h01_606C[G_h01_5E66[arg].index];
    while (p->id == arg) {
        switch (p->type) {
        case 33:
            idx = p->d;
            G_h01_5534[idx].x = p->x;
            G_h01_5534[idx].y = p->y;
            draw_masked_sprite(&G_h01_5534[idx]);
            break;
        case 40:
            idx = p->d;
            G_h01_57C0[idx].x = p->x;
            G_h01_57C0[idx].y = p->y;
            draw_masked_sprite(&G_h01_57C0[idx]);
            break;
        case 26:
            G_h01_54C8.x = p->x;
            G_h01_54C8.y = p->y;
            draw_masked_sprite(&G_h01_54C8);
            break;
        case 27:
            G_h01_54FE.x = p->x;
            G_h01_54FE.y = p->y;
            draw_masked_sprite(&G_h01_54FE);
            break;
        case 58:
            if (arg == 0)
                G_h01_5D40.x = p->x + 17;
            else
                G_h01_5D40.x = p->x + 62;
            G_h01_5D40.y = p->y;
            if (p->b6++ != 0) {
                p->b6 = 0;
            } else {
                G_h01_5D74 = p->d;
                p->d = p->d + 1;
            }
            if (p->d > 2)
                p->d = F_h00_463E() % 3;
            draw_masked_sprite(&G_h01_5D40);
            break;
        case 42:
            r = F_h00_463E() % 100;
            dxv = (int)(G_h01_5E34 - (float)p->x);
            if (p->d == 0 && p[1].d == 0 && r < 10 && dxv > -96 && dxv < 96) {
                play_sound(54);
                p->d = p->d + 1;
            } else if (p->d <= 1 && p->d != 0) {
                p->d = p->d + 1;
                G_h01_582C.x = p->x;
                G_h01_582C.y = p->y;
                draw_masked_sprite(&G_h01_582C);
            }
            break;
        case 43:
            if ((p - 1)->d > 1) {
                (p - 1)->d = 0;
                p->d = p->d + 1;
                G_h01_5862.x = p->x;
                G_h01_5862.y = p->y;
                draw_masked_sprite(&G_h01_5862);
            } else if (p->d > 0 && p->d < 2) {
                p->d = p->d + 1;
                G_h01_5862.x = p->x;
                G_h01_5862.y = p->y;
                draw_masked_sprite(&G_h01_5862);
                if (p->d == 2)
                    p->d = 0;
            }
            break;
        case 49:
            G_h01_2F1A = p->x;
            G_h01_2F1C = p->x + p->w8;
            G_h01_2F18 = p->y + 16;
            if (G_h01_2F10 > G_h01_2F18 + 16 && G_h01_2F14 > G_h01_2F1A
                && G_h01_2F16 < G_h01_2F1C) {
                plane_reward_contact_pending = 1;
            } else {
                plane_reward_contact_pending = 0;
                plane_reward_already_collected = 0;
            }
            G_h01_5AEE.x = p->x;
            G_h01_5AEE.y = p->y;
            draw_masked_sprite(&G_h01_5AEE);
            break;
        default:
            break;
        }
        p++;
    }
}
