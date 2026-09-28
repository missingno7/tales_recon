import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

import link_line
from compiler_oracle import identity,link_command,object_specs


def legacy_link_command(guest,prefix,hp,node,object_names,proxy_args,meta):
    """Verbatim single-line builder the oracle used before argument files."""
    libraries=[f'{meta["library_guest"]}lib/{meta["library"]}']
    libraries.extend(f'{x["library_guest"]}lib/{x["library"]}' for x in meta.get('additional_libraries',[]))
    return (f'{guest}bin/ln <compiler-input.txt >{prefix}-ln.log -m -t -o {prefix}.exe {hp}.o +o{node} '+
            ' '.join(name+'.o' for name in object_names)+' '+ ' '.join(proxy_args)+' +o0 '+' '.join(libraries))


META=dict(library='c.lib',library_guest='Old1:')
M_LIB=dict(META,additional_libraries=[dict(library='m.lib',library_guest='Old1:',library_sha256='0'*64)])


def names(count):
    return ['t000']+['t000_part%03d'%i for i in range(1,count)]


class LinkLineTests(unittest.TestCase):
    def test_short_form_is_byte_identical_to_legacy_builder(self):
        cases=[('Old1:','t000','h000',1,['t000'],[],META),
               ('Old1:','t017','h017',9,names(7),[],M_LIB),
               ('Tools2:','t003','h003',4,['t003','t003_part001'],['+o2','p003_00.o','+o7','p003_01.o'],META)]
        for case in cases:
            command,argument_file=link_line.plan(*case)
            self.assertIsNone(argument_file)
            self.assertEqual(command,legacy_link_command(*case))
            self.assertEqual(link_command(*case),legacy_link_command(*case))

    def test_threshold_is_on_argument_text_after_redirections(self):
        command=link_line.direct_command('Old1:','t000','h000',9,names(29),[],META)
        arguments=link_line.direct_arguments('t000','h000',9,names(29),[],META)
        self.assertTrue(command.endswith(arguments))
        self.assertEqual(len(command)-len(arguments),len('Old1:bin/ln <compiler-input.txt >t000-ln.log '))
        limit=link_line.MAX_DIRECT_ARGUMENT_CHARS
        self.assertLess(limit,510,'must stay below the measured 510-character guest limit')
        # Pad one proxy argument so the direct argument text hits the limit exactly.
        base=len(link_line.direct_arguments('t000','h000',9,names(20),['+o2','x.o'],META))
        pad='x'*(limit-base+1)+'.o'
        at=['+o2',pad]
        self.assertEqual(len(link_line.direct_arguments('t000','h000',9,names(20),at,META)),limit)
        self.assertIsNone(link_line.plan('Old1:','t000','h000',9,names(20),at,META)[1])
        over=['+o2','x'+pad]
        self.assertIsNotNone(link_line.plan('Old1:','t000','h000',9,names(20),over,META)[1])

    def test_argument_file_content_and_command(self):
        objects=names(33);proxies=['+o3','p005_00.o']
        command,argument_file=link_line.plan('Old1:','t005','h005',9,objects,proxies,M_LIB)
        self.assertEqual(command,'Old1:bin/ln <compiler-input.txt >t005-ln.log -m -t -o t005.exe -f t005-ln.lnk')
        name,text=argument_file
        self.assertEqual(name,'t005-ln.lnk')
        self.assertTrue(name.startswith('t005-'),'argument file must be collected with the trial artifacts')
        lines=text.split('\n')
        self.assertEqual(lines[-1],'')
        self.assertEqual(lines[:-1],['h005.o','+o9']+[x+'.o' for x in objects]+proxies+['+o0','Old1:lib/c.lib','Old1:lib/m.lib'])
        # Same arguments, same order as the direct form would have used.
        self.assertEqual(' '.join(lines[:-1]),
                         link_line.direct_arguments('t005','h005',9,objects,proxies,M_LIB).split(' ',4)[4].replace('  ',' '))
        self.assertTrue(text.isascii() and '\r' not in text)

    def test_identity_field_only_for_argument_file_links(self):
        source='recovered() { return 1; }\n'
        key,meta,_=identity(source,'aztec36')
        self.assertNotIn('link_argument_file',meta)
        small=[dict(source=source)]+[dict(source='f%d() { return %d; }\n'%(i,i)) for i in range(1,7)]
        trial=dict(source=''.join(x['source'] for x in small),objects=small)
        _,meta,_=identity(trial['source'],'aztec36',9,object_specs(trial))
        self.assertNotIn('link_argument_file',meta)
        large=[dict(source=source)]+[dict(source='f%d() { return %d; }\n'%(i,i)) for i in range(1,33)]
        trial=dict(source=''.join(x['source'] for x in large),objects=large)
        key,meta,_=identity(trial['source'],'aztec36',9,object_specs(trial))
        field=meta['link_argument_file']
        self.assertEqual(field['mechanism'],'ln -f')
        self.assertEqual(field['max_direct_argument_chars'],link_line.MAX_DIRECT_ARGUMENT_CHARS)
        without=dict(meta);without.pop('link_argument_file')
        from common import json_bytes,sha256
        self.assertNotEqual(key,sha256(json_bytes(without)),'argument-file links must not reuse shell-rejected cache entries')

    def test_decision_is_batch_index_independent(self):
        for index in (0,7,47,999):
            prefix='t%03d'%index;hp='h%03d'%index
            objects=[prefix]+[prefix+'_part%03d'%i for i in range(1,33)]
            self.assertIsNotNone(link_line.plan('Old1:',prefix,hp,9,objects,[],META)[1])
            objects=[prefix]+[prefix+'_part%03d'%i for i in range(1,7)]
            self.assertIsNone(link_line.plan('Old1:',prefix,hp,9,objects,[],META)[1])


if __name__=='__main__':
    unittest.main()
