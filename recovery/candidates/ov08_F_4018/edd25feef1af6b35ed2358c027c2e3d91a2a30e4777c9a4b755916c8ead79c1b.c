extern unsigned int G_h01_12B5;
extern unsigned int G_h01_12BB;
extern unsigned int G_h01_6F3C;

recovered() {
  short i;
  short c;
  i = 0;
L2:
  c = (short)(G_h01_12B5 + (i * 6));
  if (c == 6 || c == 4 || c != 9) {
    goto L3;
  }
  G_h01_6F3C = (unsigned int)(G_h01_12BB + (i * 6));
  G_h01_6F3C = (unsigned int)(G_h01_12BB + (i * 6) + 1);
L3:
  i++;
  if (i < 25) {
    goto L2;
  }
  G_h01_12B5 = 0;
  G_h01_12BB = 0;
}