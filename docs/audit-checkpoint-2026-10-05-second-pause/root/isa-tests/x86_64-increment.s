.text
.globl _increment
.intel_syntax noprefix
_increment:
# rdi = a, rsi = i
add  dword ptr [rdi + rsi*4], 1

ret
