;:ts=8
	public	_F_h11_68B0
_F_h11_68B0:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-6(a5)
.6
	move.w	-6(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9EAC,a0
	move.l	_G_h01_9F7E,(a0,d0.l)
	add.w	#1,-6(a5)
.4
	cmp.w	#6,-6(a5)
	blt	.6
.5
	clr.w	_G_h01_9EB0
	move.w	#1,_G_h01_9EC0
	move.w	#1,_G_h01_9EC2
	move.w	#2,_G_h01_9ED0
	move.w	#1,_G_h01_9ED2
	move.w	#3,_G_h01_9EE0
	move.w	#4,_G_h01_9EE2
	move.w	#2,_G_h01_9EF0
	move.w	#1,_G_h01_9EF2
	move.w	#1,_G_h01_9F00
	move.w	#1,_G_h01_9F02
	move.w	#1,-6(a5)
.9
	move.w	-6(a5),d0
	muls.w	#40,d0
	lea	_G_h01_A464,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	(a1),d0
	muls.w	#53,d0
	move.w	d0,34(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	2(a1),d0
	asl.w	#5,d0
	add.w	#33,d0
	move.w	d0,36(a0)
	move.l	-4(a5),a0
	move.w	#20,32(a0)
	move.l	-4(a5),a0
	move.w	#20,38(a0)
	move.l	-4(a5),a0
	move.w	36(a0),-(sp)
	move.l	-4(a5),a0
	move.w	34(a0),-(sp)
	move.w	#20,-(sp)
	move.l	-4(a5),a0
	pea	10(a0)
	move.w	#8,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
	add.w	#1,-6(a5)
.7
	cmp.w	#6,-6(a5)
	blt	.9
.8
.10
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	_F_h11_41F6
	public	.begin
	dseg
	public	_G_h01_A464
	public	_G_h01_9F7E
	public	_G_h01_9F02
	public	_G_h01_9F00
	public	_G_h01_9EF2
	public	_G_h01_9EF0
	public	_G_h01_9EE2
	public	_G_h01_9EE0
	public	_G_h01_9ED2
	public	_G_h01_9ED0
	public	_G_h01_9EC2
	public	_G_h01_9EC0
	public	_G_h01_9EB0
	public	_G_h01_9EAC
	end
