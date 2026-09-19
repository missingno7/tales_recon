extern unsigned int G_h01_0054;
extern unsigned int G_h01_8A3C;
extern unsigned int G_h01_8A3E;
extern unsigned int G_h01_9F76;
extern unsigned int G_h01_A6A8;
recovered(n) int n; {
  int a;
  a = n * 10;
  a += (unsigned long)G_h01_8A3C + (unsigned long)G_h01_9F76;
  *(int *)((char *)&a - 4) = a;
  if (*(short *)((char *)&a - 4) >= 0) {
    if (*(short *)(((char *)&a - 4) + 8) < 0) {
      *(short *)G_h01_A6A8 = *(short *)(((char *)&a - 4) + 4) - *(short *)G_h01_8A3E;
      *(short *)(((char *)&a - 4) + 6) = *(short *)G_h01_A6A8;
      *(int *)G_h01_A6A8 = *(int *)G_h01_A6A8;
    }
  } else {
    if (*(short *)(((char *)&a - 4) + 8) >= 0) {
      *(short *)G_h01_9F76 = 2;
    } else {
      *(short *)(((char *)&a - 4) + 8) = *(short *)(((char *)&a - 4) + 8) - 1;
      *(short *)(((char *)&a - 4) + 8) = *(short *)(((char *)&a - 4) + 8);
    }
  }
  return 0;
}