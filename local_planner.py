import json
import re
import sys
import threading
import time
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
# --- Character lookup (read-only, EU only) -------------------------------------------------
# Public data from the official AION 2 character pages. Requests are spaced out and cached so the
# planner stays a polite guest: at most one request every NC_MIN_GAP seconds, repeats served locally.
NC_MIN_GAP=0.35
NC_CACHE_TTL=600
NC_UA='AION2LocalPlanner/13 (personal character viewer)'
_nc_lock=threading.Lock()
_nc_next=0.0
_nc_cache={}
CHAR_ROUTES={
    '/api/character/search':('search',{'keyword','region'}),
    '/api/character/info':('info',{'characterId','serverId','region'}),
    '/api/character/equipment':('equipment',{'characterId','serverId','region'}),
    '/api/character/equipment/item':('item',{'id','enchantLevel','slotPos','characterId','serverId','region'}),
}
def _one(p,k):
    v=p.get(k)
    if not v or len(v)!=1: raise ValueError('Missing '+k)
    return v[0]
def _num(p,k,lo,hi):
    v=_one(p,k)
    if not re.fullmatch(r'\d{1,10}',v) or not lo<=int(v)<=hi: raise ValueError('Invalid '+k)
    return v
def char_target(path,query):
    kind,allowed=CHAR_ROUTES[path]
    p=parse_qs(query,keep_blank_values=True)
    if set(p)-allowed or any(len(v)!=1 for v in p.values()): raise ValueError('Invalid parameters')
    if _one(p,'region')!='eu': raise ValueError('Only EU characters are supported')
    if kind=='search':
        kw=_one(p,'keyword')
        if not re.fullmatch(r'\w{1,24}',kw): raise ValueError('Invalid name')
        return kind,'https://api-search.plaync.com/aion2global/search/v2/character?'+urlencode({'keyword':kw,'region':'eu','localeInfo':'en-US'})
    sid=_num(p,'serverId',1301,2323)
    if not (1301<=int(sid)<=1323 or 2301<=int(sid)<=2323): raise ValueError('Select an EU server')
    cid=_one(p,'characterId')
    if not re.fullmatch(r'[A-Za-z0-9_\-]{16,64}={0,2}',cid): raise ValueError('Invalid character id')
    q={'region':'eu','lang':'en-US','characterId':cid,'serverId':sid}
    if kind=='item':
        q={'id':_num(p,'id',1,2_000_000_000),'enchantLevel':_num(p,'enchantLevel',0,40),'characterId':cid,'serverId':sid,'slotPos':_num(p,'slotPos',1,60),'lang':'en-US','region':'eu'}
        return kind,'https://aion2.plaync.com/api/character/equipment/item?'+urlencode(q)
    return kind,'https://aion2.plaync.com/api/character/'+('info' if kind=='info' else 'equipment')+'?'+urlencode(q)
def nc_valid(kind,data):
    if not isinstance(data,dict): return False
    return {'search':isinstance(data.get('list'),list),'info':isinstance(data.get('profile'),dict),
            'equipment':isinstance(data.get('equipment'),dict),'item':'id' in data}[kind]
def nc_fetch(url):
    global _nc_next
    now=time.monotonic()
    hit=_nc_cache.get(url)
    if hit and now-hit[0]<NC_CACHE_TTL: return hit[1]
    with _nc_lock:
        wait=_nc_next-time.monotonic()
        if wait>0: time.sleep(wait)
        _nc_next=time.monotonic()+NC_MIN_GAP
    req=Request(url,headers={'Accept':'application/json','User-Agent':NC_UA,'Referer':'https://aion2.plaync.com/en-us/characters/index'})
    with opener.open(req,timeout=15) as response: body=response.read(2_000_001)
    if len(body)>2_000_000: raise ValueError('Response too large')
    if len(_nc_cache)>300: _nc_cache.clear()
    _nc_cache[url]=(time.monotonic(),body)
    return body
def friendly(exc):
    if isinstance(exc,HTTPError):
        if exc.code in (429,500,502,503,504): return 'aion2.exchange is temporarily unavailable or limiting requests (HTTP %d). Try again in a few minutes.'%exc.code
        return 'aion2.exchange returned HTTP %d.'%exc.code
    if isinstance(exc,URLError): return 'Cannot reach aion2.exchange: %s'%exc.reason
    return str(exc)
def nc_friendly(exc):
    if isinstance(exc,HTTPError):
        if exc.code==404: return 'The official site has no such character or item (HTTP 404).'
        if exc.code in (429,500,502,503,504): return 'The official AION 2 site is temporarily unavailable or limiting requests (HTTP %d). Try again in a few minutes.'%exc.code
        return 'The official AION 2 site returned HTTP %d.'%exc.code
    if isinstance(exc,URLError): return 'Cannot reach the official AION 2 site: %s'%exc.reason
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
    def relay_character(self,kind,upstream):
        try:
            data=json.loads(nc_fetch(upstream))
            if not nc_valid(kind,data): raise ValueError('Unexpected response from the official site')
            self.reply(200,json.dumps(data).encode(),'application/json')
        except Exception as exc: self.reply(502,json.dumps({'error':nc_friendly(exc)}).encode(),'application/json')
    def do_GET(self):
        if not self.host_ok(): self.send_error(403);return
        route=urlsplit(self.path)
        if route.path=='/': self.reply(200,(ROOT/'calculator.html').read_bytes(),'text/html; charset=utf-8');return
        if route.path=='/favicon.ico': self.reply(204,b'','image/x-icon');return
        if route.path in CHAR_ROUTES:
            try: kind,upstream=char_target(route.path,route.query)
            except (ValueError,TypeError): self.send_error(400);return
            self.relay_character(kind,upstream);return
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
