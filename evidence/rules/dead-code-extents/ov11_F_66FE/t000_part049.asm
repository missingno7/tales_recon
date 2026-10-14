;:ts=8
	public	_F_h11_4EC6
_F_h11_4EC6:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-6(a5)
.6
	move.w	-6(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9C8C,a0
	move.l	_G_h01_9F82,(a0,d0.l)
	move.w	-6(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9CBC,a0
	move.l	_G_h01_9F82,(a0,d0.l)
	move.w	-6(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9C92,a0
	move.w	#1,(a0,d0.l)
	move.w	-6(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9CC2,a0
	move.w	#1,(a0,d0.l)
.4
	add.w	#1,-6(a5)
	cmp.w	#3,-6(a5)
	blt	.6
.5
	move.w	#6,_G_h01_9C90
	move.w	#7,_G_h01_9CA0
	move.w	#6,_G_h01_9CB0
	move.w	#2,_G_h01_9CC0
	move.w	#3,_G_h01_9CD0
	move.w	#2,_G_h01_9CE0
	clr.w	-6(a5)
.9
	move.w	-6(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9CEC,a0
	move.l	_G_h01_9F82,(a0,d0.l)
.7
	add.w	#1,-6(a5)
	cmp.w	#4,-6(a5)
	blt	.9
.8
	clr.w	_G_h01_9CF0
	move.w	#1,_G_h01_9D00
	move.w	#4,_G_h01_9D10
	move.w	#5,_G_h01_9D20
	clr.w	-6(a5)
.12
	move.w	-6(a5),d0
	muls.w	#40,d0
	lea	_G_h01_3724,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	30(a1),d0
	muls.w	#53,d0
	move.w	d0,26(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	32(a1),d0
	asl.w	#5,d0
	add.w	#32,d0
	move.w	d0,28(a0)
	move.l	-4(a5),a0
	move.w	#14,22(a0)
	move.w	#5,-(sp)
	move.w	-6(a5),-(sp)
	jsr	_F_h11_54F8
	add.w	#4,sp
	move.l	-4(a5),a0
	move.w	28(a0),-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),-(sp)
	move.w	#14,-(sp)
	move.l	-4(a5),-(sp)
	move.w	#11,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
.10
	add.w	#1,-6(a5)
	cmp.w	#5,-6(a5)
	blt	.12
.11
	move.b	_G_h01_46E0,d0
	ext.w	d0
	ext.l	d0
	bra	.13
.15
	move.w	#80,_G_h01_371C
	move.w	#75,_G_h01_371E
	move.w	#20,_G_h01_3720
	bra	.14
.16
	move.w	#70,_G_h01_371C
	move.w	#85,_G_h01_371E
	move.w	#20,_G_h01_3720
	bra	.14
.17
	move.w	#60,_G_h01_371C
	move.w	#90,_G_h01_371E
	move.w	#10,_G_h01_3720
	bra	.14
.13
	tst.l	d0
	beq	.15
	sub.l	#1,d0
	beq	.16
	sub.l	#1,d0
	beq	.17
.14
	move.w	_G_h01_3720,d0
	muls.w	#3,d0
	move.w	d0,_G_h01_3722
.18
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	_F_h11_41F6
	public	_F_h11_54F8
	public	.begin
	dseg
	public	_G_h01_46E0
	public	_G_h01_3722
	public	_G_h01_3720
	public	_G_h01_371E
	public	_G_h01_371C
	public	_G_h01_9D20
	public	_G_h01_9D10
	public	_G_h01_9D00
	public	_G_h01_9CF0
	public	_G_h01_9CEC
	public	_G_h01_9CE0
	public	_G_h01_9CD0
	public	_G_h01_9CC0
	public	_G_h01_9CB0
	public	_G_h01_9CA0
	public	_G_h01_9C90
	public	_G_h01_9CC2
	public	_G_h01_9C92
	public	_G_h01_9CBC
	public	_G_h01_9C8C
	public	_G_h01_9F82
	public	_G_h01_3724
	end
