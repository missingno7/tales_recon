	far data
	dseg
	public _audio_channel_0_block_countdown
	public _audio_channel_0_sample_block_cursor
	cseg
	public _recon_h00_55D6
	public _recon_h00_55EC
	public _recon_h00_561C
	public _recon_h00_5632
	public _recon_h00_563C
	public _end_irq0
_recon_h00_55D6
	move.w $dff002,d0
	btst #$0,d0
	bne _recon_h00_55EC
	move.w #$80,$dff09a
	bra _recon_h00_5632
_recon_h00_55EC
	subq.w #$1,_audio_channel_0_block_countdown
	bne _recon_h00_5632
	movea.l _audio_channel_0_sample_block_cursor,a0
	move.w (a0)+,d0
	tst.w d0
	bmi _recon_h00_563C
	beq _recon_h00_561C
	move.w d0,_audio_channel_0_block_countdown
	move.w (a0)+,$dff0a4
	move.l (a0)+,$dff0a0
	move.l a0,_audio_channel_0_sample_block_cursor
	bra _recon_h00_5632
_recon_h00_561C
	move.w d0,_audio_channel_0_block_countdown
	move.w #$1,$dff096
	move.w #$80,$dff09a
_recon_h00_5632
	move.w #$80,$dff09c
	rts
_recon_h00_563C
	move.w #$7fff,_audio_channel_0_block_countdown
	bra _recon_h00_5632
_end_irq0
	dseg
	end
