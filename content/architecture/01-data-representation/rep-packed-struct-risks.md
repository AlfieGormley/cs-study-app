---
id: rep-packed-struct-risks
title: Packed members and representation leaks
level: advanced
minutes: 3
summary: Packed layout can create misaligned members.
sourceLesson: rep-memory-layout
---

Removing padding changes alignment obligations, while copying padding can expose data you never intended to send. Internal layout needs care at external boundaries.

### Packed structs

`__attribute__((packed))` (GCC/Clang) or `#pragma pack(1)` (also MSVC) reduces padding. With the earlier four-byte-int ABI, a simple char-int-char struct becomes six bytes. Nested types and explicit alignment constraints can still retain padding; inspect the actual layout. This is used to match an exact wire or file format. The costs:

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

## Key takeaways
- Packed layout can create misaligned members.
- Padding can leak information and defeats raw-byte equality checks.
- Serialise fields using an explicit external format.

## Further reading
- [Linux unaligned-memory documentation](https://docs.kernel.org/core-api/unaligned-memory-access.html)
- [Python struct documentation](https://docs.python.org/3/library/struct.html)
