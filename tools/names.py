"""Token-level spelling bridge for recovery/names.json; proofs use mechanical text.

Exclusions are identities detected in the unrenamed source, not a second name
registry. They must stay fixed after a rename (including in a fresh process).
"""
from functools import lru_cache
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SUFFIXES = frozenset(('.c', '.h', '.asm'))
IDENTIFIER = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\Z')
C_KEYWORDS = frozenset(('auto break case char const continue default do double else enum extern float '
    'for goto if int long register return short signed sizeof static struct switch typedef union '
    'unsigned void volatile while inline restrict _Alignas _Alignof _Atomic _Bool _Complex '
    '_Generic _Imaginary _Noreturn _Static_assert _Thread_local alignas alignof bool constexpr '
    'false nullptr static_assert thread_local true typeof typeof_unqual _BitInt').split())
# Pre-existing tokens (including comments), measured before enabling renames.
EXCLUDED = frozenset(('resident_F_75D8', 'resident_F_8690', 'resident_F_86C0',
    'resident_F_86E0', 'resident_F_86EE', 'resident_F_897C',
    'resident_F_89D0'))
# Comments precede literals so apostrophes/quotes in prose do not hide tokens.
TOKENS = re.compile(r"""/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|(?<![A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*""", re.S)
WORDS = re.compile(r'(?<![A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*(?![A-Za-z0-9_])')


def mechanical(key):
    if key.startswith('G_'):
        if not re.fullmatch(r'G_h[0-9]{2}_[0-9A-F]{4}', key):
            raise ValueError('invalid global identity: ' + key)
        return key
    match = re.fullmatch(r'(resident|ov([0-9]{2}))_F_([0-9A-F]{4})', key)
    if not match:
        raise ValueError('invalid function identity: ' + key)
    return 'F_h%s_%s' % (match[2] or '00', match[3])


@lru_cache(maxsize=None)
def load_registry(root=None):
    path = Path(root or ROOT) / 'recovery/names.json'
    if not path.exists():
        return {}
    document = json.loads(path.read_bytes())
    if document.get('schema_version') != 1:
        raise ValueError('unsupported names.json schema')
    entries = {}
    seen = {}
    for kind in ('functions', 'globals'):
        for key, row in document[kind].items():
            symbol, name = mechanical(key), row['name']
            if not IDENTIFIER.fullmatch(name) or name in C_KEYWORDS:
                raise ValueError('invalid readable name for %s: %s' % (key, name))
            for token in (symbol, '_' + symbol, name, '_' + name):
                if token in seen and seen[token] != key:
                    raise ValueError('name collision: %s (%s, %s)' % (token, seen[token], key))
                seen[token] = key
            entries[key] = name
    # Also reject a readable name that steals an unmapped mechanical identity.
    for key, name in entries.items():
        if re.fullmatch(r'_?[FG]_h[0-9]{2}_[0-9A-F]{4}', name):
            raise ValueError('readable name is mechanical: ' + key)
    return entries


@lru_cache(maxsize=None)
def _maps(root=None):
    forward = {}
    for key, name in load_registry(root).items():
        if key in EXCLUDED:
            continue
        symbol = mechanical(key)
        forward.update({symbol: name, '_' + symbol: '_' + name})
    return forward, {value: key for key, value in forward.items()}


def translate(text, mapping):
    """Preserve every byte, including line endings and non-ASCII source text."""
    binary = isinstance(text, bytes)
    if binary:
        text = text.decode('latin-1')
    def replace(match):
        token = match[0]
        if token.startswith(('/*', '//')):
            return WORDS.sub(lambda m: mapping.get(m[0], m[0]), token)
        return mapping.get(token, token)
    result = TOKENS.sub(replace, text)
    return result.encode('latin-1') if binary else result


def to_mechanical(text, root=None):
    return translate(text, _maps(root)[1])


def to_readable(text, root=None):
    return translate(text, _maps(root)[0])


def identity(token, root=None):
    """Return a token's mechanical C spelling (including an ABI underscore)."""
    return _maps(root)[1].get(token, token)
