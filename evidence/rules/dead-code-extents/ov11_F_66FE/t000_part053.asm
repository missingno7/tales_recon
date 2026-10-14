;:ts=8
	public	_F_h11_54F8
_F_h11_54F8:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#40,d0
	lea	_G_h01_3724,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.w	#2,12(a0)
	move.l	-4(a5),a0
	tst.w	14(a0)
	beq	.5
	cmp.w	#5,10(a5)
	bne	.4
.5
	move.l	-4(a5),a0
	move.w	10(a5),14(a0)
.4
	cmp.w	#5,10(a5)
	bne	.6
	move.w	#11,-(sp)
	move.w	#48,-(sp)
	move.w	#64,-(sp)
	move.l	-4(a5),a0
	move.w	28(a0),-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
	move.l	-4(a5),a0
	tst.w	34(a0)
	beq	.7
	move.w	#5,-(sp)
	move.l	-4(a5),a0
	move.w	34(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.7
	move.l	-4(a5),a0
	tst.w	36(a0)
	beq	.8
	move.w	#5,-(sp)
	move.l	-4(a5),a0
	move.w	36(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.8
	move.l	-4(a5),a0
	tst.w	38(a0)
	beq	.9
	move.w	#5,-(sp)
	move.l	-4(a5),a0
	move.w	38(a0),-(sp)
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
	public	_G_h01_3724
	end
