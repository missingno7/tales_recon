; Typed CODE-resident audio data; historical ownership/TU UNKNOWN.
T4_HEADER macro
	dc.b \1,\2
	endm
T4_NOTE macro
	dc.b \1,\2
	endm
T4_SELECTOR macro
	dc.l \1
	endm
T4_ENVELOPE_PTR macro
	dc.l \1
	endm
T4_ENV_INITIAL macro
	dc.b \1
	endm
T4_ENV_DELTA macro
	dc.b \1
	endm
T4_ENV_TARGET macro
	dc.b \1
	endm
T4_ENV_DELAY macro
	dc.b \1
	endm
T4_ENV_ZERO macro
	dc.b 0
	endm
T4_COUNT macro
	dc.b $80,\1
	endm
T4_LOOP macro
	dc.b $81
	ds 0
	dc.l \1
	endm
T4_TRIGGER macro
	dc.b $82,\1
	endm
T4_JUMP macro
	dc.b $84
	ds 0
	dc.l \1
	endm
T4_CALL macro
	dc.b $85
	ds 0
	dc.l \1
	endm
T4_RETURN macro
	dc.b $86
	endm
T4_TRANSPOSE macro
	dc.b $87,\1
	endm
T4_END macro
	dc.b $88
	endm
T4_REST macro
	dc.b $89,\1
	endm
T4_PLAY_NOTE macro
	dc.b $8b,\1,\2
	endm
T4_PITCH_ADJUST macro
	dc.b $8c,\1
	endm
T4_ENVELOPE macro
	dc.b $8f,\1
	endm
T4_BANK macro
	dc.b $90,\1
	endm
T4_RAMP macro
	dc.b $91,\1,\2
	endm
T4_VIBRATO macro
	dc.b $95,\1,\2
	endm
T4_TICK_INCREMENT macro
	dc.b $97,\1
	endm
T4_HOLD macro
	dc.b $a0,\1
	endm
T4_ATTENUATION macro
	dc.b $ab,\1
	endm
T4_FLAGS macro
	dc.b $83,\1
	endm
T4_RAMP_OFF macro
	dc.b $92
	endm
T4_RANDOM_NOTE macro
	dc.b $99,\1
	endm
T4_CHANNEL_ATTENUATION macro
	dc.b $9e,\1
	endm
T4_SOUND_ENABLE macro
	dc.b $9f,\1
	endm
T4_MASTER_ATTENUATION macro
	dc.b $a3,\1
	endm
T4_ADD_MASTER_ATTENUATION macro
	dc.b $a4,\1
	endm
T4_WAIT_SAMPLE macro
	dc.b $a7
	endm
T4_RESTART_ENVELOPE macro
	dc.b $a8,\1
	endm
T4_SAMPLE_TIMED macro
	dc.b $9a,\1
	ds 0
	dc.w \2
	dc.b \3
	endm
T4_SAMPLE_WAIT macro
	dc.b $9a,\1
	ds 0
	dc.w \2
	endm
T4_SAMPLE93_TIMED macro
	dc.b $93,\1
	ds 0
	dc.w \2
	dc.b \3
	endm
T4_SAMPLE93_WAIT macro
	dc.b $93,\1
	ds 0
	dc.w \2
	endm
	cseg
	public _r402_begin
	public _r402_end
	public _audio4_e_6126
	public _audio4_e_6132
	public _audio4_e_6136
	public _audio4_e_613D
_r402_begin:
_audio4_e_6126:
	T4_ENV_DELTA -1
	T4_ENV_TARGET 8
	T4_ENV_ZERO
	T4_ENV_ZERO
_audio4_e_6132:
	T4_ENV_DELTA -5
	T4_ENV_TARGET 0
_audio4_e_6136:
	T4_ENV_INITIAL 0
	T4_ENV_DELTA 40
	T4_ENV_TARGET 216
	T4_ENV_DELTA -1
	T4_ENV_TARGET 128
	T4_ENV_ZERO
	T4_ENV_ZERO
_audio4_e_613D:
	T4_ENV_DELTA -49
	T4_ENV_TARGET 0
_r402_end:
	end
