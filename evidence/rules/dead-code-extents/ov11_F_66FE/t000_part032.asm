;:ts=8
	public	_F_h11_3F90
_F_h11_3F90:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#-1,-12(a5)
	move.w	8(a5),d0
	ext.l	d0
	divs.w	#128,d0
	add.w	#1,d0
	move.w	d0,-6(a5)
	move.w	8(a5),d0
	ext.l	d0
	divs.w	#128,d0
	swap	d0
	cmp.w	_G_h01_A154,d0
	bge	.4
	sub.w	#1,-6(a5)
.4
	move.w	-6(a5),d0
	sub.w	#1,d0
	asl.w	#7,d0
	add.w	_G_h01_A154,d0
	move.w	d0,-10(a5)
	move.w	_G_h01_A158,d0
	add.w	-6(a5),d0
	ext.l	d0
	divs.w	_G_h01_A152,d0
	swap	d0
	move.w	d0,-8(a5)
	move.w	-8(a5),d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A15E,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	cmp.w	#1,4(a0)
	bne	.5
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	12(a0),d0
	cmp.w	14(a1),d0
	bge	.5
	move.l	-4(a5),a0
	move.w	8(a0),d0
	add.w	-10(a5),d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	12(a0),d0
	add.w	-10(a5),d0
	add.w	#10,d0
	move.w	d0,-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	beq	.6
	move.w	-8(a5),-12(a5)
.6
.5
	move.w	-12(a5),d0
.7
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-12
.3	reg	
	public	_F_h11_25D6
	public	.begin
	dseg
	public	_G_h01_A15E
	public	_G_h01_A158
	public	_G_h01_A154
	public	_G_h01_A152
	public	_G_h01_94BE
	public	_G_h01_94B0
	end
