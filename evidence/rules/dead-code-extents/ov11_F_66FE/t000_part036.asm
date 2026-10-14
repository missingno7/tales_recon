;:ts=8
	public	_F_h11_41F6
_F_h11_41F6:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	10(a5),a0
	clr.w	6(a0)
	move.l	10(a5),a0
	move.w	14(a5),20(a0)
	move.l	10(a5),a0
	move.w	16(a5),(a0)
	move.l	10(a5),a0
	move.w	18(a5),2(a0)
	move.w	8(a5),d0
	ext.l	d0
	bra	.4
.6
	lea	_G_h01_9F0C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	move.l	10(a5),a0
	move.w	#4,10(a0)
	move.w	#89,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	bra	.5
.7
	move.w	14(a5),d0
	ext.l	d0
	bra	.8
.10
	move.l	10(a5),a0
	move.w	#1,10(a0)
	lea	_G_h01_9C2C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.9
.11
	move.l	10(a5),a0
	move.w	#6,10(a0)
	lea	_G_h01_9C2C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.9
.8
	sub.l	#1,d0
	beq	.10
	sub.l	#2,d0
	beq	.11
.9
	bra	.5
.12
	move.w	14(a5),d0
	ext.l	d0
	bra	.13
.15
	move.l	10(a5),a0
	clr.w	10(a0)
	lea	_G_h01_9CEC,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.14
.16
	move.l	10(a5),a0
	clr.w	10(a0)
	lea	_G_h01_9CFC,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.14
.17
	move.l	10(a5),a0
	move.w	#3,10(a0)
	lea	_G_h01_9CBC,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.14
.13
	sub.l	#14,d0
	beq	.15
	sub.l	#4,d0
	beq	.16
	sub.l	#1,d0
	beq	.17
.14
	bra	.5
.18
	move.w	14(a5),d0
	ext.l	d0
	bra	.19
.21
	move.l	10(a5),a0
	move.w	#1,10(a0)
	lea	_G_h01_9EAC,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.20
.22
	move.l	10(a5),a0
	move.w	#5,10(a0)
	lea	_G_h01_9EBC,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.20
.19
	sub.l	#20,d0
	beq	.21
	sub.l	#25,d0
	beq	.22
.20
	bra	.5
.23
	move.w	14(a5),d0
	ext.l	d0
	bra	.24
.26
	move.l	10(a5),a0
	move.w	#2,10(a0)
	lea	_G_h01_9D4C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.25
.27
	move.l	10(a5),a0
	move.w	#2,10(a0)
	lea	_G_h01_9D2C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.25
.28
	move.l	10(a5),a0
	move.w	#3,10(a0)
	lea	_G_h01_9D6C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.25
.29
	move.l	10(a5),a0
	clr.w	10(a0)
	lea	_G_h01_9D3C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.25
.30
	move.l	10(a5),a0
	move.w	#12,10(a0)
	lea	_G_h01_9D9C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	clr.w	-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	pea	5
	jsr	_F_h00_86A8
	add.w	#4,sp
	move.w	#97,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	bra	.25
.31
	move.l	10(a5),a0
	move.w	#5,10(a0)
	lea	_G_h01_9E5C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.25
.32
	move.l	10(a5),a0
	clr.w	10(a0)
	lea	_G_h01_9E5C,a0
	move.l	10(a5),a1
	move.l	a0,16(a1)
	bra	.25
.33
	dc.w	.27-.34-2
	dc.w	.26-.34-2
	dc.w	.29-.34-2
	dc.w	.25-.34-2
	dc.w	.28-.34-2
	dc.w	.32-.34-2
	dc.w	.31-.34-2
	dc.w	.30-.34-2
.24
	sub.l	#11,d0
	cmp.l	#8,d0
	bcc	.25
	asl.l	#1,d0
	move.w	.33(pc,d0.w),d0
.34
	jmp	(pc,d0.w)
.25
	bra	.5
.35
.4
	sub.l	#2,d0
	beq	.23
	sub.l	#6,d0
	beq	.18
	sub.l	#3,d0
	beq	.12
	sub.l	#13,d0
	beq	.7
	sub.l	#9,d0
	beq	.6
.5
	move.l	10(a5),a0
	move.l	16(a0),a1
	move.l	10(a5),a0
	move.w	6(a1),8(a0)
.37
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h00_86A8
	public	_F_h00_57D2
	public	.begin
	dseg
	public	_G_h01_9D2C
	public	_G_h01_9D4C
	public	_G_h01_9D3C
	public	_G_h01_9D6C
	public	_G_h01_9E5C
	public	_G_h01_9D9C
	public	_G_h01_9EAC
	public	_G_h01_9EBC
	public	_G_h01_9CEC
	public	_G_h01_9CFC
	public	_G_h01_9CBC
	public	_G_h01_9C2C
	public	_G_h01_9F0C
	end
