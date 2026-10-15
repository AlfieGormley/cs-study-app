---
id: nf-ethernet-header-parser
sourceLesson: nf-layered-models
title: Parse an Ethernet header
level: basic
minutes: 3
summary: Decode a synthetic header with Python and identify what the limited parser cannot validate.
---

### Parsing headers in code

Many header fields have defined byte layouts; optional and variable-length fields need additional parsing. Python's `struct` module can unpack them (`!` means network byte order, which is big-endian):

```python
import struct

def parse_eth(frame: bytes):
    if len(frame) < 14:
        raise ValueError("short header")
    # Decode fixed fields in network order.
    dst, src, etype = struct.unpack(
        "!6s6sH", frame[:14])
    # Keep the payload as uninterpreted
    # bytes.
    return (dst.hex(":"), src.hex(":"),
            hex(etype), frame[14:])

frame = bytes.fromhex(
    "ffffffffffff" "3c22fb112233"
    "0806") + b"..."

# Show addresses and ARP protocol selection.
print(parse_eth(frame)[:3])
# ('ff:ff:ff:ff:ff:ff',
#  '3c:22:fb:11:22:33', '0x806')
```

The tuple contains the destination, source and EtherType. The final return value is the bytes after the fixed header; the displayed slice deliberately omits it. The length check rejects an incomplete fixed header before `struct.unpack` reads it.

This is a synthetic header followed by placeholder bytes, not a valid complete ARP frame. Its all-ones destination denotes broadcast and its EtherType selects ARP, which you will meet in the ARP units. This parser demonstrates an untagged Ethernet II header only. It does not handle VLAN tags, 802.3 length/LLC framing, frame length validation or FCS stripping/verification; packet-capture APIs may omit the FCS.

## Key takeaways
- Network byte order puts the most significant byte first.
- Parsing 14 header bytes does not validate the whole frame or its FCS.

## Further reading
- [RFC 1122: Requirements for Internet Hosts — Communication Layers](https://www.rfc-editor.org/rfc/rfc1122)
- [OSI model — Wikipedia](https://en.wikipedia.org/wiki/OSI_model)
- [Internet protocol suite — Wikipedia](https://en.wikipedia.org/wiki/Internet_protocol_suite)
- [Encapsulation (networking) — Wikipedia](https://en.wikipedia.org/wiki/Encapsulation_(networking))
- [RFC 3439: Some Internet Architectural Guidelines and Philosophy](https://www.rfc-editor.org/rfc/rfc3439)

- [IANA IP protocol number registry](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
- [RFC 9001: QUIC packet and header protection](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 7348: VXLAN framing](https://www.rfc-editor.org/rfc/rfc7348)
