	far data
	dseg
	public _G_h01_2BC2
	public _G_h01_2C26
	cseg
	public _recon_h00_617C
	public _recon_h00_619E
	public _end_cbbridge
_recon_h00_617C
	lea.l -$2c5c(a4),a1
	movea.l $4(a1),a1
	movea.l $4(a1),a1
	addq.l #$6,a1
	lea.l _G_h01_2BC2,a0
	move.l _G_h01_2C26,d0
	lsl.l #$2,d0
	movea.l 0(a0,d0.w),a0
	jsr (a0)
_recon_h00_619E
	rts
_end_cbbridge
	dseg
	end
