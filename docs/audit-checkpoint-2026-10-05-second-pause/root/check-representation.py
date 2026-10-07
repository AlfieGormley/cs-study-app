from pathlib import Path
import ast,re,json,io,contextlib,doctest,struct,math,itertools,subprocess,sys,unicodedata,ipaddress
from fractions import Fraction
B=Path('content/architecture/01-data-representation');D=Path('/tmp/cs-study-audit-2026-10-04/representation-tests');D.mkdir(exist_ok=True)
assertions=0;counts={};envs={};fences={};outputs={}
def check(x):
 global assertions
 assert x
 assertions+=1
for p in sorted(B.glob('*.md')):
 env={};blocks=re.findall(r'```([^\n]*)\n(.*?)```',p.read_text(),re.S);fences[p.stem]=blocks
 for lang,code in blocks:
  if lang!='python':continue
  counts['lessonPython']=counts.get('lessonPython',0)+1
  if code.startswith('>>>'):
   runner=doctest.DocTestRunner();runner.run(doctest.DocTestParser().get_doctest(code,env,p.stem,str(p),0));check(runner.failures==0)
  else:exec(code,env)
 envs[p.stem]=env
for p in sorted(B.glob('*.questions.json')):
 env=dict(envs[p.name.split('.questions')[0]])
 for q in json.loads(p.read_text()):
  for field in ('prompt','workedExample'):
   for lang,code in re.findall(r'```([^\n]*)\n(.*?)```',q[field],re.S):
    if lang=='python':
     out=io.StringIO()
     with contextlib.redirect_stdout(out):exec(code,env)
     outputs[q['id']+field]=out.getvalue();counts['quizPython']=counts.get('quizPython',0)+1
for n in range(-2048,2049):
 check(envs['rep-integers']['to_u8'](n)==n%256)
 check(envs['rep-integers']['to_s8'](n)==(n+128)%256-128)
for n in range(65536):check(envs['rep-bitwise']['popcount'](n)==n.bit_count())
try:envs['rep-bitwise']['popcount'](-1);check(False)
except ValueError:check(True)
for a,b in itertools.product(range(256),repeat=2):
 sa=(a+128)%256-128;sb=(b+128)%256-128;res=(a+b)%256;sr=(res+128)%256-128
 overflow=not(-128<=sa+sb<=127)
 check(overflow==((sa<0)==(sb<0) and (sr<0)!=(sa<0)))
 check((a*b)%256==(sa*sb)%256)
