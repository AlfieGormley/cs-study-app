---
id: rep-alignment-rules
title: Natural alignment and unaligned accesses
level: advanced
minutes: 3
summary: Natural alignment is a divisibility condition on an address.
sourceLesson: rep-memory-layout
---

This unit continues the preceding material on eight-bit bytes and multibyte object representations.

## Alignment

A value is **naturally aligned** if its address is a whole multiple of its own size:

```formula
A mod n = 0
where
A: the address where the value starts, counted in bytes
n: the size of the value in bytes (1, 2, 4 or 8 for ordinary scalar types)
mod: modulo, the remainder after dividing A by n
In words: an aligned address divides exactly by the value's size, leaving no remainder.
```

So a 4-byte `int` belongs at 0, 4, 8, and so on, and an 8-byte `double` at multiples of 8. Because sizes are powers of two, this is also a bit test: an address is a multiple of 8 exactly when its low 3 bits are 0.

### Why hardware cares

A CPU can issue byte-sized loads. Cacheable misses commonly transfer whole cache lines, often 64 bytes, while individual load and store instructions, and uncached or device accesses, have additional size and alignment rules.

```
cache line boundary at 64
          ...60 61 62 63|64 65 66 67...
aligned int at 60:  [==========]
misaligned at 62:         [====|====]
                         spans 2 lines
```

When a power-of-two access size is no larger than and divides the line/page size, natural alignment keeps that access within a boundary. This does not mean every aligned object, arbitrarily wide access or generated instruction requires only one memory transaction. A misaligned one may need two accesses, two cache lines, even two page translations. The consequences depend on the architecture:

- **x86** handles many ordinary misaligned loads in hardware; alignment-requiring instruction forms and alignment-checking modes can fault. Within a cache line they are usually as fast as aligned ones; crossing a line costs extra; crossing a page costs more. A misaligned `lock`-prefixed atomic that spans two cache lines (a **split lock**) stalls the whole memory system, and recent Linux kernels can warn about or penalise processes that do it.
- **ARMv8 (AArch64)** handles most misaligned ordinary loads and stores in hardware, but its exclusive and atomic instructions generally require aligned addresses and fault otherwise.
- **Strict-alignment targets**, including relevant older ARM, SPARC and microcontroller configurations, can fault on unsupported unaligned accesses. Linux may emulate an access or report a signal such as SIGBUS; some hardware instead performs an unintended access, so consult the target rules.
- **Atomicity** depends on the architecture, memory type and access. For example, x86-64 guarantees indivisibility for suitably aligned ordinary 8-byte loads/stores to ordinary write-back memory. A misaligned access can lack that guarantee. In C/C++, hardware non-tearing does not permit data races: use atomics or synchronisation for conflicting cross-thread accesses.

In C, conversion to an object-pointer type with unmet alignment requirements is already undefined, and dereferencing misaligned storage is not made valid by the hardware, even on x86, and compilers vectorise code on the assumption that it does not happen. Use memcpy into a suitably typed local variable for unaligned representation copies, with valid bounds and a valid destination representation; byte order still needs handling. Compilers can lower fixed-size copies to ordinary loads where the target allows them.

## Key takeaways
- Natural alignment is a divisibility condition on an address.
- Hardware tolerance does not make a misaligned C pointer valid.
- Non-tearing hardware access does not permit a C data race.

## Further reading
- [Linux unaligned-memory documentation](https://docs.kernel.org/core-api/unaligned-memory-access.html)
- [Python struct documentation](https://docs.python.org/3/library/struct.html)
