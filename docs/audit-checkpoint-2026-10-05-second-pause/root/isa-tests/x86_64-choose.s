.text
.globl _choose
.intel_syntax noprefix
_choose:

    test  edi, edi
    jle   .Lelse       # skip if x <= 0
    mov   eax, 1
    jmp   .Ldone
.Lelse:
    mov   eax, 2
.Ldone:

ret
