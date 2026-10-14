;:ts=8
	public	_F_h11_5C1A
_F_h11_5C1A:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	pea	18(a0)
	jsr	_F_h11_4610
	add.w	#4,sp
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_4610
	public	.begin
	dseg
	public	_G_h01_8BEC
	end
