"""Pinned vamos executor for the shared Aztec compile queue.

The executor keeps compiler_oracle's cache identities and extraction rules.
Each attempt gets private root/Work volumes and inventory-checked Aztec trees.
"""
from __future__ import annotations

import concurrent.futures
import json
from functools import lru_cache
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time
import uuid

import compiler_oracle
from common import FormatError, require, sha256, write_json

ROOT = compiler_oracle.ROOT
INPUT = b"n\n" * 20
DEFAULT_WORKERS = 8
MAX_WORKERS = 8
TREE_DIRECTORIES = ("SYS1/bin", "SYS1/include", "SYS1/lib", "SYS2/bin", "SYS2/lib")
MATH_LIBRARY = re.compile(r"\bmath[a-z0-9_-]*\.library\b", re.I)


class VamosFailure(RuntimeError):
    """A vamos attempt that must be retried by the WinUAE oracle."""


def strip_c_noncode(source: str) -> str:
    """Remove comments and quoted literals before checking C type tokens."""
    return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', ' ', source)


def has_float_type(source: str) -> bool:
    return bool(re.search(r"\b(?:float|double)\b", strip_c_noncode(source)))


def trace_math_libraries(trace: str | bytes) -> list[str]:
    if isinstance(trace, bytes):
        trace = trace.decode("utf-8", errors="replace")
    return sorted({match.group(0).lower() for match in MATH_LIBRARY.finditer(trace)})


def _backend_spec() -> dict:
    pin = Path(os.environ.get("TALES_VAMOS_TOOLCHAIN_PIN", "docs/toolchain.json"))
    if not pin.is_absolute():
        pin = ROOT / pin
    data = json.loads(pin.read_text(encoding="utf-8"))
    spec = data.get("runtime_worker", {}).get("vamos_backend")
    require(isinstance(spec, dict), "docs/toolchain.json has no runtime_worker.vamos_backend pin")
    return spec


def inventory_entries(root: Path, directories=TREE_DIRECTORIES) -> list[tuple[str, str]]:
    """Sorted hashes of the compiler and runtime directories mounted by a job."""
    entries = []
    for relative in directories:
        directory = root / relative
        require(directory.is_dir(), f"missing pinned vamos tool directory: {directory}")
        for path in directory.rglob("*"):
            if path.is_file():
                entries.append((path.relative_to(root).as_posix(), sha256(path.read_bytes())))
    return sorted(entries)


def inventory_sha256(root: Path, directories=TREE_DIRECTORIES) -> str:
    payload = "".join(f"{name}\0{digest}\n" for name, digest in inventory_entries(root, directories)).encode("ascii")
    return sha256(payload)


def validate_inventory(root: Path, spec: dict) -> None:
    directories = tuple(spec["tree_inventory"]["directories"])
    require(directories == TREE_DIRECTORIES, "vamos inventory directory list differs from supported layout")
    entries = inventory_entries(root, directories)
    require(len(entries) == spec["tree_inventory"]["file_count"],
            f"vamos tool inventory file count differs at {root}")
    actual = sha256("".join(f"{name}\0{digest}\n" for name, digest in entries).encode("ascii"))
    require(actual == spec["tree_inventory"]["sha256"],
            f"vamos tool inventory SHA-256 differs at {root}: {actual}")


@lru_cache(maxsize=1)
def toolchain_root() -> Path:
    """Copy the pinned Aztec 3.6a trees once, then verify every use."""
    spec = _backend_spec()
    source = ROOT / spec["toolchain_source"]
    copy_spec = Path(os.environ.get("TALES_VAMOS_TOOLCHAIN_COPY", spec["toolchain_copy"]))
    destination = copy_spec if copy_spec.is_absolute() else ROOT / copy_spec
    validate_inventory(source, spec)
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + ".copy-" + uuid.uuid4().hex[:10])
        try:
            temporary.mkdir()
            for relative in spec["tree_inventory"]["directories"]:
                target = temporary / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source / relative, target)
            validate_inventory(temporary, spec)
            try:
                temporary.rename(destination)
            except OSError:
                if destination.exists():
                    shutil.rmtree(temporary, ignore_errors=True)
                else:
                    raise
        except Exception:
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)
            raise
    validate_inventory(destination, spec)
    return destination


