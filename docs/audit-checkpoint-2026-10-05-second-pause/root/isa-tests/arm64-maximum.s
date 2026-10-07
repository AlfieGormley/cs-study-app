.text
.globl _maximum
// int _maximum(int a, int b)
_maximum:
    cmp   w0, w1
    csel  w0, w0, w1, gt   // a > b ? a : b
    ret
