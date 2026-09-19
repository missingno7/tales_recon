void ov11_F_5A12() {
    short a5;
    short d0;
    short d1;
    long a0;

    link.w a5, #$fffe;
    tst.w $8(a5);
    if (eq) {
        move.w $a(a5), d0;
        ext.l d0;
        asl.l #$1, d0;
        lea.l -$480a(a4), a0;
        move.l d0, d1;
        move.w (a0, d1.l), d0;
        unlk a5;
        rts;
    } else {
        clr.w -$2(a5);
        move.w -$2(a5), d0;
        ext.l d0;
        asl.l #$1, d0;
        lea.l -$480a(a4), a0;
        move.w -$2(a5), d1;
        addq.w #$1, d1;
        muls.w #$35, d1;
        addq.w #$2, d1;
        move.w d1, (a0, d0.l);
        addq.w #$1, -$2(a5);
        cmpi.w #$28, -$2(a5);
        if (blt) {
            bra.b $5a20;
        }
    }
    bra.b $5a5c;
}