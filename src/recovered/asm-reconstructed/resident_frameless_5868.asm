	far data
	dseg
	public _audio_pitch_effect_channel_mask
	public _audio_channel_0_state
	public _audio_channel_0_block_countdown
	public _audio_channel_1_block_countdown
	public _audio_channel_2_block_countdown
	public _audio_channel_3_block_countdown
	public _audio_global_volume_attenuation
	public _audio_volume_output_enabled
	cseg
	public _recon_h00_5868
	public _recon_h00_587A
	public _end_clear
_recon_h00_5868
	movem.l d7/a0,-(a7)
	clr.b _audio_pitch_effect_channel_mask
	lea.l _audio_channel_0_state,a0
	moveq #$4b,d7
_recon_h00_587A
	clr.l (a0)+
	dbra d7,_recon_h00_587A
	move.w #$f,$dff096
	move.w #$ff,$dff09e
	clr.w _audio_channel_0_block_countdown
	clr.w _audio_channel_1_block_countdown
	clr.w _audio_channel_2_block_countdown
	clr.w _audio_channel_3_block_countdown
	clr.b _audio_global_volume_attenuation
	move.b #$1,_audio_volume_output_enabled
	movem.l (a7)+,d7/a0
	rts
_end_clear
	dseg
	end
