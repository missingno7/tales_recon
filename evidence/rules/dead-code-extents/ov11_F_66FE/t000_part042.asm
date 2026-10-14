;:ts=8
	public	_F_h11_4848
_F_h11_4848:
	link	a5,#.2
	movem.l	.3,-(sp)
	lea	_G_h01_34EC,a0
	move.l	a0,-4(a5)
	bra	.7
.6
	move.l	-4(a5),a0
	clr.w	(a0)
.4
	add.l	#14,-4(a5)
.7
	move.l	-4(a5),d0
	lea	_G_h01_34EC,a0
	sub.l	a0,d0
	move.l	#14,d1
	jsr	.divs#
	cmp.w	#40,d0
	blt	.6
.5
.8
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	.begin
	dseg
	public	_G_h01_34EC
	end
