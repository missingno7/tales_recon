;:ts=8
	public	_F_h11_415A
_F_h11_415A:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A15E,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	12(a0),d0
	cmp.w	14(a1),d0
	bge	.5
	move.l	10(a5),a0
	move.w	(a0),-(sp)
	jsr	_F_h11_3F90
	add.w	#2,sp
	tst.w	d0
	bge	.4
.5
	clr.w	_G_h01_94B6
	clr.w	_G_h01_94D4
	move.w	#6,_G_h01_94AE
	move.w	#6,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
	bra	.6
.4
	tst.w	_G_h01_A15A
	bne	.7
	move.l	10(a5),a0
	add.w	#4,(a0)
	move.l	-4(a5),a0
	move.w	12(a0),d0
	asl.w	#1,d0
	move.l	-4(a5),a0
	add.w	2(a0),d0
	sub.w	#26,d0
	move.w	d0,-6(a5)
	tst.w	_G_h01_A156
	bne	.8
	move.w	_G_h01_94C0,_G_h01_A156
.8
	move.l	14(a5),a0
	move.w	-6(a5),d0
	sub.w	_G_h01_A156,d0
	add.w	d0,(a0)
	move.w	-6(a5),_G_h01_A156
.7
.6
.9
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	_F_h11_4B0C
	public	_F_h11_3F90
	public	.begin
	dseg
	public	_G_h01_A15E
	public	_G_h01_A15A
	public	_G_h01_A156
	public	_G_h01_94D4
	public	_G_h01_94C0
	public	_G_h01_94B6
	public	_G_h01_94AE
	end
