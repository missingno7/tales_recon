import json
from pathlib import Path

root = Path("experiments/fleet/reg-ov11_4790-5CEA")
result_path = root / "result.json"
result = json.loads(result_path.read_text(encoding="utf-8"))
ledger = [json.loads(line) for line in (root / "hypotheses.jsonl").read_text(encoding="utf-8").splitlines()]

outcomes = {
    "h24-487e-rederived-cfg-source": "partial",
    "h25-487e-cfg-step-branch-order": "partial",
    "h26-4ec6-byte-offset-word-arrays": "partial",
    "h27": "confirmed",
    "h28": "partial",
    "h29": "confirmed",
    "h30": "partial",
    "h31": "refuted",
    "h32": "partial",
    "h33": "refuted",
    "h34": "refuted",
    "h35": "partial",
    "h36": "confirmed",
    "h37": "partial",
    "h38": "refuted",
    "h39": "confirmed",
    "h40": "refuted",
    "h41": "refuted",
    "h42": "unmeasurable",
    "h43": "partial",
    "h44": "partial",
    "h45": "refuted",
    "h46": "refuted",
    "h47": "refuted",
}
keys = {
    "h24-487e-rederived-cfg-source": "8a691130",
    "h25-487e-cfg-step-branch-order": "dc8dd47",
    "h26-4ec6-byte-offset-word-arrays": "67eef540",
    "h27": "fb7f2839",
    "h28": "d0f5d354",
    "h29": "9dd5e391",
    "h30": "4828fea3",
    "h31": "3bd099e6",
    "h32": "8f5955a4",
    "h33": "91c72395",
    "h34": "d501377c",
    "h35": "17b7f99f",
    "h36": "6ebc18db",
    "h37": "3993fd98",
    "h38": "9c43b751",
    "h39": "0fee7d66",
    "h40": "9950c12a",
    "h41": "e2447373",
    "h42": "40bddb77",
    "h43": "2203ceb8",
    "h44": "f814b539",
    "h45": "7f625229",
    "h46": "03bde3a5",
    "h47": "36070652",
}
observations = {
    "h24-487e-rederived-cfg-source": "F487E 338 bytes (+2), 13 paired coarse blocks versus 9 before rewrite; still differs.",
    "h25-487e-cfg-step-branch-order": "F487E 344 bytes (+8), 97 paired instructions and similarity 0.9223; still differs.",
    "h26-4ec6-byte-offset-word-arrays": "F4EC6 reached target extent 420 bytes but local-frame instruction differences remained.",
    "h27": "F4EC6 became same_after_reference_identity and was frozen.",
    "h28": "F51C0 reached 824 bytes but alignment worsened to 66/57 unpaired and similarity 0.637.",
    "h29": "F487E reached 336 bytes; prediction confirmed, but 4/4 instructions remained unpaired.",
    "h30": "F487E 342 bytes, 2/3 unpaired, similarity 0.9557; partial improvement.",
    "h31": "F487E remained 342 bytes with the same 2/3 unpaired; declaration swap did not help.",
    "h32": "F487E 340 bytes, 1/1 unpaired and similarity 0.9901; best F487E source remains this branch's source.",
    "h33": "F487E shrank to 334 bytes but worsened to 4/2 unpaired and similarity 0.96.",
    "h34": "F51C0 fell to 810 bytes and similarity 0.5914 after the speculative success-body replacement.",
    "h35": "F55B8 row-bound change did not materially improve its block alignment; size 616 bytes.",
    "h36": "F55B8 reached 624 bytes and similarity 0.7159 after parity expression change.",
    "h37": "Fresh F55B8 rewrite reduced unpaired instructions to 10/7 and raised similarity to 0.9183, at 624 bytes.",
    "h38": "F55B8 coordinate-field swap worsened alignment to 12/9 unpaired, with no extent change.",
    "h39": "F55B8 byte-based record indexing reached 612 bytes and reduced actual-only instructions to 1; expected-only remained 10.",
    "h40": "F55B8 field declaration swap kept 612 bytes and the 10/1 unpaired counts.",
    "h41": "F487E conditional inversion worsened to 4/4 unpaired and similarity 0.9406.",
    "h42": "Compilation returned COMPILE_ERROR; no member measurement was available.",
    "h43": "F51C0 expected global updates at offsets 474-490 paired, but extent rose to 846 bytes and similarity fell to 0.5809.",
    "h44": "F51C0 stayed 846 bytes; unpaired counts improved slightly to 82/75 but prediction of 824-834 bytes was false.",
    "h45": "F487E became 324 bytes (-12) with 8/3 unpaired and similarity 0.8934.",
    "h46": "F55B8 became 614 bytes (-28) with 10/2 unpaired; entry-guard prediction was not met.",
    "h47": "F487E remained 340 bytes (+4), 1/1 unpaired; local declaration reordering had no effect.",
}
for hypothesis in ledger[23:]:
    hid = hypothesis["id"]
    result["hypotheses"].append({
        "id": hid,
        "statement": hypothesis["suspected_cause"] + " Controlled change: " + hypothesis["controlled_change"] + " Prediction: " + hypothesis["prediction"],
        "outcome": outcomes[hid],
        "evidence": "unit_diag/receipt cache " + keys[hid] + ": " + observations[hid],
    })

