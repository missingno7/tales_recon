	far data
	dseg
	public _G_h00_5E6C
	public _G_h01_292E
	public _G_h01_2A0A
	public _G_h01_2B4E
	cseg
	public _resident_asm_559E
	public _resident_asm_59A4
	public _recon_h00_5A50
	public _recon_h00_5A68
	public _recon_h00_5A72
	public _recon_h00_5A76
	public _recon_h00_5A8A
	public _recon_h00_5A9C
	public _recon_h00_5ACA
	public _recon_h00_5AE0
	public _recon_h00_5B06
	public _recon_h00_5B20
	public _recon_h00_5B26
	public _recon_h00_5B3A
	public _recon_h00_5B62
	public _recon_h00_5B8C
	public _recon_h00_5BAA
	public _recon_h00_5BBC
	public _recon_h00_5BC6
	public _recon_h00_5BE6
	public _recon_h00_5BF0
	public _recon_h00_5C4A
	public _recon_h00_5C6A
	public _recon_h00_5C7C
	public _recon_h00_5C8A
	public _recon_h00_5C90
	public _recon_h00_5CB6
	public _end_dispatch
_G_h01_27E4_A4 equ -22554
_recon_h00_5A50
	btst d7,_G_h01_2A0A
	beq _recon_h00_5A68
	move.b $19(a0),d0
	lsr.b #$1,d0
	move.b d0,$18(a0)
	move.b $37(a0),$38(a0)
_recon_h00_5A68
	move.b (a1)+,$8(a0)
	move.l a1,$4(a0)
	rts
_recon_h00_5A72
	movea.l $4(a0),a1
_recon_h00_5A76
	tst.b (a1)
	bpl _recon_h00_5A9C
	move.b (a1)+,d0
	and.w #$7f,d0
	cmp.b #$2c,d0
	ble _recon_h00_5A8A
	bra _recon_h00_5B62
_recon_h00_5A8A
	lsl.w #$2,d0
	lea _G_h01_292E,a2
	movea.l 0(a2,d0.w),a2
	clr.w d0
	move.b (a1)+,d0
	jmp (a2)
_recon_h00_5A9C
	move.w #$1,d2
	lsl.w d7,d2
	move.w d2,$dff096
	clr.w d0
	move.b (a1)+,d0
	bsr _resident_asm_59A4
	move.b #$1,$1e(a0)
	clr.b $1f(a0)
	move.l $3c(a0),d0
	move.l d0,$1a(a0)
	move.b #$1,$39(a0)
	bra _recon_h00_5A50
_recon_h00_5ACA
	move.w #$1,d2
	lsl.w d7,d2
	move.w d2,$dff096
	move.l a1,d0
	btst #$0,d0
	beq _recon_h00_5AE0
	subq.l #$1,a1
_recon_h00_5AE0
	move.w d7,d3
	lsl.w #$4,d3
	movea.l #$dff0a0,a3
	adda.w d3,a3
	move.w (a1)+,d0
	move.w d0,$6(a3)
	swap d0
	move.l d0,(a0)
	movea.l $26(a0),a2
	move.l a2,(a3)
	move.b #$1,$39(a0)
	bra _recon_h00_5A50
_recon_h00_5B06
	move.w #$1,d2
	lsl.w d7,d2
	move.w d2,$dff096
	bsr _resident_asm_59A4
	move.b #$1,$39(a0)
	bra _recon_h00_5A50
_recon_h00_5B20
	subq.l #$1,a1
	bra _recon_h00_5A50
_recon_h00_5B26
	move.b d0,d1
	jsr _resident_asm_559E(pc)
	and.b d1,d0
	addq.b #$1,d0
	move.b d0,$8(a0)
	move.l a1,$4(a0)
	rts
_recon_h00_5B3A
	move.b d0,$8(a0)
	move.w #$1,d2
	lsl.w d7,d2
	move.w d2,$dff096
	clr.b $1e(a0)
	move.l a1,$4(a0)
	move.w d7,d1
	lsl.w #$3,d1
	lea _G_h01_2B4E,a2
	clr.w 0(a2,d1.w)
	rts
