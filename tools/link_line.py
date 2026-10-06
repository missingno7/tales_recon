"""Guest command line for the Aztec ``ln`` step of the compiler oracle.

The AmigaDOS shell in the worker (Kickstart 3.0 ROM from the pinned archive)
rejects a command whose argument text -- everything after the command name and
its ``<``/``>`` redirections -- exceeds 510 characters: the redirection target is
created empty and the step returns 10 without running the program.  Measured in
worker jobs ``link-limit-001``/``link-limit-002`` (docs/toolchain.json,
``link_command_line_limit``): 510 argument characters linked, 511 failed.

Both Aztec 3.6a and 5.0a ``ln`` read further arguments from ``-f FILE`` (one
level, no nesting).  With identical objects the ``-f`` form produced
byte-identical executables and symbol files to the direct form.  A link whose
direct argument text would exceed ``MAX_DIRECT_ARGUMENT_CHARS`` therefore places
its object/overlay/library list in ``PREFIX-ln.lnk`` beside the objects.

The direct form is byte-for-byte the command the oracle always issued, and the
decision depends only on cache-identity inputs, so every short link keeps its
existing cache identity.  Only argument-file links carry an identity field.
"""
from pathlib import Path

from common import sha256

MAX_DIRECT_ARGUMENT_CHARS = 480  # measured guest limit 510; 30-character margin
ARGUMENT_FILE_MECHANISM = 'ln -f'


def library_args(meta):
    libraries = [f'{meta["library_guest"]}lib/{meta["library"]}']
    libraries.extend(f'{x["library_guest"]}lib/{x["library"]}' for x in meta.get('additional_libraries', []))
    return libraries


def _redirections(prefix):
    return f'<compiler-input.txt >{prefix}-ln.log '


def direct_arguments(prefix, hp, node, object_names, proxy_args, meta):
    """Argument text of the historical single-line form (spacing preserved)."""
    if node == 0:
        args = [hp + '.o'] + [name + '.o' for name in object_names] + list(proxy_args)
        if proxy_args:
            args.append('+o0')
        return f'-m -t -o {prefix}.exe ' + ' '.join(args + library_args(meta))
    return (f'-m -t -o {prefix}.exe {hp}.o +o{node} ' + ' '.join(name + '.o' for name in object_names) + ' ' +
            ' '.join(proxy_args) + ' +o0 ' + ' '.join(library_args(meta)))


def direct_command(guest, prefix, hp, node, object_names, proxy_args, meta):
    """Unchanged single-line link command (formerly ``compiler_oracle.link_command``)."""
    return f'{guest}bin/ln ' + _redirections(prefix) + direct_arguments(prefix, hp, node, object_names, proxy_args, meta)


def uses_argument_file(prefix, hp, node, object_names, proxy_args, meta):
    return len(direct_arguments(prefix, hp, node, object_names, proxy_args, meta)) > MAX_DIRECT_ARGUMENT_CHARS


def argument_file_name(prefix):
    # ``PREFIX-`` names are collected into the trial's cache directory.
    return prefix + '-ln.lnk'


def argument_file_text(hp, node, object_names, proxy_args, meta):
    """One ``ln`` argument per line, in exactly the direct form's order."""
    if node == 0:
        args = [hp + '.o'] + [name + '.o' for name in object_names] + list(proxy_args)
        if proxy_args:
            args.append('+o0')
        return '\n'.join(args + library_args(meta)) + '\n'
    args = [hp + '.o', f'+o{node}'] + [name + '.o' for name in object_names] + list(proxy_args) + ['+o0'] + library_args(meta)
    return '\n'.join(args) + '\n'


def plan(guest, prefix, hp, node, object_names, proxy_args, meta):
    """Return ``(command, argument_file)``; ``argument_file`` is ``None`` or ``(name, text)``."""
    if not uses_argument_file(prefix, hp, node, object_names, proxy_args, meta):
        return direct_command(guest, prefix, hp, node, object_names, proxy_args, meta), None
    name = argument_file_name(prefix)
    command = f'{guest}bin/ln ' + _redirections(prefix) + f'-m -t -o {prefix}.exe -f {name}'
    return command, (name, argument_file_text(hp, node, object_names, proxy_args, meta))


def identity_field(object_labels, proxies, target_node, meta):
    """Cache-identity addition for argument-file links, else ``None``.

    The oracle's per-batch names have fixed width (``t%03d``, ``h%03d``,
    ``p%03d_%02d``), so the decision is evaluated with index 0 and is the same
    in every batch.  Short links return ``None`` and keep their identities.
    """
    names = ['t000' if label == 'candidate' else 't000_' + label for label in object_labels]
    proxy_args = []
    for index, proxy in enumerate(proxies):
        proxy_args += [f'+o{proxy["node"]}', 'p000_%02d.o' % index]
    if not uses_argument_file('t000', 'h000', target_node, names, proxy_args, meta):
        return None
    return dict(mechanism=ARGUMENT_FILE_MECHANISM, max_direct_argument_chars=MAX_DIRECT_ARGUMENT_CHARS,
                builder_sha256=sha256(Path(__file__).read_bytes()))
