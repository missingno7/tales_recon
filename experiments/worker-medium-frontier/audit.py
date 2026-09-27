import json
from collections import Counter
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


ranked = load("evidence/functions/ranking.json")["candidates"]
evidence = load("evidence/functions/ledger.json")["functions"]
evidence_by_id = {f["id"]: f for f in evidence}
excluded = {"ov04_F_0536", "ov09_F_298E", "ov11_F_4B0C"}
band = [x for x in ranked if x["node"] != "resident" and 256 <= x["size"] <= 768 and x["extent"] == "CLOSED_CFG" and x["id"] not in excluded]
no_pending = [x for x in band if not x.get("pending_local_dependencies")]


def fails(x):
    return [name for name, yes in (
        ("not-high-confidence", x.get("confidence", "HIGH") != "HIGH"),
        ("indirect-control-flow", x.get("indirect", 0) != 0),
        ("unknown-call-limit", x.get("unknown_calls", 0) > 1),
        ("pc-relative-data", x.get("pc_relative_data", 0) != 0),
        ("data-reference-limit", x.get("data_references", 0) > 40),
        ("pending-local-dependency", bool(x.get("pending_local_dependencies"))),
        ("noncontiguous-unit", not x.get("same_node_unit_ready", True)),
    ) if yes]


print("ranked_total", len(ranked))
print("band_256_768_closed_overlay", len(band))
print("band_states", Counter(x["state"] for x in band))
print("no_pending_local_dependency", len(no_pending))
print("strict_gate_pass", [x["id"] for x in no_pending if not fails(x)])
print("failure_patterns", Counter(tuple(fails(x)) or ("PASS",) for x in no_pending))
print("single_gate_passes_or_nearest", sorted((x for x in no_pending), key=lambda x: (len(fails(x)), x["score"]))[:30])

for x in sorted(no_pending, key=lambda x: (len(fails(x)), x["score"]))[:30]:
    f = evidence_by_id[x["id"]]
    calls = [(c["id"], c["basis"], c.get("hunk"), c.get("offset"), c.get("site")) for c in f["direct_callees"]]
    data_kinds = Counter(r["kind"] for r in f["referenced_data"])
    print("DETAIL", x["id"], "size", x["size"], "score", x["score"], "state", x["state"],
          "calls", x["calls"], "unknown", x["unknown_calls"], "data", x["data_references"],
          "pcdata", x["pc_relative_data"], "relocs", len(f["relocations"]), "data_kinds", dict(data_kinds),
          "unit_ready", x["same_node_unit_ready"], "fails", fails(x), "callees", calls,
          "relocations", f["relocations"], "strings", f["referenced_strings"])
