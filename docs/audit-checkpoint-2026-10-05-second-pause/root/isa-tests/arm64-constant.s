.text
.globl _constant
_constant:
mov   x0, #0xcdef            // movz
movk  x0, #0x90ab, lsl #16   // keep rest
movk  x0, #0x5678, lsl #32
movk  x0, #0x1234, lsl #48
// x0 = 0x1234567890abcdef

ret
