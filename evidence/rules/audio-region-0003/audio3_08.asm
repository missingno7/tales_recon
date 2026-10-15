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
	public _audio3_08_begin
	public _audio3_08_end
	public _audio3_c_6A1A
	public _audio3_c_6A31
	public _audio3_c_6B0F
	public _audio3_c_6B58
	public _audio3_h_69FC
	public _audio3_h_6A0F
	public _audio3_h_6A22
	public _audio3_h_6A41
	public _audio3_h_6A78
	public _audio3_h_6AA0
	public _audio3_h_6ACC
	public _audio3_h_6ADB
	public _audio3_h_6AEF
	public _audio3_h_6B4A
_audio3_08_begin:
_audio3_h_69FC:
	T3_HEADER 0,0
	T3_ENVELOPE 30
	T3_BANK 56
	T3_TRANSPOSE 0
	T3_NOTE 8,17
	T3_RAMP 219,0
	T3_HOLD 23
	T3_RAMP_OFF
	T3_HOLD 48
	T3_END
_audio3_h_6A0F:
	T3_HEADER 2,0
	T3_ENVELOPE 28
	T3_BANK 6
	T3_ATTENUATION 80
	T3_VIBRATO 1,196
_audio3_c_6A1A:
	T3_NOTE 48,23
	T3_JUMP _audio3_c_6A1A
_audio3_h_6A22:
	T3_HEADER 1,0
	T3_ENVELOPE 26
	T3_BANK 27
	T3_NOTE 43,4
	T3_RAMP 15,0
	T3_HOLD 20
	T3_COUNT 10
_audio3_c_6A31:
	T3_RAMP 232,0
	T3_HOLD 4
	T3_RAMP 24,0
	T3_HOLD 4
	T3_LOOP _audio3_c_6A31
	T3_END
_audio3_h_6A41:
	T3_HEADER 1,0
	T3_ENVELOPE 24
	T3_BANK 27
	T3_NOTE 32,4
	T3_RAMP 252,0
	T3_HOLD 16
	T3_RAMP 253,128
	T3_HOLD 128
	T3_END
_audio3_h_6A78:
	T3_HEADER 0,0
	T3_ATTENUATION 192
	T3_BANK 6
	T3_ENVELOPE 10
	T3_RAMP 72,128
	T3_NOTE 91,16
	T3_END
_audio3_h_6AA0:
	T3_HEADER 0,0
	T3_ENVELOPE 16
	T3_BANK 6
	T3_RAMP 1,32
	T3_NOTE 80,255
	T3_END
_audio3_h_6ACC:
	T3_HEADER 0,0
	T3_ENVELOPE 10
	T3_BANK 56
	T3_ATTENUATION 176
	T3_NOTE 11,1
	T3_ATTENUATION 216
	T3_NOTE 11,2
	T3_END
_audio3_h_6ADB:
	T3_HEADER 0,0
	T3_ENVELOPE 10
	T3_BANK 48
	T3_ATTENUATION 64
	T3_NOTE 11,6
	T3_RAMP 9,32
	T3_BANK 53
	T3_CHANNEL_ATTENUATION 208
	T3_NOTE 75,16
	T3_END
_audio3_h_6AEF:
	T3_HEADER 0,0
	T3_ATTENUATION 32
	T3_TRANSPOSE 240
	T3_ENVELOPE 10
	T3_BANK 49
	T3_CALL _audio3_c_6B0F
	T3_PITCH_ADJUST 1
	T3_CALL _audio3_c_6B0F
	T3_PITCH_ADJUST 2
	T3_CALL _audio3_c_6B0F
	T3_END
_audio3_c_6B0F:
	T3_NOTE 32,4
	T3_NOTE 34,4
	T3_NOTE 36,4
	T3_NOTE 38,4
	T3_NOTE 40,4
	T3_NOTE 38,4
	T3_NOTE 36,4
	T3_NOTE 34,4
	T3_RETURN
_audio3_h_6B4A:
	T3_HEADER 0,0
	T3_ATTENUATION 144
	T3_ENVELOPE 14
	T3_BANK 6
	T3_FLAGS 255
	T3_NOTE 75,4
	T3_COUNT 32
_audio3_c_6B58:
	T3_RAMP 3,176
	T3_HOLD 4
	T3_RAMP 254,224
	T3_HOLD 4
	T3_LOOP _audio3_c_6B58
	T3_END
_audio3_08_end:
	end
