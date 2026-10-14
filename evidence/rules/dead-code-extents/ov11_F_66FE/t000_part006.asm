;:ts=8
	public	_F_h11_1372
_F_h11_1372:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	_G_h01_94C6,_G_h01_94C2
	move.w	_G_h01_94C8,_G_h01_94C4
	move.l	_G_h01_94CA,_G_h01_94CE
	tst.w	_G_h01_94B0
	beq	.4
	move.l	#16,d0
	bra	.5
.4
	move.l	#0,d0
.5
	move.w	_G_h01_94BE,d1
	sub.w	d0,d1
	move.w	d1,_G_h01_94C6
	move.w	_G_h01_94C0,_G_h01_94C8
	move.l	_G_h01_94DA,_G_h01_94CA
	move.l	_G_h01_94DA,a0
	move.w	_G_h01_94C6,d0
	sub.w	_G_h01_8A3E,d0
	move.w	d0,(a0)
	move.l	_G_h01_94DA,a0
	move.w	_G_h01_94C0,d0
	add.w	#1,d0
	move.w	d0,2(a0)
	cmp.w	#45,_G_h01_94AE
	beq	.6
	move.l	_G_h01_94DA,-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
.6
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
	public	_G_h01_94AE
	public	_G_h01_94DA
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94B0
	public	_G_h01_94CE
	public	_G_h01_94CA
	public	_G_h01_94C8
	public	_G_h01_94C6
	public	_G_h01_94C4
	public	_G_h01_94C2
	end
