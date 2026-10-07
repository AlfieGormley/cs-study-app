.text
.globl _factorial
.intel_syntax noprefix
# long _factorial(long n)
_factorial:
    push  rbx          # save callee-saved
    mov   rbx, rdi     # keep n across call
    mov   eax, 1
    cmp   rdi, 1
    jle   .Lret        # n <= 1: return 1
    lea   rdi, [rdi - 1]
    call  _factorial         # rax = _factorial(n-1)
    imul  rax, rbx     # rax = n * rax
.Lret:
    pop   rbx
    ret
