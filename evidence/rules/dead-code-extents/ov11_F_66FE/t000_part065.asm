;:ts=8
	public	_F_h11_5EC0
_F_h11_5EC0:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.w	#1,48(a0)
	clr.w	_G_h01_94B4
	clr.w	_G_h01_94D6
	clr.w	_G_h01_37F0
	clr.w	_G_h01_37EE
	move.w	#3,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_5C42
	add.w	#4,sp
	move.l	-4(a5),a0
	move.w	46(a0),-(sp)
	move.l	-4(a5),a0
	move.w	44(a0),-(sp)
	move.w	#1,-(sp)
	move.l	-4(a5),a0
	pea	18(a0)
	move.w	#24,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_41F6
	public	_F_h11_5C42
	public	.begin
	dseg
	public	_G_h01_37F0
	public	_G_h01_37EE
	public	_G_h01_94D6
	public	_G_h01_94B4
	public	_G_h01_8BEC
	end
