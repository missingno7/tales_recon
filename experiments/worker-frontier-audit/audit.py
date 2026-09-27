import json
from collections import Counter, defaultdict
from pathlib import Path


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


ranking = load("evidence/functions/ranking.json")["candidates"]
ledger = load("evidence/functions/ledger.json")
recovery = load("recovery/ledger.json")
functions = {f["id"]: f for f in ledger["functions"]}
canonical = set(recovery.get("functions", {}))
runtime = {f["id"] for f in ledger["functions"] if f.get("ownership") == "RUNTIME_CANDIDATE"}
cohort = [x for x in ranking if x["extent"] == "CLOSED_CFG" and x["size"] <= 256 and x["node"] != "resident"]


def gates(x):
    return {
        "low_confidence": x.get("confidence", "HIGH") != "HIGH",
        "indirect_control_flow": x.get("indirect", 0) != 0,
        "unknown_call_limit": x.get("unknown_calls", 0) > 1,
        "pc_relative_data": x.get("pc_relative_data", 0) != 0,
        "data_reference_limit": x.get("data_references", 0) > 40,
        "pending_local_dependency": bool(x.get("pending_local_dependencies")),
        "noncontiguous_local_unit": not x.get("same_node_unit_ready", True),
    }


def admitted(x):
    return not any(gates(x).values())


print("ranked_total", len(ranking))
print("closed_cfg_le_256_overlay", len(cohort))
print("ranked_overlays", Counter(x["node"] for x in ranking if x["node"] != "resident"))
print("admitted_by_all_current_gates", sum(admitted(x) for x in cohort))
print("admitted_nonblocked", [x["id"] for x in cohort if admitted(x) and x["state"] != "BLOCKED"])
print("gate_hits_nonexclusive", Counter(k for x in cohort for k, v in gates(x).items() if v))
print("first_deferral_reason", Counter(next((k for k, v in gates(x).items() if v), "ADMITTED") for x in cohort))
print("states_in_cohort", Counter(x["state"] for x in cohort))
print("overlap_patterns", Counter(tuple(k for k, v in gates(x).items() if v) or ("ADMITTED",) for x in cohort))

a4_calls = Counter()
a4_globals = Counter()
a4_writes = Counter()
unknown_targets = Counter()
for x in cohort:
    f = functions[x["id"]]
    a4_calls[x["id"]] = sum(c["basis"] == "A4_RELOCATED_JMP_STUB" for c in f["direct_callees"])
    a4_globals[x["id"]] = sum(r["kind"] == "A4_RELATIVE" for r in f["referenced_data"])
    for c in f["direct_callees"]:
        if c["basis"] != "A4_RELOCATED_JMP_STUB" and c["id"] not in canonical and c["id"] not in runtime:
            unknown_targets[c["id"]] += 1
    for i in f["instructions"]:
        mnemonic, operands = i["mnemonic"].lower(), i["operands"].lower().replace(" ", "")
        if operands.endswith(",a4") or (mnemonic.startswith(("clr", "neg", "not", "ext", "swap", "lsl", "lsr", "asl", "asr", "rol", "ror")) and operands == "a4"):
            a4_writes[x["id"]] += 1
print("a4_relocated_call_candidates", sum(v > 0 for v in a4_calls.values()))
print("a4_relocated_call_sites", sum(a4_calls.values()))
print("a4_relative_data_candidates", sum(v > 0 for v in a4_globals.values()))
print("a4_relative_data_refs", sum(a4_globals.values()))
print("candidate_a4_write_candidates", len(a4_writes))
print("candidate_a4_write_sites", sum(a4_writes.values()))
print("top_unresolved_callee_ids", unknown_targets.most_common(20))

unlockable = defaultdict(list)
for x in cohort:
    g = gates(x)
    deps = x.get("pending_local_dependencies", [])
    if deps and len(deps) == 1 and x.get("same_node_unit_ready", True) and not any(
        value for key, value in g.items() if key != "pending_local_dependency"
    ):
        unlockable[deps[0]].append(x["id"])
print("single_dependency_unlock_groups", sorted(((k, len(v), v) for k, v in unlockable.items()), key=lambda x: (-x[1], x[0])))
dep_frequency = Counter(d for x in cohort for d in x.get("pending_local_dependencies", []))
print("top_local_dependency_frequency", dep_frequency.most_common(20))
for x in sorted(cohort, key=lambda r: r["id"]):
    f = functions[x["id"]]
    print("candidate", x["id"], "span", f["start"], f["end"], "state", x["state"],
          "unknown", x["unknown_calls"], "pcdata", x["pc_relative_data"],
          "deps", x["pending_local_dependencies"], "unit_ready", x["same_node_unit_ready"],
          "same_node_callees", [(c["id"], c["offset"]) for c in f["direct_callees"]
                                if c["basis"] == "PC_RELATIVE" and c["hunk"] == f["hunk"]])
