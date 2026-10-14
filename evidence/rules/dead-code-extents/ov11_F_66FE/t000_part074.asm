;:ts=8
	public	_F_h11_66FE
_F_h11_66FE:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#40,d0
	lea	_G_h01_A464,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.w	#2,22(a0)
	move.l	-4(a5),a0
	tst.w	24(a0)
	beq	.5
	cmp.w	#8,10(a5)
	bne	.4
.5
	move.l	-4(a5),a0
	move.w	10(a5),24(a0)
.4
.6
	movem.l	(sp)+,.3
	unlk	a5
	rts
	cmp.w	#8,10(a5)
	bne	.7
	move.l	-4(a5),a0
	cmp.w	#45,32(a0)
	bne	.8
	move.w	#8,-(sp)
	move.w	#56,-(sp)
	move.w	#48,-(sp)
	move.l	-4(a5),a0
	move.w	36(a0),-(sp)
	move.l	-4(a5),a0
	move.w	34(a0),-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
.8
	move.l	-4(a5),a0
	tst.w	4(a0)
	beq	.9
	move.w	#8,-(sp)
	move.l	-4(a5),a0
	move.w	4(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.9
	move.l	-4(a5),a0
	tst.w	6(a0)
	beq	.10
	move.w	#8,-(sp)
	move.l	-4(a5),a0
	move.w	6(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.10
.7
	bra	.6
.2	equ	-4
.3	reg	
	public	_F_h11_5962
	public	_F_h11_4696
	public	.begin
	dseg
	public	_G_h01_A464
	end
