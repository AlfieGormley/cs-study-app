---
id: rep-endian-byte-order
title: Values and their byte order
level: advanced
minutes: 3
summary: Endianness orders bytes of a multibyte representation.
sourceLesson: rep-memory-layout
---

The previous lessons decided what bits mean. This one is about where they sit. In the common byte-addressed model used here (eight bits per byte), memory is an array of bytes, each with its own address, but most values are wider than a byte. A 32-bit integer occupies four consecutive addresses, which raises three questions:

1. In what **order** do its four bytes go? (Endianness.)
2. At which **addresses** may it start? (Alignment.)
3. When several values are grouped in a struct, what **gaps** does the compiler leave? (Padding.)

None of this is visible when your code does ordinary arithmetic. All of it becomes visible the moment you read raw bytes: a network packet, a binary file, a memory dump, or one type reinterpreted as another.

## Endianness

Take the 32-bit value `0x12345678`, stored at address 100. The **most significant byte** is `0x12`; the **least significant** is `0x78`.

```
address:        100  101  102  103
big-endian:      12   34   56   78
little-endian:   78   56   34   12
```

- **Big-endian** stores the most significant byte at the lowest address, the way we write numbers.
- **Little-endian** stores the least significant byte first.

The names come from *Gulliver's Travels*, where two nations go to war over which end of a boiled egg to crack. Danny Cohen borrowed them in a 1980 note, "On Holy Wars and a Plea for Peace", because the choice is about as arbitrary.

### Who uses which

| Little-endian | Big-endian |
|---|---|
| x86, x86-64 | TCP/IP multi-byte header fields |
| ARM (in practice) | IBM z/Architecture |
| Common RISC-V systems (ISA also defines other modes) | PNG integers, JPEG marker-segment lengths |
| Windows bitmap (.bmp) and ZIP fields specified little-endian | Java class-file multibyte items |

ARM, PowerPC and MIPS are **bi-endian** (configurable), common Android, iOS and macOS ARM systems use little-endian data. Linux also supports big-endian ARM configurations. Network and file formats specify byte order per format; not every protocol is big-endian.

One convenient property of little-endian layouts is that the low byte is always at the same address whatever the width, so reading a 64-bit value as 32 or 8 bits needs no address adjustment, and multi-word addition can start at the lowest address. Big-endian byte dumps follow the usual written order of a multibyte hexadecimal number. Neither observation proves an overall performance advantage.

### When endianness matters

It does **not** matter for arithmetic, shifts or masks inside a program. For a uint32_t value, `x >> 24` gives its most significant octet regardless of byte order, because shifts are defined on values, not on memory.

It matters whenever bytes cross a boundary:

```c
/* Inspect the representation through */
/* bytes. */
uint32_t v = 0x12345678;
unsigned char *p = (unsigned char *)&v;
printf("%02x\n", (unsigned)p[0]);
/* 78 little-endian; 12 big-endian */
```

## Key takeaways
- Endianness orders bytes of a multibyte representation.
- Arithmetic shifts operate on values independently of memory byte order.

## Further reading
- [Linux unaligned-memory documentation](https://docs.kernel.org/core-api/unaligned-memory-access.html)
- [Python struct documentation](https://docs.python.org/3/library/struct.html)
