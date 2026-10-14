---
id: api-protobuf-wire-size
title: Protobuf tags, varints and wire size
level: intermediate
minutes: 4
summary: Read a protobuf service contract and compute the size of a concrete binary message.
sourceLesson: api-rest-graphql-grpc
---

## gRPC: fast, typed service-to-service calls

gRPC, released by Google in 2015, is an RPC framework. You define services and messages in a `.proto` file, and code generators produce client and server stubs in a dozen languages.

```proto
syntax = "proto3";

service Inventory {
  rpc GetStock(StockReq)
      returns (StockResp);
  rpc WatchStock(StockReq)
      returns (stream StockResp);
}

message StockReq {
  string sku = 1;
}
message StockResp {
  // Tags identify fields on the binary
  // wire.
  string sku = 1;
  int32 qty  = 2;
}
```

The numbers (`= 1`, `= 2`) are **field tags**. They, not field names, go on the wire.

## Why protobuf is compact

Protocol Buffers encode a field key (tag number plus wire type) as a varint, followed by the encoded value. Small field keys occupy one byte; larger field numbers need more. Integers use *varints*, where small numbers take fewer bytes.

A varint byte carries 7 bits of the number (the eighth bit says "more bytes follow"), so the biggest value that fits in k bytes is:

```formula
V_max = 2^{7 × k} − 1
V_max = 2^7 − 1 = 127 for k = 1
V_max = 2^14 − 1 = 16,383 for k = 2
where
V_max: the largest whole number a varint of that length can hold
k: the number of bytes the varint uses
In words: each extra byte adds 7 bits, so the range grows by a factor of 128 per byte: up to 127 fits in one byte, up to 16,383 in two.
```

This applies to non-negative integers. Negative `int32` and `int64` values always take 10 bytes, which is why protobuf offers `sint32` and `sint64` for fields that are often negative.

Take `{"sku": "VAN-1", "qty": 150}`:

| Encoding | Bytes |
|---|---|
| JSON (no spaces) | 25 |
| Protobuf | 10 |

JSON spells out every name, quote and brace. Protobuf sends only a one-byte key, a length for strings, and the value:

```formula
B_sku = B_key + B_len + B_val
B_sku = 1 + 1 + 5 = 7 bytes
B_qty = B_key + B_val = 1 + 2 = 3 bytes
B_pb = 7 + 3 = 10 bytes
where
B_sku: the size of the sku field on the wire
B_qty: the size of the qty field on the wire
B_key: the field key (tag number plus wire type), 1 byte for tags 1 to 15
B_len: the length prefix that string fields carry, 1 byte for strings shorter than 128 bytes; integer fields have none
B_val: the value: 5 bytes for the text VAN-1; 2 bytes for 150 as a varint, because 150 is bigger than 127
B_pb: the size of the whole protobuf message
bytes: a byte is 8 bits, the unit of message size
In words: the string field costs key + length + text and the integer costs key + varint, giving 10 bytes in total.
```

The saving against the 25-byte JSON is:

```formula
S = (B_json − B_pb) / B_json × 100 %
S = (25 − 10) / 25 × 100 % = 60 %
where
S: the size saving, as a percentage of the JSON size
B_json: the size of the JSON text without spaces, 25 bytes
B_pb: the size of the protobuf message, 10 bytes
%: per cent, parts per hundred
In words: protobuf sends 15 fewer bytes than JSON's 25, which is 60% less.
```

That 60% is before any compression, and only for this message: long string values shrink much less, because the text itself dominates. Parsing cost depends on the message, implementation and workload; the size calculation alone proves no universal CPU speed-up.

> [!note] Benchmark gap
> No comparable JSON/Protobuf parsing benchmark is supplied. Fixed speed-up claims are omitted; the 60% size saving is only for the specific uncompressed message above.

## Key takeaways
- Generated stubs come from service and message definitions in a .proto contract.
- A field carries a tag/wire-type key and an encoded value; names are absent from the binary wire format.
- Non-negative varints carry seven value bits per byte; negative int32/int64 values take ten bytes.
- The demonstrated 60% saving is specific to one uncompressed message and says nothing universal about CPU speed.

## Further reading
- [gRPC: Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)
- [Protocol Buffers: Language guide (proto3)](https://protobuf.dev/programming-guides/proto3/)
- [Protocol Buffers: Encoding](https://protobuf.dev/programming-guides/encoding/)
