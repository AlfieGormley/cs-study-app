.text
.globl _sum
.intel_syntax noprefix
_sum:
    test  rsi, rsi
    jle   .Lzero          # n <= 0
    xor   ecx, ecx        # i = 0
    xor   eax, eax        # s = 0
.Lloop:
    add   rax, [rdi + 8*rcx]
    inc   rcx             # i++
    cmp   rsi, rcx
    jne   .Lloop          # until i == n
    ret
.Lzero:
    xor   eax, eax
    ret
