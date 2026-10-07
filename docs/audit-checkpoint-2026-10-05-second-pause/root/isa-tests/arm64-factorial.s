.text
.globl _factorial
// long _factorial(long n)
_factorial:
    stp   x29, x30, [sp, #-32]!
    mov   x29, sp
    str   x19, [sp, #16]   // callee-saved
    mov   x19, x0          // keep n
    mov   x0, #1
    cmp   x19, #1
    b.le  .Lret            // n <= 1
    sub   x0, x19, #1
    bl    _factorial             // x0 = _factorial(n-1)
    mul   x0, x0, x19
.Lret:
    ldr   x19, [sp, #16]
    ldp   x29, x30, [sp], #32
    ret
