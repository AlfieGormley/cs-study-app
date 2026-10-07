.text
.globl _increment
_increment:
// x0 = a, x1 = i
ldr  w8, [x0, x1, lsl #2]   // w8 = a[i]
add  w8, w8, #1
str  w8, [x0, x1, lsl #2]   // a[i] = w8

ret
