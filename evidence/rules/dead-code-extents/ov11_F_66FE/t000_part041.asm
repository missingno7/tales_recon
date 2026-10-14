;:ts=8
	public	_F_h11_4790
_F_h11_4790:
	link	a5,#.2
	movem.l	.3,-(sp)
	lea	_G_h01_34EC,a0
	move.l	a0,-4(a5)
	bra	.7
.6
	move.l	-4(a5),a0
	tst.w	(a0)
	beq	.8
	move.l	-4(a5),a0
	sub.w	#1,(a0)
	move.l	-4(a5),a0
	tst.w	6(a0)
	ble	.9
	move.l	-4(a5),a0
	tst.w	8(a0)
	ble	.10
	clr.l	-(sp)
	pea	255
	pea	192
	move.l	-4(a5),a0
	move.w	8(a0),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	-4(a5),a0
	move.w	6(a0),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	-4(a5),a0
	move.w	4(a0),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	-4(a5),a0
	move.w	2(a0),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46D2,-(sp)
	move.l	-4(a5),a0
	move.w	4(a0),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	-4(a5),a0
	move.w	2(a0),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46CE,-(sp)
	jsr	_F_h00_8A46
	lea	44(sp),sp
.10
.9
.8
.4
	add.l	#14,-4(a5)
.7
	move.l	-4(a5),d0
	lea	_G_h01_34EC,a0
	sub.l	a0,d0
	move.l	#14,d1
	jsr	.divs#
	cmp.w	#40,d0
	blt	.6
.5
.11
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h00_8A46
	public	.begin
	dseg
	public	_G_h01_46D2
	public	_G_h01_46CE
	public	_G_h01_34EC
	end
