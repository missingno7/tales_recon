;:ts=8
	public	_F_h11_0B4C
_F_h11_0B4C:
	link	a5,#.2
	movem.l	.3,-(sp)
	tst.w	_G_h01_94B4
	beq	.4
	pea	_G_h01_94C0
	move.w	_G_h01_94D6,-(sp)
	jsr	_F_h11_5FB2
	add.w	#6,sp
	bra	.5
.4
	tst.w	_G_h01_94B6
	beq	.6
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_405A
	add.w	#2,sp
	tst.w	d0
	beq	.7
	move.w	#2,_G_h01_94AE
	move.w	#2,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
	clr.w	_G_h01_94B6
	bra	.8
.7
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_415A
	lea	10(sp),sp
	move.w	#10,-(sp)
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_40E0
	add.w	#4,sp
.8
.6
.5
.9
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h11_40E0
	public	_F_h11_415A
	public	_F_h11_4B0C
	public	_F_h11_405A
	public	_F_h11_5FB2
	public	.begin
	dseg
	public	_G_h01_94D6
	public	_G_h01_94D4
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94B6
	public	_G_h01_94B4
	public	_G_h01_94AE
	end
