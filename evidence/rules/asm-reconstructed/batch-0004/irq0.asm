	far data
	dseg
	public _G_h01_2B4E
	public _G_h01_2B52
	cseg
	public _recon_h00_55D6
	public _recon_h00_55EC
	public _recon_h00_561C
	public _recon_h00_5632
	public _recon_h00_563C
	public _end_irq0
_recon_h00_55D6
	move.w $dff002,d0
	btst #$0,d0
	bne _recon_h00_55EC
	move.w #$80,$dff09a
	bra _recon_h00_5632
_recon_h00_55EC
	subq.w #$1,_G_h01_2B4E
	bne _recon_h00_5632
	movea.l _G_h01_2B52,a0
	move.w (a0)+,d0
	tst.w d0
	bmi _recon_h00_563C
	beq _recon_h00_561C
	move.w d0,_G_h01_2B4E
	move.w (a0)+,$dff0a4
	move.l (a0)+,$dff0a0
	move.l a0,_G_h01_2B52
	bra _recon_h00_5632
_recon_h00_561C
	move.w d0,_G_h01_2B4E
	move.w #$1,$dff096
	move.w #$80,$dff09a
_recon_h00_5632
	move.w #$80,$dff09c
	rts
_recon_h00_563C
	move.w #$7fff,_G_h01_2B4E
	bra _recon_h00_5632
_end_irq0
	dseg
	end
