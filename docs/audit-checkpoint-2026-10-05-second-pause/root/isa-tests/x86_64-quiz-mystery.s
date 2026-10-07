.text
.intel_syntax noprefix
.globl _mystery
_mystery:
    xor   eax, eax
.L1:
    test  rdi, rdi
    je    .L2
    lea   rcx, [rdi - 1]
    and   rdi, rcx
    inc   eax
    jmp   .L1
.L2:
    ret
