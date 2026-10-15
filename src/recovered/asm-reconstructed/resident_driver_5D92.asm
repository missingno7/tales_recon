	far data
	dseg
	public _G_h01_2B86
	public _G_h01_2B8A
	public _G_h01_2B8C
	public _G_h01_2B8D
	cseg
	public _resident_asm_559E
	public _recon_h00_5A76
	public _recon_h00_5D92
	public _recon_h00_5D98
	public _recon_h00_5DA0
	public _recon_h00_5DA4
	public _recon_h00_5DAC
	public _recon_h00_5DB4
	public _recon_h00_5DBC
	public _recon_h00_5DC6
	public _recon_h00_5DD0
	public _recon_h00_5DDA
	public _recon_h00_5DF6
	public _recon_h00_5DFE
	public _recon_h00_5E64
	public _end_handlers_d
_recon_h00_5D92
	subq.l #$1,a1
	bra _recon_h00_5A76
_recon_h00_5D98
	move.b d0,$3a(a0)
	bra _recon_h00_5A76
_recon_h00_5DA0
	bra _recon_h00_5A76
_recon_h00_5DA4
	move.b d0,$49(a0)
	bra _recon_h00_5A76
_recon_h00_5DAC
	move.b d0,$44(a0)
	bra _recon_h00_5A76
_recon_h00_5DB4
	move.b d0,$46(a0)
	bra _recon_h00_5A76
_recon_h00_5DBC
	move.b d0,_G_h01_2B8D
	bra _recon_h00_5A76
_recon_h00_5DC6
	move.b d0,_G_h01_2B8C
	bra _recon_h00_5A76
_recon_h00_5DD0
	add.b d0,_G_h01_2B8C
	bra _recon_h00_5A76
_recon_h00_5DDA
	move.b d0,$8(a0)
	move.l $3c(a0),d0
	move.l d0,$1a(a0)
	move.b #$1,$1e(a0)
	clr.b $1f(a0)
	move.l a1,$4(a0)
	rts
_recon_h00_5DF6
	move.b d0,$3b(a0)
	bra _recon_h00_5A76
_recon_h00_5DFE
	move.b d0,$8(a0)
	move.l $3c(a0),d0
	move.l d0,$1a(a0)
	move.b #$1,$1e(a0)
	clr.b $1f(a0)
	move.l a1,$4(a0)
	move.b #$1,$39(a0)
	move.w #$1,d2
	lsl.w d7,d2
	move.w d2,$dff096
	jsr _resident_asm_559E(pc)
	move.w _G_h01_2B8A,d2
	and.w #$3ff,d2
	clr.l d0
	move.w _G_h01_2B86,d0
	lsr.w #$3,d0
	move.w #$e08,d1
	sub.w d0,d1
	add.w #$fa5,d1
	add.w d2,d1
	move.w d7,d3
	lsl.w #$4,d3
	movea.l #$dff0a0,a3
	adda.w d3,a3
	move.w d1,$6(a3)
	swap d1
	move.l d1,(a0)
	rts
_recon_h00_5E64
	move.b d0,$46(a0)
	bra _recon_h00_5A76
_end_handlers_d
	dseg
	end
