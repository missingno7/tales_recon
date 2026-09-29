import json
from pathlib import Path

result = {
    "schema_version": 1,
    "task_id": "fn-ov11_F_2272",
    "worker": "luna-fn-ov11_F_2272",
    "status": "NEAR",
    "target": "ov11_F_2272",
    "best": {
        "source": "experiments/fleet/fn-ov11_F_2272/ov11_F_2272-case-break.c",
        "profile": "aztec36",
        "cache_key": "1e370d66d982cc0853cca05dbaed34d79f7d1f6c17271c13407157da5408473a",
        "verdict": "DIFFER",
        "verifier": "check_function",
        "entry": "ov11_F_2272",
        "options": [],
        "expected_length": 386,
        "actual_length": None,
    },
    "hypotheses": [
        {
            "id": "h1",
            "statement": "Encoding timer states 0 and 1 as a switch is shorter than the measured if/else-if parent.",
            "outcome": "refuted",
            "evidence": "hypothesis-ledger.jsonl line 180: child grew by 8 bytes versus the predicted -2; candidate-only count fell by 2.",
        },
        {
            "id": "h2",
            "statement": "Routing both case-zero exits through switch breaks shares the epilogue and removes inline return instructions.",
            "outcome": "confirmed",
            "evidence": "hypothesis-ledger.jsonl line 182: predicted 0 length delta and 2 fewer candidate-only instructions were measured.",
        },
        {
            "id": "h3",
            "statement": "Alternative positive-guard and local-join control forms may reproduce the oracle branch layout.",
            "outcome": "untested",
            "evidence": "manifest-02.json, manifest-03.json, and manifest-05.json were rejected with natural function ordering/extent differs; no slice accepted.",
        },
        {
            "id": "h4",
            "statement": "A complete natural unit or object grouping can reproduce the short late call to F_h11_2430.",
            "outcome": "unmeasurable",
            "evidence": "check_unit --prepare-only is blocked by unrecovered same-node ov11_F_2EEA; facts-ov11_F_2EEA.json records its 1608-byte closed extent. The compact interval also reports GAP_DEPENDENT_ENCODING.",
        },
    ],
    "compile_trials": 3,
    "ledger_lines": [180, 181, 182],
    "explanation": "The best candidate models the timer dispatch, state cases, hit test, updates, and observed calls; diagnostics bound its entry member at 386 bytes. Exact check_function comparison is DIFFER: the multi-object unit is 3990 bytes versus 3988 expected. Diagnostics leave 47 A4 references layout-only and show the late F_h11_2430 call as JSR where the oracle uses BSR.B. Natural-unit preparation is blocked by unrecovered ov11_F_2EEA (1608 bytes), and the compact interval has GAP_DEPENDENT_ENCODING. Exact source/layout evidence is still missing; no promotion was made.",
    "proposed_blocker": None,
}

out = Path("experiments/fleet/fn-ov11_F_2272/result.json")
with out.open("w", encoding="utf-8", newline="\n") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
    f.write("\n")
