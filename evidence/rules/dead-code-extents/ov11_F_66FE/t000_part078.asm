;:ts=8
	public	_F_h11_6A44
_F_h11_6A44:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#86,-(sp)
	move.l	8(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	move.l	d0,-4(a5)
	pea	-8(a5)
	pea	.1+0
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	12(sp),sp
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	clr.w	-6(a5)
	bra	.7
.6
	pea	-10(a5)
	pea	.1+5
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	12(sp),sp
	cmp.w	#1,d0
	bge	.8
	move.w	#888,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
	bra	.9
.8
	move.w	-10(a5),d0
	muls.w	#34,d0
	lea	_G_h01_A554,a0
	add.l	a0,d0
	move.l	d0,-14(a5)
	move.l	-14(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.l	-14(a5),-(sp)
	move.l	-14(a5),a0
	pea	28(a0)
	move.l	-14(a5),a0
	pea	26(a0)
	move.l	-14(a5),a0
	pea	24(a0)
	move.l	-14(a5),a0
	pea	16(a0)
	move.l	-14(a5),a0
	pea	14(a0)
	move.l	-14(a5),a0
	pea	12(a0)
	pea	.1+8
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	40(sp),sp
	cmp.w	#8,d0
	bne	.10
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	bra	.9
.10
	move.w	#890,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.9
.4
	add.w	#1,-6(a5)
.7
	move.w	-6(a5),d0
	cmp.w	-8(a5),d0
	blt	.6
.5
	move.w	#74,-(sp)
	move.l	8(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	move.l	d0,-4(a5)
	pea	-8(a5)
	pea	.1+37
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	12(sp),sp
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	clr.w	-6(a5)
	bra	.14
.13
	pea	-10(a5)
	pea	.1+42
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	12(sp),sp
	cmp.w	#1,d0
	bge	.15
	move.w	#988,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
	bra	.16
.15
	move.w	-10(a5),d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_945C,a0
	add.l	a0,d0
	move.l	d0,-(sp)
	pea	.1+45
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	12(sp),sp
	cmp.w	#1,d0
	bne	.17
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	bra	.16
.17
	move.w	#990,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.16
.11
	add.w	#1,-6(a5)
.14
	move.w	-6(a5),d0
	cmp.w	-8(a5),d0
	blt	.13
.12
.18
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-14
.3	reg	
.1
	dc.b	86,32,37,100,0,37,100,0,37,42,100,32,37,100,32
	dc.b	37,100,32,37,100,32,37,100,32,37,100,32,37,100,32
	dc.b	37,100,32,37,100,10,0,74,32,37,100,0,37,100,0
	dc.b	37,42,100,32,37,100,32,10,0
	ds	0
	public	_F_h00_3674
	public	_F_h00_704E
	public	_F_h00_75D8
	public	.begin
	dseg
	public	_G_h01_945C
	public	_G_h01_A554
	end
