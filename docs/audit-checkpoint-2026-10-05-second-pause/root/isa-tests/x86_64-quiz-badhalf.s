.text
.intel_syntax noprefix
.globl _badhalf
_badhalf:              # int _badhalf(int x)
    mov   eax, edi
    sar   eax, 1
    ret
