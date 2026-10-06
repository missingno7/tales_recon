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
	global	_G_h01_0100,2
	public	_F_h00_0200
_F_h00_0200:
	link	a5,#.5
	movem.l	.6,-(sp)
	move.l	#0,d0
.7
	movem.l	(sp)+,.6
	unlk	a5
	rts
.5	equ	0
.6	reg	
	public	_recovered
	public	.begin
	dseg
	end
