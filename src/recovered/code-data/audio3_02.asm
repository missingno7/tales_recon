; Typed CODE-resident audio data; historical ownership/TU UNKNOWN.
T3_HEADER macro
	dc.b \1,\2
	endm
T3_NOTE macro
	dc.b \1,\2
	endm
T3_SELECTOR macro
	dc.l \1
	endm
T3_ENVELOPE_PTR macro
	dc.l \1
	endm
T3_ENV_INITIAL macro
	dc.b \1
	endm
T3_ENV_DELTA macro
	dc.b \1
	endm
T3_ENV_TARGET macro
	dc.b \1
	endm
T3_ENV_DELAY macro
	dc.b \1
	endm
T3_ENV_ZERO macro
	dc.b 0
	endm
T3_COUNT macro
	dc.b $80,\1
	endm
T3_LOOP macro
	dc.b $81
	ds 0
	dc.l \1
	endm
T3_TRIGGER macro
	dc.b $82,\1
	endm
T3_JUMP macro
	dc.b $84
	ds 0
	dc.l \1
	endm
T3_CALL macro
	dc.b $85
	ds 0
	dc.l \1
	endm
T3_RETURN macro
	dc.b $86
	endm
T3_TRANSPOSE macro
	dc.b $87,\1
	endm
T3_END macro
	dc.b $88
	endm
T3_REST macro
	dc.b $89,\1
	endm
T3_PLAY_NOTE macro
	dc.b $8b,\1,\2
	endm
T3_PITCH_ADJUST macro
	dc.b $8c,\1
	endm
T3_ENVELOPE macro
	dc.b $8f,\1
	endm
T3_BANK macro
	dc.b $90,\1
	endm
T3_RAMP macro
	dc.b $91,\1,\2
	endm
T3_VIBRATO macro
	dc.b $95,\1,\2
	endm
T3_TICK_INCREMENT macro
	dc.b $97,\1
	endm
T3_HOLD macro
	dc.b $a0,\1
	endm
T3_ATTENUATION macro
	dc.b $ab,\1
	endm
T3_FLAGS macro
	dc.b $83,\1
	endm
T3_RAMP_OFF macro
	dc.b $92
	endm
T3_RANDOM_NOTE macro
	dc.b $99,\1
	endm
T3_CHANNEL_ATTENUATION macro
	dc.b $9e,\1
	endm
T3_SOUND_ENABLE macro
	dc.b $9f,\1
	endm
T3_MASTER_ATTENUATION macro
	dc.b $a3,\1
	endm
T3_ADD_MASTER_ATTENUATION macro
	dc.b $a4,\1
	endm
	cseg
	public _audio3_02_begin
	public _audio3_02_end
	public _audio3_e_60FC
	public _audio3_e_6102
_audio3_02_begin:
_audio3_e_60FC:
	T3_ENV_ZERO
	T3_ENV_DELAY 22
	T3_ENV_DELTA -2
	T3_ENV_TARGET 0
_audio3_e_6102:
	T3_ENV_INITIAL 255
	T3_ENV_DELTA -11
	T3_ENV_TARGET 0
_audio3_02_end:
	end
