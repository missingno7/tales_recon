;:ts=8
	public	_F_h11_6080
_F_h11_6080:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#65,-(sp)
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
	move.w	#231,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.4
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	clr.w	-12(a5)
	bra	.8
.7
	move.w	-12(a5),d0
	ext.l	d0
	asl.l	#3,d0
	lea	_G_h01_8B1C+6,a0
	add.l	a0,d0
	move.l	d0,-(sp)
	move.w	-12(a5),d0
	ext.l	d0
	asl.l	#3,d0
	lea	_G_h01_8B1C+4,a0
	add.l	a0,d0
	move.l	d0,-(sp)
	move.w	-12(a5),d0
	ext.l	d0
	asl.l	#3,d0
	lea	_G_h01_8B1C+2,a0
	add.l	a0,d0
	move.l	d0,-(sp)
	move.w	-12(a5),d0
	ext.l	d0
	asl.l	#3,d0
	lea	_G_h01_8B1C,a0
	add.l	a0,d0
	move.l	d0,-(sp)
	pea	.1+5
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	24(sp),sp
	cmp.w	#4,d0
	bne	.9
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	bra	.10
.9
	move.w	#241,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.10
.5
	add.w	#1,-12(a5)
.8
	move.w	-12(a5),d0
	cmp.w	-6(a5),d0
	blt	.7
.6
	move.w	#66,-(sp)
	move.l	8(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	move.l	d0,-4(a5)
	pea	-6(a5)
	pea	.1+22
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	12(sp),sp
	cmp.w	#1,d0
	bge	.11
	move.w	#88,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.11
	move.w	-6(a5),_G_h01_37EC
	cmp.w	#40,_G_h01_37EC
	ble	.12
	move.w	#89,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.12
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	clr.w	-12(a5)
	lea	_G_h01_8BEC,a0
	move.l	a0,-10(a5)
	bra	.16
.15
	move.l	-10(a5),a0
	pea	16(a0)
	move.l	-10(a5),a0
	pea	14(a0)
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
	pea	46(a0)
	move.l	-10(a5),a0
	pea	44(a0)
	move.l	-10(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.l	-10(a5),-(sp)
	pea	.1+27
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	52(sp),sp
	cmp.w	#11,d0
	bne	.17
	move.w	#10,-(sp)
	move.l	-4(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	add.l	#1,d0
	move.l	d0,-4(a5)
	bra	.18
.17
	move.w	#89,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.18
.13
	add.w	#1,-12(a5)
	add.l	#52,-10(a5)
.16
	move.w	-12(a5),d0
	cmp.w	-6(a5),d0
	blt	.15
.14
.19
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-12
.3	reg	
.1
	dc.b	65,32,37,100,0,37,42,100,32,37,100,32,37,100,32
	dc.b	37,100,32,37,100,10,0,66,32,37,100,0,37,42,100
	dc.b	32,37,100,32,37,100,32,37,100,32,37,100,32,37,100
	dc.b	32,37,100,32,37,100,32,37,100,32,37,100,32,37,100
	dc.b	32,37,100,10,0
	ds	0
	public	_F_h00_3674
	public	_F_h00_704E
	public	_F_h00_75D8
	public	.begin
	dseg
	public	_G_h01_37EC
	public	_G_h01_8BEC
	public	_G_h01_8B1C
	end
