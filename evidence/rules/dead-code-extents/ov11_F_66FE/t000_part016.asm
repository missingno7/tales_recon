;:ts=8
	public	_F_h11_262E
_F_h11_262E:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	20(a5),d0
	cmp.w	8(a5),d0
	blt	.4
	move.w	16(a5),d0
	cmp.w	12(a5),d0
	bgt	.4
	move.w	22(a5),d0
	cmp.w	10(a5),d0
	blt	.4
	move.w	18(a5),d0
	cmp.w	14(a5),d0
	bgt	.4
	move.l	#1,d0
	bra	.5
.4
	move.l	#0,d0
.5
.6
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	.begin
	dseg
	end
