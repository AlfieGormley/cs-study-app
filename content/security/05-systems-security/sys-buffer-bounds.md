---
id: sys-buffer-bounds
title: Buffers, boundaries and off-by-one errors
level: basic
minutes: 5
sourceLesson: sys-memory-bugs
summary: A C buffer has an object boundary even when adjacent bytes are mapped and writable.
---

C and C++ provide pointer operations without universal run-time bounds or lifetime checks. Accessing an object outside its bounds or lifetime can cause **undefined behaviour**: the language does not promise a clean crash, a particular overwrite, or access to arbitrary addresses. Operating-system mappings and permissions still constrain hardware accesses. The C examples below use the C11/C17 model. Memory-safe languages add those bounds and lifetime checks for you; a later lesson in this module covers what that changes and what it leaves.

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

> [!analogy] Real-world analogy: a paper form with fixed boxes
> A form has a box of 16 squares for your name, and right next to it a small box marked "Staff use: approved". Nothing about paper stops a pen at the edge of a box, so a very long name can run on into the approval box.
>
> **How it maps:** The boxes are neighbouring objects in a stack frame or allocation. The pen is `strcpy`, which keeps writing until the source ends, because it is never told where the box ends. Text spilling into "approved" is an overflow changing a nearby authorisation flag or control pointer.
>
> **Where it stops:** A C string also needs one square for its terminating NUL, so 16 bytes hold only 15 letters. On a form everyone can see which box comes next. In memory the compiler, ABI and allocator decide what is adjacent, and the C standard promises no particular result for the invalid write: it may corrupt data, crash or appear to work.

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

`strcpy` requires enough destination space for all source bytes and the terminating NUL, the zero byte that marks the end of a C string. It is never told the destination's size, so it cannot check. A string therefore needs one byte more than its length: the longest name that fits in `buf[16]` is 15 characters, and a 40-character name needs 41 bytes, 25 more than `buf` holds.

Calling it with such a name violates that requirement; a neighbouring-data overwrite is one possible result, not a guaranteed execution trace. A common review mistake is a length check that accepts names of up to 16 characters: it forgets the NUL, so a 16-character name still writes one byte too many. Include `<string.h>` and `<stdio.h>` when compiling these function fragments.

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
