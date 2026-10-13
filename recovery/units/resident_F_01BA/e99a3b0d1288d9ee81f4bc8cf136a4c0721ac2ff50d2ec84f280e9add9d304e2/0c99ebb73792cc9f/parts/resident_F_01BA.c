struct Point { char reserved[36]; unsigned int value; };
struct PointRef { struct Point *point; char reserved[8]; };

extern struct PointRef G_h01_4524[36];
extern unsigned char G_h01_46C8;
extern int F_h00_0FDE();
extern int F_h00_033E();
extern int F_h00_7978();
extern int F_h00_7522();
extern int F_h08_0000();
extern int F_h09_0000();
extern int F_h10_0000();
extern int F_h11_0000();

recovered(arg)
int arg;
{
    int result = 0;
    int unused;

    F_h00_0FDE(1);
    switch (G_h01_4524[arg].point->value & 0x000f) {
    case 1:
        F_h00_7978(F_h11_0000);
        F_h00_033E(1);
        G_h01_46C8 |= 1;
        result = F_h11_0000(G_h01_4524[arg].point->value >> 4);
        F_h00_7522(F_h11_0000);
        break;
    case 2:
        F_h00_7978(F_h08_0000);
        F_h00_033E(2);
        G_h01_46C8 |= 2;
        result = F_h08_0000(G_h01_4524[arg].point->value >> 4);
        F_h00_7522(F_h08_0000);
        break;
    case 8:
        F_h00_7978(F_h10_0000);
        F_h00_033E(4);
        G_h01_46C8 |= 4;
        result = F_h10_0000(G_h01_4524[arg].point->value >> 4);
        F_h00_7522(F_h10_0000);
        break;
    case 4:
        F_h00_7978(F_h09_0000);
        F_h00_033E(8);
        G_h01_46C8 |= 8;
        result = F_h09_0000(G_h01_4524[arg].point->value >> 4);
        F_h00_7522(F_h09_0000);
        break;
    default:
        break;
    }
    return result;
}