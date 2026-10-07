---
id: rep-memory-layout
title: Endianness, alignment and struct padding
level: advanced
minutes: 15
summary: How multi-byte values are ordered in memory and on the wire, why CPUs want data aligned, and how C compilers pad structs, with the bugs and security holes each one causes.
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
| BMP and ZIP fields specified little-endian | Java class-file multibyte items |

ARM, PowerPC and MIPS are **bi-endian** (configurable), common Android, iOS and macOS ARM systems use little-endian data. Linux also supports big-endian ARM configurations. Network and file formats specify byte order per format; not every protocol is big-endian.

One convenient property of little-endian layouts is that the low byte is always at the same address whatever the width, so reading a 64-bit value as 32 or 8 bits needs no address adjustment, and multi-word addition can start at the lowest address. Big-endian byte dumps follow the usual written order of a multibyte hexadecimal number. Neither observation proves an overall performance advantage.

### When endianness matters

It does **not** matter for arithmetic, shifts or masks inside a program. For a uint32_t value, `x >> 24` gives its most significant octet regardless of byte order, because shifts are defined on values, not on memory.

It matters whenever bytes cross a boundary:

```c
uint32_t v = 0x12345678;
unsigned char *p = (unsigned char *)&v;
printf("%02x\n", (unsigned)p[0]);
/* 78 little-endian; 12 big-endian */
```

### Network byte order

TCP/IP headers are big-endian, called **network byte order**. C programs convert with `htons`/`htonl` (host to network, short/long) and `ntohs`/`ntohl`. On a big-endian host they do nothing; on little-endian they swap bytes (the compiler chooses appropriate instructions or folds a constant).

```c
struct sockaddr_in addr;
addr.sin_port = htons(8080);
/* bytes in memory: 1F 90 */
```

Forget `htons` on a little-endian machine and the bytes go out as `90 1F`, so the server listens on port 0x901F = 36,895 instead of 8,080.

In Python, `struct` and `int.to_bytes` make byte order explicit:

```python
import struct
struct.pack('<I', 0x12345678).hex()
# '78563412'  (< = little-endian)
struct.pack('>I', 0x12345678).hex()
# '12345678'  (> = big-endian)
struct.pack('!H', 8080).hex()
# '1f90'      (! = network order)

int.from_bytes(b'\x01\x00\x00\x00',
               'little')   # 1
```

> [!tip] Write byte-order-independent code
> Instead of casting a buffer to `uint32_t *`, assemble the value with shifts. This works on any host and has no alignment problems. Optimising compilers often recognise this pattern; the exact instruction sequence depends on alignment support, target and optimisation settings.

```c
uint32_t rd_be32(const uint8_t *b) {
    return (uint32_t)b[0] << 24 |
           (uint32_t)b[1] << 16 |
           (uint32_t)b[2] << 8  |
           (uint32_t)b[3];
}
```

File formats either fix an order (PNG is big-endian; BMP, ZIP and most Windows formats are little-endian) or record it. TIFF files start with `II` (Intel, little) or `MM` (Motorola, big). UTF-16 can use a byte order mark or an externally specified byte-order convention; a BOM is not universally required.

## Alignment

A value of size *n* is **naturally aligned** if its address is a multiple of *n*: a 4-byte `int` at 0, 4, 8, and so on; an 8-byte `double` at multiples of 8.

### Why hardware cares

A CPU can issue byte-sized loads. Cacheable misses commonly transfer whole cache lines, often 64 bytes, while load/store execution and uncached or device accesses have additional size and alignment rules.

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
- **Atomicity** depends on the architecture, memory type and access. For example, x86-64 guarantees indivisibility for suitably aligned ordinary 8-byte loads/stores to normal memory. A misaligned access can lack that guarantee. In C/C++, hardware non-tearing does not permit data races: use atomics or synchronisation for conflicting cross-thread accesses.

In C, conversion to an object-pointer type with unmet alignment requirements is already undefined, and dereferencing misaligned storage is not made valid by the hardware, even on x86, and compilers vectorise code on the assumption that it does not happen. Use memcpy into a suitably typed local variable for unaligned representation copies, with valid bounds and a valid destination representation; byte order still needs handling. Compilers can lower fixed-size copies to ordinary loads where the target allows them.

## Struct padding

A C compiler lays out struct members **in declaration order** (it may not reorder them) and inserts **padding** so that each member is aligned. For ordinary unpacked structs without bit-fields, explicit over-alignment or unusual members, mainstream ABIs such as x86-64 System V and AArch64 use these rules:

1. Each member starts at an offset that is a multiple of its alignment.
2. The struct's alignment is the largest alignment of its members.
3. The struct's size is rounded up to a multiple of its alignment (**tail padding**).

### Worked example

```c
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

Six bytes of data, six bytes of padding. Why the tail padding? In an array `struct A arr[2]`, `arr[1]` starts sizeof(struct A) **bytes** after arr[0], namely `(unsigned char *)arr + sizeof(struct A)`. The expression `arr + sizeof(struct A)` would incorrectly scale that count by the element size again. If the size were 9, `arr[1].b` would sit at offset 13, misaligned. Rounding the size to 12 keeps every element aligned.

Reorder the members largest first and the padding mostly vanishes:

```c
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
#include <stddef.h>
printf("%zu %zu %zu\n",
       sizeof(struct A),
       offsetof(struct A, c),
       _Alignof(struct A));
