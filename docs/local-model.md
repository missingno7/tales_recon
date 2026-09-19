# Local GPU grinder

The local adapter plugs Qwen3-Coder-30B-A3B-Instruct Q4_K_M into the existing
grinder, historical compiler and exact verifier. A persistent native Windows CUDA
llama.cpp b11053 server keeps the model resident. The desktop stays on the RTX 4090.
WinUAE continues to run only the historical Aztec compiler tools.

## Measured results and limits

With 21,073 MiB free before loading, the 8,192-token context and one inference slot
remained stable across three frontier runs. Peak sampled whole-GPU usage was
21,877 MiB; minimum free memory was 2,262 MiB, including desktop allocations.
Generation measured 199–209 tokens/sec. Temperature was 0.3.

The runs attempted **19 unrecovered functions with 47 local model calls and zero
new promotions**. Verified new bytes/functions per GPU-hour and new matches per
100 calls are therefore zero. The backend works, but productive sustained
convergence has not been demonstrated. Canonical coverage remains **23 functions /
1,158 bytes**; no complete overlay matches. Declaration errors, unresolved call
units, malformed output and persistent code-generation differences are retained.

A separate live calibration withheld existing source and previous attempts from
three already verified functions. The model reproduced ov14_F_03AE exactly
(20 bytes); the other two returned DIFFER and BLOCKED. This was real local
inference, not a fixture proposer, but adds zero recovery coverage. All three
model responses replayed from cache, and compiler replay required zero worker
invocations. Restarting the ordinary run skipped the parked frontier with zero
model calls and zero compiler jobs.

- `evidence/experiments/local-grinder-acceptance.json`: aggregate acceptance and pinned receipts.
- `evidence/experiments/local-grinder-calibration.json`: live comparison and cache replay.
- `recovery/reports/*.json`: quality, token rates, prompt budgets, GPU samples, timing and blocker groups.
- `recovery/runs/*.json`: permanent orchestration receipts.

## Commands

```powershell
python tools/setup_local_model.py
python tools/local_model_server.py start --context 8192
python tools/local_model_server.py status
python tools/grinder.py run --batch-size 16 --max-rounds 1000 --max-attempts 5 --profile aztec36 --proposer python tools/local_model_proposer.py
python tools/grinder_report.py
```

Put `--proposer` last. Append adapter options such as `--temperature 0.2` or
`--max-output-tokens 1536` after it. Default output reservation is 1,024 tokens.
Use one grinder writer per checkout. Ctrl+C stops the foreground grinder;
completed responses and compiler trials remain cached. The model stays resident.
Run the same command to resume. Completed ownership and active blockers are
skipped; infrastructure failures pause without blaming the selected function.

After improving a shared blocker mechanism, explicitly requeue a function:

```powershell
python tools/grinder.py retry ov11_F_4610
python tools/grinder.py run --ids ov11_F_4610 --max-rounds 5 --proposer python tools/local_model_proposer.py --max-output-tokens 1536
python tools/local_grinder_smoke.py
```

The last command repeats calibration without promoting previously owned bytes.
Do not repeatedly requeue the failed frontier without a changed hypothesis.
Reports group supervisor work by declaration, data ownership, reference identity,
call binding and code-generation mechanism.

The existing ranking is retained. Default eligibility requires a high-confidence
closed overlay CFG, <=256 bytes, no indirect control flow, <=1 unknown callee,
<=8 data references and no unrecovered same-node PC-relative callee. The census
already prevents closed ABI proof around explicit A4 changes. Aztec36 alone is
the inner-loop default. Alternate profiles remain available to the supervisor.
Optional `--adaptive` starts at 64 bytes and expands toward 128/256 only after ten
distinct attempts and a 30% promotion rate. GPU concurrency never increases
automatically. Larger tiers need measured convergence.

## Memory fallback

Startup and generation sample actual VRAM with nvidia-smi. No fixed 21 GB budget
is assumed. If desktop pressure makes the current setup unstable, reduce context,
then move KV storage to CPU:

```powershell
python tools/local_model_server.py stop
python tools/local_model_server.py start --context 4096
# If still necessary:
python tools/local_model_server.py stop
python tools/local_model_server.py start --context 4096 --kv-cpu
```

Only if those remain insufficient, install with
`python tools/setup_local_model.py --quantization Q4_K_S`, then start with
`--quantization Q4_K_S --context 4096`. The fallback requires another 17.46 GB disk
space; setup checks space and retains existing weights. It was not needed or
downloaded during acceptance. CPU KV and Q4_K_S performance are unmeasured.
Settings changes require an explicit stop; start rejects conflicting live
configuration. Stop verifies the managed PID/executable even if HTTP is unhealthy.

## Fact boundary and caches

The adapter receives bounded JSON facts on stdin and emits only
`{"source":"..."}` on stdout. Metrics use a host-created sidecar. The serving
model's apply-template/tokenize endpoints measure the actual token budget,
reserving output space and 256 tokens. Reductions remove examples, older failures,
redundant instruction hex and distant ownership labels in that order. Complete
instruction lines, CFG, ABI, references, current C and latest mismatch remain.
Oversized required facts become a context blocker rather than being truncated.

Revisions retain original facts, current C and latest feedback. Server prompt
caching reuses prefixes. The model has no Git, shell, filesystem, emulator or
editing tools. Empty/non-ASCII/oversize source, malformed JSON, tool calls and
truncated responses are rejected. Only the unchanged full-contribution verifier
and regression checks can promote source ownership.

The server binds 127.0.0.1:18087, uses an ignored generated credential and offline
mode, and disables agent/web UI features. `--endpoint` or TALES_LOCAL_ENDPOINT
accepts only loopback HTTP, without proxies, redirects or remote fallback. A
custom server also requires `--identity-file` containing model_sha256,
runner_sha256, model, alias and context_size, optionally key_file. The managed
default needs no endpoint/key configuration.

`build/local-model-proposals` retains exact facts/messages, raw responses, C and
hash receipts. Keys include fact hash, model/runner, context/KV configuration,
generation parameters and prompt/adapter implementation. Completed rejected
responses are cached too. `build/compile-cache` remains the independent compiler
cache. Public proposal receipts contain hashes/metrics, never the credential.
Downloads and binaries are ignored by Git. Old Qwen2.5 7B files remain installed.

Weights and runtime are hash-pinned in toolchain/qwen3-coder.lock.json against the
[quantizer repository](https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF)
and [llama.cpp b11053](https://github.com/ggml-org/llama.cpp/releases/tag/b11053).
The [server API](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)
provides schema-constrained chat, tokenization, prompt caching and timing.
