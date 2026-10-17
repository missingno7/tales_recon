"""One publisher entry point: promote.py CLASS MANIFEST [--verify-only].

Class-specific validators and publishers retain their existing regression,
unchanged-input and transaction checks. This command grants no new proof level.
Function and unit checker CLIs remain available for candidate development.

MANIFEST uses the existing batch format for functions, ASM, DATA and CODE data;
behavioral uses [{id, source, profile}]. Complete C uses {id}; mixed objects use
{kind: exit|startup, validation_inputs, regression_log}, retaining their existing
publisher's evidence requirements. Without --verify-only this command publishes.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from acceptance import REGISTRY, proof_class
from common import FormatError, require

ROOT = Path(__file__).resolve().parents[1]


def dispatch(name, manifest, verify_only=False):
    entry = proof_class(name)
    mode = '--verify-only' if verify_only else '--promote'
    if entry.name == 'functions':
        args = [str(manifest)] + (['--verify-only'] if verify_only else [])
    elif entry.name in ('asm', 'code_data'):
        args = ['--manifest', str(manifest), mode]
    elif entry.name == 'data':
        # Several DATA manifests share one publisher run: one gate, one publish.
        args = [a for m in (manifest if isinstance(manifest, list) else [manifest]) for a in ('--manifest', str(m))]
        args += ['--verify-only'] if verify_only else []
    elif entry.name == 'behavioral':
        if verify_only:
            import behavioral
            requests = json.loads(Path(manifest).read_bytes())
            require(isinstance(requests, list) and requests, 'behavioral manifest must be a nonempty request list')
            results = [behavioral.check(r['id'], r['source'], r.get('profile', 'aztec36')) for r in requests]
            require(all(r.get('verdict') == 'BEHAVIORAL_EQUAL' for r in results), 'behavioral verification failed')
            print(json.dumps(dict(verdict='BEHAVIORAL_EQUAL', source_acceptance=False, items=results), default=str))
            return 0
        args = ['--promote', str(manifest)]
    elif entry.name == 'dead_code':
        # The existing publisher admits one complete object atomically. A list
        # would invent a multi-object transaction that it does not provide.
        request = json.loads(Path(manifest).read_bytes())
        require(isinstance(request, dict) and set(request) == {'id'} and isinstance(request['id'], str),
                'complete-C manifest must contain exactly one id')
        args = [request['id'], '--isolated' if verify_only else '--promote']
    elif entry.name == 'mixed':
        request = json.loads(Path(manifest).read_bytes())
        require(isinstance(request, dict) and request.get('kind') in ('exit', 'startup') and
                set(request) <= {'kind', 'validation_inputs', 'regression_log'} and
                all(isinstance(v,str) for v in request.values()), 'mixed publisher manifest')
        publisher = 'promote_mixed' if request['kind'] == 'exit' else 'promote_startup'
        args = ['--verify-only'] if verify_only else []
        for key in ('validation_inputs', 'regression_log'):
            if key in request:
                args.extend(['--' + key.replace('_', '-'), request[key]])
        return subprocess.run([sys.executable, str(ROOT/'tools'/(publisher+'.py')), *args]).returncode
    else:
        raise FormatError('proof class has no publisher: ' + entry.name)
    return subprocess.run([sys.executable, str(ROOT/'tools'/(entry.publisher+'.py')), *args]).returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('proof_class', metavar='CLASS', help=', '.join(c.name for c in REGISTRY))
    parser.add_argument('manifests', metavar='MANIFEST', nargs='+',
                        help='one or more batch manifests, published in order')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args(argv)
    entry = proof_class(args.proof_class)
    if entry.name == 'data':
        # One publisher run for all pending DATA manifests: the regression gate and
        # the evidence refresh run once per call, not once per manifest.
        pending = [m for m in args.manifests if args.verify_only or not published(entry, m)]
        for skipped in sorted(set(args.manifests) - set(pending)):
            print('SKIP (already published): ' + skipped)
        if not pending:
            return 0
        code = dispatch(args.proof_class, pending, args.verify_only)
        return refresh() if code == 0 and not args.verify_only else code
    for manifest in args.manifests:
        # Resumable: a manifest already in the ledger is skipped, so the same
        # command continues after an interruption instead of failing.
        if not args.verify_only and published(entry, manifest):
            print('SKIP (already published): ' + manifest)
            continue
        code = dispatch(args.proof_class, manifest, args.verify_only)
        if code == 0 and not args.verify_only:
            code = refresh()
        if code:
            return code
    return 0


def published(entry, manifest):
    """True when every member of a fact-list manifest is in the ledger.

    Only fact-list manifests (DATA, ASM, CODE data) are recognized; a partially
    published manifest is an error, never a silent skip."""
    document = json.loads(Path(manifest).read_bytes())
    facts = document.get('facts') if isinstance(document, dict) else None
    if not isinstance(facts, list) or not facts:
        return False
    ids = [json.loads((ROOT / name).read_bytes())['id'] for name in facts]
    ledger = json.loads((ROOT / 'recovery/ledger.json').read_bytes()).get(entry.ledger_map, {})
    present = [i in ledger for i in ids]
    require(all(present) or not any(present),
            'manifest is partially published: ' + str(manifest) + '; inspect the ledger before retrying')
    return all(present)


# A publish changes canonical inputs; the next gate's canonical tier checks the
# generated evidence, so regenerate it here instead of leaving it stale between
# batches.
REFRESH = (('type_evidence.py', '--write'), ('census.py', '--write'), ('hybrid_image.py', '--write'))


def refresh():
    for script, flag in REFRESH:
        code = subprocess.run([sys.executable, str(ROOT/'tools'/script), flag]).returncode
        if code:
            print('BLOCKED: published, but ' + script + ' ' + flag + ' failed', file=sys.stderr)
            return code
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (FormatError, OSError, ValueError, KeyError) as exc:
        print('BLOCKED: ' + str(exc), file=sys.stderr)
        sys.exit(2)
