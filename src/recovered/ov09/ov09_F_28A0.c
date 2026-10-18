/* ov09_F_28A0 (fleet v3; two locals without references occupy the original frame). */
extern int draw_masked_sprite();
extern int G_h01_3ACA; extern int G_h01_3B00; extern int G_h01_3B36;
extern int G_h01_3B6C; extern int G_h01_3BA2; extern int G_h01_3BD8;
extern int G_h01_3C0E; extern int G_h01_3C44; extern int G_h01_3C7A;
extern int G_h01_3CB0; extern int G_h01_3CE6; extern int G_h01_3D1C;
extern int G_h01_3D52;

recovered(a) char a;
{
    long la;
    long lb;
    switch (a) {
    case 1:
        draw_masked_sprite(&G_h01_3ACA);
        break;
    case 2:
        draw_masked_sprite(&G_h01_3B00);
        break;
    case 4:
        draw_masked_sprite(&G_h01_3B6C);
    case 3:
        draw_masked_sprite(&G_h01_3B36);
        break;
    case 5:
        draw_masked_sprite(&G_h01_3BA2);
    case 7:
        draw_masked_sprite(&G_h01_3C0E);
        break;
    case 6:
        draw_masked_sprite(&G_h01_3BD8);
        break;
    case 8:
        draw_masked_sprite(&G_h01_3C44);
        draw_masked_sprite(&G_h01_3C0E);
        break;
    case 9:
        draw_masked_sprite(&G_h01_3C7A);
    case 11:
        draw_masked_sprite(&G_h01_3CE6);
        break;
    case 10:
        draw_masked_sprite(&G_h01_3CB0);
        break;
    case 12:
        draw_masked_sprite(&G_h01_3D1C);
        break;
    case 13:
        draw_masked_sprite(&G_h01_3D52);
        break;
    default:
        break;
    }
}
