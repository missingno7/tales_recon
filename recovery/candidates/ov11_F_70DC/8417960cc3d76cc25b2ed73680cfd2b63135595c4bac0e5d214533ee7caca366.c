extern int G_h01_12FE;
extern int G_h01_94B0;
extern int G_h01_94BA;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_A6A8;
int F_h11_25D6(a, b, c) int a, b, c; {}
int F_h11_25F8(a, b, c, d, e, f) int a, b, c, d, e, f; {}
recovered(a, b) int a, b; {
  int *p;
  int c;
  p = (int *)(((long)a * 10) + (long)G_h01_94B0);
  c = *p;
  c++;
  F_h11_25D6(c, G_h01_12FE, a);
  if (c == 0)
    return 0;
  c = *(p + 3);
  c += 30;
  *(p + 2) += 48;
  *(p + 1) += 16;
  *(p + 3) = (G_h01_94BA >> 1) + G_h01_94C0;
  F_h11_25F8(*(p + 3), *(p + 2), *(p + 1), c, a, b);
  if (c == 0)
    return 0;
  G_h01_94BE = 1;
  return 0;
}