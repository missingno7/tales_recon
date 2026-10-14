;:ts=8
	public	_F_h11_2E26
_F_h11_2E26:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#6,d0
	lea	_G_h01_9FCE,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.w	#2,14(a0)
	move.l	-4(a5),a0
	tst.w	16(a0)
	beq	.5
	cmp.w	#7,10(a5)
	bne	.4
.5
	move.l	-4(a5),a0
	move.w	10(a5),16(a0)
.4
	cmp.w	#7,10(a5)
	bne	.6
	move.w	8(a5),d0
	add.w	#1,d0
	move.w	d0,-(sp)
	move.w	#74,-(sp)
	move.w	#64,-(sp)
	move.l	-4(a5),a0
	move.w	42(a0),-(sp)
	move.l	-4(a5),a0
	move.w	38(a0),-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
	move.l	-4(a5),a0
	tst.w	24(a0)
	beq	.7
	move.w	#7,-(sp)
	move.l	-4(a5),a0
	move.w	24(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.7
	move.l	-4(a5),a0
	tst.w	26(a0)
	beq	.8
	move.w	#7,-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.8
	move.l	-4(a5),a0
	tst.w	28(a0)
	beq	.9
	move.w	#7,-(sp)
	move.l	-4(a5),a0
	move.w	28(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.9
.6
.10
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_5962
	public	_F_h11_4696
	public	.begin
	dseg
	public	_G_h01_9FCE
	end
