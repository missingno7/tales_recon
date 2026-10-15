# `.as` indexed files (`dt1.as`, `dt2.as`)

## Container and record kinds

Both files have a measured 16-bit little-endian count and 32-bit little-endian
offset table, followed by 16-byte record headers. Each header’s `u32` at `+0`
spans the stored payload to the next distinct offset; `u16` at `+4` is the
record kind and `+6..+15` are five metadata words. `dt1.as` has 84 references
and kinds 3, 5, and 6; `dt2.as` has 84 references and kinds 3 and 5, with
repeated offsets aliasing records. This is a measured structural inference;
no matched `.as` parser call path establishes this container layout.

## What the matched code establishes

The only matched filename reference is `resident_F_0FDE`: it opens
`"dt2:dt2.as"` and stores the result in `G_h01_A7D2`. That handle is not read
or otherwise used by matched C, and no matched C names `dt1.as`. Although the
unmatched `resident_F_291E` dispatch contains branches for record kinds 3, 5,
and 6, no matched caller connects that reader to either `.as` handle; assigning
those branches to `.as` is therefore **UNKNOWN**.

The accepted host decoder preserves these stored payloads unchanged. The
meanings of kinds 3/5/6, their metadata words, and any inner compression are
**UNKNOWN**. The LZW codec in `resident_F_3C4C` is established for `.arc` kind
4 only; it is not evidence for the `.as` kinds.

## Audio relationship

`docs/audio-code-data.md` and `docs/code-data-providers.md` describe bytecode
measured inside the executable resident CODE hunk at `H0+[0x13B8,0x2816)`.
Those docs establish 2,400 commands and 35 headers in that CODE-resident
region; they do not connect the streams to `dt1.as`/`dt2.as`, their record
kinds, or samples/instruments. Any such relationship is **UNKNOWN**.
