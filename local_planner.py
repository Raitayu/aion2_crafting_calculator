import json
import threading
import webbrowser
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs, urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler
ROOT=Path(__file__).resolve().parent
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None
opener=build_opener(NoRedirect())
def target(query):
    p=parse_qs(query,keep_blank_values=True)
    if set(p)-{'server','sort','order','window','limit','offset','q'} or any(len(v)!=1 for v in p.values()): raise ValueError('Invalid parameters')
    sid=int(p.get('server',['12317'])[0])
    if not (11301<=sid<=11323 or 12301<=sid<=12323): raise ValueError('Select an EU server')
    if not 1<=int(p.get('limit',['1000'])[0])<=1000 or int(p.get('offset',['0'])[0])<0: raise ValueError('Invalid pagination')
    return 'https://aion2.exchange/api/items?'+urlencode({k:v[0] for k,v in p.items()})
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        host='127.0.0.1:'+str(self.server.server_port)
        if self.headers.get('Host')!=host or self.headers.get('Origin','http://'+host)!='http://'+host:
            self.send_error(403);return
        route=urlsplit(self.path)
        if route.path=='/': self.reply(200,(ROOT/'calculator.html').read_bytes(),'text/html; charset=utf-8');return
        if route.path=='/favicon.ico': self.reply(204,b'','image/x-icon');return
        if route.path!='/api/items': self.send_error(404);return
        try: upstream=target(route.query)
        except (ValueError,TypeError): self.send_error(400);return
        try:
            req=Request(upstream,headers={'Accept':'application/json','User-Agent':'AION2LocalPlanner/9.3'})
            with opener.open(req,timeout=15) as response: body=response.read(8_000_001)
            if len(body)>8_000_000: raise ValueError('Response too large')
            data=json.loads(body)
            if not isinstance(data,dict) or not isinstance(data.get('items'),list): raise ValueError('Unexpected API response')
            self.reply(200,json.dumps(data).encode(),'application/json')
        except Exception as exc: self.reply(502,json.dumps({'error':str(exc)}).encode(),'application/json')
    def reply(self,status,body,kind):
        self.send_response(status)
        for k,v in [('Content-Type',kind),('Content-Length',str(len(body))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')]: self.send_header(k,v)
        self.end_headers();self.wfile.write(body)
def main():
    if not (ROOT/'calculator.html').exists(): raise SystemExit('Extract the full ZIP first.')
    try: httpd=ThreadingHTTPServer(('127.0.0.1',8765),Handler)
    except OSError: raise SystemExit('Port 8765 in use. Close the previous launcher first.')
    print('Calculator: http://127.0.0.1:8765/\nKeep this window open. Ctrl+C stops the app.')
    threading.Timer(.5,lambda:webbrowser.open('http://127.0.0.1:8765/')).start()
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
    finally: httpd.server_close()
if __name__=='__main__': main()
