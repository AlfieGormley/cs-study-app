import os,ctypes,ctypes.util,json,errno,subprocess,pathlib
checks=[];gaps=[]
assert os.getpid()==1;checks.append('container entrypoint is PID 1 in its PID namespace')
ns={p.name:os.readlink(p) for p in pathlib.Path('/proc/self/ns').iterdir()};assert all(k in ns for k in ['pid','mnt','net','uts','ipc','user','cgroup','time']);checks.append('read actual eight namespace handles')
status=dict(l.split(':',1) for l in pathlib.Path('/proc/self/status').read_text().splitlines() if ':' in l);assert int(status['CapEff'].strip(),16)==0;checks.append('cap-drop ALL gives zero effective capability mask')
cg=pathlib.Path('/sys/fs/cgroup');vals={n:(cg/n).read_text().strip() for n in ['cpu.max','memory.max','pids.max']};assert vals=={'cpu.max':'50000 100000','memory.max':'268435456','pids.max':'100'},vals;checks.append('Docker resource settings yield specified cgroup v2 files')
libc=ctypes.CDLL(None,use_errno=True);prctl=libc.prctl;assert prctl(38,1,0,0,0)==0;assert prctl(39,0,0,0,0)==1;assert prctl(38,0,0,0,0)==-1;assert ctypes.get_errno()==errno.EINVAL;checks.append('no_new_privs set/read and cannot clear')
secpath=ctypes.util.find_library('seccomp')
if secpath:
 sc=ctypes.CDLL(secpath);sc.seccomp_init.argtypes=[ctypes.c_uint];sc.seccomp_init.restype=ctypes.c_void_p;sc.seccomp_rule_add.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_uint];sc.seccomp_load.argtypes=[ctypes.c_void_p];sc.seccomp_release.argtypes=[ctypes.c_void_p];sc.seccomp_syscall_resolve_name.argtypes=[ctypes.c_char_p];sc.seccomp_syscall_resolve_name.restype=ctypes.c_int
 before=int(status.get('Seccomp_filters','0'));ctx=sc.seccomp_init(0x7fff0000);assert ctx
 nums=[]
 for name in [b'keyctl',b'kexec_load']:
  num=sc.seccomp_syscall_resolve_name(name);assert num>=0;nums.append(num);assert sc.seccomp_rule_add(ctx,0x50000|errno.EPERM,num,0)==0
 assert sc.seccomp_load(ctx)==0;sc.seccomp_release(ctx)
 status2=dict(l.split(':',1) for l in pathlib.Path('/proc/self/status').read_text().splitlines() if ':' in l)
 assert int(status2['Seccomp_filters'])==before+1
 for num in nums:
  ctypes.set_errno(0);assert libc.syscall(ctypes.c_long(num),0,0,0,0,0,0)==-1;assert ctypes.get_errno()==errno.EPERM
 assert os.getppid()>=0;checks.append('real libseccomp equivalent calls load additional deny filter, release preserves filter, calls return EPERM')
 gaps.append('Outer container policy already restricts sensitive calls, so denial alone does not isolate which filter denied them; Seccomp_filters verifies stacking. C fragment was exercised via libseccomp ctypes ABI, not C compilation.')
else:gaps.append('libseccomp unavailable')
res=subprocess.run(['unshare','--user','--map-root-user','true'],capture_output=True,text=True);gaps.append('Unprivileged user namespace probe return '+str(res.returncode)+': '+res.stderr.strip())
gaps += ['No privileged namespace/mount/overlay mutation or host cgroup changes. No live KVM, Kubernetes, migration, passthrough, gVisor, Firecracker, Kata or historical exploit execution.']
print(json.dumps({'checks':checks,'count':len(checks),'cgroup':vals,'namespaceHandles':ns,'limitations':gaps},indent=2))
