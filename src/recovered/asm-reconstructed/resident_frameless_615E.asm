	far data
	dseg
	public _G_h01_2B4A
	public _G_h01_B1EC
	cseg
	public _recon_h00_58BC
	public _recon_h00_615E
	public _end_cbwrap
_recon_h00_615E
	movem.l d1-d7/a0-a5,-(a7)
	addq.l #$1,_G_h01_B1EC
	movea.l _G_h01_2B4A,a4
	bsr _end_cbwrap
	jsr _recon_h00_58BC
	movem.l (a7)+,d1-d7/a0-a5
	clr.l d0
	rts
_end_cbwrap
	dseg
	end
