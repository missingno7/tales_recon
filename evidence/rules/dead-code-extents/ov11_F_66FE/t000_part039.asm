;:ts=8
	public	_F_h11_4610
_F_h11_4610:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	8(a5),a0
	move.l	16(a0),-4(a5)
	move.l	-4(a5),a0
	move.l	(a0),-8(a5)
	move.l	8(a5),a0
	tst.w	12(a0)
	ble	.4
	move.l	-8(a5),a0
	move.l	-4(a5),a1
	move.l	8(a5),a6
	move.w	12(a1),d0
	add.w	(a6),d0
	sub.w	_G_h01_8A3E,d0
	move.w	d0,(a0)
	move.l	-8(a5),a0
	move.l	8(a5),a1
	move.l	-4(a5),a6
	move.w	2(a1),d0
	add.w	14(a6),d0
	move.w	d0,2(a0)
	move.l	-4(a5),a0
	move.l	-8(a5),a1
	move.b	5(a0),52(a1)
	move.l	-8(a5),-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
	move.l	8(a5),a0
	sub.w	#1,12(a0)
	move.l	8(a5),a0
	tst.w	12(a0)
	bne	.5
	move.l	8(a5),a0
	clr.w	14(a0)
.5
.4
.6
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-8
.3	reg	
	public	_F_h00_34E0
	public	.begin
	dseg
	public	_G_h01_8A3E
	end
