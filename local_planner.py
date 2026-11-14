import json
import re
import sys
import threading
import webbrowser
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, parse_qs, urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler
ROOT=Path(getattr(sys,'_MEIPASS',None) or Path(__file__).resolve().parent)
PORT=8765
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None
opener=build_opener(NoRedirect())
def check_server(p):
    sid=int(p.get('server',['12317'])[0])
    if not (11301<=sid<=11323 or 12301<=sid<=12323): raise ValueError('Select an EU server')
def items_target(query):
    p=parse_qs(query,keep_blank_values=True)
    if set(p)-{'server','sort','order','window','limit','offset','q'} or any(len(v)!=1 for v in p.values()): raise ValueError('Invalid parameters')
    check_server(p)
    if not 1<=int(p.get('limit',['1000'])[0])<=1000 or int(p.get('offset',['0'])[0])<0: raise ValueError('Invalid pagination')
    return 'https://aion2.exchange/api/items?'+urlencode({k:v[0] for k,v in p.items()})
def crafts_target(query):
    p=parse_qs(query,keep_blank_values=True)
    if set(p)-{'category','sort','order','server'} or any(len(v)!=1 for v in p.values()): raise ValueError('Invalid parameters')
    check_server(p)
    if 'category' in p and not re.fullmatch(r'[A-Za-z ]{1,24}',p['category'][0]): raise ValueError('Invalid category')
    if p.get('sort',['name'])[0] not in ('name','cost','margin','margin_pct','market_price'): raise ValueError('Invalid sort')
    if p.get('order',['asc'])[0] not in ('asc','desc'): raise ValueError('Invalid order')
    return 'https://aion2.exchange/api/crafts?'+urlencode({k:v[0] for k,v in p.items()})
def friendly(exc):
    if isinstance(exc,HTTPError):
        if exc.code in (429,500,502,503,504): return 'aion2.exchange is temporarily unavailable or limiting requests (HTTP %d). Try again in a few minutes.'%exc.code
        return 'aion2.exchange returned HTTP %d.'%exc.code
    if isinstance(exc,URLError): return 'Cannot reach aion2.exchange: %s'%exc.reason
    return str(exc)
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def host_ok(self):
        host='127.0.0.1:'+str(self.server.server_port)
        return self.headers.get('Host')==host and self.headers.get('Origin','http://'+host)=='http://'+host
    def relay(self,upstream,key):
        try:
            req=Request(upstream,headers={'Accept':'application/json','User-Agent':'AION2LocalPlanner/10.2'})
            with opener.open(req,timeout=15) as response: body=response.read(8_000_001)
            if len(body)>8_000_000: raise ValueError('Response too large')
            data=json.loads(body)
            if not isinstance(data,dict) or not isinstance(data.get(key),list): raise ValueError('Unexpected API response')
            self.reply(200,json.dumps(data).encode(),'application/json')
        except Exception as exc: self.reply(502,json.dumps({'error':friendly(exc)}).encode(),'application/json')
    def do_GET(self):
        if not self.host_ok(): self.send_error(403);return
        route=urlsplit(self.path)
        if route.path=='/': self.reply(200,(ROOT/'calculator.html').read_bytes(),'text/html; charset=utf-8');return
        if route.path=='/favicon.ico': self.reply(204,b'','image/x-icon');return
        if route.path not in ('/api/items','/api/crafts'): self.send_error(404);return
        try: upstream=(items_target if route.path=='/api/items' else crafts_target)(route.query)
        except (ValueError,TypeError): self.send_error(400);return
        self.relay(upstream,'items' if route.path=='/api/items' else 'targets')
    def do_POST(self):
        host='http://127.0.0.1:'+str(self.server.server_port)
        if self.headers.get('Host')!=host[7:] or self.headers.get('Origin')!=host: self.send_error(403);return
        if urlsplit(self.path).path!='/api/quit': self.send_error(404);return
        self.reply(200,b'{"ok":true}','application/json')
        threading.Thread(target=self.server.shutdown,daemon=True).start()
    def reply(self,status,body,kind):
        self.send_response(status)
        for k,v in [('Content-Type',kind),('Content-Length',str(len(body))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')]: self.send_header(k,v)
        self.end_headers();self.wfile.write(body)
def main():
    if not (ROOT/'calculator.html').exists(): raise SystemExit('calculator.html not found next to the program.')
    url='http://127.0.0.1:%d/'%PORT
    try: httpd=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
    except OSError:
        print('Already running - opening it in your browser.');webbrowser.open(url);return
    print('Calculator: '+url+'\nKeep this window open. Use the Exit button in the page, or Ctrl+C, to stop.')
    threading.Timer(.5,lambda:webbrowser.open(url)).start()
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
    finally: httpd.server_close()
if __name__=='__main__': main()
