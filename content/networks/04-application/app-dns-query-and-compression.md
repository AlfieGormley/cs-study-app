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

The 29 bytes are the 12-byte header, 13 bytes of encoded name and 4 bytes of type and class. The encoded name is two bytes longer than the dotted text `example.com` (11 characters): one length byte per label replaces each `.` separator, plus the leading length and the root byte. A hypothetical reply with flags `0x8180` would decode as `QR=1, RD=1, RA=1` and RCODE 0.

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

Clear the two `11` marker bits and the remaining 14 bits are a byte offset from the start of the message: `c0 0c` points to offset 12. The other fields are ordinary big-endian numbers; `00 00 01 0e` is a TTL of 270 seconds.

Offset 12 is where the question's name starts, straight after the header, so `c0 0c` means "example.com". Parsers must guard against pointer loops; a self-referential pointer can otherwise cause an infinite loop or resource exhaustion. Parsers also need bounds and expanded-name-length checks.

> [!analogy] Real-world analogy: "See note 3" in a footnote
> A book that cites the same long source many times writes it out once, then says "see note 3" each time after that.
>
> **How it maps:** The first full copy of `example.com` in the question is the original note, and `c0 0c` is "see the name at byte 12". A pointer can also stand for the end of a name, so `www` followed by a pointer to `example.com` spells `www.example.com`.
>
> **Where it stops:** A reader would notice a note that only says "see this note". A parser will not, unless it limits how many pointers it follows, insists that pointers lead to earlier bytes, or keeps the expanded name within 255 bytes. A hostile message can otherwise trap it in a loop.

## Key takeaways
- A DNS question combines a fixed header, encoded name and four bytes of type/class.
- Compression pointers are message-relative offsets; parsers also need loop and bounds checks.

## Further reading
- [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035)
