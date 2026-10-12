#!/usr/bin/env python3
"""Fetch only same-origin pages discovered through challenge HTML links."""
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import hashlib, json, re, time

BASE='https://hollow-houses.ctf.csaw.io/'
ORIGIN=urlparse(BASE).netloc
OUT=Path('artifacts/crawl')
OUT.mkdir(parents=True, exist_ok=True)
q=deque(['/'])
seen=set()
manifest=[]
while q:
    path=q.popleft()
    if path in seen: continue
    seen.add(path)
    if len(seen)>250: raise SystemExit('link traversal safety limit exceeded')
    url=urljoin(BASE,path)
    req=Request(url,headers={'User-Agent':'CTF-solver-linked-crawl/1.0'})
    try:
        with urlopen(req,timeout=15) as f:
            body=f.read(); status=f.status; ct=f.headers.get_content_type()
    except Exception as e:
        manifest.append({'path':path,'error':repr(e)})
        continue
    name='root.html' if path=='/' else path.strip('/').replace('/','__')+'.html'
    (OUT/name).write_bytes(body)
    links=[]
    if ct=='text/html':
        text=body.decode('utf-8','replace')
        for href in re.findall(r'''href=["']([^"']+)["']''',text,re.I):
            u=urlparse(urljoin(url,href))
            if u.netloc==ORIGIN and u.path.endswith('/') and u.path not in seen:
                q.append(u.path)
            links.append(href)
    manifest.append({'path':path,'status':status,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'links':links})
    time.sleep(.05)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(f'fetched {sum("status" in x for x in manifest)} linked HTML pages; {sum("error" in x for x in manifest)} errors')
