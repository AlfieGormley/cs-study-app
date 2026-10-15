---
id: isa-array-layout-addresses
title: Array strides, row-major layout and signed indices
level: intermediate
minutes: 4
sourceLesson: isa-loops-arrays-structs
summary: Compute one- and two-dimensional element addresses and read their assembly.
---

The target is Linux LP64 with four-byte `int` and eight-byte `long`. These are byte addresses, and every illustrated access assumes valid object bounds.

## Arrays: address arithmetic

Element `a[i]` starts at a fixed distance from the start of the array:

```formula
addr = base + i × s
addr = 0x1000 + 5 × 4 = 0x1014
where
addr: the byte address where element i starts
base: the address of element 0, the start of the array (here 0x1000, hexadecimal)
i: the element index, counting from 0 (here 5)
s: the element size in bytes (here 4, for an `int`)
In words: skip i whole elements of s bytes each; element 5 of an int array at 0x1000 starts 20 bytes in, at 0x1014.
```

C’s typed expression `a + i` already applies that scaling. x86-64 addressing modes can scale an index by 1, 2, 4 or 8, which covers `char`, `short`, `int`/`float` and `long`/`double`/pointers in a single operand. ARM64 does the same with a shifted register: `ldr w9, [x0, x1, lsl #2]` loads `a[i]` for a 4-byte `int`.

### 2-D arrays

C stores multidimensional arrays in **row-major** order: rows one after another. For `int a[R][C]` (R rows of C columns), with 4-byte `int`, element `a[i][j]` sits after i complete rows and j more elements:

```formula
addr = base + 4(iC + j)
addr = base + (2 × 3 + 1) × 4 = base + 28
where
addr: the byte address of element a[i][j]
base: the address of a[0][0], where the array starts
i: the row index, counting from 0 (here 2)
j: the column index, counting from 0 (here 1)
C: the number of columns per row (here 3)
4: the size of an `int` in bytes
In words: count how many elements come before a[i][j] in the long row-by-row line (2 rows of 3, plus 1, makes 7), then turn that count into bytes.
```

This is byte arithmetic, not a literal typed C pointer expression. The listing below has C = 3.

```
// int get(int a[][3], long i, long j)
get:
    lea   rax, [rsi + 2*rsi]   # i*3
    lea   rax, [rdi + 4*rax]   # &a[i]
    mov   eax, [rax + 4*rdx]   # a[i][j]
    ret
```

The compiler computes `i*3` with `lea` (no multiply), turns that into the address of row `i` (each row is 3 × 4 = 12 bytes, so row i starts 12 × i bytes in), then indexes the column. Only the column count `C` matters; the number of rows never appears, which is why C lets you omit the first dimension in a parameter.

The order of your loops matters a lot for row-major data: walking `j` in the inner loop touches consecutive addresses, while walking `i` in the inner loop jumps 12 bytes (or 4 KB for a 1024-column `int` array) each step. That difference shows up in cache behaviour, covered in the memory-hierarchy module.

### Signed indices

If the index is a 32-bit `int` passed in from outside, it must be sign-extended before use as a 64-bit offset:

```
// long at(long *a, int i)
at:
    movsxd rax, esi       # sign-extend i
    mov   rax, [rdi + 8*rax]
    ret
```

Inside a loop where the compiler can prove `i` never goes negative, it usually promotes the counter to 64 bits once and drops the extension.

## Key takeaways
- Array indexing scales the index by the element’s byte size.
- A C multidimensional array stores complete rows consecutively.
- A signed narrow index needs its value preserved when widened.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [Branch table — Wikipedia](https://en.wikipedia.org/wiki/Branch_table)
- [Data structure alignment — Wikipedia](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Strength reduction — Wikipedia](https://en.wikipedia.org/wiki/Strength_reduction)
- [Loop unrolling — Wikipedia](https://en.wikipedia.org/wiki/Loop_unrolling)
- [Computer Systems: A Programmer's Perspective (CS:APP), chapter 3](https://csapp.cs.cmu.edu/)