check(len({x&999 for x in range(1024)})==256)
check(int(ipaddress.IPv4Address('192.168.1.10'))==3232235786)
check(int('11010110',2)==214);check(int('3c7',16)==967)
x=Fraction(1,10);digits=''
for i in range(8):x*=2;digits+=str(x.numerator//x.denominator);x%=1
check(digits=='00011001')
for val,h in [(-6.25,'c0c80000'),(13.5,'41580000'),(-20.5,'c1a40000'),(.625,'3f200000'),(5.,'40a00000')]:check(struct.pack('>f',val).hex()==h)
check(struct.unpack('>f',bytes.fromhex('c1c80000'))[0]==-25)
check(struct.unpack('>f',struct.pack('>f',2**24+1))[0]==2**24)
check(float(2**53+1)==2**53);check(1e16+1-1e16==0)
check(struct.pack('>f',.1).hex()=='3dcccccd')
check(math.ulp(1e16)==2);check(math.ulp(1.)==2**-52)
check((2-2**-10)*2**15==65504)
check(round(2.675,2)==2.67);check(sum([.1]*10)==1.)
check(math.fsum([.1]*10)==1.);check(Fraction(.1)!=Fraction(1,10))
for cp in range(0x110000):
 if 0xD800<=cp<=0xDFFF:continue
 ch=chr(cp);u8=ch.encode('utf8');u16=ch.encode('utf-16-be')
 check(len(u8)==(1 if cp<128 else 2 if cp<2048 else 3 if cp<65536 else 4))
 check(len(u16)==(2 if cp<65536 else 4))
 if cp>=65536:
  z=cp-65536;check(u16==struct.pack('>HH',0xD800+(z>>10),0xDC00+(z&1023)))
for bad in [b'\xc0\xaf',b'\xed\xa0\x80',b'\xf4\x90\x80\x80',b'\xff']:
 try:bad.decode('utf8');check(False)
 except UnicodeDecodeError:check(True)
check('€'.encode().hex()=='e282ac');check('😀'.encode().hex()=='f09f9880')
check('👍'.encode('utf-16-be').hex()=='d83ddc4d')
check('don’t'.encode().decode('cp1252')=='donâ€™t')
check('café'!='cafe\u0301');check(unicodedata.normalize('NFC','cafe\u0301')=='café')
check('Straße'.upper()=='STRASSE')
check(struct.calcsize('@cic')==9);check(struct.calcsize('@cic0i')==12);check(struct.calcsize('<cic')==6)
check(int.from_bytes(bytes.fromhex('000001f4'),'little')==4093706240)
# Use actual C lesson fences, adding only includes, scaffolding and test fixtures.
headers='''#include <stdint.h>\n#include <stddef.h>\n#include <stdio.h>\n#include <limits.h>\n#include <assert.h>\n#include <string.h>\n#include <fcntl.h>\n#include <unistd.h>\n#include <arpa/inet.h>\n'''
def block(name,i):return fences[name][i][1]
funcs=block('rep-memory-layout',4)+block('rep-memory-layout',6)+block('rep-memory-layout',8)+block('rep-integers',10)+'\nstatic int errors; void handle_error(void){errors++;}\n'
main=[]
def case(code):main.append('{\n'+code+'\n}')
case(block('rep-number-systems',11))
case(block('rep-integers',8)+'assert(a==-3 && b==253);')
case('int a=INT_MAX,b=1;'+block('rep-integers',11)+'assert(errors==1);')
case(block('rep-integers',12))
case('unsigned x=44,k=3;'+block('rep-bitwise',1)+'assert(x==44);')
case(block('rep-bitwise',3)+'assert(fd>=0);close(fd);unlink("log.txt");')
case(block('rep-memory-layout',1))
case(block('rep-memory-layout',2)+'unsigned char *b=(unsigned char*)&addr.sin_port;assert(b[0]==31&&b[1]==144);')
case(block('rep-memory-layout',9))
case('unsigned char b[]={0x12,0x34,0x56,0x78};assert(rd_be32(b)==0x12345678);assert(sizeof(struct B)==8);')
# Actual quiz fragments (excluding UB demonstrations, isolated functions/return alternatives and incomplete packed-pointer fixture).
for p in B.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  for lang,code in re.findall(r'```([^\n]*)\n(.*?)```',q['prompt'],re.S):
   if lang!='c':continue
   if q['id']=='rep-integers-q9':continue # same function already extracted
   if q['id']=='rep-memory-layout-q10':continue # deliberate invalid access, no run
   case(code)
   counts['quizCCompiled']=counts.get('quizCCompiled',0)+1
case('struct G{uint8_t t;uint64_t x;uint16_t y;uint32_t z;};assert(sizeof(struct G)==24);assert(offsetof(struct G,z)==20);')
case('struct E{char a;short s;char c;int i;};assert(offsetof(struct E,i)==8);')
case('for(unsigned x=0;x<65536;x++){assert((x^x)==0);assert((x>>1)==x/2);}')
case('assert(will_overflow(INT_MAX-1)==0);')
source=headers+funcs+'\nint main(void){\n'+'\n'.join(main)+'\nreturn 0;}\n'
(D/'examples.c').write_text(source)
subprocess.run(['clang','-std=c17','-O2','-Wall','-Wextra',str(D/'examples.c'),'-o',str(D/'examples')],check=True,capture_output=True,text=True,timeout=30)
result=subprocess.run([str(D/'examples')],cwd=D,check=True,capture_output=True,text=True,timeout=5);outputs['nativeC']=result.stdout
# UBSan demonstrations stop at the invalid operation; no resulting value is claimed.
for name,code,expected in [('overflow','volatile int x=INT_MAX; return x+1;','signed integer overflow'),('shift','volatile int x=1;return x<<31;','left shift'),('bad_reverse','int a[1]={0};size_t n=0;return a[n-1];','index')]:
 src=D/(name+'.c');src.write_text(headers+'int main(void){'+code+'}')
 exe=D/name
 subprocess.run(['clang','-std=c17','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',str(src),'-o',str(exe)],check=True,capture_output=True,text=True,timeout=30)
 p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);check(p.returncode!=0);check(expected in p.stderr);outputs[name]=p.stderr.splitlines()[0]
js="""const assert=require('node:assert/strict');assert.equal('😀'.length,2);assert.equal('👍🏽'.length,4);assert.equal([...new Intl.Segmenter('en',{granularity:'grapheme'}).segment('👍🏽')].length,1);assert.equal('😀'.slice(0,1).isWellFormed(),false);assert.equal(0.1+0.2===0.3,false);"""
subprocess.run(['node','-e',js],check=True,timeout=10)
report={'assertions':assertions,'fences':counts,'outputs':outputs,'native':'Apple Clang/macOS arm64; C17 ordinary ABI, not x86 runtime','limitations':['C23 stdckdint/std bit helpers source-checked; no successful C23 library execution claimed.','Java abs/floorMod and MySQL ALTER are source-checked rather than executed in their unavailable runtimes.','Incomplete C condition-only and return-alternative teaching fragments checked through equivalent completed fixtures.','Deliberate UB excerpts are bounded/sanitized demonstrations, never evidence of a portable result.','No benchmark, device DMA, split lock, live kernel copy_to_user or physical failure reproduction attempted.']}
(D/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
