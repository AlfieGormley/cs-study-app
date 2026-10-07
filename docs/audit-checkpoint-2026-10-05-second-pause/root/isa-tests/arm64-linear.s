.text
.globl _linear
// ARM64
_linear:
    add   x8, x0, x0, lsl #2   // x8 = x*5
    add   x0, x8, #7
    ret
