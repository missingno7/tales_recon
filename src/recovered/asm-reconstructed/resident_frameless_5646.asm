	far data
	dseg
	public _G_h01_2B56
	public _G_h01_2B5A
	cseg
	public _recon_h00_5646
	public _recon_h00_565C
	public _recon_h00_568C
	public _recon_h00_56A2
	public _recon_h00_56AC
	public _end_irq1
_recon_h00_5646
	move.w $dff002,d0
	btst #$1,d0
	bne _recon_h00_565C
	move.w #$100,$dff09a
	bra _recon_h00_56A2
_recon_h00_565C
	subq.w #$1,_G_h01_2B56
	bne _recon_h00_56A2
	movea.l _G_h01_2B5A,a0
	move.w (a0)+,d0
	tst.w d0
	bmi _recon_h00_56AC
	beq _recon_h00_568C
	move.w d0,_G_h01_2B56
	move.w (a0)+,$dff0b4
	move.l (a0)+,$dff0b0
	move.l a0,_G_h01_2B5A
	bra _recon_h00_56A2
_recon_h00_568C
	move.w d0,_G_h01_2B56
	move.w #$2,$dff096
	move.w #$100,$dff09a
_recon_h00_56A2
	move.w #$100,$dff09c
	rts
_recon_h00_56AC
	move.w #$7fff,_G_h01_2B56
	bra _recon_h00_56A2
_end_irq1
	dseg
	end
