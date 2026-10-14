;:ts=8
	public	_F_h11_6ED6
_F_h11_6ED6:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#34,d0
	lea	_G_h01_A554,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.l	10(a5),a1
	move.w	12(a0),(a1)
	move.l	-4(a5),a0
	move.l	14(a5),a1
	move.w	14(a0),(a1)
	move.l	-4(a5),a0
	move.l	18(a5),a1
	move.w	18(a0),(a1)
	move.l	-4(a5),a0
	move.l	22(a5),a1
	move.w	20(a0),(a1)
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	.begin
	dseg
	public	_G_h01_A554
	end
