;:ts=8
	public	_F_h11_506A
_F_h11_506A:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#80,-(sp)
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
	move.w	#435,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
	bra	.9
.8
	move.w	-10(a5),d0
	muls.w	#40,d0
	lea	_G_h01_3724,a0
	add.l	a0,d0
	move.l	d0,-14(a5)
	move.l	-14(a5),a0
	pea	24(a0)
	move.l	-14(a5),a0
	pea	32(a0)
	move.l	-14(a5),a0
	pea	30(a0)
	move.l	-14(a5),a0
	pea	28(a0)
	move.l	-14(a5),a0
	pea	26(a0)
	move.l	-14(a5),a0
	pea	38(a0)
	move.l	-14(a5),a0
	pea	36(a0)
	move.l	-14(a5),a0
	pea	34(a0)
	pea	.1+10
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
	move.w	#444,-(sp)
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
.11
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-14
.3	reg	
.1
	dc.b	80,32,37,100,0,32,37,100,32,0,37,42,100,32,37
	dc.b	100,32,37,100,32,37,100,32,37,100,32,37,100,32,37
	dc.b	100,32,37,100,32,37,100,10,0
	ds	0
	public	_F_h00_3674
	public	_F_h00_704E
	public	_F_h00_75D8
	public	.begin
	dseg
	public	_G_h01_3724
	end
