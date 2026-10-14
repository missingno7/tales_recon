	far data
	public _resident_asm_59A4,_resident_asm_5A50
_G_h01_27E4_A4 equ -22554
_resident_asm_59A4
	movem.l a2-a4,-(sp)
	and.w #$ff,d0
	clr.l d1
	move.b d0,d1
	and.b #$f,d1
	add.b $12(a0),d1
	cmp.b #$b,d1
	ble _L59C6
	add.b #$10,d0
	sub.b #$c,d1
_L59C6
	add.b $23(a0),d0
	bpl _L59CE
	clr.w d0
_L59CE
	lsr.b #4,d0
	move.w d7,d3
	lsl.w #3,d3
	lea _G_h01_2B4E,a2
	adda.w d3,a2
	move.w d7,d3
	lsl.w #4,d3
	movea.l #$dff0a0,a3
	adda.w d3,a3
	cmp.b #1,d0
	bhi _L59F6
	moveq #2,d3
	sub.b d0,d3
	clr.l d0
	bra _L59FA
_L59F6
	subq.b #2,d0
	moveq #0,d3
_L59FA
	add.b $3a(a0),d0
	lsl.w #2,d0
	lea _G_h01_27E4_A4(a4),a4
	movea.l 0(a4,d0.w),a4
	move.w (a4)+,(a2)
	move.w (a4)+,4(a3)
	move.l (a4)+,(a3)
	move.l a4,4(a2)
	move.b #1,$39(a0)
	lsl.w #1,d1
	lea _G_h01_29DE,a2
	move.w 0(a2,d1.w),d1
	add.w $c(a0),d1
	lsl.l d3,d1
	move.w d1,6(a3)
	btst d7,_G_h01_2A0A
	beq _L5A46
	move.l d1,d2
	clr.l d3
	move.b $25(a0),d3
	lsl.l d3,d2
	move.l d2,$14(a0)
_L5A46
	swap d1
	move.l d1,(a0)
	movem.l (sp)+,a2-a4
	rts
_resident_asm_5A50
	dseg
	public _G_h01_2B4E,_G_h01_29DE,_G_h01_2A0A
	end
