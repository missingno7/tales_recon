struct TextBlock {
    unsigned int length;
    char *data;
};
extern long G_h01_46DA;
extern unsigned int G_h01_A7DA;
extern unsigned int G_h01_A7DC;
extern unsigned int G_h01_A7DE;
extern unsigned int G_h01_A7E0;
extern unsigned int G_h01_A7E4;
extern unsigned int G_h01_A7D8;
extern long G_h01_A7D6;
extern long G_h01_542A;
extern char G_h01_0971;
extern int F_h00_287C();
extern int F_h00_3674();
extern long F_h00_3B16();
extern long F_h00_3870();
extern int F_h00_3A6E();
extern void F_h00_404A();
extern void F_h00_4184();
extern int F_h00_3C4C();
extern int F_h04_27FE();
extern long F_h00_86F6();
extern int F_h00_7BD8();

long recovered(index, destination)
int index;
char *destination;
{
    unsigned int width;
    unsigned int stride;
    unsigned int height;
    unsigned int multiplier;
    int mode;
    unsigned int length;
    char *result;
    char *bitmap;
    char *graphic;
    struct TextBlock *block;

    if (F_h00_287C(index, G_h01_46DA))
        F_h00_3674(index + 1000);
    switch (G_h01_A7DA) {
    case 1:
        bitmap = destination;
        width = G_h01_A7DC;
        height = G_h01_A7DE;
        if (bitmap == 0) {
            bitmap = F_h00_3B16(width, height);
            if (bitmap == 0)
                F_h00_3674(index + 2000);
        }
        F_h00_404A(bitmap);
        result = bitmap;
        break;
    case 2:
        graphic = destination;
        width = G_h01_A7DC;
        height = G_h01_A7DE;
        multiplier = G_h01_A7E0;
        if (graphic == 0) {
            graphic = F_h00_3870(&G_h01_542A, 54L);
            if (graphic == 0)
                F_h00_3674(index + 3000);
        }
        stride = width >> 3;
        *(int *)graphic = 0;
        *(int *)(graphic + 2) = 0;
        *(unsigned int *)(graphic + 4) = stride;
        *(unsigned int *)(graphic + 6) = height;
        *(unsigned int *)(graphic + 8) = stride * multiplier;
        *(unsigned int *)(graphic + 10) = height;
        *(char *)(graphic + 13) = G_h01_0971;
        F_h00_3A6E(graphic + 16, stride * multiplier, height);
        if (*(long *)(graphic + 16) == 0)
            F_h00_3674(index + 4000);
        *(char *)(graphic + 52) = 0;
        F_h00_404A(graphic + 8);
        result = graphic;
        break;
    case 3:
        result = 0;
        block = destination;
        if (block == 0) {
            block = F_h00_3870(&G_h01_542A, 6L);
            if (block == 0)
                F_h04_27FE("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7D8;
        block->length = length;
        block->data = F_h00_3870(&G_h01_542A, (unsigned long)length);
        F_h00_86F6(G_h01_46DA, block->data, G_h01_A7D6);
        break;
    case 4:
        result = 0;
        block = destination;
        if (block == 0) {
            block = F_h00_3870(&G_h01_542A, 6L);
            if (block == 0)
                F_h04_27FE("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7DC;
        block->length = length;
        block->data = F_h00_3870(&G_h01_542A, (unsigned long)length);
        mode = 1;
        F_h00_3C4C(mode, G_h01_46DA, block->data, length);
        break;
    case 5:
        result = 0;
        block = destination;
        if (block == 0) {
            block = F_h00_3870(&G_h01_542A, 6L);
            if (block == 0)
                F_h04_27FE("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7DC;
        block->length = length;
        block->data = F_h00_3870(&G_h01_542A, (unsigned long)length);
        F_h00_4184(G_h01_A7D6, block->data);
        break;
    case 6:
        result = 0;
        block = destination;
        if (block == 0) {
            block = F_h00_3870(&G_h01_542A, 6L);
            if (block == 0)
                F_h04_27FE("Can't allocate TSTRUCT");
            result = block;
        }
        length = G_h01_A7E4;
        block->length = length;
        block->data = F_h00_3870(&G_h01_542A, (unsigned long)length);
        F_h00_86F6(G_h01_46DA, block->data, G_h01_A7D6);
        break;
    default:
        F_h00_7BD8("LIT: #%d\n", index);
        F_h00_3674(G_h01_A7DA + 5000);
        break;
    }
    return result;
}
