extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;
extern int G_h01_A15E;

recovered(a, b) int a, b; {
  int c, d, e, f, g, h;
  c = -1;
  d = a;
  if ((d & 0xff) == 0x80) {
    d = (d >> 8) + 1;
  } else {
    d = (d >> 8);
  }
  e = d;
  if (e >= G_h01_2156) {
    e = e - 1;
  }
  f = e;
  g = G_h01_215A + f;
  if ((g & 0xff) == 0x80) {
    g = (g >> 8) + 1;
  } else {
    g = (g >> 8);
  }
  h = g;
  h = (h << 7) + G_h01_2156;
  if (F_h11_25D6(h, a, b) == 0) {
    c = G_h01_A15E;
  }
  return c;
}