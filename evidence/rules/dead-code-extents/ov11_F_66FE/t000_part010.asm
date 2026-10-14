;:ts=8
	public	_F_h11_20AE
_F_h11_20AE:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#67,-(sp)
	move.l	8(a5),-(sp)
	jsr	_F_h00_75D8
	add.w	#6,sp
	move.l	d0,-4(a5)
	pea	_G_h01_7A94
	pea	.1+0
	move.l	-4(a5),-(sp)
	jsr	_F_h00_704E
	lea	12(sp),sp
	cmp.w	#1,d0
	bge	.4
	move.w	#44,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
.4
.5
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
.1
	dc.b	67,32,37,100,0
	ds	0
	public	_F_h00_3674
	public	_F_h00_704E
	public	_F_h00_75D8
	public	.begin
	dseg
	public	_G_h01_7A94
	end
