;:ts=8
	public	_F_h11_14BA
_F_h11_14BA:
	link	a5,#.2
	movem.l	.3,-(sp)
	tst.w	8(a5)
	beq	.4
	move.w	#1,_G_h01_94AC
	bra	.5
.4
	add.w	#1,_G_h01_94AC
.5
	move.l	#3,d0
	sub.w	_G_h01_94AC,d0
	add.w	#1,d0
	move.w	d0,-2(a5)
	move.w	-2(a5),d0
	ext.l	d0
	bra	.6
.8
	move.w	#98,_G_h01_1708
	move.w	#130,_G_h01_170A
	move.w	#179,_G_h01_170C
	move.w	#1240,_G_h01_170E
	bra	.7
.9
	move.w	#5,_G_h01_1708
	move.w	#8,_G_h01_170A
	move.w	#284,_G_h01_170C
	move.w	#1101,_G_h01_170E
	bra	.7
.10
	move.w	#1280,_G_h01_1708
	move.w	#2048,_G_h01_170A
	move.w	#3072,_G_h01_170C
	move.w	#3396,_G_h01_170E
	bra	.7
.6
	sub.l	#1,d0
	beq	.10
	sub.l	#1,d0
	beq	.9
	sub.l	#1,d0
	beq	.8
.7
	clr.w	-(sp)
	jsr	_F_h00_30F0
	add.w	#2,sp
	move.w	#5,_G_h01_94AE
	move.w	#1,_G_h01_94B0
	clr.w	_G_h01_94B2
	clr.w	_G_h01_94B6
	clr.w	_G_h01_94B4
	clr.w	_G_h01_94D4
	clr.w	_G_h01_94D6
	clr.w	_G_h01_94D8
	pea	_G_h01_94BC
	pea	_G_h01_94BA
	jsr	_F_h11_5BC4
	add.w	#8,sp
	move.w	_G_h01_94BA,d0
	muls.w	#53,d0
	add.w	#8,d0
	move.w	d0,_G_h01_94BE
	move.w	_G_h01_94BC,d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	tst.w	_G_h01_94B0
	beq	.11
	move.l	#16,d0
	bra	.12
.11
	move.l	#0,d0
.12
	move.w	_G_h01_94BE,d1
	sub.w	d0,d1
	move.w	d1,_G_h01_94C6
	move.w	d1,_G_h01_94C2
	move.w	_G_h01_94C0,_G_h01_94C8
	move.w	_G_h01_94C0,_G_h01_94C4
	move.w	_G_h01_94AE,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
.13
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-2
.3	reg	
	public	_F_h11_4B0C
	public	_F_h11_5BC4
	public	_F_h00_30F0
	public	.begin
	dseg
	public	_G_h01_94D8
	public	_G_h01_94D6
	public	_G_h01_94D4
	public	_G_h01_94C8
	public	_G_h01_94C6
	public	_G_h01_94C4
	public	_G_h01_94C2
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94BC
	public	_G_h01_94BA
	public	_G_h01_94B6
	public	_G_h01_94B4
	public	_G_h01_94B2
	public	_G_h01_94B0
	public	_G_h01_94AE
	public	_G_h01_94AC
	public	_G_h01_170E
	public	_G_h01_170C
	public	_G_h01_170A
	public	_G_h01_1708
	end
