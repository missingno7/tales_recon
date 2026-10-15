	far data
	dseg
	public _G_h01_2B5E
	public _G_h01_2B62
	cseg
	public _recon_h00_56B6
	public _recon_h00_56CC
	public _recon_h00_56FC
	public _recon_h00_5712
	public _recon_h00_571C
	public _end_irq2
_recon_h00_56B6
	move.w $dff002,d0
	btst #$2,d0
	bne _recon_h00_56CC
	move.w #$200,$dff09a
	bra _recon_h00_5712
_recon_h00_56CC
	subq.w #$1,_G_h01_2B5E
	bne _recon_h00_5712
	movea.l _G_h01_2B62,a0
	move.w (a0)+,d0
	tst.w d0
	bmi _recon_h00_571C
	beq _recon_h00_56FC
	move.w d0,_G_h01_2B5E
	move.w (a0)+,$dff0c4
	move.l (a0)+,$dff0c0
	move.l a0,_G_h01_2B62
	bra _recon_h00_5712
_recon_h00_56FC
	move.w d0,_G_h01_2B5E
	move.w #$4,$dff096
	move.w #$200,$dff09a
_recon_h00_5712
	move.w #$200,$dff09c
	rts
_recon_h00_571C
	move.w #$7fff,_G_h01_2B5E
	bra _recon_h00_5712
_end_irq2
	dseg
	end
