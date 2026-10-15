---
id: sys-buffer-bounds
title: Buffers, boundaries and off-by-one errors
level: basic
minutes: 5
sourceLesson: sys-memory-bugs
summary: A C buffer has an object boundary even when adjacent bytes are mapped and writable.
---

C and C++ provide pointer operations without universal run-time bounds or lifetime checks. Accessing an object outside its bounds or lifetime can cause **undefined behaviour**: the language does not promise a clean crash, a particular overwrite, or access to arbitrary addresses. Operating-system mappings and permissions still constrain hardware accesses. The C examples below use the C11/C17 model.

These bugs can expose secrets or alter decisions as well as crash programs. Chromium reports that memory unsafety accounted for around 70% of a sample of 912 high/critical Stable-channel security bugs since 2015. This is a historical, project-specific sample, not a current universal percentage.

## Why a bug becomes a vulnerability

The diagram is an illustrative conventional process layout, not a C requirement (addresses increase upwards). Real systems may use multiple heap mappings; stack direction, saved registers and return-address storage depend on the architecture and compiler.

```
high  +------------------------+
      | stack (grows down)     |
      |  locals, saved regs,   |
      |  return addresses      |
      +------------------------+
      |         ...            |
      +------------------------+
      | heap (grows up)        |
      |  malloc'd objects and  |
      |  allocator metadata    |
      +------------------------+
      | globals, .data, .bss   |
      | program code (.text)   |
low   +------------------------+
```

The security concern is proximity: a buffer can share an allocation or stack frame with sensitive data. Depending on the implementation, nearby data can include control pointers or allocator metadata. Corrupting an authorisation flag can also compromise a program without hijacking control flow.

So a bug that writes past the end of a buffer does not just corrupt "some data". It can overwrite something that decides **what the program does next**. That is the step from crash to compromise, and it is why the defences later in this module focus on protecting that control data.

Two important families are spatial errors and temporal errors. This two-family split does not describe every issue below; uninitialised-value use also needs separate attention.

| Family | Question it breaks | Examples |
|---|---|---|
| Spatial | Is this address inside the object? | Overflow, OOB read |
| Temporal | Is the object still alive? | Use-after-free, double free |

## Stack buffer overflow

The classic bug is copying input into a fixed-size buffer without checking its length.

```c
void greet(const char *name) {
    char buf[16];
    /* BUG: capacity is never checked. */
    strcpy(buf, name);
    /* Invalid copy: no promised output. */
    printf("Hello, %s\n", buf);
}
```

`strcpy` requires enough destination space for all source bytes and the terminating NUL, the zero byte that marks the end of a C string. It is never told the destination's size, so it cannot check. The space needed, and how far a copy goes past the end, are:

```formula
B_need = L + 1
B_over = B_need − C
B_need = 40 B + 1 B = 41 B
B_over = 41 B − 16 B = 25 B
where
B_need: the destination space strcpy needs, in bytes (B)
L: the length of the source string in bytes, not counting its NUL; 40 B for this name
1: the one extra byte for the terminating NUL
B_over: how many bytes the copy needs beyond the destination's capacity; anything above 0 means the call is invalid
C: the destination's capacity in bytes; buf is declared char buf[16], so 16 B
B: byte, a unit of 8 bits of memory
In words: strcpy needs the string's length plus one byte for the NUL, so a 40-byte name needs 41 bytes, 25 more than the 16-byte buf holds.
```

So a valid 40-byte name exceeds `buf` by 25 bytes, and the longest name that fits is 15 bytes (15 + 1 = 16). Calling it here violates that requirement; a neighbouring-data overwrite is one possible result, not a guaranteed execution trace. Include `<string.h>` and `<stdio.h>` when compiling these function fragments.

### Off-by-one errors

Many overflows are a single element too far:

```c
char id[8];
/* BUG: index eight is out of bounds. */
for (int i = 0; i <= 8; i++)
    id[i] = src[i];
```

With a source of at least nine bytes, the faulty loop attempts indices 0 through 8: nine writes into an eight-element array, whose valid indices are 0 through 7. For an eight-byte raw copy, use `i < 8` and a source of at least eight bytes. That correction does not create a NUL-terminated string: reserve and write a terminator if string APIs will consume the result.

## Key takeaways
- A C buffer has an object boundary even when adjacent bytes are mapped and writable.
- Copying a string requires space for its terminating NUL.
- An eight-element array has valid indices zero through seven; a raw copy does not create a string.

## Further reading
- [C11 committee draft: objects and library contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Memory safety — Chromium](https://www.chromium.org/Home/chromium-security/memory-safety/)
