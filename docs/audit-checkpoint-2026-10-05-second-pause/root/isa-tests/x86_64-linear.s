.text
.globl _linear
.intel_syntax noprefix
# x86-64, Intel syntax (GCC/Clang)
_linear:
    lea   rax, [rdi + rdi*4 + 7]
    ret
