	far data
	dseg
	public _audio_channel_3_block_countdown
	public _audio_channel_3_sample_block_cursor
	cseg
	public _recon_h00_5726
	public _recon_h00_573C
	public _recon_h00_576C
	public _recon_h00_5782
	public _recon_h00_578C
	public _end_irq3
_recon_h00_5726
	move.w $dff002,d0
	btst #$3,d0
	bne _recon_h00_573C
	move.w #$400,$dff09a
	bra _recon_h00_5782
_recon_h00_573C
	subq.w #$1,_audio_channel_3_block_countdown
	bne _recon_h00_5782
	movea.l _audio_channel_3_sample_block_cursor,a0
	move.w (a0)+,d0
	tst.w d0
	bmi _recon_h00_578C
	beq _recon_h00_576C
	move.w d0,_audio_channel_3_block_countdown
	move.w (a0)+,$dff0d4
	move.l (a0)+,$dff0d0
	move.l a0,_audio_channel_3_sample_block_cursor
	bra _recon_h00_5782
_recon_h00_576C
	move.w d0,_audio_channel_3_block_countdown
	move.w #$8,$dff096
	move.w #$400,$dff09a
_recon_h00_5782
	move.w #$400,$dff09c
	rts
_recon_h00_578C
	move.w #$7fff,_audio_channel_3_block_countdown
	bra _recon_h00_5782
_end_irq3
	dseg
	end
