;:ts=8
	public	_F_h11_4AA4
_F_h11_4AA4:
	link	a5,#.2
	movem.l	.3,-(sp)
	tst.w	_G_h01_94E4
	ble	.4
	sub.w	#1,_G_h01_94E4
	bra	.5
.4
	add.w	#1,_G_h01_94DE
	move.w	_G_h01_94DE,d0
	cmp.w	_G_h01_94E0,d0
	bge	.6
	tst.l	_G_h01_94E8
	beq	.7
	add.l	#16,_G_h01_94E8
	move.l	_G_h01_94E8,a0
	move.w	12(a0),d0
	add.w	d0,_G_h01_94BE
	move.l	_G_h01_94E8,a0
	move.w	14(a0),d0
	add.w	d0,_G_h01_94C0
	move.l	_G_h01_94E8,a0
	move.l	(a0),_G_h01_94DA
	move.l	_G_h01_94E8,a0
	move.l	_G_h01_94DA,a1
	move.b	5(a0),52(a1)
	move.l	_G_h01_94E8,a0
	move.w	6(a0),_G_h01_94E4
.7
.6
.5
.8
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	.begin
	dseg
	public	_G_h01_94E8
	public	_G_h01_94E4
	public	_G_h01_94E0
	public	_G_h01_94DE
	public	_G_h01_94DA
	public	_G_h01_94C0
	public	_G_h01_94BE
	end
