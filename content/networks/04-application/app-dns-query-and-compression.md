---
id: app-dns-query-and-compression
title: "Build a DNS query and decode compressed names"
level: intermediate
minutes: 4
sourceLesson: app-dns-wire
summary: "A DNS question combines a fixed header, encoded name and four bytes of type/class."
---

A DNS name is encoded as a length byte before each label, followed by the zero-length root label. The twelve-byte message header precedes the question. Resource-record names may instead reuse earlier name data through compression pointers.

### Building a query by hand

This builds an ordinary ASCII-label question, not a full resolver. It accepts an optional trailing `.`, checks wire-length bounds, and uses a random DNS transaction ID unless a test ID is supplied. Internationalised presentation names require a suitable IDNA conversion before this restricted encoder.

```python
import secrets, struct

def build_query(name, qtype=1, qid=None):
    if qid is None:
        # Unpredictable sixteen-bit ID.
        qid = secrets.randbelow(65536)
    if (type(qid) is not int
            or not 0 <= qid <= 65535
            or type(qtype) is not int
            or not 0 <= qtype <= 65535):
        raise ValueError("bad field")
    if name == ".":
        labels = []
    else:
        if name.endswith("."):
            name = name[:-1]
        labels = [p.encode("ascii")
                  for p in name.split(".")]
        if any(not 1 <= len(p) <= 63
               for p in labels):
            raise ValueError("bad label")
    # Prefix each label, then add root.
    qname = b"".join(
        bytes([len(p)]) + p
        for p in labels) + b"\0"
    if len(qname) > 255:
        raise ValueError("name too long")
    # ! selects network byte order.
    # RD set; one question, no answers.
    header = struct.pack("!HHHHHH",
        qid, 0x0100, 1, 0, 0, 0)
    # Type plus Internet class end it.
    return header + qname + struct.pack(
        "!HH", qtype, 1)

q = build_query("example.com", qid=0xABCD)
print(len(q))  # 29
print(q[:4].hex(" "))  # ab cd 01 00
```

The length adds up from the three parts:

```formula
Q = H + N + T
Q = 12 B + 13 B + 4 B = 29 B
N = (1 + 7) B + (1 + 3) B + 1 B = 13 B
where
Q: the total query length, in bytes (B)
H: the fixed header: six 16-bit fields, 12 bytes
N: the encoded name: a length byte plus "example" (7 letters), a length byte plus "com" (3 letters), then the zero byte for the root
T: QTYPE and QCLASS, two 16-bit fields, 4 bytes
B: bytes
In words: 12 bytes of header, 13 bytes of length-prefixed name and 4 bytes of type and class make the 29 bytes printed above.
```

Note that the encoded name is two bytes longer than the dotted text `example.com` (11 characters): one length byte per label replaces each `.` separator, plus the leading length and the root byte. A hypothetical reply with flags `0x8180` would decode as `QR=1, RD=1, RA=1` and RCODE 0.

### Resource records and compression

Each answer is a **resource record** (RR): name, TYPE (16 bits), CLASS (16), TTL (32-bit seconds), RDLENGTH (16) and RDATA. An A record's RDATA is 4 bytes; AAAA's is 16.

Names repeat constantly in a response, so DNS uses **compression pointers**. A length byte whose top two bits are `11` is not a length: it and the next byte form a 14-bit offset into the message where the rest of the name can be found. An illustrative A answer could begin with this compressed owner name:

```
c0 0c  name: pointer to offset 12
00 01  TYPE A
00 01  CLASS IN
00 00 01 0e  TTL 270 s
00 04  RDLENGTH 4
xx xx xx xx  IPv4 address
```

The 14-bit offset is what remains after removing the two `11` marker bits, which are worth `0xc000` together:

```formula
o = P − 0xc000
o = 0xc00c − 0xc000 = 0x0c = 12
where
o: the offset, counted in bytes from the first byte of the DNS message, where the rest of the name is stored
P: the two pointer bytes read as one 16-bit number, here 0xc00c. Numbers starting 0x are hexadecimal (base 16); 0x0c is 12
In words: drop the top two marker bits and the remaining number is the byte position to jump to.
```

The TTL bytes decode the same way, as one big-endian number: `00 00 01 0e` is 1 × 256 + 14 = 270 seconds.

Offset 12 is where the question's name starts, straight after the header, so `c0 0c` means "example.com". Parsers must guard against pointer loops; a self-referential pointer can otherwise cause an infinite loop or resource exhaustion. Parsers also need bounds and expanded-name-length checks.

## Key takeaways
- A DNS question combines a fixed header, encoded name and four bytes of type/class.
- Compression pointers are message-relative offsets; parsers also need loop and bounds checks.

## Further reading
- [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035)
