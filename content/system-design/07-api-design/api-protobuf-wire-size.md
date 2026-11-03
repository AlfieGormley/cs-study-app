---
id: api-protobuf-wire-size
title: Protobuf tags, varints and wire size
level: intermediate
minutes: 4
summary: Explain how field tags and varints affect message size, without assuming a universal compression or speed advantage.
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

A varint byte carries seven value bits; its high bit says whether more bytes follow. Small positive values through 127 fit in one byte; values through 16,383 fit in two. Protobuf integer types are limited to 64 bits, so a ten-byte varint cannot use seven value bits in its last byte.


This applies to non-negative integers. Negative `int32` and `int64` values always take 10 bytes, which is why protobuf offers `sint32` and `sint64` for fields that are often negative.

Take `{"sku": "VAN-1", "qty": 150}`:

| Encoding | Bytes |
|---|---|
| JSON (no spaces) | 25 |
| Protobuf | 10 |

JSON spells out every name, quote and brace. Protobuf sends only a one-byte key, a length for strings, and the value:

For these small field numbers, the string uses seven bytes: its key, its length and five UTF-8 bytes. The integer uses three: its key and a two-byte varint.

The protobuf message is 15 bytes smaller, a 60% saving for this particular uncompressed example.

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
