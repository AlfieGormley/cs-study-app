.text
.globl _maximum
.intel_syntax noprefix
# int _maximum(int a, int b)
_maximum:
    mov   eax, esi       # eax = b
    cmp   edi, esi       # compare a with b
    cmovg eax, edi       # if a > b: eax = a
    ret
