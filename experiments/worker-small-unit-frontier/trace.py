import json
from pathlib import Path

ledger = json.loads(Path("evidence/functions/ledger.json").read_text(encoding="utf-8"))
ranking = json.loads(Path("evidence/functions/ranking.json").read_text(encoding="utf-8"))["candidates"]
rank_by = {x["id"]: x for x in ranking}
functions = {x["id"]: x for x in ledger["functions"]}

for seed in ("ov11_F_2430", "ov11_F_5EC0"):
    root = functions[seed]
    hunk = root["hunk"]
    local = [c for c in root["direct_callees"] if c["basis"] == "PC_RELATIVE" and c["hunk"] == hunk]
    lo = min([root["start"]] + [c["offset"] for c in local])
    hi = max([root["end"]] + [c["offset"] for c in local])
    print("\nSEED", seed, "size", root["size"], "start_end", root["start"], root["end"],
          "rank", rank_by.get(seed), "direct-local-window", lo, hi, hi-lo)
    for c in root["direct_callees"]:
        callee = functions.get(c["id"])
        print(" EDGE", c["id"], "basis", c["basis"], "site", c["site"], "target", c["offset"],
              "callee-size", callee and callee["size"], "callee-range", callee and (callee["start"], callee["end"]),
              "callee-rank", rank_by.get(c["id"], {}).get("state", "not-in-ranked-queue"))

    if seed == "ov11_F_5EC0":
        for fid in ("ov11_F_5962", "ov11_F_5C42", "ov11_F_5D14", "ov11_F_5EC0"):
            f = functions[fid]
            print(" UNIT_EDGES", fid, [(c["id"], c["basis"], c["offset"], c["site"])
                                       for c in f["direct_callees"]])

    # Recursively traverse only same-hunk PC-relative callees that remain
    # pending in the ranked snapshot; report function sizes and cycles.
    seen, stack = set(), [seed]
    edges = []
    while stack:
        fid = stack.pop()
        if fid in seen or fid not in functions:
            continue
        seen.add(fid)
        f = functions[fid]
        for c in f["direct_callees"]:
            if c["basis"] == "PC_RELATIVE" and c["hunk"] == hunk:
                callee = c["id"]
                if callee in rank_by and callee not in seen:
                    edges.append((fid, callee))
                    stack.append(callee)
    print(" TRANSITIVE_PENDING_LOCAL_NODES", sorted((fid, functions[fid]["size"], functions[fid]["start"], functions[fid]["end"], rank_by[fid]["pending_local_dependencies"]) for fid in seen if fid in rank_by))
    print(" TRANSITIVE_PENDING_EDGES", sorted(set(edges)))

    # The entire interval including every discovered function entry needed to
    # preserve the measured natural order; omitted bytes remain a physical gap.
    members = sorted((f for f in ledger["functions"] if f["hunk"] == hunk and lo <= f["start"] and f["end"] <= hi), key=lambda f: f["start"])
    covered = sum(f["size"] for f in members)
    print(" INTERVAL_FUNCTIONS", len(members), "known_bytes", covered, "unassigned_bytes", hi-lo-covered)
    for f in members:
        print("  MEMBER", f["id"], f["start"], f["end"], f["size"], f["extent_status"], f["ownership"],
              rank_by.get(f["id"], {}).get("state", "not-in-ranked-queue"),
              "source", Path("src/recovered/ov11") .joinpath(f["id"] + ".c").exists())
