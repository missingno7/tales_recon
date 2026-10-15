import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch,MagicMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
from local_proposer import parse_response
from compiler_oracle import validate_source
from local_model_server import request,PORT


class LocalProposerTests(unittest.TestCase):
    def response(self,**message):
        return dict(choices=[dict(finish_reason='stop',message=dict(content=json.dumps(dict(source='recovered() { return 1; }')),**message))])

    def test_source_only(self):
        self.assertIn('return 1',parse_response(self.response()))

    def test_tools_rejected(self):
        with self.assertRaises(FormatError):parse_response(self.response(tool_calls=[dict(name='read_file')]))

    def test_truncation_rejected(self):
        r=self.response();r['choices'][0]['finish_reason']='length'
        with self.assertRaises(FormatError):parse_response(r)

    def test_unbounded_source_rejected(self):
        r=self.response();r['choices'][0]['message']['content']=json.dumps(dict(source='a'*16385))
        with self.assertRaises(FormatError):parse_response(r)

    def test_protocol_newlines_do_not_corrupt_c_literals(self):
        with self.assertRaises(FormatError):validate_source(r'recovered() {\nreturn 1;\n}')
        validate_source('recovered() { return puts("line\\n"); }')

    def test_transport_is_literal_loopback(self):
        response=MagicMock(status=200);response.read.return_value=b'{"status":"ok"}'
        with patch('local_model_server.http.client.HTTPConnection') as cls:
            cls.return_value.getresponse.return_value=response
            self.assertEqual(request(dict(port=PORT,key='test'),'/health'),dict(status='ok'))
            cls.assert_called_once_with('127.0.0.1',PORT,timeout=10)
            cls.return_value.close.assert_called_once()

    def test_redirect_not_followed(self):
        response=MagicMock(status=302);response.read.return_value=b'redirect'
        with patch('local_model_server.http.client.HTTPConnection') as cls:
            cls.return_value.getresponse.return_value=response
            with self.assertRaises(FormatError):request(dict(port=PORT,key='test'),'/health')
            self.assertEqual(cls.call_count,1)

    def test_port_override_rejected(self):
        with patch('local_model_server.http.client.HTTPConnection') as cls:
            with self.assertRaises(FormatError):request(dict(port=443,key='test'),'/health')
            cls.assert_not_called()


if __name__=='__main__':unittest.main()
