;:ts=8
	public	_F_h11_59E6
_F_h11_59E6:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#1,-2(a5)
	bra	.7
.6
	move.w	#2,-(sp)
	move.w	-2(a5),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.4
	add.w	#1,-2(a5)
.7
	move.w	-2(a5),d0
	cmp.w	_G_h01_37EC,d0
	blt	.6
.5
.8
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-2
.3	reg	
	public	_F_h11_5962
	public	.begin
	dseg
	public	_G_h01_37EC
	end
