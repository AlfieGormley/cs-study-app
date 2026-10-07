.text
.intel_syntax noprefix
.globl _unsignedcompare
_unsignedcompare:
mov edi,-1
mov esi,1
cmp edi,esi
seta al
movzx eax,al
ret
