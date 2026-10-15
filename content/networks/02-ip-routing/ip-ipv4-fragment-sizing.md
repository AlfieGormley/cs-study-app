---
id: ip-ipv4-fragment-sizing
title: Size and trace IPv4 fragments
level: basic
minutes: 5
sourceLesson: ip-ipv4
summary: Use MTU, eight-byte offsets and the MF flag to split a DF-clear IPv4 datagram.
---

Use MTU, eight-byte offsets and the MF flag to split a DF-clear IPv4 datagram.

## Fragmentation

An IP interface's **maximum transmission unit** (MTU) is the largest IP packet it supports without IP fragmentation. Link-specific mechanisms may fragment below IP. Basic Ethernet commonly uses 1,500 bytes. PPPoE plus PPP consumes 8 bytes within its Ethernet payload, giving 1,492 unless larger payload support is negotiated as in RFC 4638. Encapsulation reduces the inner MTU for a fixed outer path MTU.

If a router must forward a datagram bigger than the next link's MTU, IPv4 gives it two choices:

1. **Fragment** it into smaller datagrams, if the **DF** (Don't Fragment) flag is clear.
2. **Drop** it if DF is set, and report ICMP "Fragmentation Needed" when error-generation and rate rules permit.

In ordinary IP forwarding, reassembly is performed at the **destination**, not as a normal transit-router step. Firewalls/NATs may track or reassemble fragments for their separate functions, and a tunnel endpoint is the destination of the outer packet. Each fragment has its own IP header; option-copy rules mean not every option appears in every fragment. Fragments share the same **Identification field** value, carry an **offset** in 8-byte units and have **MF** set unless they contain the end of the original payload.

Two rules set the fragment sizes. Every fragment except the last must carry a multiple of 8 bytes of payload, because the offset field counts in 8-byte units. So a router fits as much data as the MTU allows after the header, rounded down to a multiple of 8:

```formula
D = ⌊(MTU − H) / 8⌋ × 8
F = O / 8
where
D: the data carried by each non-final fragment, in bytes (B)
MTU: the maximum transmission unit of the outgoing link: the largest IP packet it carries, in bytes
H: the IP header length of each fragment, in bytes; 20 with no options
⌊ ⌋: floor: round down to a whole number, so ⌊185.9⌋ = 185
F: the value written in a fragment's Fragment Offset field, in 8-byte units
O: where the fragment's data starts within the original data, in bytes, counting from 0
B: bytes; one byte is 8 bits
In words: take the room left after the header, round it down to a multiple of 8, and record each fragment's starting position divided by 8.
```

The example below applies these rules.

> [!example] Fragmenting 4,000 bytes over a 1,500-byte link
> A datagram has a 20-byte header and 3,980 bytes of data. Each fragment can carry 1,500 − 20 = 1,480 bytes of payload (a multiple of 8, as required).
>
> - Fragment 1: 1,480 bytes, offset 0, MF set
> - Fragment 2: 1,480 bytes, offset 185 (1,480 ÷ 8), MF set
> - Fragment 3: 1,020 bytes, offset 370, MF clear
>
> Check: 1,480 + 1,480 + 1,020 = 3,980. Total lengths on the wire are 1,500, 1,500 and 1,040.

The same numbers, worked with the formula:

```formula
D = ⌊(1500 − 20) / 8⌋ × 8 = 1480 B
F_2 = 1480 / 8 = 185
F_3 = 2960 / 8 = 370
D_3 = 3980 − 2960 = 1020 B
where
D: the data carried by each non-final fragment, in bytes (B); 1,480 is already a multiple of 8, so rounding changes nothing here
⌊ ⌋: floor: round down to a whole number
F_2, F_3: the Fragment Offset field values of fragments 2 and 3, in 8-byte units; fragment 1 starts at 0
D_3: the data left over for the last fragment, in bytes
B: bytes; one byte is 8 bits
In words: two full fragments carry 1,480 bytes each and start at bytes 0 and 1,480; the third starts at byte 2,960 (field value 370) and carries the remaining 1,020 bytes.
```

The rounding matters when the room left is not a multiple of 8: an MTU of 1,000 leaves 980 bytes, but only 976 can be used.

```python
def fragment(data_len, mtu, hdr=20):
    # Unfragmented, DF-clear input.
    # Equal headers; no option-copy logic.
    sizes = (data_len, mtu, hdr)
    integer = all(type(v) is int
                  for v in sizes)
    if not integer:
        raise ValueError("not integers")
    if (hdr < 20 or hdr > 60 or hdr % 4
            or data_len < 0
            or data_len + hdr > 65535
            or mtu < hdr):
        raise ValueError("invalid sizes")
    capacity = mtu - hdr
    if data_len <= capacity:
        yield 0, data_len, False
        return
    # Align non-final data to eight bytes.
    per = capacity // 8 * 8
    if per == 0:
        raise ValueError("MTU too small")
    off = 0
    while off < data_len:
        left = data_len - off
        size = min(left, capacity)
        if left > capacity:
            size = per
        mf = off + size < data_len
        # Offset counts eight-byte groups.
        yield off // 8, size, mf
        off += size

for f in fragment(3980, 1500):
    print(f)
# (0, 1480, True)
# (185, 1480, True)
# (370, 1020, False)
```

## Key takeaways
- Each fragment has an IP header; ordinary transit routers leave reassembly to the destination.
- Non-final fragment payloads must be multiples of eight bytes.
- Offsets count eight-byte units; MF is clear on the piece containing the payload end.

## Further reading
- [RFC 791: Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 8900: IP fragmentation fragility](https://www.rfc-editor.org/rfc/rfc8900.html)
- [RFC 6864: IPv4 Identification](https://www.rfc-editor.org/rfc/rfc6864)
