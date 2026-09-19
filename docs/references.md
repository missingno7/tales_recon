# Research and provenance references

Consulted 2026-09-19. These are research inputs, not executable dependencies.

- [Laurent Clévy / ADFlib ADF format documentation](https://adflib.github.io/FAQ/adf_info.html):
  filesystem field layouts, checksums, file chains, directory hashing and bitmap interpretation.
- [Amiga ROM Kernel Reference Manual: DOS](https://developer.amigaos3.net/sites/default/files/downloads/2024-10/Amiga_ROM_Kernel_Reference_Manual_DOS.pdf),
  chapter 11, especially section 11.4.10: HUNK and Manx overlay ABI. The supplied
  binary uses one-based node IDs and a descriptor-count convention different
  from the illustrative text. The parser preserves measurements.
- [Official LoadSeg documentation](https://developer.amigaos3.net/autodocs/dos.library/LoadSeg.html):
  resident overlay header and loader interface context.
- [Aztec C Museum distribution index](https://www.aztecmuseum.ca/compilers.htm):
  candidate Amiga 5.0a distribution, not proof of use by DuckTales.
  The linked `aztecc50a.zip` download returned HTTP 465 during acquisition.
- `D:/Prog/empires_reconstruction/README.md` and `docs/build-reconstruction.md`:
  natural-layout proof and isolation of original fixtures. Its fixed-placement
  and raw-fallback bootstrap techniques are not adopted here.
- `D:/Prog/icytower_recon/README.md` and `docs/proof-levels.md`:
  runtime/library separation, compiler provenance, and distinction between
  function, compilation-unit, linked-layout and whole-file proof.

The two sibling projects were read only. This project has no runtime/build
dependency on either of them and imported none of their source or binary data.
