---
id: rep-native-layout-performance
title: Native packing and performance alignment
level: advanced
minutes: 3
summary: Python native struct packing omits automatic tail padding.
sourceLesson: rep-memory-layout
---

This unit continues the preceding material on eight-bit bytes and multibyte object representations.

### Python's struct module and padding

Python's `struct` uses native alignment with the default `@` prefix, but does **not** add tail padding:

```python
# Native packing omits automatic tail pads.
import struct
struct.calcsize('@cic')    # 9, not 12
struct.calcsize('@cic0i')  # 12: 0i pads
struct.calcsize('<cic')    # 6: no padding
```

The `0i` trick pads the end to an `int` boundary. Any explicit byte-order prefix (`<`, `>`, `!`, `=`) turns alignment off entirely. ctypes.Structure can model supported C ABIs with tail padding; its layout/packing options must match the actual compiler ABI and flags, so it is not a universal mirror of arbitrary structs.

## Alignment for performance

Sometimes you want **more** alignment than natural:

- **SIMD**: aligned AVX/AVX-512 load forms require their specified alignment; unaligned forms also exist. Alignment can avoid split accesses, but performance depends on the instruction and processor.
- **False sharing**: two threads updating different variables on the same 64-byte cache line force the line to bounce between CPU cores. Separate counters by the relevant cache-line size, including alignment and stride/padding. alignas(64) on the start of an array alone does not separate adjacent counters. C++17 hardware_destructive_interference_size is an implementation-provided size hint, used with alignas and an appropriate layout; speedups depend on the workload. The caches module covers why, in its lesson on coherence.
- **Pages**: mapping and device interfaces may require page or device-specific alignment. Query the page size; 4 KiB is common, not universal. aligned_alloc and posix_memalign align virtual allocations, but do not alone pin memory, ensure physical contiguity or map it for DMA; use the required operating-system device API.

## Key takeaways
- Python native struct packing omits automatic tail padding.
- Alignment, stride and object layout together affect false sharing.
- An aligned allocation alone is not a DMA mapping.

## Further reading
- [Linux unaligned-memory documentation](https://docs.kernel.org/core-api/unaligned-memory-access.html)
- [Python struct documentation](https://docs.python.org/3/library/struct.html)
- [Endianness — Wikipedia](https://en.wikipedia.org/wiki/Endianness)
- [Data structure alignment — Wikipedia](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [The Lost Art of Structure Packing — Eric S. Raymond](http://www.catb.org/esr/structure-packing/)
- [struct: interpret bytes as packed binary data — Python docs](https://docs.python.org/3/library/struct.html)
- [On Holy Wars and a Plea for Peace (IEN 137) — Danny Cohen](https://www.rfc-editor.org/ien/ien137.txt)
- [byteorder(3) — Linux manual page](https://man7.org/linux/man-pages/man3/byteorder.3.html)
