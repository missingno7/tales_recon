	far data
	dseg
	public _G_h01_2BFE
	public _G_h01_2C26
	public _G_h01_2C2A
	public _G_h01_2C2B
	public _G_h01_2C2C
	cseg
	public _recon_h00_61A0
	public _recon_h00_61B0
	public _recon_h00_61D8
	public _recon_h00_61F6
	public _end_cbcopy
_recon_h00_61A0
	move.b _G_h01_2C2C,d0
	sub.b d0,_G_h01_2C2A
	bmi _recon_h00_61B0
	rts
_recon_h00_61B0
	move.b #$7f,_G_h01_2C2A
	lea.l _G_h01_2BFE,a2
	move.l _G_h01_2C26,d0
	lsl.l #$3,d0
	adda.l d0,a2
	clr.l d0
	move.b _G_h01_2C2B,d0
	subq.l #$1,d0
	bpl _recon_h00_61D8
	move.w $4(a2),d0
_recon_h00_61D8
	move.b d0,_G_h01_2C2B
	lsl.w #$1,d0
	movea.l (a2),a0
	and.l #$ff,d0
	adda.l d0,a0
	move.w $6(a2),d0
	lsl.l #$2,d0
	adda.l d0,a1
	move.w $4(a2),d7
_recon_h00_61F6
	move.w (a0)+,(a1)+
	addq.l #$2,a1
	dbra d7,_recon_h00_61F6
	rts
_end_cbcopy
	dseg
	end
