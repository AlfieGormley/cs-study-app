.text
.intel_syntax noprefix
.globl _times
# long _times(long x)
_times:
    lea   rax, [rdi + rdi*2]
    shl   rax, 2
    ret
