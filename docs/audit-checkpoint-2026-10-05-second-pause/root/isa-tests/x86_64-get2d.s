.text
.globl _get2d
.intel_syntax noprefix

_get2d:
    lea   rax, [rsi + 2*rsi]   # i*3
    lea   rax, [rdi + 4*rax]   # &a[i]
    mov   eax, [rax + 4*rdx]   # a[i][j]
    ret
