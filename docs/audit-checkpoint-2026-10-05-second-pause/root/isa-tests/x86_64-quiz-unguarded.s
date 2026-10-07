.text
.intel_syntax noprefix
.globl _unguarded
 # int _unguarded(unsigned n), n in edi
_unguarded:
    xor   eax, eax
.L:
    add   eax, edi
    dec   edi
    jne   .L
    ret
