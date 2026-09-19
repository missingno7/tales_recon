extern unsigned int G_h01_007E;
extern unsigned int G_h01_6F48;
extern unsigned int G_h01_6F4A;
extern unsigned int G_h01_6F50;

recovered() {
  unsigned int d0;
  unsigned int a0;
  unsigned int d1;
  unsigned int a7;
  
  register unsigned int *a5;
  
  a5 = (unsigned int *)(((char *)a4) - 2);
  *(a5 - 1) = 1;
  d0 = *(a5 - 1);
  d0 *= 54;
  a0 = (unsigned int)((char *)a4 - 4276);
  *(unsigned short *)(a7 - 2) = *(unsigned short *)(a0 + d0);
  d0 = *(a5 - 1);
  d0 *= 54;
  a0 = (unsigned int)((char *)a4 - 4278);
  *(unsigned short *)(a7 - 2) = *(unsigned short *)(a0 + d0);
  d0 = *(a5 - 1);
  d0 *= 54;
  a0 = (unsigned int)((char *)a4 - 4274);
  d0 += a0;
  *(unsigned long *)(a7 - 4) = d0;
  jsr F_h00_3AE4;
  a7 += 8;
  *(a5 - 1) += 1;
  if (*(a5 - 1) < 11)
    goto L3f7a;
  return;
L3f7a:
  return;
}