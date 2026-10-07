.text
.globl _linearatt
# x86-64, AT&T syntax (GDB, objdump)
_linearatt:
    leaq  7(%rdi,%rdi,4), %rax
    ret
