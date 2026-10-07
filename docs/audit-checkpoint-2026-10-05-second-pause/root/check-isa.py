from pathlib import Path
import subprocess,re,json,math,contextlib,io
root=Path('/Users/alfiegormley/Github/cs-study-app');base=root/'content/architecture/03-isa';out=Path('/tmp/cs-study-audit-2026-10-04/isa-tests');out.mkdir(exist_ok=True)
def fences(stem):return [b for lang,b in re.findall(r'^```([^\n]*)\n(.*?)^```',(base/(stem+'.md')).read_text(),re.S|re.M)]
def run(args):
 p=subprocess.run(args,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(str(args)+'\n'+p.stdout+p.stderr)
 return p.stdout
ns={};exec(fences('isa-stored-program')[1],ns)
class Mem(list):
 def __getitem__(self,i):
  if i<9:self.fetches+=1
  return super().__getitem__(i)
checks=0
for n in range(1001):
 m=Mem([120,508,221,421,120,322,420,600,0]+[0]*11+[n,0,1]);m.fetches=0;ns['run'](m)
 assert m[21]==n*(n+1)//2;assert m.fetches==8*n+3;checks+=2
buf=io.StringIO()
with contextlib.redirect_stdout(buf):exec(fences('isa-stored-program')[3],ns)
assert buf.getvalue()=='6\n';checks+=1
try:ns['run']([700]);raise AssertionError('unknown opcode accepted')
except ValueError:checks+=1
m=[120,508,221,421,120,322,420,0,0]+[0]*11+[3,0,1];ns['run'](m);assert m[21]==3;checks+=1
specs={'x86_64': [('isa-reading-assembly',0,'f','linear'),('isa-reading-assembly',1,'f','linearatt'),('isa-reading-assembly',4,'count_pos','positives'),('isa-reading-assembly',6,'half','half'),('isa-reading-assembly',7,'max','maximum'),('isa-calling-conventions',2,'fact','factorial'),('isa-calling-conventions',5,'f','identity'),('isa-loops-arrays-structs',3,'sum','sum'),('isa-loops-arrays-structs',5,'get','get2d'),('isa-loops-arrays-structs',6,'at','at'),('isa-loops-arrays-structs',8,'getn','getn'),('isa-loops-arrays-structs',0,None,'choose'),('isa-loops-arrays-structs',1,None,'choose2'),('isa-risc-cisc',0,None,'increment')], 'arm64':[('isa-reading-assembly',2,'f','linear'),('isa-reading-assembly',5,'count_pos','positives'),('isa-reading-assembly',8,'max','maximum'),('isa-calling-conventions',3,'fact','factorial'),('isa-loops-arrays-structs',4,'sum','sum'),('isa-risc-cisc',1,None,'increment'),('isa-risc-cisc',3,None,'constant')]}
results={}
for arch,items in specs.items():
 objs=[]
 for stem,i,old,name in items:
  code=fences(stem)[i]
  if arch=='x86_64':code=re.sub(r'//[^\n]*','',code)
  if old:code=re.sub(r'\b'+old+r'\b','_'+name,code)
  else:code='_'+name+':\n'+code+'\nret\n'
  header='.text\n.globl _'+name+'\n'
  if arch=='x86_64' and name!='linearatt':header+='.intel_syntax noprefix\n'
  path=out/(arch+'-'+name+'.s');path.write_text(header+code);obj=path.with_suffix('.o')
  run(['clang','-arch',arch,'-c',str(path),'-o',str(obj)]);objs.append(str(obj))
 c='''#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <limits.h>
#include <stddef.h>
struct S {char tag; int n; long v; short k;};
struct T {char c; int x; char d;};
struct P {char a; double b; char c; int d;};
struct R {double b;int d;char a,c;};
extern long linear(long), positives(const long*,long), factorial(long),sum(long*,long);
extern int maximum(int,int);extern void increment(int*,long);
static long count=0;
#define CHECK(x) do{assert(x);++count;}while(0)
int main(void){
CHECK(sizeof(struct S)==24);CHECK(offsetof(struct S,n)==4);CHECK(offsetof(struct S,k)==16);CHECK(sizeof(struct T)==12);CHECK(sizeof(struct P)==24);CHECK(sizeof(struct R)==16);
long a[101];for(int i=0;i<101;i++)a[i]=i-50;
for(long n=-2;n<=101;n++) {long s=0,p=0;for(long j=0;j<n;j++){s+=a[j];p+=a[j]>0;}CHECK(sum(a,n)==s);CHECK(positives(a,n)==p);}
for(long i=-1000;i<=1000;i++)CHECK(linear(i)==i*5+7);
long f=1;for(long n=0;n<=20;n++){if(n>0)f*=n;CHECK(factorial(n)==f);}CHECK(factorial(-2)==1);
int vals[]={INT_MIN,INT_MIN+1,-10,-1,0,1,10,INT_MAX};for(int i=0;i<8;i++)for(int j=0;j<8;j++)CHECK(maximum(vals[i],vals[j])==(vals[i]>vals[j]?vals[i]:vals[j]));
int b[]={0,2,-4};increment(b,1);CHECK(b[0]==0 && b[1]==3 && b[2]==-4);
'''
 if arch=='x86_64':c+='''extern long linearatt(long),identity(long),at(long*,int);extern int half(int),choose(int),choose2(int),get2d(int (*)[3],long,long),getn(struct S*,long);
for(int i=-100000;i<=100000;i++){CHECK(half(i)==i/2);CHECK(choose(i)==(i>0?1:2));CHECK(choose2(i)==(i>0?1:2));CHECK(linearatt(i)==i*5L+7);CHECK(identity(i)==i);}
for(int i=0;i<8;i++)CHECK(half(vals[i])==vals[i]/2);
for(int i=-50;i<=50;i++)CHECK(at(a+50,i)==i);
int m[2][3]={{1,2,3},{4,5,6}};for(int i=0;i<2;i++)for(int j=0;j<3;j++)CHECK(get2d(m,i,j)==m[i][j]);
struct S structs[5]={0};for(int i=0;i<5;i++){structs[i].n=19-i;CHECK(getn(structs,i)==19-i);}
'''
 else:c+='extern uint64_t constant(void);CHECK(constant()==UINT64_C(0x1234567890abcdef));\n'
 c+='printf("%ld\\n",count);return 0;}\n'
 p=out/(arch+'-driver.c');p.write_text(c);exe=out/(arch+'-examples');run(['clang','-arch',arch,'-O2',str(p),*objs,'-o',str(exe)]);results[arch]={'assertions':int(run([str(exe)])),'lessonAssemblyFencesExecuted':len(items)}
# Exact encoding / immediate rejection via assembled Mach-O disassembly.
encodings={'x86_64':[('ret','c3'),('push rbp','55'),('add rax,rdi','48 01 f8'),('mov eax,1','b8 01 00 00 00'),('mov dword ptr [rax+rbx*4+16],5','c7 44 98 10 05 00 00 00'),('add dword ptr [rdi+rsi*4],1','83 04 b7 01')], 'arm64':[('add x0,x0,x1','8b010000'),('sub x0,x1,x2','cb020020')]}
for arch,seq in encodings.items():
 for i,(code,expected) in enumerate(seq):
  p=out/(arch+'-encoding-'+str(i)+'.s');p.write_text('.text\n'+('.intel_syntax noprefix\n' if arch=='x86_64' else '')+code+'\n');obj=p.with_suffix('.o');run(['clang','-arch',arch,'-c',str(p),'-o',str(obj)]);dis=run(['objdump','-d',str(obj)]);assert expected in dis,dis;checks+=1
for code in ['add x0,x0,#4097','mov x0,#0x12345','add w0,w0,[x1]']:
 p=out/'invalid.s';p.write_text('.text\n'+code+'\n');res=subprocess.run(['clang','-c',str(p),'-o',str(p.with_suffix('.o'))],capture_output=True);assert res.returncode!=0;checks+=1
for code in ['add x0,x0,#4095','add x0,x0,#4096','mov x0,#0xff00ff00ff00ff00']:
 p=out/'valid.s';p.write_text('.text\n'+code+'\n');run(['clang','-c',str(p),'-o',str(p.with_suffix('.o'))]);checks+=1
results['pythonArithmeticAndEncodingAssertions']=checks;results['totalAssertions']=checks+sum(v['assertions'] for v in results.values() if isinstance(v,dict));(out/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
