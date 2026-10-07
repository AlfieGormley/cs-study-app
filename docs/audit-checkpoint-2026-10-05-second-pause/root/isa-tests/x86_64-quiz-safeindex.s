.text
.intel_syntax noprefix
.globl _safeindex
_safeindex:
mov esi,esi
    mov   eax, dword ptr [rdi + rsi*4]
ret
