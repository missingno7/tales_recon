;:ts=8
	public	_F_h11_407C
_F_h11_407C:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A15E+14,a0
	move.w	8(a5),d1
	ext.l	d1
	asl.l	#5,d1
	lea	_G_h01_A15E+12,a1
	move.w	(a0,d0.l),(a1,d1.l)
	move.w	#6,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_40E0
	add.w	#4,sp
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h11_40AE
_F_h11_40AE:
	link	a5,#.5
	movem.l	.6,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A15E,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	clr.w	_G_h01_A156
	pea	5
	jsr	_F_h00_86A8
	add.w	#4,sp
	move.w	#91,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
.7
	movem.l	(sp)+,.6
	unlk	a5
	rts
.5	equ	-4
.6	reg	
	public	_F_h11_40E0
_F_h11_40E0:
	link	a5,#.8
	movem.l	.9,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A15E,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.w	#2,28(a0)
	move.l	-4(a5),a0
	tst.w	30(a0)
	beq	.11
	cmp.w	#6,10(a5)
	bne	.10
.11
	move.l	-4(a5),a0
	move.w	10(a5),30(a0)
.10
	cmp.w	#6,10(a5)
	bne	.12
	move.w	8(a5),d0
	ext.l	d0
	divs.w	#4,d0
	swap	d0
	add.w	#18,d0
	move.w	d0,-(sp)
	move.w	#30,-(sp)
	move.w	#88,-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),-(sp)
	move.l	-4(a5),a0
	move.w	22(a0),-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
.12
.13
	movem.l	(sp)+,.9
	unlk	a5
	rts
.8	equ	-4
.9	reg	
	public	_F_h11_4696
	public	_F_h00_86A8
	public	_F_h00_57D2
	public	.begin
	dseg
	public	_G_h01_A156
	public	_G_h01_A15E
	end
