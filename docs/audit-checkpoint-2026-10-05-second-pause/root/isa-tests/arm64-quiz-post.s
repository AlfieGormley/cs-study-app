.text
.globl _post
_post:
ldr  w1, [x0], #4
ldr  w2, [x0]

add w0,w1,w2
ret
