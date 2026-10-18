	far data
	dseg
	public _noise_period_offset
	cseg
	public _recon_h00_57D2
	public _end_stackstart
_recon_h00_57D2
	move.w $4(a7),d0
	cmp.b #$8,d0
	bne _end_stackstart
	move.w d0,_noise_period_offset
	rts
_end_stackstart
	dseg
	end
