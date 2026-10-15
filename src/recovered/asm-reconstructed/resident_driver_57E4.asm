	far data
	dseg
	public _G_h01_29FA
	public _G_h01_2A0A
	public _G_h01_B39A
	cseg
	public _recon_h00_57E4
	public _recon_h00_5862
	public _end_start
_recon_h00_57E4
	movem.l d0-d2/a0-a1,-(sp)
	and.l #$ff,d0
	lsl.l #$2,d0
	movea.l _G_h01_B39A,a0
	movea.l 0(a0,d0.l),a0
	clr.w d0
	move.b (a0)+,d0
	move.b (a0)+,d1
	and.w #$ff,d1
	lsl.l #$2,d0
	lea _G_h01_29FA,a1
	movea.l 0(a1,d0.w),a1
	move.b $3b(a1),d2
	and.w #$ff,d2
	cmp.w d2,d1
	bcs _recon_h00_5862
	move.b d1,$3b(a1)
	lsr.l #$2,d0
	bclr d0,_G_h01_2A0A
	move.l a0,$4(a1)
	clr.b $24(a1)
	clr.w $12(a1)
	clr.w $c(a1)
	clr.l $e(a1)
	clr.b $23(a1)
	clr.b $45(a1)
	clr.b $46(a1)
	clr.b $47(a1)
	clr.b $48(a1)
	move.b #$ff,$49(a1)
	move.b #$1,$8(a1)
	move.b #$1,$44(a1)
_recon_h00_5862
	movem.l (sp)+,d0-d2/a0-a1
	rts
_end_start
	dseg
	end
