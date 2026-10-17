; Typed envelope DATA only. Historical source/TU/owner UNKNOWN.
E6_PTR macro
	dc.l \1
	endm
E6_INITIAL macro
	dc.b \1
	endm
E6_DELTA macro
	dc.b \1
	endm
E6_TARGET macro
	dc.b \1
	endm
E6_DELAY macro
	dc.b \1
	endm
E6_ZERO macro
	dc.b 0
	endm
	cseg
	public _r602_begin
	public _r602_end
	public _audio6_e_6106
	public _audio6_e_6122
_r602_begin:
_audio6_e_6106:
	E6_ZERO
	E6_ZERO
_audio6_e_6122:
	E6_INITIAL 32
	E6_DELTA -1
	E6_TARGET 0
_r602_end:
	end
