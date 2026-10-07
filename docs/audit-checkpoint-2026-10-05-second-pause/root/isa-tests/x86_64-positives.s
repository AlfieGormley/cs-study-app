.text
.globl _positives
.intel_syntax noprefix
# long _positives(const long *a, long n)
_positives:
    xor   eax, eax         # c = 0
    test  rsi, rsi
    jle   .Ldone           # n <= 0: done
    xor   ecx, ecx         # i = 0
.Lloop:
    xor   edx, edx         # edx = 0
    cmp   qword ptr [rdi + rcx*8], 0
    setg  dl               # dl = (a[i] > 0)
    add   rax, rdx         # c += dl
    inc   rcx              # i++
    cmp   rcx, rsi
    jne   .Lloop           # i != n
.Ldone:
    ret
