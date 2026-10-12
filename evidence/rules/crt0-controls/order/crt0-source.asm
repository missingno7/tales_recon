;:ts=8
; Copyright (C) 1986,1987 by Manx Software Systems, Inc.
;


;	Initial startup routine for Aztec C.

;	NOTE: code down to "start" must be placed at beginning of
;		all programs linked with Aztec Linker using small
;		code or small data.


	mc68881
	entry	.begin
	public	.begin
.begin
	bsr	_geta4			;get A4
	lea	__H1_end,a1
	lea	__H2_org,a2
	cmp.l	a1,a2			;check if BSS and DATA together
	bne	start			;no, don't have to clear
	move.w	#((__H2_end-__H2_org)/4)-1,d1
	bmi	start			;skip if no bss
	move.l	#0,d2
loop
	move.l	d2,(a1)+		;clear out memory
	dbra	d1,loop

start
	move.l	sp,__savsp		;save stack pointer
	move.l	4,a6			;get Exec's library base pointer
	move.l	a6,_SysBase		;put where we can get it
	movem.l	d0/a0,-(sp)		;save CLI command parameters

	btst.b	#4,$129(a6)		;check for 68881 flag in AttnFlags
	beq	1$			;skip if not
	lea	2$,a5
	jsr	-30(a6)			;do it in supervisor mode
	bra	1$
2$
	clr.l	-(sp)
	frestore (sp)+			;reset the ffp stuff
	rte				;and return
1$

	lea	dos_name,a1		;get name of dos library
	jsr	-408(a6)		;open the library any version
	move.l	d0,_DOSBase		;set it up
	bne	3$			;skip if okay

  	move.l  #$38007,d7		;AG_OpenLib | AO_DOSLib
	jsr     -108(a6)		;Alert
	bra	4$
3$
	jsr	__main			;call the startup stuff
4$
	add.w	#8,sp			;pop args
	rts				;and return

dos_name:
	dc.b	'dos.library',0

	public	_geta4
_geta4:
	far	data
	lea	__H1_org+32766,a4
	rts

	public	__main,__H0_org

	dseg

	public	_SysBase,__savsp,_DOSBase
	public	__H1_org,__H1_end,__H2_org,__H2_end

