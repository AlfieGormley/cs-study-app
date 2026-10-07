.text
.globl _getn
.intel_syntax noprefix


_getn:
    lea   rax, [rsi + 2*rsi]       # i*3
    mov   eax, [rdi + 8*rax + 4]   # p+24i+4
    ret
