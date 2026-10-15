	far data
	dseg
	public _G_h01_2A0A
	public _G_h01_2A12
	public _G_h01_2B4E
	public _G_h01_2B56
	public _G_h01_2B5E
	public _G_h01_2B66
	public _G_h01_2B8C
	public _G_h01_2B8D
	cseg
	public _recon_h00_5868
	public _recon_h00_587A
	public _end_clear
_recon_h00_5868
	movem.l d7/a0,-(a7)
	clr.b _G_h01_2A0A
	lea.l _G_h01_2A12,a0
	moveq #$4b,d7
_recon_h00_587A
	clr.l (a0)+
	dbra d7,_recon_h00_587A
	move.w #$f,$dff096
	move.w #$ff,$dff09e
	clr.w _G_h01_2B4E
	clr.w _G_h01_2B56
	clr.w _G_h01_2B5E
	clr.w _G_h01_2B66
	clr.b _G_h01_2B8C
	move.b #$1,_G_h01_2B8D
	movem.l (a7)+,d7/a0
	rts
_end_clear
	dseg
	end
