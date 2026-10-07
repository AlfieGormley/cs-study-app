.text
.globl _choose2
.intel_syntax noprefix
_choose2:
    xor   eax, eax
    test  edi, edi
    setle al           # al = (x <= 0)
    inc   eax          # 1 or 2

ret
