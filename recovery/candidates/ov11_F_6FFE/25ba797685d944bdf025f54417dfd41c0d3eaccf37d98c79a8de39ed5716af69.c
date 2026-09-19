extern int G_h01_9F76;
extern int G_h01_A6A8;
recovered() {
    int *a0;
    int *a1;
    int d0;
    int d1;
    int *a4;
    a4 = (int *)0x26aa;
    a0 = a4;
    a1 = a4;
    d0 = *a1;
    d0 = d0 * 0x35;
    d0 = d0 + 0xc;
    *a0 = d0;
    a0 = a4;
    a1 = a4;
    d0 = *(a1 + 1);
    d0 = d0 << 5;
    d0 = d0 + 0x15;
    *(a0 + 3) = d0;
    *(--(int *)0x703e) = 0x9;
    *(--(int *)0x7042) = *(((int *)0xfffa) + 1);
    F_h11_717A();
    ((int *)0x704a)[0] = ((int *)0x704a)[0] + 4;
    *(((int *)0xfffa) + 1) = *(((int *)0xfffa) + 1) + 1;
    a4 = (int *)(((int *)0xfffa) - 2);
    a4[0] = a4[0] + 0xa;
    if (*(((int *)0xfffa) + 1) < 3)
        goto L1;
    *(int *)0x7060 = (int)0x1f78;
    *(char *)0x7064 = 0;
    return;
L1:
    a0 = (int *)0xfffc;
    a1 = (int *)0xfffc;
    d0 = *a1;
    d0 = d0 * 0x35;
    d0 = d0 + 0xc;
    *a0 = d0;
    a0 = (int *)0xfffc;
    a1 = (int *)0xfffc;
    d0 = *(a1 + 1);
    d0 = d0 << 5;
    d0 = d0 + 0x15;
    *(a0 + 3) = d0;
    *(--(int *)0x703e) = 0x9;
    *(--(int *)0x7042) = *(((int *)0xfffa) + 1);
    F_h11_717A();
    ((int *)0x704a)[0] = ((int *)0x704a)[0] + 4;
    *(((int *)0xfffa) + 1) = *(((int *)0xfffa) + 1) + 1;
    a4 = (int *)(((int *)0xfffa) - 2);
    a4[0] = a4[0] + 0xa;
    if (*(((int *)0xfffa) + 1) < 3)
        goto L1;
    *(int *)0x7060 = (int)0x1f78;
    *(char *)0x7064 = 0;
}