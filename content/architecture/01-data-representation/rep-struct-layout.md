---
id: rep-struct-layout
title: Struct member offsets and tail padding
level: advanced
minutes: 3
summary: The ABI determines member alignment and struct layout.
sourceLesson: rep-memory-layout
---

This unit continues the preceding material on eight-bit bytes and multibyte object representations.

## Struct padding

A C compiler lays out struct members **in declaration order** (it may not reorder them) and inserts **padding** so that each member is aligned. For ordinary unpacked structs without bit-fields, explicit over-alignment or unusual members, mainstream ABIs such as x86-64 System V and AArch64 use these rules:

1. Each member starts at an offset that is a multiple of its alignment.
2. The struct's alignment is the largest alignment of its members.
3. The struct's size is rounded up to a multiple of its alignment (**tail padding**).

### Worked example

```c
/* ABI alignment leaves gaps between */
/* fields. */
struct A {
    char a;   /* 1 byte  */
    int  b;   /* 4 bytes */
    char c;   /* 1 byte  */
};
```

Lay it out byte by byte:

```
offset 0     a
offset 1-3   padding (b needs 4)
offset 4-7   b
offset 8     c
offset 9-11  tail padding
sizeof = 12, alignment 4
```

The offsets follow from rounding up to the next multiple of each alignment:

```formula
o = ⌈p / a⌉a
o_b = ⌈1 / 4⌉ × 4 = 4
S = ⌈9 / 4⌉ × 4 = 12
where
o: the offset where a member starts, in bytes from the start of the struct
p: the first free offset, just after the previous member
a: the member's alignment in bytes (4 for int)
o_b: the offset of b: the first free byte is 1, rounded up to a multiple of 4
S: the struct's size: the 9 bytes used so far, rounded up to a multiple of the struct's alignment, 4
⌈ ⌉: ceiling: round up to the next whole number, so ⌈1/4⌉ = 1 and ⌈9/4⌉ = 3
In words: each member moves forward to the next multiple of its alignment, and the whole struct is rounded up the same way.
```

Six bytes of data, six bytes of padding. Why the tail padding? In an array `struct A arr[2]`, `arr[1]` starts sizeof(struct A) **bytes** after arr[0], namely `(unsigned char *)arr + sizeof(struct A)`. The expression `arr + sizeof(struct A)` would incorrectly scale that count by the element size again. If the size were 9, `arr[1].b` would sit at offset 13, misaligned. Rounding the size to 12 keeps every element aligned.

Reorder the members largest first and the padding mostly vanishes:

```c
/* Place the widest member first. */
struct B {
    int  b;   /* offset 0 */
    char a;   /* offset 4 */
    char c;   /* offset 5 */
};            /* sizeof = 8 */
```

With 8-byte members the effect is larger:

| Struct | Layout | Size |
|---|---|---|
| `{char; double; char}` | 1+7+8+1+7 | 24 |
| `{double; char; char}` | 8+1+1+6 | 16 |

For an array of ten million of them, that is 240 MB against 160 MB, and more of the useful data fits in each cache line. Tools such as `pahole` (from the `dwarves` package) print a struct's layout with every hole, and Clang's `-Wpadded` warns about padding.

You can always check the compiler's decisions:

```c
/* Inspect size, member offset / */
/* alignment. */
#include <stddef.h>
printf("%zu %zu %zu\n",
       sizeof(struct A),
       offsetof(struct A, c),
       _Alignof(struct A));
/* 12 8 4 */
```

> [!note] ABI-dependent
> Alignment of each type comes from the platform ABI, not the C standard. On 32-bit x86 Linux (i386 System V), a `double` inside a struct is only 4-byte aligned, so `{char; double; char}` is 16 bytes there, not 24. Code that shares binary structs between platforms cannot rely on the layout.

## Key takeaways
- The ABI determines member alignment and struct layout.
- Tail padding preserves alignment in an array.
- Reordering members can reduce wasted space.

## Further reading
- [Linux unaligned-memory documentation](https://docs.kernel.org/core-api/unaligned-memory-access.html)
- [Python struct documentation](https://docs.python.org/3/library/struct.html)
