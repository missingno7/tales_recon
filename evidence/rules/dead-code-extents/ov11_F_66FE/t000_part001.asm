;:ts=8
	public	_F_h11_0558
_F_h11_0558:
	link	a5,#.2
	movem.l	.3,-(sp)
	tst.w	_G_h01_8A42
	beq	.4
	cmp.w	#1,_G_h01_8A48
	bne	.5
	add.w	#8,_G_h01_8A3E
	move.w	_G_h01_8A3E,d0
	cmp.w	_G_h01_8A4A,d0
	blt	.6
	move.w	_G_h01_8A4A,_G_h01_8A3E
	clr.w	_G_h01_8A42
	move.w	#1,_G_h01_8A44
.6
	bra	.7
.5
	sub.w	#8,_G_h01_8A3E
	move.w	_G_h01_8A3E,d0
	cmp.w	_G_h01_8A4A,d0
	bgt	.8
	move.w	_G_h01_8A4A,_G_h01_8A3E
	clr.w	_G_h01_8A42
	move.w	#1,_G_h01_8A44
.8
.7
	bra	.9
.4
	move.w	_G_h01_8A3E,d0
	add.w	#240,d0
	move.w	_G_h01_94BE,d1
	cmp.w	d0,d1
	blt	.10
	cmp.w	#856,_G_h01_8A3E
	bge	.10
	move.w	#1,_G_h01_8A42
	move.w	_G_h01_94BE,d0
	ext.l	d0
	divs.w	#104,d0
	sub.w	#1,d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_1300,a0
	move.w	(a0,d0.l),_G_h01_8A4A
	move.w	#1,_G_h01_8A48
	bra	.11
.10
	move.w	_G_h01_8A3E,d0
	add.w	#72,d0
	move.w	_G_h01_94BE,d1
	cmp.w	d0,d1
	bge	.12
	cmp.w	#8,_G_h01_94AE
	beq	.12
	cmp.w	#6,_G_h01_94AE
	beq	.12
	tst.w	_G_h01_8A3E
	ble	.12
	move.w	#1,_G_h01_8A42
	move.w	_G_h01_94BE,d0
	ext.l	d0
	divs.w	#104,d0
	sub.w	#1,d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_1300,a0
	move.w	(a0,d0.l),_G_h01_8A4A
	clr.w	_G_h01_8A48
.12
.11
.9
.13
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	.begin
	dseg
	public	_G_h01_1300
	public	_G_h01_94AE
	public	_G_h01_94BE
	public	_G_h01_8A4A
	public	_G_h01_8A3E
	public	_G_h01_8A48
	public	_G_h01_8A44
	public	_G_h01_8A42
	end
