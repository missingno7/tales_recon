	far data
	dseg
	public _G_h01_2B6E
	public _G_h01_2B8C
	public _G_h01_2B8D
	cseg
	public _recon_h00_544C
	public _recon_h00_5480
	public _recon_h00_548A
	public _recon_h00_5496
	public _recon_h00_5498
	public _recon_h00_54AE
	public _recon_h00_54B0
	public _recon_h00_54B6
	public _recon_h00_54CA
	public _recon_h00_54DE
	public _recon_h00_54E8
	public _recon_h00_54EE
	public _recon_h00_5530
	public _recon_h00_553C
	public _recon_h00_5558
	public _recon_h00_5568
	public _recon_h00_5574
	public _recon_h00_5586
	public _end_envelope
_recon_h00_544C
	tst.b $1e(a0)
	beq _recon_h00_54AE
	clr.w d3
	move.b $1f(a0),d3
	movea.l $1a(a0),a3
	clr.w d0
	move.b $1e(a0),d0
	lsl.l #$2,d0
	lea _G_h01_2B6E,a2
	movea.l 0(a2,d0.w),a2
	jsr (a2)
	clr.w d2
	move.b $22(a0),d2
	sub.b $45(a0),d2
	bcc _recon_h00_5480
	clr.b d2
	bra _recon_h00_5498
_recon_h00_5480
	sub.b $46(a0),d2
	bcc _recon_h00_548A
	clr.b d2
	bra _recon_h00_5498
_recon_h00_548A
	sub.b _G_h01_2B8C,d2
	bcc _recon_h00_5496
	clr.b d2
	bra _recon_h00_5498
_recon_h00_5496
	lsr.w #$2,d2
_recon_h00_5498
	move.l d7,d3
	lsl.w #$4,d3
	movea.l #$dff0a8,a2
	adda.l d3,a2
	tst.b _G_h01_2B8D
	beq _recon_h00_54B0
	move.w d2,(a2)
_recon_h00_54AE
	rts
_recon_h00_54B0
	clr.w d2
	move.w d2,(a2)
	rts
_recon_h00_54B6
	tst.b 0(a3,d3.w)
	bne _recon_h00_54DE
	addq.w #$1,d3
	tst.b 0(a3,d3.w)
	bne _recon_h00_54CA
	clr.b $1e(a0)
	rts
_recon_h00_54CA
	move.b #$4,$1e(a0)
	move.b 0(a3,d3.w),$21(a0)
	addq.b #$1,d3
	move.b d3,$1f(a0)
	rts
_recon_h00_54DE
	bmi _recon_h00_54E8
	move.b #$2,$1e(a0)
	bra _recon_h00_54EE
_recon_h00_54E8
	move.b #$3,$1e(a0)
_recon_h00_54EE
	move.b 0(a3,d3.w),$20(a0)
	addq.b #$1,d3
	move.b 0(a3,d3.w),$21(a0)
	addq.b #$1,d3
	move.b d3,$1f(a0)
	rts
	move.l $40(a0),d0
	move.l d0,$1a(a0)
	movea.l d0,a3
	clr.l d3
	bsr _recon_h00_54B6
	rts
	move.b 0(a3,d3.w),$22(a0)
	addq.w #$1,d3
	bsr _recon_h00_54B6
	rts
	move.b $22(a0),d0
	add.b $20(a0),d0
	bcs _recon_h00_5530
	cmp.b $21(a0),d0
	bcs _recon_h00_553C
_recon_h00_5530
	move.b $21(a0),d0
	move.b d0,$22(a0)
	jsr _recon_h00_54B6(pc)
_recon_h00_553C
	move.b d0,$22(a0)
	rts
	move.b $22(a0),d0
	move.b d0,d1
	add.b $20(a0),d0
	beq _recon_h00_5558
	cmp.b d1,d0
	bcc _recon_h00_5558
	cmp.b $21(a0),d0
	bcc _recon_h00_5574
_recon_h00_5558
	tst.b $21(a0)
	bne _recon_h00_5568
	clr.b $22(a0)
	clr.b $1e(a0)
	rts
_recon_h00_5568
	move.b $21(a0),d0
	move.b d0,$22(a0)
	jsr _recon_h00_54B6(pc)
_recon_h00_5574
	move.b d0,$22(a0)
	rts
	subq.b #$1,$21(a0)
	tst.b $21(a0)
	beq _recon_h00_5586
	rts
_recon_h00_5586
	bra _recon_h00_54B6
_end_envelope
	dseg
	end
