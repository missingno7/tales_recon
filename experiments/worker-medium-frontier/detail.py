import json
from pathlib import Path

ledger = json.loads(Path("evidence/functions/ledger.json").read_text(encoding="utf-8"))
ranked = json.loads(Path("evidence/functions/ranking.json").read_text(encoding="utf-8"))["candidates"]
funcs = ledger["functions"]
by_id = {f["id"]: f for f in funcs}
rank_by = {f["id"]: f for f in ranked}

for fid in ("ov04_F_149C", "ov04_F_1822", "ov11_F_27CC", "ov11_F_25D6", "ov11_F_25F8", "ov11_F_262E"):
    f = by_id[fid]
    print("FUNCTION", fid, "range", f["start"], f["end"], "size", f["size"], "rank", rank_by.get(fid))
    if fid == "ov04_F_149C":
        print("STRINGS", [(s["offset"], s["text"], s["confidence"]) for s in f["referenced_strings"]])
        print("NEXT", [(x["id"], x["start"], x["size"]) for x in funcs if x["hunk"] == f["hunk"] and x["start"] >= f["end"]][:5])
    if fid == "ov11_F_27CC":
        print("CALLEES", [(c["id"], c["basis"], c.get("offset"), c.get("site")) for c in f["direct_callees"]])
