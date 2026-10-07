import contextlib,io,itertools,math,os,pathlib,random,re,socket,ssl,subprocess,sys,tempfile,threading
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.')
base=root/'content/networks/06-wireless-modern'
ns={}; outputs={}; checks=0
def check(x):
 global checks
 assert x
 checks+=1
for p in base.glob('*.md'):
 fences=re.findall(r'```python\n(.*?)```',p.read_text(),re.S)
 for code in fences:
  scope={}; out=io.StringIO()
  with contextlib.redirect_stdout(out):exec(compile(code,str(p),'exec'),scope)
  ns[p.stem]=scope;outputs[p.stem]=out.getvalue()
check(len(ns)==5)
check(outputs['wm-cellular']=='1200.0 120.0\n')
check(outputs['wm-datacentre']=='[1, 3, 2, 2, 3, 1]\n')
check(outputs['wm-sdn']=='a 10.20.0.0/20 4091\nb 10.20.16.0/20 4091\nc 10.20.32.0/20 4091\n')
check(outputs['wm-internet-structure']=='54.6\n477\n7.3\n')
rng=random.Random(42); radio=ns['wm-cellular']['radio_on']
for _ in range(5000):
 times=[rng.randrange(-50,100) for _ in range(rng.randrange(30))];tail=rng.randrange(25)
 oracle=len({t+j for t in times for j in range(tail)})
 check(radio(times,tail)==oracle)
 check(radio(iter(reversed(times)),tail)==oracle)
for times,tail in [([],float('nan')),([],float('inf')),([], -1),([float('inf')],1),([float('nan')],1)]:
 try:radio(times,tail)
 except ValueError:check(True)
 else:raise AssertionError('expected ValueError')
pick=ns['wm-datacentre']['pick_uplink']
for n in range(1,33):
 for port in range(40000,40200):
  flow=('10.0.1.5',port,'10.0.9.7',443,'tcp')
  check(0<=pick(flow,n)<n);check(pick(flow,n)==pick(flow,n))
for n in [0,-1,True,2.5]:
 try:pick(('a',),n)
 except ValueError:check(True)
 else:raise AssertionError('invalid count accepted')
for n in [4,8]:
 period=n*(n-1); healthy=[h for h in range(period) if h%n!=n-1]
 changed=sum(h%n!=h%(n-1) for h in healthy)
 check(math.isclose(changed/len(healthy),(n-2)/(n-1)))
check(round(math.factorial(8)/8**8,6)==0.002403)
check(round(8*(7/8)**8,3)==2.749)
subnets=ns['wm-sdn']['subnets'];vpc=ns['wm-sdn']['vpc']
check(len(subnets)==16);check(sum(s.num_addresses for s in subnets)==vpc.num_addresses)
for i,a in enumerate(subnets):
 check(a.subnet_of(vpc))
 for b in subnets[i+1:]:check(not a.overlaps(b))
rtt=ns['wm-internet-structure']['rtt_ms']
for _ in range(3000):
 km=rng.random()*40000;speed=rng.uniform(100000,300000);legs=rng.randrange(1,6)
 check(math.isclose(rtt(km,speed,legs),km/speed*1000*legs))
for args in [(-1,10),(1,0),(1,-10),(1,10,0)]:
 try:rtt(*args)
 except ValueError:check(True)
 else:raise AssertionError('invalid model accepted')
# Real TLS handshake to a loopback server using a generated, locally trusted fixture.
# This tests certificate and hostname checking without public network dependencies.
with tempfile.TemporaryDirectory() as tmp:
 cert=tmp+'/cert.pem';key=tmp+'/key.pem'
 subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-keyout',key,'-out',cert,'-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 os.environ['SSL_CERT_FILE']=cert
 serverctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);serverctx.load_cert_chain(cert,key)
 def serve_once(listener,errors):
  try:
   with listener:
    conn,_=listener.accept()
    with conn:
     with serverctx.wrap_socket(conn,server_side=True) as tls:pass
  except ssl.SSLError as e:errors.append(e)
 for host,expected in [('localhost',True),('127.0.0.1',False)]:
  # Match first getaddrinfo address exactly, including IPv6 where available.
  info=socket.getaddrinfo(host,0,type=socket.SOCK_STREAM)[0]
  listener=socket.socket(info[0],info[1],info[2]);listener.bind(info[4]);listener.listen();listener.settimeout(5)
  port=listener.getsockname()[1];errors=[]
  th=threading.Thread(target=serve_once,args=(listener,errors));th.start()
  try:
   result=ns['wm-debugging']['phases'](host,port,2)
   check(expected);check(set(result)=={'dns','tcp','tls'});check(all(v>=0 for v in result.values()))
  except ssl.SSLCertVerificationError:check(not expected)
  finally:th.join(6);check(not th.is_alive())
print(f'PASS {checks} assertions; all 5 Python fences, printed outputs, random arithmetic/model checks, real loopback TLS success and hostname rejection. No WAN/radio/cloud hardware tests.')
