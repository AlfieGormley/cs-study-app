.text
.globl _identity
.intel_syntax noprefix
# long _identity(long x), -O0 style
_identity:
    push  rbp          # save caller's rbp
    mov   rbp, rsp     # rbp = frame base
    sub   rsp, 32      # room for locals
    mov   qword ptr [rbp - 8], rdi  # x
    mov   rax, qword ptr [rbp - 8]
    leave              # rsp = rbp, pop rbp
    ret
