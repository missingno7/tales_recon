;:ts=8
	public	_F_h11_36F8
_F_h11_36F8:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#6,d0
	lea	_G_h01_9FCE,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	tst.w	46(a0)
	beq	.4
	move.l	_G_h01_9F6E,a0
	move.l	-4(a5),a1
	move.w	50(a1),d0
	sub.w	_G_h01_8A3E,d0
	move.w	d0,(a0)
	move.l	-4(a5),a0
	move.l	_G_h01_9F6E,a1
	move.w	52(a0),2(a1)
	move.l	_G_h01_9F6E,a0
	clr.b	52(a0)
	move.l	_G_h01_9F6E,a0
	tst.w	(a0)
	ble	.5
	move.l	_G_h01_9F6E,a0
	cmp.w	#154,2(a0)
	bge	.6
	move.l	_G_h01_9F6E,-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
.6
.5
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	54(a0),56(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	58(a0),60(a1)
	move.l	-4(a5),a0
	move.l	_G_h01_9F6E,a1
	move.w	(a1),d0
	add.w	_G_h01_8A3E,d0
	move.w	d0,54(a0)
	move.l	_G_h01_9F6E,a0
	move.l	-4(a5),a1
	move.w	2(a0),58(a1)
.4
.7
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h00_34E0
	public	.begin
	dseg
	public	_G_h01_8A3E
	public	_G_h01_9F6E
	public	_G_h01_9FCE
	end
