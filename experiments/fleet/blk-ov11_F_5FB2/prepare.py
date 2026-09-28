import json
from pathlib import Path
root = Path('experiments/fleet/blk-ov11_F_5FB2')
source = Path('experiments/worker-ffp-link/ov11_F_5FB2.c').read_text(encoding='utf-8')
(root / 'ffp-lowering.c').write_text(source, encoding='utf-8', newline='')
manifest = {
  'schema_version': 2,
  'function_id': 'ov11_F_5FB2',
  'budget': {'max_variants': 1, 'max_unique_compiles': 1},
  'variants': [{
    'id': 'native-ffp-lowering',
    'causal_family': 'ffp_helper_register_abi',
    'diagnostic_scope': 'call_target_or_encoding',
    'source': str(root / 'ffp-lowering.c').replace('\\', '/'),
    'profile': 'aztec36',
    'parent': 'recovery/candidates/ov11_F_5FB2/092de8e0061c20c4e1f074d1c7172e0443ae434872164bb1bd5cba465bac4eec.c',
    'suspected_cause': 'The resident D0/D1 calls are private Aztec FFP helpers selected by C floating-point lowering, not ordinary source-visible register-call APIs.',
    'controlled_change': 'Replace the explicit F_h00_8Dxx call model and integer expression with native float arithmetic so Aztec emits its private FFP helper sequence.',
    'predicted_effect': {
      'length_delta': None,
      'removed_candidate_only': None,
      'register_role_diffs': 'same',
      'note': 'Expected the native FFP helper sequence to preserve the 206-byte body and bind the seven helper sites to the resident F_8Dxx A4 gates; the parent pragma candidate did not compile, so parent-relative role measurement may be unavailable.'
    }
  }]
}
(root / 'manifest-01.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('wrote', root / 'ffp-lowering.c')
print('wrote', root / 'manifest-01.json')
