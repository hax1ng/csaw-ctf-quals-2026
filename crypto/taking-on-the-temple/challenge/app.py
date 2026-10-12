from flask import Flask, render_template_string, request, session, send_from_directory
from pathlib import Path
import hmac, json, os, re
from artifacts import build_artifacts

BASE=Path(__file__).resolve().parent.parent
DATA=BASE/"data"

def load_secret(name):
    secret_file=os.getenv(f"{name}_FILE")
    if secret_file:
        secret_path=Path(secret_file)
        if not secret_path.is_file():
            raise RuntimeError(f"{name}_FILE must point to a readable file, not a directory: {secret_file}")
        value=secret_path.read_text(encoding="utf-8").strip()
    else:
        value=os.getenv(name,"").strip()
    if not value:
        raise RuntimeError(f"Set {name} or {name}_FILE before starting the challenge")
    return value

FLAG=load_secret("FLAG")
if not re.fullmatch(r"csaw\{[^{}\r\n]+\}",FLAG):
    raise RuntimeError("FLAG must use the csaw{...} format")
CHALLENGE_SEED=load_secret("CHALLENGE_SEED")
K1,K2,K3=build_artifacts(DATA,CHALLENGE_SEED,FLAG)

app=Flask(__name__)
app.secret_key=load_secret("SESSION_SECRET")

def verify(text, marker):
    return marker.upper() in re.sub(r"\s+"," ",text.strip()).upper()

HTML="""<!doctype html><html><head><title>Midnight Vault</title>
<style>
body{font-family:monospace;background:#101418;color:#d9e2ea;max-width:1000px;margin:30px auto;padding:0 20px}
pre,textarea,input{background:#171d23;color:#d9e2ea;border:1px solid #52616b;padding:12px}
pre{white-space:pre-wrap}textarea{width:100%;height:160px}input{width:70%}
a,button{color:#101418;background:#b9d6e8;border:0;padding:8px 12px;text-decoration:none;font-weight:bold}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:15px 0}.ok{color:#9be29b}.bad{color:#ff9d9d}
</style></head><body><h1>THE MIDNIGHT VAULT</h1>
<nav><a href="/">Crew Brief</a><a href="/stone">Granite</a><a href="/frost">Frost</a>
<a href="/iron">Iron</a><a href="/altar">Vault Map</a><a href="/inventory">Crew Kit</a></nav>
{% if msg %}<p class="{{cls}}">{{msg}}</p>{% endif %}{{body|safe}}</body></html>"""

def page(body,msg="",cls=""):
    return render_template_string(HTML,body=body,msg=msg,cls=cls)

def artifact_unlocked(name):
    if name == "stone.json":
        return True
    if name in {"frost.txt","frost.bin"}:
        return session.get("k1") == K1
    if name == "iron.json":
        return session.get("k1") == K1 and session.get("k2") == K2
    if name == "vault.json":
        return all(session.get(k) for k in ("k1","k2","k3"))
    return False

@app.route("/")
def index():
    return page("""<pre>
The crew hit the wrong safehouse and found a ghost ledger hidden in the snow.

Three lockboxes were built to protect a vault on the black market circuit.
Each hides a fragment of the final key.
None of them alone will open the job.

The first remembers.
The second preserves.
The third endures.

A final note on the stolen page reads:

    ⠁ ⠅⠑⠽ ⠙⠊⠧⠊⠙⠑⠙
    ⠃⠗⠁⠊⠇⠇⠑ ⠕⠏⠑⠝⠎ ⠞⠓⠑ ⠕⠇⠙ ⠗⠑⠛⠊⠎

The rest of the plan is missing.

Recover the three fragments, rebuild the key, and wake the old registry before the getaway van leaves.

The score goes to whoever gets in, gets out, and keeps their hands clean.
</pre>
<p>Hard mode: algorithm names are intentionally absent. Inspect the supplied artifacts.</p>""")

@app.route("/stone",methods=["GET","POST"])
def stone():
    d=json.loads((DATA/"stone.json").read_text()); msg=""
    if request.method=="POST":
        if verify(request.form.get("answer",""),K1):
            session["k1"]=K1
            return page(f"<pre>FRAGMENT ONE RECOVERED\nMEMORY OPENS WHAT STONE HAS SEALED.\nMARKER: {K1}</pre>","The first lockbox clicks open.","ok")
        msg="The lockbox stays cold and shut."
    body=f"""<pre>GRANITE SAFE

Braille: {d["braille"]}  ⠗⠑⠍⠑⠍⠃⠑⠗ ⠞⠓⠑ ⠇⠕⠉⠅
Inscription: {d["inscription"]}

Ciphertext:
{d["ciphertext"]}

Other markings:
- {d["decoys"][0]}
- {d["decoys"][1]}
- {d["decoys"][2]}

The vault team needs the recovered plaintext fragment to wake the old registry and crack the first seal.</pre>
<form method="post"><textarea name="answer" placeholder="Recovered plaintext"></textarea><br><button>Submit</button></form>"""
    return page(body,msg,"bad" if msg else "")

