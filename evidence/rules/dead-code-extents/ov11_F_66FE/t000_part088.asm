;:ts=8
	far	data
	public	_F_h11_729C
_F_h11_729C:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	lsr.w	#2,d0
	and.w	#63,d0
	move.l	#0,d1
	move.w	d0,d1
	asl.l	#1,d1
	lea	_G_h01_13A2,a0
	move.w	(a0,d1.l),d0
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	.begin
	dseg
	public	_G_h01_13A2
	end
