;:ts=8
	public	_F_h11_5C42
_F_h11_5C42:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.w	#2,30(a0)
	move.l	-4(a5),a0
	tst.w	32(a0)
	beq	.5
	cmp.w	#3,10(a5)
	bne	.4
.5
	move.l	-4(a5),a0
	move.w	10(a5),32(a0)
.4
	cmp.w	#3,10(a5)
	bne	.6
	move.w	#24,-(sp)
	move.w	#32,-(sp)
	move.w	#72,-(sp)
	move.l	-4(a5),a0
	move.w	46(a0),d0
	sub.w	#6,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	44(a0),-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
	move.l	-4(a5),a0
	tst.w	14(a0)
	beq	.7
	move.w	#2,-(sp)
	move.l	-4(a5),a0
	move.w	14(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.7
	move.l	-4(a5),a0
	tst.w	16(a0)
	beq	.8
	move.w	#2,-(sp)
	move.l	-4(a5),a0
	move.w	16(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.8
.6
.9
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_5962
	public	_F_h11_4696
	public	.begin
	dseg
	public	_G_h01_8BEC
	end
