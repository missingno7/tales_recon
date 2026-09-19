# Optional local proposer

The primary grinder uses the user-approved OpenAI adapter. A separate local-only
experiment uses Qwen2.5-Coder-7B-Instruct Q4_K_M under the native Windows CUDA
llama.cpp server. The bounded trial produced no exact matches: some proposals
copied irrelevant examples or emitted invalid C. This is retained experimental
infrastructure, not a validated recovery model. The server is currently stopped;
weights and runtime remain installed at the user's request.

The [official Qwen model](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF)
is Apache-2.0 licensed. The [llama.cpp release](https://github.com/ggml-org/llama.cpp/releases/tag/b11053)
and model revision, download sizes and upstream SHA-256 values are pinned in
`toolchain/local-model.lock.json`. Downloads and installed binaries are ignored
by Git. Setup downloads public files only and verifies hashes before extraction.

```powershell
python tools/setup_local_model.py
python tools/local_model_server.py start
python tools/local_model_server.py status
python tools/grinder.py run --batch-size 4 --max-rounds 10 --proposer python tools/local_proposer.py
python tools/local_model_server.py stop
```

The server binds only 127.0.0.1:18087, uses a generated local credential, offline
mode, no agent tools, and no web UI. Model requests use a literal loopback HTTP
connection without proxies, redirects, DNS, or remote fallback. The adapter
accepts only completed, bounded ASCII source responses; tool calls are rejected.
It caches proposals by facts, prompt, model, runner and adapter identities, then
passes candidates to the same historical verifier used by hosted models.

The 16K context and one inference slot were tested on the workstation's RTX 4090.
The model has no compiler, filesystem, shell, or emulator interface. Only the host
adapter saves its response; the verifier alone grants source ownership. Starting
and stopping checks the server executable and live PID; it never kills unrelated
emulators or inference servers.
