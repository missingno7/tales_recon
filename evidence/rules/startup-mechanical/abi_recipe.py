from common import require

def abi_views(base):
    source=base['candidate']
    edits=[('register struct Process *pp, *F_h00_8964();','register struct Process *pp;\n\tlong F_h00_8964();'),
     ('void *_OpenLibrary(), *F_h00_899C(), *F_h00_892A();','void *_OpenLibrary();\n\tlong F_h00_899C(), F_h00_892A();'),
     ('G_h01_B3A6 = F_h00_892A(','G_h01_B3A6 = (struct _dev *)F_h00_892A('),
     ('pp = F_h00_8964(','pp = (struct Process *)F_h00_8964('),
     ('G_h01_B3B0 = F_h00_899C(','G_h01_B3B0 = (struct WBStartup *)F_h00_899C(')]
    for before,after in edits:
        require(source.count(before)==1,'ABI view selection differs: '+before)
        source=source.replace(before,after)
    marked=source.replace('#asm\n','#asm\n\tpublic _startup_asm_begin\n_startup_asm_begin:\n',1).replace('#endasm','\tpublic _startup_asm_end\n_startup_asm_end:\n#endasm',1)
    root=base['root']
    for before,after in [('void * F_h00_892A','long F_h00_892A'),('void * F_h00_899C','long F_h00_899C'),('struct Process * F_h00_8964','long F_h00_8964')]:
        require(root.count(before)==1,'root ABI definition differs');root=root.replace(before,after)
    return dict(candidate=source, marked=marked, root=root, overlay=base['overlay'])
