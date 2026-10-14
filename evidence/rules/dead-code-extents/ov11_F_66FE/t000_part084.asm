;:ts=8
	public	_F_h11_706C
_F_h11_706C:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#10,d0
	lea	_G_h01_A6A8,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	tst.w	_G_h01_8A3C
	bgt	.5
	move.l	-4(a5),a0
	tst.w	8(a0)
	ble	.4
.5
	move.l	_G_h01_9F76,a0
	move.l	-4(a5),a1
	move.w	4(a1),d0
	sub.w	_G_h01_8A3E,d0
	move.w	d0,(a0)
	move.l	-4(a5),a0
	move.l	_G_h01_9F76,a1
	move.w	6(a0),2(a1)
	move.l	_G_h01_9F76,-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
	tst.w	_G_h01_8A3C
	beq	.6
	move.l	#2,d0
	bra	.7
.6
	move.l	-4(a5),a0
	move.w	8(a0),d0
	sub.w	#1,d0
.7
	move.l	-4(a5),a0
	move.w	d0,8(a0)
.4
.8
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h00_34E0
	public	.begin
	dseg
	public	_G_h01_9F76
	public	_G_h01_8A3E
	public	_G_h01_8A3C
	public	_G_h01_A6A8
	end
