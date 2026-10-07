.text
.globl _at
.intel_syntax noprefix

_at:
    movsxd rax, esi       # sign-extend i
    mov   rax, [rdi + 8*rax]
    ret
