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



def split_source_ref(ref):
    """A source reference is a path, optionally followed by #C_identifier."""
    path, separator, name = str(ref).partition('#')
    if not path or separator and not IDENTIFIER.fullmatch(name):
        raise ValueError('invalid source reference: ' + str(ref))
    return path, name if separator else None


def source_path(root, ref, *, scratch=False):
    """Validate and resolve the physical file, including module references."""
    from repo_paths import canonical_path, candidate_path
    path, _ = split_source_ref(ref)
    return candidate_path(root, Path(root) / path) if scratch else canonical_path(root, path)


# Modules are readability groups, not object/TU claims. Masking comments and
# literals keeps braces in prose/strings harmless. Support ANSI and K&R headers.
_C_NONCODE = re.compile(r"""/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'""", re.S)
_C_DEFINITION = re.compile(
    r'^[ \t]*(?:(?:[A-Za-z_]\w*)[ \t]+|\*[ \t]*)*?'
    r'([A-Za-z_]\w*)[ \t]*\([^;{}]*\)[ \t\r\n]*'
    r'(?:[A-Za-z_][^{};]*;[ \t\r\n]*)*\{', re.M)


def module_parts(text):
    """Return (shared prefix, {name: commented definition}); refuse ambiguity.

    No preprocessor conditionals or inter-function declarations: everything
    shared must precede the first definition. This is a small source extractor,
    not a C preprocessor. Unsupported shapes fail before exact compilation.
    """
    if re.search(r'^\s*#\s*(?:if|ifdef|ifndef|elif|else|endif)\b', text, re.M):
        raise ValueError('module source conditionals are unsupported')
    masked = _C_NONCODE.sub(lambda m: re.sub(r'[^\r\n]', ' ', m[0]), text)
    headers = {m.end()-1: m for m in _C_DEFINITION.finditer(masked)}
    spans = []; depth = 0; header = None
    for i, char in enumerate(masked):
        if char == '{':
            if depth == 0:
                header = headers.get(i)
                if header and header[1] in C_KEYWORDS:
                    header = None
            depth += 1
        elif char == '}':
            depth -= 1
            if depth < 0:
                raise ValueError('unbalanced module braces')
            if depth == 0 and header:
                start = header.start()
                # Attach immediately preceding comments, never a declaration
                # or a comment separated from the header by a blank line.
                comments = [m for m in _C_NONCODE.finditer(text[:start]) if m[0].startswith(('/*','//'))]
                for comment in reversed(comments):
                    gap = text[comment.end():start]
                    if gap.strip() or gap.count('\n') > 1:
                        break
                    line_start = text.rfind('\n', 0, comment.start()) + 1
                    if text[line_start:comment.start()].strip():
                        break
                    start = line_start
                end = i + 1
                if text[end:end+2] == '\r\n': end += 2
                elif text[end:end+1] == '\n': end += 1
                spans.append((header[1], start, end))
                header = None
    if depth or not spans:
        raise ValueError('unbalanced or missing module definitions')
    parts = {}; cursor = spans[0][1]
    for name, start, end in spans:
        if name in parts:
            raise ValueError('duplicate module definition: ' + name)
        if _C_NONCODE.sub('', text[cursor:start]).strip():
            raise ValueError('declarations between module functions are unsupported')
        parts[name] = text[start:end]
        cursor = end
    if _C_NONCODE.sub('', text[cursor:]).strip():
        raise ValueError('unexpected text after module functions')
    return text[:spans[0][1]], parts


def read_source(root, ref, *, scratch=False):
    """Read a normalized compile unit; plain paths preserve the existing bytes.

    path#name selects shared declarations plus that commented definition only.
    Its own identifier (declarations and recursive calls included) becomes
    recovered; other functions keep their mechanical identities. No source copy
    is retained, and the existing exact compiler/object proof remains the gate.
    """
    _, name = split_source_ref(ref)
    raw = source_path(root, ref, scratch=scratch).read_bytes()
    if name is None:
        return to_mechanical(raw, root)
    shared, parts = module_parts(raw.decode('latin-1'))
    if name not in parts:
        raise ValueError('unknown module function: ' + name)
    unit = to_mechanical((shared + parts[name]).encode('latin-1'), root)
    return translate(unit, {identity(name, root): 'recovered'})



def read_source_text(root, ref, *, scratch=False, encoding='utf-8', errors='strict'):
    """Text-mode adapter for former read_text sites; plain files keep universal newlines."""
    text = read_source(root, ref, scratch=scratch).decode(encoding, errors)
    return text.replace('\r\n', '\n').replace('\r', '\n') if split_source_ref(ref)[1] is None else text
