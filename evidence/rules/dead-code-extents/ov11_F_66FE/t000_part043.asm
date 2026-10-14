;:ts=8
	public	_F_h11_487E
_F_h11_487E:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	10(a5),-8(a5)
	clr.w	-10(a5)
	move.w	8(a5),d0
	add.w	#48,d0
	ext.l	d0
	divs.w	#104,d0
	swap	d0
	move.w	d0,-2(a5)
.4
	move.w	-10(a5),d0
	cmp.w	12(a5),d0
	bge	.5
	move.l	#104,d0
	sub.w	-2(a5),d0
	move.w	12(a5),d1
	sub.w	-10(a5),d1
	cmp.w	d1,d0
	bge	.6
	move.l	#104,d0
	sub.w	-2(a5),d0
	bra	.7
.6
	move.w	12(a5),d0
	sub.w	-10(a5),d0
.7
	move.w	d0,-6(a5)
	clr.l	-(sp)
	pea	255
	pea	192
	pea	176
	move.w	-6(a5),d0
	ext.l	d0
	move.l	d0,-(sp)
	clr.l	-(sp)
	move.w	-8(a5),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46D2,-(sp)
	clr.l	-(sp)
	move.w	-2(a5),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_A460,-(sp)
	jsr	_F_h00_8A46
	lea	44(sp),sp
	move.w	-6(a5),d0
	add.w	d0,-10(a5)
	move.w	-6(a5),d0
	add.w	d0,-8(a5)
	clr.w	-2(a5)
	bra	.4
.5
	jsr	_F_h11_55B8
	move.w	8(a5),d0
	ext.l	d0
	divs.w	#104,d0
	move.w	d0,-2(a5)
	move.w	8(a5),d0
	add.w	#320,d0
	ext.l	d0
	divs.w	#104,d0
	move.w	d0,-4(a5)
	bra	.11
.10
	move.w	-2(a5),d0
	muls.w	#14,d0
	lea	_G_h01_8A6E,a0
	tst.w	(a0,d0.l)
	beq	.12
	cmp.w	#45,_G_h01_94AE
	beq	.12
	move.w	-2(a5),d0
	muls.w	#14,d0
	lea	_G_h01_8A6E,a0
	move.w	(a0,d0.l),-(sp)
	jsr	_F_h11_645E
	add.w	#2,sp
.12
.8
	add.w	#1,-2(a5)
.11
	move.w	-2(a5),d0
	cmp.w	-4(a5),d0
	ble	.10
.9
	tst.w	14(a5)
	beq	.13
	clr.l	-(sp)
	pea	255
	pea	192
	pea	200
	move.w	12(a5),d0
	ext.l	d0
	move.l	d0,-(sp)
	clr.l	-(sp)
	move.w	10(a5),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46CE,-(sp)
	clr.l	-(sp)
	move.w	10(a5),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46D2,-(sp)
	jsr	_F_h00_8A46
	lea	44(sp),sp
	move.w	_G_h01_8A3E,_G_h01_A45E
.13
.14
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-12
.3	reg	
	public	_F_h11_645E
	public	_F_h11_55B8
	public	_F_h00_8A46
	public	.begin
	dseg
	public	_G_h01_A45E
	public	_G_h01_94AE
	public	_G_h01_8A3E
	public	_G_h01_8A6E
	public	_G_h01_A460
	public	_G_h01_46D2
	public	_G_h01_46CE
	end
