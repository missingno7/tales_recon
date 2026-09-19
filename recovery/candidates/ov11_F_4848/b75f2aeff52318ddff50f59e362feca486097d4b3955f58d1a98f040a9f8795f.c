extern unsigned int G_h01_00FC;
extern unsigned int G_h01_34EC;
recovered() {
  char *a0;
  int d0;
  int d1;
  a0 = (char *)-19218(a4);
  *(char **)(-4(a5)) = a0;
  goto L4864;
L4856:
  *(char *)(a0) = 0;
  (-4(a5)) += 14;
L4864:
  d0 = (-4(a5));
  a0 = (char *)-19218(a4);
  d0 -= (long)a0;
  d1 = 14;
  jsr -32514(a4);
  if (d0 < 28) goto L4856;
  unlk a5;
  rts;
}