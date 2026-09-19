void F_h00_3B84() {
  link.w a5, #$0;
  move.l $2462(a4), -(a7);
  jsr -$7f74(a4);
  addq.w #$4, a7;
  unlk a5;
  rts;
}