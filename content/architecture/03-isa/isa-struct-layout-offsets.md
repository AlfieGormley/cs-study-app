---
id: isa-struct-layout-offsets
title: Struct fields, padding and array-of-struct access
level: intermediate
minutes: 4
sourceLesson: isa-loops-arrays-structs
summary: Measure struct padding and recover strides and field offsets from loads.
---

These layouts assume ordinary, unpacked Linux LP64 scalar types: one-byte char, four-byte int, eight-byte long and two-byte short, with their ABI alignments. Other ABIs and packing directives can change the result.

## Structs: fixed offsets

A struct is just a block of memory with each field at a **fixed offset** known at compile time. Each field has a type- and ABI-defined alignment, not necessarily equal to its size, and the struct's total size is rounded up to a multiple of its largest alignment so arrays of it stay aligned.

```
struct S {
    char  tag;   // offset 0
                 // 3 bytes padding
    int   n;     // offset 4
    long  v;     // offset 8
    short k;     // offset 16
                 // 6 bytes padding
};               // sizeof = 24
```

Fields add up to 1 + 4 + 8 + 2 = 15 bytes, yet the struct takes 24. Reordering from largest to smallest (`long`, `int`, `short`, `char`) leaves no gaps between fields, so only the end needs rounding up:

```formula
s_S = ⌈s_f / A⌉ × A
s_S = ⌈15 / 8⌉ × 8 = 2 × 8 = 16
Δ = (24 − 16) × 1000000 = 8000000
where
s_S: the size of the struct in bytes (what `sizeof` reports)
s_f: the bytes used by the fields plus any padding between them: 15, with no gaps in this order
A: the struct's alignment: the largest alignment of any field, 8 for the `long`
⌈ ⌉: ceiling: round up to the next whole number
Δ: the bytes saved across an array of a million structs
In words: round the fields' total up to the next multiple of the largest alignment, so 15 bytes become 16, and a million structs shrink by 8,000,000 bytes.
```

The rounding only accounts for tail padding; in the original order, the 3 bytes after `tag` are padding between fields, which is why that layout needs 24. A full front-to-back byte scan has roughly one-third less data; actual cache-line traffic depends on alignment and which fields are accessed.

Field access is a constant displacement: `p->v` is `mov rax, [rdi + 8]`. Array-of-struct access combines both ideas:

```
// int getn(struct S *p, long i)
// returns p[i].n
getn:
    lea   rax, [rsi + 2*rsi]       # i*3
    mov   eax, [rdi + 8*rax + 4]   # p+24i+4
    ret
```

```formula
addr = p + 24i + 4
addr = p + 8 × (3 × i) + 4
addr = p + 24 × 2 + 4 = p + 52
where
addr: the address of p[i].n
p: the address of the first struct in the array
i: which struct, counting from 0 (here 2)
24: sizeof(struct S): the stride from one struct to the next
4: the offset of field n inside each struct
In words: jump over i whole 24-byte structs, then 4 bytes into the one you want.
```

24 isn't a legal scale, so the compiler splits it as `3 × 8`: an `lea` for the 3 and the addressing mode's scale for the 8. The `+ 4` is the offset of `n`. Reading this backwards is a standard reverse-engineering skill: under the assumed direct p[i].field access, stride 24 and offset 4 reveal element size and field offset; they do not uniquely reconstruct the original type or declaration.

## Key takeaways
- Field offsets and alignment come from the target ABI.
- Tail padding makes every array element correctly aligned.
- A non-power-of-two stride may use LEA plus a legal addressing scale.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [Branch table — Wikipedia](https://en.wikipedia.org/wiki/Branch_table)
- [Data structure alignment — Wikipedia](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Strength reduction — Wikipedia](https://en.wikipedia.org/wiki/Strength_reduction)
- [Loop unrolling — Wikipedia](https://en.wikipedia.org/wiki/Loop_unrolling)
- [Computer Systems: A Programmer's Perspective (CS:APP), chapter 3](https://csapp.cs.cmu.edu/)