/* 12 8 4 */
```

> [!note] ABI-dependent
> Alignment of each type comes from the platform ABI, not the C standard. On 32-bit x86 Linux (i386 System V), a `double` inside a struct is only 4-byte aligned, so `{char; double; char}` is 16 bytes there, not 24. Code that shares binary structs between platforms must not rely on the layout.

### Packed structs

`__attribute__((packed))` (GCC/Clang) or `#pragma pack(1)` (also MSVC) removes padding: `struct A` becomes 6 bytes. This is used to match an exact wire or file format. The costs:

- Members may be misaligned, so the compiler must use slower byte-by-byte or unaligned access sequences on some targets.
- Taking a pointer to a packed member (`&p->b`) can produce a misaligned int pointer. Using it can fault or otherwise misbehave; GCC warns with `-Waddress-of-packed-member`.
- Atomic operations on packed members may be impossible or not atomic.

Reordering members is almost always a better first step than packing.

## Bugs and security holes

### Padding leaks data

Assigning a struct's fields does not guarantee defined values for its padding. Copying its entire object representation can therefore disclose stale bytes, which might be part of a key, a pointer (defeating ASLR) or another user's data. Implementation-specific fixes may zero storage before filling it. Portable C still permits padding to take unspecified values when a struct or member is stored, so a blanket memset-then-fill recipe is not a universal guarantee. Serialise the intended fields into an explicitly defined output buffer, including explicit zero bytes where the format requires them.

The same padding makes `memcmp(&x, &y, sizeof x)` unreliable for equality: two structs with equal members can differ in their padding bytes. Compare members individually.

### Raw structs are not a file format

`fwrite(&s, sizeof s, 1, f)` on one machine and `fread` on another breaks as soon as the two differ in endianness, padding, type sizes (`long` is 8 bytes on 64-bit Linux, 4 on 64-bit Windows) or compiler flags. Use an explicit format: fixed-width types written field by field in a stated byte order, or a serialisation library such as Protocol Buffers, FlatBuffers or Cap'n Proto, which specify their byte layouts exactly.

### Python's struct module and padding

Python's `struct` uses native alignment with the default `@` prefix, but does **not** add tail padding:

```python
import struct
struct.calcsize('@cic')    # 9, not 12
struct.calcsize('@cic0i')  # 12: 0i pads
struct.calcsize('<cic')    # 6: no padding
```

The `0i` trick pads the end to an `int` boundary. Any explicit byte-order prefix (`<`, `>`, `!`, `=`) turns alignment off entirely. ctypes.Structure can model supported C ABIs with tail padding; its layout/packing options must match the actual compiler ABI and flags, so it is not a universal mirror of arbitrary structs.

## Alignment for performance

Sometimes you want **more** alignment than natural:

- **SIMD**: aligned AVX/AVX-512 load forms require their specified alignment; unaligned forms also exist. Alignment can avoid split accesses, but performance depends on the instruction and processor.
- **False sharing**: two threads updating different variables on the same 64-byte cache line force the line to bounce between cores. Separate counters by the relevant cache-line size, including alignment and stride/padding. alignas(64) on the start of an array alone does not separate adjacent counters. C++17 hardware_destructive_interference_size is an implementation-provided size hint, used with alignas and an appropriate layout; speedups depend on the workload. The caches module covers why, in its lesson on coherence.
- **Pages**: mapping and device interfaces may require page or device-specific alignment. Query the page size; 4 KiB is common, not universal. aligned_alloc and posix_memalign align virtual allocations, but do not alone pin memory, ensure physical contiguity or map it for DMA; use the required operating-system device API.

## Key takeaways
- Little-endian stores the least significant byte at the lowest address (x86 and common ARM/RISC-V configurations); big-endian stores the most significant first (network byte order).
- Endianness is invisible to arithmetic and shifts; it matters only when bytes cross a boundary. Use `htonl`/`ntohl`, Python's `struct` prefixes, or shift-based assembly.
- A naturally aligned power-of-two access within the stated size assumptions does not span a cache line; misaligned access ranges from a small penalty (x86) to a crash (strict-alignment CPUs) and can break atomicity.
- Struct members stay in order, each aligned, with the size rounded to the struct's alignment. `{char; int; char}` is 12 bytes; reordering largest first saves space.
- Packing removes padding but costs speed and safety; reorder first.
- Uninitialised padding leaks data and breaks `memcmp`; never ship raw structs as a file or wire format.

## Further reading
- [Endianness — Wikipedia](https://en.wikipedia.org/wiki/Endianness)
- [Data structure alignment — Wikipedia](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [The Lost Art of Structure Packing — Eric S. Raymond](http://www.catb.org/esr/structure-packing/)
- [struct: interpret bytes as packed binary data — Python docs](https://docs.python.org/3/library/struct.html)
- [On Holy Wars and a Plea for Peace (IEN 137) — Danny Cohen](https://www.rfc-editor.org/ien/ien137.txt)
- [byteorder(3) — Linux manual page](https://man7.org/linux/man-pages/man3/byteorder.3.html)
