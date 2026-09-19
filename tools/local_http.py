"""Configurable loopback HTTP transport without proxies or redirect following."""
import http.client
import ipaddress
import json
from urllib.parse import urlsplit
from common import require


class LocalHTTP:
    def __init__(self,endpoint='http://127.0.0.1:18087',key=''):
        u=urlsplit(endpoint)
        require(u.scheme=='http' and not u.username and not u.password and not u.query and not u.fragment,'local endpoint must be plain loopback HTTP without credentials/query')
        host='127.0.0.1' if u.hostname=='localhost' else u.hostname
        try:local=ipaddress.ip_address(host).is_loopback
        except ValueError:local=False
        require(local,'only loopback endpoints are permitted')
        require(u.path.rstrip('/') in ('','/v1'),'endpoint path must be empty or /v1')
        self.host=host;self.port=u.port or 80;self.key=key
    def call(self,path,payload=None,timeout=30):
        require(path.startswith('/') and not path.startswith('//'),'invalid local API path')
        conn=http.client.HTTPConnection(self.host,self.port,timeout=timeout)
        try:
            headers={'Content-Type':'application/json'}
            if self.key:headers['Authorization']='Bearer '+self.key
            conn.request('POST' if payload is not None else 'GET',path,
                         None if payload is None else json.dumps(payload).encode('utf-8'),headers)
            response=conn.getresponse();raw=response.read(2*1024*1024+1)
            require(len(raw)<=2*1024*1024,'local response exceeds size bound')
            require(response.status==200,'local inference HTTP %d: %s'%(response.status,raw[:300].decode(errors='replace')))
            return json.loads(raw)
        finally:conn.close()
    def count(self,messages):
        prompt=self.call('/apply-template',dict(messages=messages))['prompt']
        return len(self.call('/tokenize',dict(content=prompt,add_special=False,parse_special=True))['tokens'])
