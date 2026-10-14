;:ts=8
	public	_F_h11_20F2
_F_h11_20F2:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#76,-(sp)
	move.l	8(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	move.l	d0,-4(a5)
	pea	-6(a5)
	pea	.1+0
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	12(sp),sp
	cmp.w	#1,d0
	bge	.4
	move.w	#55,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.4
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	lea	_G_h01_8A66,a0
	move.l	a0,-10(a5)
	bra	.8
.7
	move.l	-10(a5),a0
	pea	12(a0)
	move.l	-10(a5),a0
	pea	10(a0)
	move.l	-10(a5),a0
	add.l	#8,a0
	move.l	a0,-(sp)
	move.l	-10(a5),a0
	add.l	#6,a0
	move.l	a0,-(sp)
	move.l	-10(a5),a0
	add.l	#4,a0
	move.l	a0,-(sp)
	move.l	-10(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.l	-10(a5),-(sp)
	pea	.1+5
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	36(sp),sp
	cmp.w	#7,d0
	bne	.9
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	bra	.10
.9
	move.w	#67,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.10
.5
	add.l	#14,-10(a5)
.8
	move.l	-10(a5),d0
	lea	_G_h01_8A66,a0
	sub.l	a0,d0
	move.l	#14,d1
	jsr	.divs#
	cmp.w	-6(a5),d0
	blt	.7
.6
.11
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-10
.3	reg	
.1
	dc.b	76,32,37,100,0,37,42,100,32,37,100,32,37,100,32
	dc.b	37,100,32,37,100,32,37,100,32,37,100,32,37,100,10
	dc.b	0
	ds	0
	public	_F_h00_3674
	public	_F_h00_704E
	public	_F_h00_75D8
	public	.begin
	dseg
	public	_G_h01_8A66
	end
