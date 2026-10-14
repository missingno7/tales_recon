;:ts=8
	public	_F_h11_6486
_F_h11_6486:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#40,d0
	lea	_G_h01_A464,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	sub.w	#1,38(a0)
	move.l	-4(a5),a0
	move.w	32(a0),d0
	ext.l	d0
	bra	.4
.6
	bra	.5
.7
	move.w	#3,_G_h01_8A3C
	move.l	-4(a5),a0
	pea	10(a0)
	jsr	_F_h11_45EC
	add.w	#4,sp
	tst.w	d0
	beq	.8
	move.l	-4(a5),a0
	move.w	#20,32(a0)
	move.w	#8,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_66FE
	add.w	#4,sp
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
	move.w	#2,_G_h01_94AE
	move.w	#2,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
	bra	.9
.8
	move.w	#8,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_66FE
	add.w	#4,sp
	move.l	-4(a5),a0
	pea	10(a0)
	move.w	#8,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.9
	bra	.5
.4
	sub.l	#20,d0
	beq	.6
	sub.l	#25,d0
	beq	.7
.5
	tst.w	_G_h01_8A3C
	beq	.10
	move.w	#8,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_66FE
	add.w	#4,sp
.10
	move.l	-4(a5),a0
	tst.w	38(a0)
	bgt	.11
	move.l	-4(a5),a0
	move.w	#20,38(a0)
.11
.12
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_4474
	public	_F_h11_4B0C
	public	_F_h11_41F6
	public	_F_h11_66FE
	public	_F_h11_45EC
	public	.begin
	dseg
	public	_G_h01_94AE
	public	_G_h01_8A3C
	public	_G_h01_A464
	end
