# Vamos availability probe

Date: 2026-09-27

## Result

The existing Windows environment had no amitools/vamos installation. An
isolated workspace-local install of `amitools 0.8.1` and `machine68k 0.3.0`
then launched, but its first pinned Aztec compiler attempt failed while
creating the mapped `Work:/` current-directory lock, before loading `cc`.
There is no direct-versus-WinUAE output comparison, so vamos is not justified
as a replacement worker. The exact failure is recorded below.

The repo's proven comparison candidate is the host-written C probe in
`experiments/aztec36-smoke/probe.c`, compiled by the pinned 3.6a `cc`, then
assembled by `as`, linked with `ln` and `c.lib`, and run. The preserved
`aztec36-004` WinUAE run completed all 14 steps successfully. Its basic
compile/assemble/link/run sequence returned zero for each step. Preserved
WinUAE output hashes:

```text
Old1:bin/cc >compile.log -a probe.c
Old1:bin/as >assemble.log -o probe.o probe.asm
Old1:bin/ln >link.log -o probe probe.o Old1:lib/c.lib
probe >run.log
```

| Output | SHA-256 |
| --- | --- |
| `probe.asm` | `5c10f8cfe0f52c883cd7372930ac66ba9119d51a2ac4d92c5aca94f573ff8102` |
| `probe.o` | `97c89d122a4d3b59bb590926d10c37ee9204689c06a6cd2aeaab54d26fb719f6` |
| linked `probe` | `69dc9f8095db9a5f8b01af326c3861be25049d79d7cc99af37da63f279655a51` |

The input source hash is `b67605076b89361d3447d1000b75a61e1c8f58d7aaade8c38685f4d1fb1701955`.
The original WinUAE artifacts remain under
`build/worker-jobs/aztec36-004/sys/work/`.

## Inventory commands and results

Commands run:

```powershell
Get-Command vamos, amitools -All -ErrorAction SilentlyContinue
python -c "import importlib.util; print('amitools=',importlib.util.find_spec('amitools'))"
python -m pip show amitools
Get-Command python
```

`Get-Command vamos, amitools` returned no commands. The Python import probe
returned `amitools=None`; `pip show` returned `Package(s) not found: amitools`.
The active Python is `C:\msys64\mingw64\bin\python.exe`.

## Pinned tool identities

| Tool | Path | SHA-256 |
| --- | --- | --- |
| Aztec 3.6a `cc` | `toolchain/installed/aztec-3.6a/SYS1/bin/cc` | `22edc2b6067fc0dfb201f69d894e0c5e9fa4500467cd8a34c1c5cb5199d924fa` |
| Aztec 3.6a `as` | `toolchain/installed/aztec-3.6a/SYS1/bin/as` | `96ddb35c570786993fe3c32b9535bb9b61251754f3774678132a0fa73209f098` |
| Aztec 3.6a `ln` | `toolchain/installed/aztec-3.6a/SYS1/bin/ln` | `1d93d91c7fbe7a97291a0a2441a713354937e4e8a6bf221e734a199ccb6cab45` |
| WinUAE | `C:\Program Files\WinUAE\winuae64.exe` | `c3c691589eb67f86712c75f60dda5719d90d7acbb8df58ffd18b115c74758258` |

## Initial availability and setup

The initial blocker was missing host software, not missing compiler inputs: the pinned
3.6a SYS1/SYS2 files, including `cc`, `as`, `ln`, and libraries, are already
present. The amitools project documents `pip install 'amitools[vamos]'` as the
stable install including its `machine68k` CPU backend. It says Windows might
work but is heavily untested. Vamos is an API-level AmigaOS emulator intended
to run CLI Amiga binaries; its DOS setup supports volume mappings and assigns.
See the [official install notes](https://github.com/cnvogelg/amitools#installation)
and [vamos documentation](https://github.com/cnvogelg/amitools/blob/main/docs/vamos.md).

The isolated installation and single execution attempt below address that
availability question. Generated ASM, object, and linked HUNK/executable must
still match the WinUAE hashes above byte-for-byte before switching workers.

No canonical ledgers, fixtures, promoted sources, or worker code were changed.

## Follow-up: isolated installation and one execution attempt

After the availability-only probe, the user explicitly authorized obtaining the
required tools. I created `build/vamos-probe-venv` with the active MSYS Python
using `python -m venv build/vamos-probe-venv`, then installed only into that
environment:

```powershell
build/vamos-probe-venv/bin/python.exe -m pip install 'amitools[vamos]'
```

The first install attempt was blocked by the default sandbox's network policy;
the authorized retry succeeded. Installed versions are `amitools 0.8.1` and
`machine68k 0.3.0`. Built wheel SHA-256 values were
`amitools-0.8.1`: `139660c3690b8b906d2a2ddcafc48e4eaec7faafa682203ee2e5e211038185cc`
and `machine68k-0.3.0`: `2ef34c02c95c9d6f62577416988dd9a8f8ff88cc9361ddf03ab577db592e38e2`.
The installed entry point is `build/vamos-probe-venv/bin/vamos.exe`.

The single compiler execution attempt was:

```powershell
build/vamos-probe-venv/bin/vamos.exe -S -v --logging path:debug --auto-volumes off -A c -A s -A libs -A devs -V System:D:/Prog/tales_recon/toolchain/installed/aztec-3.6a/SYS1 -V Old1:D:/Prog/tales_recon/toolchain/installed/aztec-3.6a/SYS1 -V Old2:D:/Prog/tales_recon/toolchain/installed/aztec-3.6a/SYS2 -V Work:D:/Prog/tales_recon/experiments/vamos/attempt-001 -a INCLUDE:System:include --cwd Work:/ -- Old1:bin/cc -a probe.c
```

Vamos resolved all four host volume paths and initialized the volume/assign
tables, but failed before loading or running `cc`: `Process.init_cwd` raised
`AttributeError: 'NoneType' object has no attribute 'locks'` while trying to
create the process's current-directory lock for `Work:/`. The command returned
1 and generated no ASM or object. `attempt-001` contains only the copied
`probe.c`, whose hash matches the WinUAE input. Thus no output hashes or byte
differences exist for this attempt, and byte identity is unverified.

Recommendation remains to keep WinUAE as the worker. The Windows package
installed and launched, but its volume mapping/current-directory setup failed
before the compiler ran. Stop here pending a focused compatibility fix or a
documented working Windows invocation; do not change the existing worker based
on this result.
