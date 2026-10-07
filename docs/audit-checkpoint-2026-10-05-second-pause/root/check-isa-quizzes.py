from pathlib import Path
import json,re,subprocess
root=Path('/Users/alfiegormley/Github/cs-study-app');base=root/'content/architecture/03-isa';out=Path('/tmp/cs-study-audit-2026-10-04/isa-tests')
def fences(s):return [b for _,b in re.findall(r'```([^\n]*)\n(.*?)```',s,re.S)]
def q(stem,n):return json.loads((base/(stem+'.questions.json')).read_text())[n-1]
def run(a):
 p=subprocess.run(a,text=True,capture_output=True)
 if p.returncode:raise RuntimeError(str(a)+'\n'+p.stdout+p.stderr)
 return p.stdout
x=[];a=[]
# Complete quiz functions retain their bodies; renamed only for linking.
for n,name in [(4,'times'),(8,'mystery'),(9,'badhalf')]:
 b=fences(q('isa-reading-assembly',n)['prompt'])[0];old={4:'times',8:'mystery',9:'half'}[n];x.append((name,re.sub(r'\b'+old+r'\b','_'+name,b)))
x.append(('unguarded',re.sub(r'\bf\b','_unguarded',fences(q('isa-loops-arrays-structs',10)['prompt'])[0]).replace('//',' #')))
a.append(('absbits',re.sub(r'\bf\b','_absbits',fences(q('isa-reading-assembly',6)['prompt'])[0])))
a.append(('post', '_post:\n'+fences(q('isa-risc-cisc',7)['prompt'])[0]+'\nadd w0,w1,w2\nret\n'))
# Flag/register snippets get setup and return scaffolding.
x.extend([('zeroextend','_zeroextend:\nmov rax,-1\n'+fences(q('isa-reading-assembly',1)['prompt'])[0]+'ret\n'),('unsignedcompare','_unsignedcompare:\nmov edi,-1\nmov esi,1\ncmp edi,esi\nseta al\nmovzx eax,al\nret\n'),('safeindex','_safeindex:\nmov esi,esi\n'+fences(q('isa-reading-assembly',10)['prompt'])[0]+'ret\n')])
results={}
for arch,items in [('x86_64',x),('arm64',a)]:
 objs=[]
 for name,body in items:
  p=out/(arch+'-quiz-'+name+'.s');p.write_text('.text\n'+('.intel_syntax noprefix\n' if arch=='x86_64' else '')+'.globl _'+name+'\n'+body);obj=p.with_suffix('.o');run(['clang','-arch',arch,'-c',str(p),'-o',str(obj)]);objs.append(str(obj))
 c='#include <assert.h>\n#include <stdint.h>\n#include <limits.h>\n#include <stdio.h>\n'
 if arch=='x86_64':
  c+='''extern long times(long);extern int mystery(uint64_t),badhalf(int),unguarded(unsigned),unsignedcompare(void),safeindex(int*,uint64_t);extern uint64_t zeroextend(void);
int main(void){long count=0;assert(times(7)==84);assert(zeroextend()==UINT64_C(0x12345678));assert(unsignedcompare()==1);assert(badhalf(-7)==-4);count+=4;
for(uint64_t i=0;i<65536;i++){assert(mystery(i)==__builtin_popcountll(i));++count;}assert(mystery(UINT64_MAX)==64);++count;
for(unsigned i=1;i<1000;i++){assert(unguarded(i)==i*(i+1)/2);++count;}
int array[]={3,7,9};assert(safeindex(array,UINT64_C(0x7777777700000001))==7);++count;printf("%ld\\n",count);}
'''
 else:
  c+='''extern uint32_t absbits(int32_t);extern int post(const int*);
int main(void){long count=0;for(int32_t i=-100000;i<=100000;i++){assert(absbits(i)==(uint32_t)(i<0?-i:i));++count;}assert(absbits(INT_MIN)==UINT32_C(0x80000000));++count;int x[]={7,9};assert(post(x)==16);++count;printf("%ld\\n",count);}
'''
 p=out/(arch+'-quiz-driver.c');p.write_text(c);exe=p.with_suffix('');run(['clang','-arch',arch,str(p),*objs,'-o',str(exe)]);results[arch]={'assertions':int(run([str(exe)])),'quizFixturesExecuted':len(items)}
# GNU/ELF assembler fixtures and relocations; compiler targets Linux, not Mach-O.
for name,b in [('got',fences((base/'isa-compile-link-load.md').read_text())[3]),('call','call puts\nret\n')]:
 p=out/(name+'-elf.s');p.write_text('.text\n.intel_syntax noprefix\n'+b);obj=p.with_suffix('.o');run(['clang','-target','x86_64-linux-gnu','-c',str(p),'-o',str(obj)]);dis=run(['objdump','-dr',str(obj)]);(out/(name+'-relocations.txt')).write_text(dis);assert 'GOTPCREL' in dis if name=='got' else 'R_X86_64_PLT32' in dis
# Reduced-width exhaustive analogue checks the unguarded loop's 2^w iterations from zero.
for w in range(1,13):
 n=0;s=0;steps=0;mask=(1<<w)-1
 while True:
  s=(s+n)&mask;n=(n-1)&mask;steps+=1
  if n==0:break
 assert steps==1<<w;assert s==1<<(w-1)
results['boundedModelAndRelocationAssertions']=26
results['totalAssertions']=26+sum(x['assertions'] for x in results.values() if isinstance(x,dict))
(out/'quiz-results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
