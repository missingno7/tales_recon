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
	global	_G_h01_B39E,4
	global	_G_h01_B3AA,4
	global	_G_h01_B3AE,2
	global	_G_h01_B3B8,2
	global	_G_h01_B3BA,2
	global	_G_h01_B3B4,4
	global	_G_h01_B3BC,4
	global	_G_h01_B3B0,4
	global	_G_h01_B3A6,4
	global	_G_h01_2EB0,2
	public	_F_h00_77A4
_F_h00_77A4:
	link	a5,#.5
	movem.l	.6,-(sp)
	move.l	#0,d0
.7
	movem.l	(sp)+,.6
	unlk	a5
	rts
.5	equ	0
.6	reg	
	public	_F_h00_7B24
_F_h00_7B24:
	link	a5,#.8
	movem.l	.9,-(sp)
	move.l	#0,d0
.10
	movem.l	(sp)+,.9
	unlk	a5
	rts
.8	equ	0
.9	reg	
	public	_F_h00_869C
_F_h00_869C:
	link	a5,#.11
	movem.l	.12,-(sp)
	move.l	#0,d0
.13
	movem.l	(sp)+,.12
	unlk	a5
	rts
.11	equ	0
.12	reg	
	public	_F_h00_86C0
_F_h00_86C0:
	link	a5,#.14
	movem.l	.15,-(sp)
	move.l	#0,d0
.16
	movem.l	(sp)+,.15
	unlk	a5
	rts
.14	equ	0
.15	reg	
	public	_F_h00_86E0
_F_h00_86E0:
	link	a5,#.17
	movem.l	.18,-(sp)
	move.l	#0,d0
.19
	movem.l	(sp)+,.18
	unlk	a5
	rts
.17	equ	0
.18	reg	
	public	_F_h00_86EE
_F_h00_86EE:
	link	a5,#.20
	movem.l	.21,-(sp)
	move.l	#0,d0
.22
	movem.l	(sp)+,.21
	unlk	a5
	rts
.20	equ	0
.21	reg	
	public	_F_h00_8744
_F_h00_8744:
	link	a5,#.23
	movem.l	.24,-(sp)
	move.l	#0,d0
.25
	movem.l	(sp)+,.24
	unlk	a5
	rts
.23	equ	0
.24	reg	
	public	_F_h00_892A
_F_h00_892A:
	link	a5,#.26
	movem.l	.27,-(sp)
	move.l	#0,d0
.28
	movem.l	(sp)+,.27
	unlk	a5
	rts
.26	equ	0
.27	reg	
	public	_F_h00_8964
_F_h00_8964:
	link	a5,#.29
	movem.l	.30,-(sp)
	move.l	#0,d0
.31
	movem.l	(sp)+,.30
	unlk	a5
	rts
.29	equ	0
.30	reg	
	public	_F_h00_899C
_F_h00_899C:
	link	a5,#.32
	movem.l	.33,-(sp)
	move.l	#0,d0
.34
	movem.l	(sp)+,.33
	unlk	a5
	rts
.32	equ	0
.33	reg	
	public	_F_h00_8A3A
_F_h00_8A3A:
	link	a5,#.35
	movem.l	.36,-(sp)
	move.l	#0,d0
.37
	movem.l	(sp)+,.36
	unlk	a5
	rts
.35	equ	0
.36	reg	
	dseg
	public _F_h00_8534
_F_h00_8534:
	dc.w $4ef9
	dc.l _exit_body
	cseg
	public	_exit_body
_exit_body:
	link	a5,#.38
	movem.l	.39,-(sp)
	move.l	#0,d0
.40
	movem.l	(sp)+,.39
	unlk	a5
	rts
.38	equ	0
.39	reg	
	public	_recovered
	public	.begin
	dseg
	end
