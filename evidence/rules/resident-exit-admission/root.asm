;:ts=8
	dseg
	ds	0
	public	_candidate_reference
_candidate_reference:
	dc.l	_recovered
	cseg
	public	_main
_main:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	#0,d0
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	global	_G_h01_B3A6,4
	global	_G_h01_2EB0,2
	global	_G_h01_B3C8,4
	global	_G_h01_B3CE,4
	global	_G_h01_B3D2,4
	global	_G_h01_B3D6,4
	global	_G_h01_B3B0,4
	global	_G_h01_B3BC,4
	global	_G_h01_B3BA,2
	global	_G_h01_B3B8,2
	global	_G_h01_B3B4,4
	global	_G_h01_B39E,4
	public	_F_h00_8640
_F_h00_8640:
	link	a5,#.5
	movem.l	.6,-(sp)
	move.l	#0,d0
.7
	movem.l	(sp)+,.6
	unlk	a5
	rts
.5	equ	0
.6	reg	
	public	_F_h00_8980
_F_h00_8980:
	link	a5,#.8
	movem.l	.9,-(sp)
	move.l	#0,d0
.10
	movem.l	(sp)+,.9
	unlk	a5
	rts
.8	equ	0
.9	reg	
	public	_F_h00_8788
_F_h00_8788:
	link	a5,#.11
	movem.l	.12,-(sp)
	move.l	#0,d0
.13
	movem.l	(sp)+,.12
	unlk	a5
	rts
.11	equ	0
.12	reg	
	public	_F_h00_8974
_F_h00_8974:
	link	a5,#.14
	movem.l	.15,-(sp)
	move.l	#0,d0
.16
	movem.l	(sp)+,.15
	unlk	a5
	rts
.14	equ	0
.15	reg	
	public	_F_h00_8A12
_F_h00_8A12:
	link	a5,#.17
	movem.l	.18,-(sp)
	move.l	#0,d0
.19
	movem.l	(sp)+,.18
	unlk	a5
	rts
.17	equ	0
.18	reg	
	public	_recovered
	public	.begin
	dseg
	end
