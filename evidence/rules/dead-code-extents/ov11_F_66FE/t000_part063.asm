;:ts=8
	public	_F_h11_5CEA
_F_h11_5CEA:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	tst.w	30(a0)
	ble	.4
	move.l	#1,d0
	bra	.5
.4
	move.l	#0,d0
.5
.6
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	.begin
	dseg
	public	_G_h01_8BEC
	end
