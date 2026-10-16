	far data
	dseg
	cseg
	public _recon_h00_6FDE
	public _recon_h00_701A
	public _recon_h00_702E
	public _end_debugfmt
_recon_h00_701A
	lea.l $8(a7),a1
	movea.l $4(a7),a0
	move.l a2,-(a7)
	lea.l _recon_h00_6FDE,a2
	bsr _recon_h00_702E
	movea.l (a7)+,a2
	rts
_recon_h00_702E
	move.l a6,-(a7)
	movea.l $4,a6
	jsr -$20a(a6)
	movea.l (a7)+,a6
	rts
_end_debugfmt
	dseg
	end
