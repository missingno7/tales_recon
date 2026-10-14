;:ts=8
	public	_F_h11_2A3A
_F_h11_2A3A:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-2(a5)
.6
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9D4C,a0
	move.l	_G_h01_9F6A,(a0,d0.l)
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9D2C,a0
	move.l	_G_h01_9F6A,(a0,d0.l)
.4
	add.w	#1,-2(a5)
	cmp.w	#2,-2(a5)
	blt	.6
.5
	clr.w	_G_h01_9D50
	clr.w	_G_h01_9D5A
	move.w	#1,_G_h01_9D60
	move.w	#12,_G_h01_9D6A
	clr.w	_G_h01_9D30
	move.w	#1,_G_h01_9D40
	move.w	#12,_G_h01_9D4A
	clr.w	-2(a5)
.9
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9D6C,a0
	move.l	_G_h01_9F6A,(a0,d0.l)
.7
	add.w	#1,-2(a5)
	cmp.w	#3,-2(a5)
	blt	.9
.8
	move.w	#2,_G_h01_9D70
	move.w	#5,_G_h01_9D72
	move.w	#3,_G_h01_9D80
	move.w	#128,_G_h01_9D82
	move.w	#1,_G_h01_9D90
	clr.w	-2(a5)
.12
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9D9C,a0
	move.l	_G_h01_9F6A,(a0,d0.l)
.10
	add.w	#1,-2(a5)
	cmp.w	#12,-2(a5)
	blt	.12
.11
	move.w	#4,_G_h01_9DA0
	move.w	#5,_G_h01_9DB0
	move.w	#2,_G_h01_9DB2
	move.w	#4,_G_h01_9DC0
	move.w	#5,_G_h01_9DD0
	move.w	#2,_G_h01_9DD2
	move.w	#4,_G_h01_9DE0
	move.w	#5,_G_h01_9DF0
	move.w	#2,_G_h01_9DF2
	move.w	#4,_G_h01_9E00
	move.w	#5,_G_h01_9E10
	move.w	#2,_G_h01_9E12
	move.w	#4,_G_h01_9E20
	move.w	#5,_G_h01_9E30
	move.w	#2,_G_h01_9E32
	move.w	#4,_G_h01_9E40
	move.w	#5,_G_h01_9E50
	move.w	#2,_G_h01_9E52
	clr.w	-2(a5)
.15
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9E5C,a0
	move.l	_G_h01_9F6A,(a0,d0.l)
.13
	add.w	#1,-2(a5)
	cmp.w	#5,-2(a5)
	blt	.15
.14
	move.w	#6,_G_h01_9E60
	move.w	#3,_G_h01_9E62
	move.w	#7,_G_h01_9E70
	clr.w	_G_h01_9E72
	move.w	#7,_G_h01_9E80
	clr.w	_G_h01_9E82
	move.w	#7,_G_h01_9E90
	move.w	#64,_G_h01_9E92
	move.w	#6,_G_h01_9EA0
	move.w	#3,_G_h01_9EA2
	move.b	_G_h01_46E0,d0
	ext.w	d0
	ext.l	d0
	bra	.16
.18
	move.w	#6,_G_h01_34D8+16
	bra	.17
.19
	move.w	#50,_G_h01_1300+26
	move.w	#75,_G_h01_1300+28
	move.w	#75,_G_h01_1300+30
	move.w	#3,_G_h01_34D8+16
	bra	.17
.20
	move.w	#75,_G_h01_1300+26
	move.w	#75,_G_h01_1300+28
	move.w	#85,_G_h01_1300+30
	move.w	#2,_G_h01_34D8+16
	bra	.17
.16
	tst.l	d0
	beq	.18
	sub.l	#1,d0
	beq	.19
	sub.l	#1,d0
	beq	.20
.17
	clr.w	-2(a5)
.23
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#6,d0
	lea	_G_h01_9FCE,a0
	add.l	a0,d0
	move.l	d0,-6(a5)
	move.l	-6(a5),a0
	move.l	-6(a5),a1
	move.w	34(a0),30(a1)
	move.l	-6(a5),a0
	move.w	#14,44(a0)
	move.l	-6(a5),a0
	clr.w	46(a0)
	move.l	-6(a5),a0
	move.w	_G_h01_34D8+16,62(a0)
	move.w	#7,-(sp)
	move.w	-2(a5),-(sp)
	jsr	_F_h11_2E26
	add.w	#4,sp
	move.l	-6(a5),a0
	move.w	32(a0),-(sp)
	move.l	-6(a5),a0
	move.w	30(a0),-(sp)
	move.w	#14,-(sp)
	move.l	-6(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
.21
	add.w	#1,-2(a5)
	cmp.w	#6,-2(a5)
	blt	.23
.22
.24
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	_F_h11_41F6
	public	_F_h11_2E26
	public	.begin
	dseg
	public	_G_h01_9EA2
	public	_G_h01_9EA0
	public	_G_h01_9E92
	public	_G_h01_9E90
	public	_G_h01_9E82
	public	_G_h01_9E80
	public	_G_h01_9E72
	public	_G_h01_9E70
	public	_G_h01_9E62
	public	_G_h01_9E60
	public	_G_h01_9E52
	public	_G_h01_9E50
	public	_G_h01_9E40
	public	_G_h01_9E32
	public	_G_h01_9E30
	public	_G_h01_9E20
	public	_G_h01_9E12
	public	_G_h01_9E10
	public	_G_h01_9E00
	public	_G_h01_9DF2
	public	_G_h01_9DF0
	public	_G_h01_9DE0
	public	_G_h01_9DD2
	public	_G_h01_9DD0
	public	_G_h01_9DC0
	public	_G_h01_9DB2
	public	_G_h01_9DB0
	public	_G_h01_9DA0
	public	_G_h01_9D90
	public	_G_h01_9D82
	public	_G_h01_9D80
	public	_G_h01_9D72
	public	_G_h01_9D70
	public	_G_h01_9D6A
	public	_G_h01_9D60
	public	_G_h01_9D5A
	public	_G_h01_9D50
	public	_G_h01_9D4A
	public	_G_h01_9D40
	public	_G_h01_9D30
	public	_G_h01_34D8
	public	_G_h01_1300
	public	_G_h01_9FCE
	public	_G_h01_9F6A
	public	_G_h01_9E5C
	public	_G_h01_9D9C
	public	_G_h01_9D6C
	public	_G_h01_9D4C
	public	_G_h01_9D2C
	public	_G_h01_46E0
	end
