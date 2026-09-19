extern unsigned int G_h01_007E;
extern unsigned int G_h01_6F48;
extern unsigned int G_h01_6F4A;
extern unsigned int G_h01_6F50;

recovered() {
  unsigned int d0;
  unsigned int a0;
  unsigned int d1;
  unsigned int a7;
  
  link a5, #-2
  move.w #1, -2(a5)
  move.w -2(a5), d0
  muls.w #54, d0
  lea.l -4276(a4), a0
  move.w (a0, d0.l), -(a7)
  move.w -2(a5), d0
  muls.w #54, d0
  lea.l -4278(a4), a0
  move.w (a0, d0.l), -(a7)
  move.w -2(a5), d0
  muls.w #54, d0
  lea.l -4274(a4), a0
  add.l a0, d0
  move.l d0, -(a7)
  jsr -32640(a4)
  addq.w #8, a7
  addq.w #1, -2(a5)
  cmpi.w #11, -2(a5)
  blt.b $3f7a
  unlk a5
  rts
}