.text
.globl _half
.intel_syntax noprefix
# int _half(int x) { return x / 2; }
_half:
    mov   eax, edi
    shr   eax, 31        # 1 if x<0 else 0
    add   eax, edi       # bias negatives
    sar   eax, 1         # arithmetic shift
    ret