@app.route("/frost",methods=["GET","POST"])
def frost():
    if session.get("k1") != K1:
        return page("<pre>FROST VAULT\n\nThe chamber remains sealed. The granite fragment must be recovered before the frost archive unlocks.</pre>")
    msg=""
    if request.method=="POST":
        if verify(request.form.get("answer",""),K2):
            session["k2"]=K2
            return page(f"<pre>FRAGMENT TWO RECOVERED\nPRESERVATION IS A TRACE OF ORIGIN.\nMARKER: {K2}</pre>","The frozen lock yields and the chamber fogs over.","ok")
        msg="The cold vault ignores you."
    body="""<pre>FROST VAULT

Braille: ⠊⠉⠑ ⠏⠗⠑⠎⠑⠗⠧⠑ ⠞⠓⠑ ⠗⠑⠛⠊⠎
Inscription: WHAT IS PRESERVED REMEMBERS WHERE IT CAME FROM.

The copper plate points to two artifacts.
The binary payload must be interpreted, not merely copied.
The cold metal hums with one sentence: wake the old registry, then follow the origin.

<a href="/artifact/frost.txt">frost.txt</a>
<a href="/artifact/frost.bin">frost.bin</a></pre>
<form method="post"><textarea name="answer" placeholder="Recovered plaintext"></textarea><br><button>Submit</button></form>"""
    return page(body,msg,"bad" if msg else "")

@app.route("/iron",methods=["GET","POST"])
def iron():
    if session.get("k1") != K1 or session.get("k2") != K2:
        return page("<pre>IRON SAFEGUARD\n\nThe steel plate remains dormant. The frost archive must be opened before the final lock reveals itself.</pre>")
    msg=""
    if request.method=="POST":
        if verify(request.form.get("answer",""),K3):
            session["k3"]=K3
            return page(f"<pre>FRAGMENT THREE RECOVERED\nENDURANCE JOINS WHAT MEMORY AND PRESERVATION HOLD.\nMARKER: {K3}</pre>","The steel vault shudders and the final lockbox rolls open.","ok")
        msg="The steel plate rejects the fragment."
    body="""<pre>IRON SAFEGUARD

Braille: ⠊⠗⠕⠝ ⠎⠞⠑⠑⠇ ⠞⠓⠑ ⠗⠑⠛⠊⠎
Inscription: THE SHAPE OF THE ANSWER IS NOT THE ANSWER.

The tablet contains four digest columns and a binary payload.
Only when the old registry stirs does the chain become honest.

<a href="/artifact/iron.json">iron.json</a>

The crew needs the recovered plaintext fragment to finish the set.</pre>
<form method="post"><textarea name="answer" placeholder="Recovered plaintext"></textarea><br><button>Submit</button></form>"""
    return page(body,msg,"bad" if msg else "")

@app.route("/altar")
def altar():
    if not all(session.get(k) for k in ("k1","k2","k3")):
        return page("<pre>Three lock segments are still missing. The vault map refuses to align.</pre>")
    return page("""<pre>THE VAULT MAP

Three fragments were stashed beneath the frost,
Each guarding the piece the others lost.
Stone keeps memory, frost keeps time,
Iron joins the broken line.
Set all three where old locks meet;
The hidden cache will yield its seat.

The order is not decorative.

<a href="/vault">Proceed to the vault</a></pre>""")

@app.route("/vault",methods=["GET","POST"])
def vault():
    if not all(session.get(k) for k in ("k1","k2","k3")):
        return page("<pre>The vault remains sealed until the team finishes the lock set.</pre>")
    msg=""
    if request.method=="POST":
        if hmac.compare_digest(request.form.get("flag","").strip(),FLAG):
            session["won"]=True
            return page("""<pre>The coffer clicks.
Once. Twice. Then the locks release.

Inside is a collection of objects wrapped in ancient cloth,
untouched for generations.

Something enormous shifts beneath the city.

The crew gets away clean.</pre>""","THE VAULT IS OPEN.","ok")
        msg="The final lock rejects the key."
    return page("""<pre>THE VAULT

Three pieces. One key. No second attempt.

The vault map supplied the ordering rule.
vault.json contains the final artifact.

<a href="/artifact/vault.json">vault.json</a>

Decrypt the payload and submit the loot flag.</pre>
<form method="post"><input name="flag" placeholder="csaw{...}"><button>Open</button></form>""",msg,"bad" if msg else "")

@app.route("/inventory")
def inventory():
    rows=[f"{n}: {session.get(k,'[unrecovered]')}" for k,n in
          [("k1","Stone"),("k2","Frost"),("k3","Iron")]]
    rows.append("Vault: "+("OPEN" if session.get("won") else "SEALED"))
    return page("<pre>CREW KIT\n\n"+"\n".join(rows)+"</pre>")

@app.route("/artifact/<path:name>")
def artifact(name):
    if name not in {"frost.txt","frost.bin","iron.json","vault.json","stone.json"}:
        return "Not found",404
    if not artifact_unlocked(name):
        return "Artifact remains sealed until the prior stage is solved.",403
    return send_from_directory(DATA,name,as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