@lru_cache(maxsize=1)
def _runtime() -> tuple[Path, dict]:
    spec = _backend_spec()
    vamos = ROOT / spec["vamos_executable"]
    python = ROOT / spec["vamos_python"]
    require(vamos.is_file() and sha256(vamos.read_bytes()) == spec["vamos_executable_sha256"],
            "pinned vamos executable is missing or changed")
    require(python.is_file() and sha256(python.read_bytes()) == spec["vamos_python_sha256"],
            "pinned vamos Python is missing or changed")
    probe = "import importlib.metadata as m; print(m.version('amitools')+' '+m.version('machine68k'))"
    result = subprocess.run([str(python), "-c", probe], cwd=ROOT, capture_output=True,
                            text=True, timeout=30)
    expected = f"{spec['amitools_version']} {spec['machine68k_version']}"
    require(result.returncode == 0 and result.stdout.strip() == expected,
            "pinned vamos package versions differ: " + (result.stdout + result.stderr).strip())
    return vamos, spec


def worker_count() -> int:
    raw = os.environ.get("TALES_VAMOS_JOBS", str(DEFAULT_WORKERS))
    try:
        value = int(raw)
    except ValueError as exc:
        raise FormatError("TALES_VAMOS_JOBS must be an integer from 1 to 8") from exc
    require(1 <= value <= MAX_WORKERS, "TALES_VAMOS_JOBS must be between 1 and 8")
    return value


def build_vamos_args(vamos: Path, sysroot: Path, toolchain: Path, work: Path,
                     guest: str, guest_args: list[str], trace: Path | None = None) -> list[str]:
    """Build one command with private root/Work and pinned compiler volumes."""
    argv = [str(vamos), "-S", "-q", "--auto-volumes", "off",
            "-V", f"root:{sysroot.resolve().as_posix()}",
            "-V", f"System:{(toolchain / 'SYS1').resolve().as_posix()}",
            "-V", f"Old1:{(toolchain / 'SYS1').resolve().as_posix()}",
            "-V", f"Old2:{(toolchain / 'SYS2').resolve().as_posix()}",
            "-V", f"Work:{work.resolve().as_posix()}",
            "-V", f"INCLUDE:{(toolchain / 'SYS1/include').resolve().as_posix()}",
            "-a", "LIB:Old1:lib", "-A", "c", "-A", "s", "-A", "libs", "-A", "devs"]
    if trace is not None:
        argv += ["-l", "exec:info,lib:info,math:info", "-L", str(trace.resolve())]
    argv += ["--cwd", "Work:", "--", guest, *guest_args]
    return argv


def link_guest_command(command: str) -> tuple[str, list[str]]:
    """Remove Amiga shell redirection tokens while retaining every linker arg."""
    tokens = shlex.split(command, posix=False)
    require(tokens and not tokens[0].startswith(('<', '>')), "malformed pinned linker command")
    guest = tokens[0]
    args = [token for token in tokens[1:] if not token.startswith(('<', '>'))]
    return guest, args


def compatibility_shim() -> Path:
    spec = _backend_spec()
    override = os.environ.get("TALES_VAMOS_COMPAT_PATH")
    directory = Path(override) if override else ROOT / Path(spec["compatibility_shim"]).parent
    shim_file = directory / "sitecustomize.py"
    require(shim_file.is_file() and sha256(shim_file.read_bytes()) == spec["compatibility_shim_sha256"],
            "pinned vamos compatibility shim is missing or changed")
    return directory


