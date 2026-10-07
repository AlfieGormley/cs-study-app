.text
.globl _sum
_sum:
    cmp   x1, #1
    b.lt  .Lzero          // n < 1
    mov   x8, xzr         // s = 0
.Lloop:
    ldr   x9, [x0], #8    // load; advance 8 bytes
    subs  x1, x1, #1      // n--, set flags
    add   x8, x9, x8
    b.ne  .Lloop          // until n == 0
    mov   x0, x8
    ret
.Lzero:
    mov   x0, #0
    ret
