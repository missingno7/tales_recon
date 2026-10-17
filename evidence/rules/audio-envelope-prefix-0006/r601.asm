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
	public _r601_begin
	public _r601_end
	public _audio6_e_60FC
	public _audio6_e_6102
_r601_begin:
_audio6_e_60FC:
	E6_ZERO
	E6_DELAY 22
	E6_DELTA -2
	E6_TARGET 0
_audio6_e_6102:
	E6_INITIAL 255
	E6_DELTA -11
	E6_TARGET 0
_r601_end:
	end
