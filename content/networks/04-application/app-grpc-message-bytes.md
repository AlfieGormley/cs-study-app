---
id: app-grpc-message-bytes
title: "gRPC requests and protobuf message bytes"
level: advanced
minutes: 4
sourceLesson: app-ntp-ssh-grpc
summary: "A native gRPC call uses an HTTP/2 stream containing length-prefixed messages; this example uses protobuf."
---

## gRPC on the wire

This section describes native gRPC over **HTTP/2**. Each call is one HTTP/2 stream. Knowing the framing helps you debug it with ordinary HTTP tools.

### The request

```
HEADERS (stream 1)
  :method POST
  :scheme https
  :path /shop.Catalog/GetItem
  :authority api.shop.example
  content-type application/grpc
  te trailers
  grpc-timeout 250m
DATA (stream 1, END_STREAM)
  <length-prefixed message>
```

- The **path** is `/package.Service/Method`, which is how proxies route and authorise per method.
- `te: trailers` tells proxies the client understands trailers, which gRPC needs.
- `grpc-timeout` carries the **gRPC deadline**: `250m` means 250 milliseconds (units are H, M, S, m, u, n). Applications should propagate the remaining budget downstream; automatic support and configuration differ by language/library.

### Message framing

The gRPC framing is independent of its message encoding; protobuf is the usual default, rather than a requirement of this wire protocol. Inside DATA frames, each encoded message is prefixed with **5 bytes**: a 1-byte compressed flag and a 4-byte big-endian length. Take this message:

```
message GetItemRequest {
  int32 id = 1;
  string name = 2;
}
```

Protobuf encodes each field as a **protobuf tag** followed by the value. The tag packs the field number and the wire type into one varint: the field number is shifted left by 3 bits (`<< 3` in code, the same as multiplying by 8), leaving the low 3 bits for the wire type. So field 1 as a varint (wire type 0) has tag `08`, and field 2 as a length-delimited string (wire type 2) has tag `12`, hexadecimal for 18.

```python
import struct

def pb_varint(n):
    # Unsigned uint64 helper only.
    if (type(n) is not int
            or not 0 <= n < 2**64):
        raise ValueError("expected uint64")
    out = bytearray()
    while True:
        # Extract the low seven value bits.
        b = n & 0x7F
        n >>= 7
        if n:
            # Signal another group follows.
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)

# id=150, name="hi"
msg = (b"\x08" + pb_varint(150)
       + b"\x12\x02hi")
# Prefix: uncompressed flag and length.
frame = struct.pack("!BI", 0,
                    len(msg)) + msg
print(frame.hex(" "))
# 00 00 00 00 07 08 96 01 12 02 68 69
```

- `08` = field 1, varint. `96 01` = 150. Each varint byte carries 7 bits of the number, least significant group first, and its top bit means "more bytes follow". `96` has that bit set and carries 22; `01` is the last byte and carries 1 lot of 128. 22 + 128 = 150.
- `12` = field 2, length-delimited. `02` = 2 bytes. `68 69` = "hi".
- The 5-byte prefix `00 00 00 00 07`: not compressed, 7 bytes.

This helper demonstrates nonnegative values; signed `int32` negatives use sign-extended varints, while `sint32` uses ZigZag encoding.

The message boundaries are independent of DATA frame boundaries: one message can span many DATA frames, and one DATA frame can carry several messages. **Streaming RPCs** simply send more length-prefixed messages on the same stream.

## Key takeaways
- A native gRPC call uses an HTTP/2 stream containing length-prefixed messages; this example uses protobuf.
- A message has a five-byte gRPC prefix, independent of HTTP/2 DATA frame boundaries.

## Further reading
- [gRPC HTTP/2 protocol](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)
- [Protobuf encoding](https://protobuf.dev/programming-guides/encoding/)
