	far data
	dseg
	public _G_h01_2B86
	cseg
	public _recon_h00_57D2
	public _end_stackstart
_recon_h00_57D2
	move.w $4(a7),d0
	cmp.b #$8,d0
	bne _end_stackstart
	move.w d0,_G_h01_2B86
	rts
_end_stackstart
	dseg
	end
