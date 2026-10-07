.text
.intel_syntax noprefix
mov  rax, [rip + environ@GOTPCREL]
mov  rax, [rax]     # value of environ
