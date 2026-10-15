	far data
	dseg
	public _G_h01_2B4A
	cseg
	public _recon_h00_5064
	public _recon_h00_5796
	public _recon_h00_579E
	public _recon_h00_57B6
	public _end_world
_recon_h00_5796
	movea.l _G_h01_2B4A,a4
	rts
_recon_h00_579E
	movem.l d1-d7/a0-a6,-(sp)
	movem.l a0-a1,-(sp)
	bsr _recon_h00_5796
	jsr _recon_h00_5064(pc)
	addq.l #$8,sp
	movem.l (sp)+,d1-d7/a0-a6
	clr.l d0
	rts
_recon_h00_57B6
	lea _G_h01_2B4A,a0
	move.l a4,(a0)
	rts
_end_world
	dseg
	end
