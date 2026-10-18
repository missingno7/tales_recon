"""Rename reviewed functions/globals in src; dry run unless --apply is given."""
import argparse
from pathlib import Path
import sys

import names
from repo_paths import active_files

ROOT = Path(__file__).resolve().parents[1]


def rename(root=ROOT, only=None, apply=False):
    root = Path(root)
    entries = names.load_registry(root)
    selected = set(entries if only is None else only)
    unknown = selected - entries.keys()
    if unknown:
        raise ValueError('unknown identities: ' + ', '.join(sorted(unknown)))
    for key in sorted(selected & names.EXCLUDED):
        print('EXCLUDED %s (%s): pre-existing src token' % (key, entries[key]))
    selected -= names.EXCLUDED
    mapping = {}
    for key in sorted(selected):
        symbol, readable = names.mechanical(key), entries[key]
        mapping.update({symbol: readable, '_' + symbol: '_' + readable})
    files = {p: p.read_bytes() for p in active_files(root / 'src')
             if p.suffix in names.SOURCE_SUFFIXES}
    # The lexer includes comments but excludes actual string/character literals.
    tokens = set()
    for raw in files.values():
        for match in names.TOKENS.finditer(raw.decode('latin-1')):
            token = match[0]
            if token.startswith(('/*', '//')):
                tokens.update(names.WORDS.findall(token))
            elif names.IDENTIFIER.fullmatch(token):
                tokens.add(token)
    collisions = tokens & set(mapping.values())
    if collisions:
        raise ValueError('readable names already occur in src: ' + ', '.join(sorted(collisions)))
    changes = {p: names.translate(raw, mapping) for p, raw in files.items()}
    changes = {p: raw for p, raw in changes.items() if raw != files[p]}
    for path in sorted(changes):
        print(('%s ' % ('RENAME' if apply else 'WOULD RENAME')) + path.relative_to(root).as_posix())
    if apply:
        # Use the complete registry inverse, not merely the selected subset.
        try:
            for path, raw in changes.items():
                path.write_bytes(raw)
            for path in changes:
                if names.to_mechanical(path.read_bytes(), root) != files[path]:
                    raise ValueError('normalization changed source bytes: ' + str(path))
        except BaseException:
            for path in changes:
                path.write_bytes(files[path])
            raise
    print('%d files %s' % (len(changes), 'renamed and verified' if apply else 'would change'))
    return changes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--only', nargs='+', metavar='ID')
    args = parser.parse_args(argv)
    try:
        rename(only=args.only, apply=args.apply)
    except (OSError, ValueError) as exc:
        print('REFUSED: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
