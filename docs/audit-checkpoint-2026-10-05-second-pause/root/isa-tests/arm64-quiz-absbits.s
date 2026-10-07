.text
.globl _absbits
// int _absbits(int x)
_absbits:
    cmp   w0, #0
    cneg  w0, w0, lt
    ret
