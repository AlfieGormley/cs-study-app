import json,re,subprocess,tempfile,os,math
from pathlib import Path
root=Path('content/os/01-processes');tmp=Path('/tmp/cs-study-audit-full/os01-host');tmp.mkdir(exist_ok=True)
headers='#include <stdio.h>\n#include <stdlib.h>\n#include <unistd.h>\n#include <fcntl.h>\n#include <errno.h>\n#include <string.h>\n#include <signal.h>\n#include <sys/wait.h>\n#include <sys/mman.h>\n#include <time.h>\n'
n=0;programs=[]
def ck(b):
 global n
 assert b;n+=1
def run(name,body,wrap=False,args=[]):
 source=headers+('int main(void){\n'+body+'\nreturn 0;}' if wrap else body)
 p=tmp/(name+'.c');p.write_text(source);binary=tmp/name
 c=subprocess.run(['cc','-O0',str(p),'-o',str(binary)],capture_output=True,text=True);assert c.returncode==0,c.stderr
 p=subprocess.run([str(binary),*args],cwd=tmp,capture_output=True,text=True,timeout=20)
 programs.append({'name':name,'returncode':p.returncode,'stdout':p.stdout[:200]});return p
blocks=lambda id:re.findall(r'```c\n(.*?)```',(root/(id+'.md')).read_text(),re.S)
(tmp/'notes.txt').write_text('copied example\n');ck(run('cat_example',blocks('proc-what-os-does')[0]).stdout=='copied example\n')
ck(run('layout',blocks('proc-process-abstraction')[0]).returncode==0)
ck(run('fork_private',blocks('proc-fork-exec-wait')[0]).stdout=='child 15\nparent 10\n')
ck(run('exec_ls',blocks('proc-fork-exec-wait')[1],True).returncode==0)
ck(run('redirect',blocks('proc-fork-exec-wait')[2],True).returncode==0);ck((tmp/'out.txt').stat().st_size>0)
# This specifically catches the old close(fd) bug when open returns stdout itself.
ck(run('redirect_closed_stdout','close(1);\n'+blocks('proc-fork-exec-wait')[2],True).returncode==0);ck((tmp/'out.txt').stat().st_size>0)
ck(run('wait_status','pid_t pid=fork(); if(pid==0) _exit(300);\n'+blocks('proc-fork-exec-wait')[3],True).stdout=='exit 44\n')
ck(run('pipe',blocks('proc-ipc')[0],True).stdout=='hello\n')
# Shorter iteration count avoids treating this host run as a benchmark.
ck(run('pingpong',blocks('proc-context-switching')[0].replace('#define N 100000','#define N 1000')).returncode==0)
qfile=lambda id:json.loads((root/(id+'.questions.json')).read_text())
for id,num,expected in [('proc-fork-exec-wait',1,4),('proc-fork-exec-wait',6,3)]:
 q=next(x for x in qfile(id) if x['id'].endswith('-q'+str(num)));code=re.search(r'```c\n(.*?)```',q['prompt'],re.S)[1]
 out=run('quiz_fork'+str(num),code,'int main' not in code).stdout.splitlines();ck(len(out)==expected)
 if num==6:ck(out.count('A')==1 and out.count('B')==2)
# Explicit buffering examples rather than relying on terminal environment.
code='setvbuf(stdout,NULL,_IOFBF,4096);printf("a\\n");fork();printf("b\\n");'
ck(run('fork_buffered',code,True).stdout=='a\nb\na\nb\n')
ck(run('fork_linebuffered',code.replace('_IOFBF','_IOLBF'),True).stdout=='a\nb\nb\n')
# Pipe byte stream concatenation and partial read, no message-boundary preservation.
ck(run('pipe_stream','int p[2];char b[20]={0};pipe(p);write(p[1],"HELLO",5);write(p[1],"WORLD",5);int n=read(p[0],b,7);printf("%d %s\\n",n,b);',True).stdout=='7 HELLOWO\n')
# Shared mapping stays shared across fork, unlike private heap/local examples.
ck(run('shared_fork','int *p=mmap(NULL,4096,PROT_READ|PROT_WRITE,MAP_SHARED|MAP_ANON,-1,0);*p=1;pid_t c=fork();if(!c){*p=42;_exit(0);}waitpid(c,NULL,0);printf("%d\\n",*p);',True).stdout=='42\n')
for x,y in [(2**3,8),(300&255,44),(1024**3/4096*2*500e-9-1024**3/1024**2*2*500e-9,.26112),(1-2.5/3,1/6),(8*1024,8192),(30*1024**3/4096*8,60*1024**2),(512*1024/64*15,122880),(256*1024/64*20,81920),(.5/100000/2,2.5e-6),(10000/16,625),(65536/4096,16)]:ck(math.isclose(x,y))
qs=[q for p in root.glob('*.questions.json') for q in json.loads(p.read_text())];ck(len(qs)==67 and len({q['id'] for q in qs})==67)
for q in qs:
 ans=q['answer'] if isinstance(q['answer'],list) else [q['answer']];assert all(0<=i<len(q['options']) for i in ans)
r={'host':os.uname().sysname+' '+os.uname().machine,'assertionsPassed':n,'programs':programs,'limitations':'POSIX examples exercised on macOS, not proof of Linux ABI/defaults. Timing output not used as a benchmark. Linux-specific and schematic snippets require separate checks.'}
(tmp/'results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'host':r['host'],'assertionsPassed':n,'programsExecuted':len(programs),'questionsValidated':len(qs)}))
