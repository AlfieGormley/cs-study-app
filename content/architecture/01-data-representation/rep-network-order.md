---
id: rep-network-order
title: Network order and explicit byte assembly
level: advanced
minutes: 3
summary: Convert protocol fields at the host/wire boundary.
sourceLesson: rep-memory-layout
---

A protocol fixes the order of bytes on the wire independently of the host's memory layout. Convert when crossing that boundary.

### Network byte order

TCP/IP headers are big-endian, called **network byte order**. C programs convert with `htons`/`htonl` (host to network, short/long) and `ntohs`/`ntohl`. On a big-endian host they do nothing; on little-endian they swap bytes (the compiler chooses appropriate instructions or folds a constant).

```c
/* Convert the numeric port to wire */
/* order. */
struct sockaddr_in addr;
addr.sin_port = htons(8080);
/* bytes in memory: 1F 90 */
```

Forget `htons` on a little-endian machine and the bytes go out as `90 1F`, so the server listens on port 0x901F = 36,895 instead of 8,080.

In Python, `struct` and `int.to_bytes` make byte order explicit:

```python
# Pack values with an explicit byte order.
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
/* Assemble bytes as values, not */
/* pointers. */
uint32_t rd_be32(const uint8_t *b) {
    return (uint32_t)b[0] << 24 |
           (uint32_t)b[1] << 16 |
           (uint32_t)b[2] << 8  |
           (uint32_t)b[3];
}
```

File formats either fix an order (PNG is big-endian; Windows bitmap images, ZIP and most Windows formats are little-endian) or record it. TIFF files start with `II` (Intel, little) or `MM` (Motorola, big). UTF-16 can use a byte order mark or an externally specified byte-order convention; a BOM is not universally required.

## Key takeaways
- Convert protocol fields at the host/wire boundary.
- Byte-by-byte assembly avoids a misaligned typed pointer.

## Further reading
- [Linux unaligned-memory documentation](https://docs.kernel.org/core-api/unaligned-memory-access.html)
- [Python struct documentation](https://docs.python.org/3/library/struct.html)
