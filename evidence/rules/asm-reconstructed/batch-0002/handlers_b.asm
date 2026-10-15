	far data
	dseg
	cseg
	public _recon_h00_57E4
	public _recon_h00_5A76
	public _recon_h00_5CC6
	public _recon_h00_5CD0
	public _recon_h00_5CD6
	public _recon_h00_5CDE
	public _recon_h00_5CEE
	public _recon_h00_5CF4
	public _recon_h00_5D02
	public _recon_h00_5D08
	public _recon_h00_5D1E
	public _recon_h00_5D28
	public _recon_h00_5D44
	public _recon_h00_5D5A
	public _recon_h00_5D62
	public _recon_h00_5D6C
	public _end_handlers_b
_recon_h00_5CC6
	move.l a1,d0
	btst #$0,d0
	beq _recon_h00_5CD0
	subq.l #$1,a1
_recon_h00_5CD0
	movea.l (a1),a1
	bra _recon_h00_5A76
_recon_h00_5CD6
	move.b d0,$a(a0)
	bra _recon_h00_5A76
_recon_h00_5CDE
	subq.b #$1,$a(a0)
	beq _recon_h00_5CF4
	move.l a1,d0
	btst #$0,d0
	beq _recon_h00_5CEE
	subq.l #$1,a1
_recon_h00_5CEE
	movea.l (a1),a1
	bra _recon_h00_5A76
_recon_h00_5CF4
	move.l a1,d0
	btst #$0,d0
	beq _recon_h00_5D02
	addq.l #$3,a1
	bra _recon_h00_5A76
_recon_h00_5D02
	addq.l #$4,a1
	bra _recon_h00_5A76
_recon_h00_5D08
	movem.l a0-a1,-(sp)
	and.l #$ff,d0
	jsr _recon_h00_57E4(pc)
	movem.l (sp)+,a0-a1
	bra _recon_h00_5A76
_recon_h00_5D1E
	move.l a1,d0
	btst #$0,d0
	beq _recon_h00_5D28
	subq.l #$1,a1
_recon_h00_5D28
	movea.l (a1)+,a3
	clr.w d0
	move.b $24(a0),d0
	lsl.b #$2,d0
	lea $2a(a0),a2
	move.l a1,0(a2,d0.w)
	addq.b #$1,$24(a0)
	movea.l a3,a1
	bra _recon_h00_5A76
_recon_h00_5D44
	clr.w d0
	subq.b #$1,$24(a0)
	move.b $24(a0),d0
	lea $2a(a0),a1
	movea.l 0(a1,d0.w),a1
	bra _recon_h00_5A76
_recon_h00_5D5A
	move.b d0,$12(a0)
	bra _recon_h00_5A76
_recon_h00_5D62
	move.l a1,d0
	btst #$0,d0
	beq _recon_h00_5D6C
	subq.l #$1,a1
_recon_h00_5D6C
	move.w (a1)+,$c(a0)
	bra _recon_h00_5A76
_end_handlers_b
	dseg
	end
