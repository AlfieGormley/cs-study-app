import re,json,io,contextlib,hashlib,hmac,math,random
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa,padding,x25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
b=Path('content/security/02-crypto-basics'); results=[]
for p in b.glob('*.md'):
 for i,code in enumerate(re.findall(r'```python\n(.*?)```',p.read_text(),re.S)):
  out=io.StringIO();ns={}
  with contextlib.redirect_stdout(out):exec(code,ns)
  results.append({'file':str(p),'snippet':i,'stdout':out.getvalue(),'status':'pass'})
for p in b.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  for field in ['prompt','workedExample']:
   for i,code in enumerate(re.findall(r'```python\n(.*?)```',q[field],re.S)):
    ns={'hashlib':hashlib,'AESGCM':AESGCM,'user_password':'test password','pub':rsa.generate_private_key(public_exponent=65537,key_size=2048).public_key(),'oaep':padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None)}
    out=io.StringIO()
    with contextlib.redirect_stdout(out):exec(code,ns)
    results.append({'file':str(p),'question':q['id'],'field':field,'stdout':out.getvalue(),'status':'pass'})
# Exhaustive toy RSA, including non-coprime representatives
assert all(pow(pow(m,17,3233),2753,3233)==m for m in range(3233))
assert pow(66,17,3233)==524 and pow(3,-1,40)==27 and math.gcd(3233,4087)==61
assert pow(2790*pow(3,17,3233)%3233,2753,3233)==195
# Exhaustive toy elliptic curve and order
O=None
def add(P,Q):
 if P is None:return Q
 if Q is None:return P
 x,y=P;u,v=Q
 if x==u and (y+v)%17==0:return O
 slope=((3*x*x+2)*pow(2*y,-1,17) if P==Q else (v-y)*pow(u-x,-1,17))%17
 w=(slope*slope-x-u)%17
 return w,(slope*(x-w)-y)%17
points=[(x,y) for x in range(17) for y in range(17) if (y*y-x*x*x-2*x-2)%17==0]
assert len(points)==18
G=(5,1);multiples=[O]
for i in range(22):multiples.append(add(multiples[-1],G))
assert [multiples[i] for i in [1,2,3,4,5,7,18,19,21,22]]==[(5,1),(6,3),(10,6),(3,1),(9,16),(0,6),(5,16),None,(6,3),(10,6)]
assert pow(5,6,23)==8 and pow(5,15,23)==19 and pow(19,6,23)==pow(8,15,23)==2
assert pow(10,6,23)==pow(8,3,23)==6 and pow(10,15,23)==pow(19,3,23)==5
assert pow(10,4,23)==18 and pow(22,6,23)==1
assert len({pow(2,a*b,23) for a in range(11) for b in range(11)})==11
# AESGCM tampering and output length
key=AESGCM.generate_key(256);ag=AESGCM(key);nonce=b'\x01'*12;aad=b'order-id:4711';ct=ag.encrypt(nonce,b'pay Bob 10',aad)
assert len(ct)==26 and ag.decrypt(nonce,ct,aad)==b'pay Bob 10'
for nn,cc,aa in [(nonce,bytes([ct[0]^1])+ct[1:],aad),(b'\x02'+nonce[1:],ct,aad),(nonce,ct,aad+b'x')]:
 try:ag.decrypt(nn,cc,aa);raise AssertionError('Tamper accepted')
 except InvalidTag:pass
assert 0x5a^0x4f^0x41==0x54 and ord('1')^ord('7')==6
assert len(b'country=GB;tier=')==16 and len(b'YELLOW SUBMARINE')==16
assert b'CorrectHorseBatteryStaple1!'[:12]==b'CorrectHorse'
# OAEP boundary and randomized outputs
priv=rsa.generate_private_key(public_exponent=65537,key_size=3072);pub=priv.public_key();oaep=padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None)
z=pub.encrypt(b'x'*318,oaep);assert len(z)==384 and priv.decrypt(z,oaep)==b'x'*318
try:pub.encrypt(b'x'*319,oaep);raise AssertionError('Oversize accepted')
except ValueError:pass
assert pub.encrypt(b'same',oaep)!=pub.encrypt(b'same',oaep)
# X25519 rejects zero shared key; ordinary exchange works
alice=x25519.X25519PrivateKey.generate();bob=x25519.X25519PrivateKey.generate();assert alice.exchange(bob.public_key())==bob.exchange(alice.public_key())
try:alice.exchange(x25519.X25519PublicKey.from_public_bytes(bytes(32)));raise AssertionError('zero accepted')
except ValueError:pass
# MT state recovery, full consecutive outputs only
rng=random.Random(1234);values=[rng.getrandbits(32) for _ in range(624)]
def untemper(y):
 z=y
 for _ in range(5):z=y^(z>>18)
 y=z
 for _ in range(5):z=y^((z<<15)&0xefc60000)
 y=z
 for _ in range(5):z=y^((z<<7)&0x9d2c5680)
 y=z
 for _ in range(5):z=y^(z>>11)
 return z
clone=random.Random();clone.setstate((3,tuple(untemper(v) for v in values)+(624,),None))
assert [clone.getrandbits(32) for _ in range(100)]==[rng.getrandbits(32) for _ in range(100)]
import bcrypt
try:bcrypt.hashpw(b'x'*73,bcrypt.gensalt(rounds=4));raise AssertionError('bcrypt5 accepted long input')
except ValueError:pass
results.append({'checks':['all 3233 RSA representatives','toy RSA values and malleability','enumerated ECC group and named multiples','DH arithmetic MITM and subgroup counts','AESGCM tamper nonce/AAD/ciphertext rejection and lengths','OAEP318/319byte boundary','X25519 normal/zero-input handling','MT624-output clone predicts100nextwords','bcrypt5 rejects73bytes','quiz XOR and string length arithmetic'],'status':'pass'})
Path('/tmp/cs-study-audit-full/sec02-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
