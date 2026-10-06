from pathlib import Path
import re
from common import require

def source_views(repo_root):
    ROOT = Path(repo_root).resolve()
    sdk_path = ROOT / 'toolchain/installed/aztec-3.6a/SYS2/crt_src/_main.c'
    sdk = sdk_path.read_bytes().decode('ascii').replace('\r\n', '\n')
    includes = '\n'.join(line for line in sdk.splitlines() if line.startswith('#include')) + '\n'
    body = sdk[sdk.index('_main(alen, aptr)'):sdk.index('\n#ifdef DETACH\nextern long')]
    body = body.replace('_main(alen, aptr)', 'recovered(alen, aptr)', 1)
    global_views = [('long','_savsp','B39E'),('long','_stkbase','B3AA'),('int','Enable_Abort','B3AE'),
        ('int','_argc','B3B8'),('int','_arg_len','B3BA'),('char **','_argv','B3B4'),('char *','_arg_lin','B3BC'),
        ('struct WBStartup *','WBenchMsg','B3B0'),('struct _dev *','_devtab','B3A6'),('short','_numdev','2EB0')]
    # Keep original C argument and pointer-return views; these are lab stand-ins.
    calls = {'_AllocMem':35114, 'Alert':34628, '_FindTask':35172, '_cli_parse':30628,
        '_WaitPort':35386, '_GetMsg':35228, '_CurrentDir':34460, '_wb_parse':31524,
        '_Input':34496, '_Output':34542, '_Open':34528, 'exit':34100, 'main':None}
    for old, target in calls.items():
        body = re.sub(r'\b' + re.escape(old) + r'\b', 'F_h03_0000' if target is None else 'F_h00_%04X' % target, body)
    for typ, old, suffix in global_views:
        body = re.sub(r'\b' + re.escape(old) + r'\b', 'G_h01_' + suffix, body)
    body = body.replace('__savsp', '_G_h01_B39E')
    header = ('/* SDK-derived complete mixed startup experiment; original provider/TU unknown. */\n' + includes +
        ''.join('extern ' + typ + ' G_h01_' + suffix + ';\n' for typ, old, suffix in global_views))
    header += 'extern int F_h00_8534();\nextern int F_h03_0000();\n'
    source = header + body
    require(source.count('#asm') == 1, 'unexpected startup assembly count')
    marked = source.replace('#asm\n', '#asm\n\tpublic _startup_asm_begin\n_startup_asm_begin:\n', 1).replace(
        '#endasm', '\tpublic _startup_asm_end\n_startup_asm_end:\n#endasm', 1)
    root = includes + 'extern int recovered();\nint (*candidate_reference)() = recovered;\nmain() { return 0; }\n'
    root += ''.join(typ + ' G_h01_' + suffix + ';\n' for typ, old, suffix in global_views)
    returns = {35114:'void *',35172:'struct Process *',35228:'void *',34496:'long',34542:'long',34528:'long'}
    for target in sorted(set(v for v in calls.values() if v is not None and v != 34100)):
        root += returns.get(target, 'int') + ' F_h00_%04X() { return 0; }\n' % target
    root += ('#asm\n\tdseg\n\tpublic _F_h00_8534\n_F_h00_8534:\n\tdc.w $4ef9\n\tdc.l _exit_body\n\tcseg\n#endasm\n'
             'exit_body() { return 0; }\n')
    overlay = 'F_h03_0000(argc,argv) int argc; char **argv; { return 0; }\n'
    return dict(candidate=source, marked=marked, root=root, overlay=overlay)