def _run_guest(vamos: Path, sysroot: Path, toolchain: Path, work: Path, guest: str,
               guest_args: list[str], log: Path, trace: Path | None = None,
               timeout: int = 120) -> dict:
    argv = build_vamos_args(vamos, sysroot, toolchain, work, guest, guest_args, trace)
    env = os.environ.copy()
    shim = str(compatibility_shim())
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = shim + (os.pathsep + existing if existing else "")
    start = time.perf_counter()
    try:
        proc = subprocess.run(argv, cwd=ROOT, env=env, input=INPUT, capture_output=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        raise VamosFailure(f"vamos could not run {guest}: {exc}") from exc
    elapsed = time.perf_counter() - start
    log.write_bytes(proc.stdout + (b"\n--- STDERR ---\n" + proc.stderr if proc.stderr else b""))
    record = {"guest": guest, "argv": argv, "returncode": proc.returncode,
              "wall_seconds": elapsed, "log": log.name}
    if proc.returncode != 0:
        raise VamosFailure(f"{guest} returned {proc.returncode}; see {log}")
    return record


def _c_compile(work: Path, name: str, profile: str, toolchain: Path,
               vamos: Path, sysroot: Path, trace: Path, flags: list[str] | None = None) -> list[dict]:
    p = compiler_oracle.PROFILES[profile]
    guest = p["guest"] + "bin/cc"
    args = ["-a", *(p["flags"] if flags is None else flags)]
    if profile == "aztec36-x3":
        args += ["-I", "Old1:include"]
    args += [name + ".c"]
    cc = _run_guest(vamos, sysroot, toolchain, work, guest, args,
                    work / (name + "-cc.log"), trace=trace)
    if not (work / (name + ".asm")).is_file():
        raise VamosFailure(f"{name}: cc returned zero without emitting assembly")
    if not trace.is_file():
        raise VamosFailure(f"{name}: vamos did not create the required library trace")
    math_libraries = trace_math_libraries(trace.read_bytes())
    if math_libraries:
        raise VamosFailure("math-library-use:" + ",".join(math_libraries))
    ass = _run_guest(vamos, sysroot, toolchain, work, p["guest"] + "bin/as",
                     ["-o", name + ".o", name + ".asm"], work / (name + "-as.log"))
    if not (work / (name + ".o")).is_file():
        raise VamosFailure(f"{name}: as returned zero without emitting an object")
    return [cc, ass]


def compile_source_pair(source: str, profile: str, job_dir: Path, stem: str = "unit",
                        flags: list[str] | None = None) -> dict:
    """Compile one float-free C source and AJ object; used by the opt-in corpus test."""
    p = compiler_oracle.PROFILES[profile]
    if not p["version"].startswith("3.6"):
        raise VamosFailure("unsupported-profile:" + profile)
    require(not has_float_type(source), "float/double source is statically routed to WinUAE")
    toolchain = toolchain_root()
    vamos, _ = _runtime()
    sysroot = job_dir / "sys"
    work = sysroot / "work"
    work.mkdir(parents=True, exist_ok=True)
    (work / (stem + ".c")).write_text(source, encoding="ascii", newline="\n")
    (work / "compiler-input.txt").write_bytes(INPUT)
    trace = job_dir / (stem + "-cc.trace.log")
    steps = _c_compile(work, stem, profile, toolchain, vamos, sysroot, trace, flags=flags)
    return {"steps": steps, "asm": work / (stem + ".asm"), "object": work / (stem + ".o"),
            "trace": trace, "job_dir": job_dir}


def compile_asm_source(source: str, job_dir: Path, stem: str = "unit") -> dict:
    """Assemble one standalone source for the opt-in equivalence corpus."""
    toolchain = toolchain_root()
    vamos, _ = _runtime()
    sysroot = job_dir / "sys"
    work = sysroot / "work"
    work.mkdir(parents=True, exist_ok=True)
    (work / (stem + ".asm")).write_text(source, encoding="ascii", newline="\n")
    step = _run_guest(vamos, sysroot, toolchain, work, "Old1:bin/as",
                      ["-o", stem + ".o", stem + ".asm"], work / (stem + "-as.log"))
    require((work / (stem + ".o")).is_file(), f"{stem}: as returned zero without emitting an object")
    return {"step": step, "object": work / (stem + ".o"), "job_dir": job_dir}


SUPPORTED_PROFILES = frozenset(("aztec36", "aztec36-large-data", "aztec36-x3"))


def _safe_sources(objects: list[dict], harness: str, proxies: list[dict]) -> bool:
    sources = [obj["source"] for obj in objects] + [harness] + [proxy["source"] for proxy in proxies]
    return not any(has_float_type(source) for source in sources)


def _copy_trial_artifacts(work: Path, dest: Path, prefix: str, hp: str, idx: int) -> None:
    for path in work.iterdir():
        if not path.is_file():
            continue
        name = path.name
        if (name == "compiler-input.txt" or name.startswith(prefix + ".") or
                name.startswith(prefix + "_") or name.startswith(prefix + "-") or
                name.startswith(hp + ".") or name.startswith(hp + "-") or name.startswith(f"p{idx:03d}_")):
            shutil.copyfile(path, dest / name)


def _compile_vamos_trial(trial: dict, key: str, idx: int) -> tuple[dict | None, str | None, dict | None]:
    """Return (cache result, fallback reason, attempt record) for one cache miss."""
    import link_line
    from queued_oracle import trial_plan
    try:
        profile = trial["profile"]
        profiles = set(trial.get("object_profiles") or [profile])
        if profile not in SUPPORTED_PROFILES or not profiles <= SUPPORTED_PROFILES:
            return None, "unsupported-profile:" + profile, None
        planned_key, meta, harness, objects = trial_plan(trial)
        require(planned_key == key, "vamos trial plan changed its cache key")
        proxies = compiler_oracle.overlay_proxies(trial["source"], trial.get("target_node", 1))
        if not _safe_sources(objects, harness, proxies):
            return None, "source-token-float-or-double", None
        toolchain = toolchain_root()
        vamos, runtime_spec = _runtime()
    except Exception as exc:
        return None, "vamos-admission:" + str(exc), None

    job_id = "vamos-" + uuid.uuid4().hex[:12]
    job_dir = Path(os.environ.get("TALES_VAMOS_JOB_ROOT", ROOT / "build/vamos-jobs")) / job_id
    work = job_dir / "sys/work"
    sysroot = job_dir / "sys"
    work.mkdir(parents=True, exist_ok=False)
    (work / "compiler-input.txt").write_bytes(INPUT)
    prefix, hp = "t000", "h000"
    object_names, sources = [], []
    object_profiles = trial.get("object_profiles") or [profile] * len(objects)
    for obj, object_profile in zip(objects, object_profiles):
        name = prefix if obj["label"] == "candidate" else prefix + "_" + obj["label"]
        object_names.append(name)
        (work / (name + ".c")).write_text(obj["source"], encoding="ascii", newline="\n")
        sources.append((name, object_profile))
    (work / (hp + ".c")).write_text(harness, encoding="ascii", newline="\n")
    sources.append((hp, profile))
    steps = []
    try:
        for name, source_profile in sources:
            trace = job_dir / (name + "-cc.trace.log")
            try:
                steps.extend(_c_compile(work, name, source_profile, toolchain, vamos, sysroot, trace))
            except VamosFailure as exc:
                reason = str(exc)
                attempt = {"job": job_id, "outcome": "FALLBACK", "reason": reason,
                           "trace": trace.relative_to(job_dir).as_posix() if trace.exists() else None}
                write_json(job_dir / "result.json", dict(schema_version=1, backend="vamos",
                    outcome="FALLBACK", reason=reason,
                    trace_math_libraries=trace_math_libraries(trace.read_bytes() if trace.exists() else b""),
                    runtime=runtime_spec))
                return None, reason, attempt
        proxy_args = []
        for proxy_index, proxy in enumerate(proxies):
            name = "p000_%02d" % proxy_index
            (work / (name + ".c")).write_text(proxy["source"], encoding="ascii", newline="\n")
            trace = job_dir / (name + "-cc.trace.log")
            steps.extend(_c_compile(work, name, profile, toolchain, vamos, sysroot, trace))
            proxy_args += [f"+o{proxy['node']}", name + ".o"]

        from mixed_object_dependencies import stage as stage_mixed
        from reconstructed_asm_dependencies import stage as stage_asm
        object_names += stage_mixed(trial, work, prefix)
        object_names += stage_asm(trial, work, prefix)
        node = trial.get("target_node", 1)
        guest = compiler_oracle.PROFILES[profile]["guest"]
        command, argument_file = link_line.plan(guest, prefix, hp, node, object_names, proxy_args, meta)
        require((argument_file is not None) == ("link_argument_file" in meta),
                "link argument-file decision differs from the cache identity")
        if argument_file is not None:
            (work / argument_file[0]).write_text(argument_file[1], encoding="ascii", newline="\n")
        link_guest, link_args = link_guest_command(command)
        link_step = _run_guest(vamos, sysroot, toolchain, work, link_guest, link_args,
                               work / (prefix + "-ln.log"))
        steps.append(link_step)
        if not (work / (prefix + ".exe")).is_file():
            raise VamosFailure("ln returned zero without emitting the linked executable")

        dest = compiler_oracle.CACHE / key
        require(not dest.exists(), "vamos cache destination appeared during execution")
        dest.mkdir(parents=True)
        try:
            _copy_trial_artifacts(work, dest, prefix, hp, 0)
            receipt = dict(cache_key=key, identity=meta, status="COMPILED", guest_returncodes=[0] * len(steps),
                worker_job=(job_dir.relative_to(ROOT).as_posix()), worker_receipt_sha256="",
                prefix=prefix, noninteractive_input_sha256=sha256(INPUT), backend="vamos",
                backend_attempts=[dict(backend="vamos", outcome="COMPILED")])
            receipt["contribution"] = compiler_oracle.extract(
                dest, prefix, meta.get("object_labels"), trial.get("entry_function", "recovered"),
                meta.get("same_overlay_exports"),
                **({"resident_data_interfaces": meta["resident_data_interfaces"]}
                   if "resident_data_interfaces" in meta else {}),
                **({"resident": True} if "resident_object_extractor_sha256" in meta else {}))
            if trial.get("mixed_object_dependencies"):
                from mixed_object_dependencies import validate_linked
                validate_linked(dict(receipt, directory=str(dest)))
            worker_result = dict(schema_version=1, backend="vamos", outcome="COMPILED",
                job=job_id, toolchain_inventory_sha256=runtime_spec["tree_inventory"]["sha256"],
                steps=steps, artifacts=[dict(path=path.relative_to(work).as_posix(),
                    size=path.stat().st_size, sha256=sha256(path.read_bytes()))
                    for path in sorted(work.iterdir()) if path.is_file()])
            write_json(job_dir / "result.json", worker_result)
            receipt["worker_receipt_sha256"] = sha256((job_dir / "result.json").read_bytes())
            receipt["artifacts"] = [dict(path=path.name, size=path.stat().st_size,
                sha256=sha256(path.read_bytes())) for path in sorted(dest.iterdir()) if path.is_file()]
            write_json(dest / "receipt.json", receipt)
        except Exception:
            shutil.rmtree(dest, ignore_errors=True)
            raise
        result = compiler_oracle.cached(key)
        require(result is not None, "vamos output did not produce a valid cache entry")
        return result, None, dict(job=job_id, outcome="COMPILED")
    except Exception as exc:
        attempt = {"job": job_id, "outcome": "FALLBACK", "reason": str(exc)}
        write_json(job_dir / "result.json", dict(schema_version=1, backend="vamos",
            outcome="FALLBACK", reason=str(exc), steps=steps))
        return None, str(exc), attempt


def _legacy_batch(trials):
    if any(t.get("reconstructed_asm_dependencies") or t.get("mixed_object_dependencies") or
           t.get("object_profiles") for t in trials):
        from queued_oracle import compile_many
        return compile_many(trials)
    return compiler_oracle.compile_many(trials)


def compile_many(trials, legacy_compile_many=None):
    """Compile eligible misses with vamos and retry every routed/failed row on WinUAE."""
    trials = list(trials)
    legacy_compile_many = legacy_compile_many or _legacy_batch
    results = [None] * len(trials)
    keys = []
    fallback = []
    attempts = {}
    unique = {}
    for index, trial in enumerate(trials):
        try:
            from compile_queue import trial_key
            key = trial_key(trial)
            keys.append(key)
            cached = compiler_oracle.cached(key)
            if cached is not None:
                results[index] = cached
                continue
            unique.setdefault(key, (index, trial))
        except Exception as exc:
            keys.append(None)
            fallback.append((index, trial, None, "identity:" + str(exc)))

    def run_one(pair):
        key, (index, trial) = pair
        try:
            outcome = _compile_vamos_trial(trial, key, index)
        except Exception as exc:
            # Admission, workdir setup, emulator launch and receipt failures all
            # remain retryable through the established WinUAE oracle.
            outcome = (None, "vamos-executor:" + str(exc), None)
        return key, index, outcome

    if unique:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(worker_count(), len(unique))) as pool:
            for key, index, (compiled, reason, attempt) in pool.map(run_one, unique.items()):
                if attempt:
                    attempts[key] = attempt
                if compiled is not None:
                    results[index] = compiled
                else:
                    fallback.append((index, unique[key][1], key, reason or "vamos-failed"))

    if fallback:
        fallback_results = legacy_compile_many([row[1] for row in fallback])
        if fallback_results is None:
            return results
        for (index, _trial, key, reason), result in zip(fallback, fallback_results):
            results[index] = result
            if key:
                from compile_queue import write_backend_receipt
                attempt = attempts.get(key)
                write_backend_receipt(key, "winuae", [
                    dict(backend="vamos", outcome="FALLBACK", reason=reason,
                         job=attempt.get("job") if attempt else None),
                    dict(backend="winuae", outcome=result.get("status", "COMPILED"))])

    by_key = {}
    for index, key in enumerate(keys):
        if key is not None:
            by_key[key] = results[index]
    return [by_key[key] if key is not None else results[index] for index, key in enumerate(keys)]
