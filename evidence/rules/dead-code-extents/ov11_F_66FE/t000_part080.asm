;:ts=8
	public	_F_h11_6CFE
_F_h11_6CFE:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#34,d0
	lea	_G_h01_A554,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	28(a1),d0
	add.w	d0,22(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	22(a0),d0
	cmp.w	26(a1),d0
	ble	.4
	move.l	-4(a5),a0
	move.w	28(a0),d0
	muls.w	#-1,d0
	move.w	d0,28(a0)
	cmp.w	#8,_G_h01_94AE
	bne	.5
	move.w	8(a5),d0
	cmp.w	_G_h01_94D8,d0
	bne	.5
	move.w	#90,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
.5
	bra	.6
.4
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	22(a0),d0
	cmp.w	24(a1),d0
	bge	.7
	move.l	-4(a5),a0
	move.w	28(a0),d0
	muls.w	#-1,d0
	move.w	d0,28(a0)
	cmp.w	#8,_G_h01_94AE
	bne	.8
	move.w	8(a5),d0
	cmp.w	_G_h01_94D8,d0
	bne	.8
	move.w	#93,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
.8
.7
.6
	move.l	-4(a5),a0
	move.l	a0,-(sp)
	move.l	-4(a5),a0
	move.w	22(a0),d0
	sub.w	#128,d0
	move.w	d0,-(sp)
	jsr	_F_h11_729C
	add.w	#2,sp
	move.l	-4(a5),a0
	muls.w	16(a0),d0
	ext.l	d0
	divs.w	#256,d0
	move.l	(sp)+,a0
	move.l	-4(a5),a1
	add.w	12(a1),d0
	move.w	d0,18(a0)
	move.l	-4(a5),a0
	move.l	a0,-(sp)
	move.l	-4(a5),a0
	move.w	22(a0),d0
	sub.w	#128,d0
	move.w	d0,-(sp)
	jsr	_F_h11_727A
	add.w	#2,sp
	move.l	-4(a5),a0
	muls.w	16(a0),d0
	ext.l	d0
	divs.w	#256,d0
	move.l	(sp)+,a0
	move.l	-4(a5),a1
	add.w	14(a1),d0
	move.w	d0,20(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	12(a0),d0
	cmp.w	6(a1),d0
	bgt	.9
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	6(a0),d0
	sub.w	12(a1),d0
	move.w	d0,-6(a5)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	12(a0),6(a1)
	bra	.10
.9
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	12(a0),d0
	sub.w	6(a1),d0
	move.w	d0,-6(a5)
.10
	add.w	#16,-6(a5)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	10(a0),d0
	sub.w	14(a1),d0
	add.w	#1,d0
	move.w	d0,-8(a5)
	move.w	8(a5),d0
	add.w	#28,d0
	move.w	d0,-(sp)
	move.w	-8(a5),-(sp)
	move.w	-6(a5),-(sp)
	move.l	-4(a5),a0
	move.w	14(a0),-(sp)
	move.l	-4(a5),a0
	move.w	6(a0),-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
	move.l	-4(a5),a0
	tst.w	(a0)
	beq	.11
	move.w	#4,-(sp)
	move.l	-4(a5),a0
	move.w	(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.11
	move.l	-4(a5),a0
	tst.w	2(a0)
	beq	.12
	move.w	#4,-(sp)
	move.l	-4(a5),a0
	move.w	2(a0),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.12
.13
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-8
.3	reg	
	public	_F_h11_729C
	public	_F_h11_727A
	public	_F_h11_5962
	public	_F_h11_4696
	public	_F_h00_57D2
	public	.begin
	dseg
	public	_G_h01_A554
	public	_G_h01_94D8
	public	_G_h01_94AE
	end
