;:ts=8
	public	_F_h11_4474
_F_h11_4474:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	10(a5),a0
	tst.w	8(a0)
	ble	.4
	move.l	10(a5),a0
	sub.w	#1,8(a0)
	bra	.5
.4
	move.l	10(a5),a0
	add.w	#1,6(a0)
	move.l	10(a5),a0
	move.l	10(a5),a1
	move.w	6(a0),d0
	cmp.w	10(a1),d0
	bge	.6
	move.l	10(a5),a0
	tst.l	16(a0)
	beq	.6
	move.l	10(a5),a0
	add.l	#16,16(a0)
.6
	move.w	8(a5),d0
	ext.l	d0
	bra	.7
.9
	move.l	10(a5),a0
	tst.w	20(a0)
	beq	.10
	move.l	10(a5),a0
	move.l	10(a5),a1
	move.w	6(a0),d0
	cmp.w	10(a1),d0
	blt	.10
	move.l	10(a5),a0
	clr.w	6(a0)
	move.l	10(a5),a0
	move.w	#4,10(a0)
	lea	_G_h01_9F0C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
.10
	bra	.8
.11
	move.l	10(a5),a0
	move.w	20(a0),d0
	ext.l	d0
	bra	.12
.14
	move.l	10(a5),a0
	move.l	10(a5),a1
	move.w	6(a0),d0
	cmp.w	10(a1),d0
	blt	.15
	move.l	10(a5),a0
	clr.w	6(a0)
	move.l	10(a5),a0
	move.w	#1,10(a0)
	lea	_G_h01_9C2C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
.15
	bra	.13
.16
	move.l	10(a5),a0
	move.l	10(a5),a1
	move.w	6(a0),d0
	cmp.w	10(a1),d0
	blt	.17
	move.l	10(a5),a0
	clr.w	6(a0)
	move.l	10(a5),a0
	move.w	#6,10(a0)
	lea	_G_h01_9C2C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	move.w	#94,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	bra	.18
.17
	move.l	10(a5),a0
	cmp.w	#3,6(a0)
	bne	.19
	move.w	#87,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
.19
.18
	bra	.13
.12
	sub.l	#1,d0
	beq	.14
	sub.l	#2,d0
	beq	.16
.13
	bra	.8
.7
	sub.l	#24,d0
	beq	.11
	sub.l	#9,d0
	beq	.9
.8
	move.l	10(a5),a0
	move.l	10(a5),a1
	move.w	6(a0),d0
	cmp.w	10(a1),d0
	bge	.20
	move.l	10(a5),a0
	tst.l	16(a0)
	beq	.20
	move.l	10(a5),a0
	move.l	16(a0),a1
	move.l	10(a5),a0
	move.w	6(a1),8(a0)
.20
.5
.21
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h00_57D2
	public	.begin
	dseg
	public	_G_h01_9C2C
	public	_G_h01_9F0C
	end