result.update({
    "schema_version": 1,
    "task_id": "reg-ov11_4790-5CEA",
    "worker": "luna-reg-ov11-r5",
    "status": "NEAR",
    "target": "ov11_F_487E,ov11_F_4EC6,ov11_F_51C0,ov11_F_54F8,ov11_F_55B8,ov11_F_583A,ov11_F_5962,ov11_F_5C42",
    "compile_trials": 40,
    "ledger_lines": list(range(1, len(ledger) + 1)),
    "explanation": "The best complete-unit run is v32 (cache 0fee7d66...). Five of eight new members are EQUAL or same_after_reference_identity: 4EC6, 54F8, 583A, 5962, and 5C42. F487E remains +4 bytes (340 vs 336; 1/1 unpaired, similarity 0.9901), F51C0 remains -12 (812 vs 824; 56/41 unpaired, similarity 0.6411), and F55B8 remains -30 (612 vs 642; 10/1 unpaired, similarity 0.9341). The 44-byte gap remains unclaimed and all 12 crossing encodings are GAP_INDEPENDENT_ENCODING. The exact complete-unit verdict is DIFFER, 7200 vs 7198 bytes. All 40 trials are exhausted.",
    "proposed_blocker": None,
})
result["best"] = {
    "source": "experiments/fleet/reg-ov11_4790-5CEA/v32/ov11_F_487E.c",
    "profile": "aztec36",
    "cache_key": "0fee7d66ddd5df3e357e0fe8c5509e482cfba4fcffa364f693babe428ccb2cc6",
    "verdict": "DIFFER",
    "verifier": "check_unit",
    "entry": "ov11_F_487E",
    "options": ["separate_objects", "natural_interval"],
    "expected_length": 7198,
    "actual_length": 7200,
    "members": {
        "ov11_F_4EC6": "experiments/fleet/reg-ov11_4790-5CEA/v32/ov11_F_4EC6.c",
        "ov11_F_51C0": "experiments/fleet/reg-ov11_4790-5CEA/v32/ov11_F_51C0.c",
        "ov11_F_54F8": "experiments/fleet/reg-ov11_4790-5CEA/v32/ov11_F_54F8.c",
        "ov11_F_55B8": "experiments/fleet/reg-ov11_4790-5CEA/v32/ov11_F_55B8.c",
        "ov11_F_583A": "experiments/fleet/reg-ov11_4790-5CEA/v32/ov11_F_583A.c",
        "ov11_F_5962": "experiments/fleet/reg-ov11_4790-5CEA/v32/ov11_F_5962.c",
        "ov11_F_5C42": "experiments/fleet/reg-ov11_4790-5CEA/v32/ov11_F_5C42.c",
    },
    "object_groups": [["ov11_F_583A", "ov11_F_5962"]],
}
result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", result_path, "hypotheses", len(result["hypotheses"]), "trials", result["compile_trials"])

