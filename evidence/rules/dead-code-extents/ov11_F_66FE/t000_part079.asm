;:ts=8
	public	_F_h11_6C3A
_F_h11_6C3A:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#34,d0
	lea	_G_h01_A554,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.l	_G_h01_5370,a1
	move.b	31(a0),(a1)
	move.l	_G_h01_5370,a0
	move.b	(a0),d0
	ext.w	d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46CA,-(sp)
	jsr	_F_h00_8B88
	add.w	#8,sp
	move.l	-4(a5),a0
	move.w	14(a0),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	-4(a5),a0
	move.w	12(a0),d0
	sub.w	_G_h01_8A3E,d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46CA,-(sp)
	jsr	_F_h00_8B4C
	lea	12(sp),sp
	move.l	-4(a5),a0
	move.w	20(a0),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	-4(a5),a0
	move.w	18(a0),d0
	sub.w	_G_h01_8A3E,d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46CA,-(sp)
	jsr	_F_h00_8AA8
	lea	12(sp),sp
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	4(a0),6(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	18(a0),4(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	8(a0),10(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	20(a0),8(a1)
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h00_8AA8
	public	_F_h00_8B4C
	public	_F_h00_8B88
	public	.begin
	dseg
	public	_G_h01_8A3E
	public	_G_h01_46CA
	public	_G_h01_5370
	public	_G_h01_A554
	end
