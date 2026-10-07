.text
.globl _positives
// long _positives(const long *a, long n)
_positives:
    mov   x8, #0           // c = 0
    cmp   x1, #1
    b.lt  .Ldone           // n < 1: done
.Lloop:
    ldr   x9, [x0], #8     // x9 = *a++
    cmp   x9, #0
    cinc  x8, x8, gt       // if > 0: c++
    subs  x1, x1, #1       // n--, set flags
    b.ne  .Lloop
.Ldone:
    mov   x0, x8
    ret