_recon_h00_5B62
	clr.l $4(a0)
	move.w #$1,d2
	lsl.w d7,d2
	move.w d2,$dff096
	clr.b $1e(a0)
	move.w d7,d1
	lsl.w #$3,d1
	lea _G_h01_2B4E,a2
	clr.w 0(a2,d1.w)
	move.b #$0,$3b(a0)
	rts
_recon_h00_5B8C
	and.w #$ff,d0
	lsl.w #$2,d0
	lea _G_h00_5E6C,a2
	move.l 0(a2,d0.w),$3c(a0)
	addq.w #$4,d0
	move.l 0(a2,d0.w),$40(a0)
	bra _recon_h00_5A76
_recon_h00_5BAA
	move.b d0,d1
	lsl.w #$8,d1
	move.b (a1)+,d1
	ext.l d1
	lsl.l #$8,d1
	move.l d1,$e(a0)
	bra _recon_h00_5A76
_recon_h00_5BBC
	clr.l $e(a0)
	subq.l #$1,a1
	bra _recon_h00_5A76
_recon_h00_5BC6
	move.w d7,d1
	lsl.w #$3,d1
	lea _G_h01_2B4E,a2
	tst.w 0(a2,d1.w)
	beq _recon_h00_5BF0
	clr.l $4(a0)
	clr.b $1e(a0)
	move.b #$0,$3b(a0)
	rts
_recon_h00_5BE6
	move.w d7,d1
	lsl.w #$3,d1
	lea _G_h01_2B4E,a2
_recon_h00_5BF0
	movem.l a3-a4,-(sp)
	move.w #$1,d2
	lsl.w d7,d2
	move.w d2,$dff096
	move.w d7,d3
	lsl.w #$4,d3
	movea.l #$dff0a0,a3
	adda.w d3,a3
	and.w #$ff,d0
	lsl.w #$2,d0
	lea _G_h01_27E4_A4(a4),a4
	movea.l 0(a4,d0.w),a4
	move.w (a4)+,0(a2,d1.w)
	move.w (a4)+,$4(a3)
	move.l (a4)+,(a3)
	move.l a4,$4(a2,d1.w)
	move.b #$1,$39(a0)
	move.l $3c(a0),d0
	move.l d0,$1a(a0)
	move.b #$1,$1e(a0)
	clr.b $1f(a0)
	move.l a1,d0
	btst #$0,d0
	beq _recon_h00_5C4A
	addq.l #$1,a1
_recon_h00_5C4A
	move.w (a1)+,d0
	move.w d0,$6(a3)
	swap d0
	move.l d0,(a0)
	movem.l (sp)+,a3-a4
	move.b (a1)+,d0
	cmp.b #$a7,d0
	beq _recon_h00_5C7C
	move.b d0,$8(a0)
	move.l a1,$4(a0)
	rts
_recon_h00_5C6A
	move.w d7,d3
	lsl.w #$3,d3
	lea _G_h01_2B4E,a2
	adda.w d3,a2
	tst.w (a2)
	beq _recon_h00_5C8A
	subq.l #$1,a1
_recon_h00_5C7C
	subq.l #$1,a1
	move.b #$1,$8(a0)
	move.l a1,$4(a0)
	rts
_recon_h00_5C8A
	subq.l #$1,a1
	bra _recon_h00_5A76
_recon_h00_5C90
	move.b d0,$37(a0)
	move.b (a1)+,d0
	move.b d0,d1
	and.b #$f,d0
	move.b d0,$19(a0)
	move.b $19(a0),$18(a0)
	lsr.b #$4,d1
	move.b d1,$25(a0)
	bset d7,_G_h01_2A0A
	bra _recon_h00_5A76
_recon_h00_5CB6
	bclr d7,_G_h01_2A0A
	subq.l #$1,a1
	bra _recon_h00_5A76
_end_dispatch
	dseg
	end
