---
id: api-protobuf-schema-evolution
title: Evolving protobuf schemas safely
level: intermediate
minutes: 2
summary: Preserve field meaning across old and new binary readers by reserving removed tags.
sourceLesson: api-rest-graphql-grpc
---

The previous unit showed that binary protobuf identifies fields by tags and wire types. Protobuf schema changes must preserve what deployed readers think each tag means. Wire compatibility also differs from source-code or business compatibility.

## Protobuf schema evolution rules

Because tags identify fields, you can evolve a protobuf schema safely if you:

- **Add** new fields with **new** tag numbers. Old readers ignore unknown tags.
- **Never reuse** a removed field's tag. Mark it `reserved 3;`.
- **Do not change** a field's tag number. Prefer a new field rather than changing its type; the proto3 guide permits some wire-compatible type changes, but their value ranges and application semantics still need review.

Break these rules and you get silent damage, not an error. If you reuse tag 3 for a new field with the same *wire type* (say, one `string` replaced by another), an old client happily reads the new value as the old field. If the wire types differ, most parsers set the field aside as unknown, so the old client just sees it as missing.

Renaming a field is safe for the binary format, because names never go on the wire. It does break anything that uses protobuf's JSON mapping, which keys by field name.

For binary proto3 messages with implicit scalar presence, a deleted field can be treated as unknown by the other reader, and a missing scalar reads as its default. Reserve both the removed tag and its old name; this does not guarantee that an application which required the field will still behave correctly.

## Key takeaways
- Add fields with unused tags and reserve removed tags and names.
- Reusing a tag can silently reinterpret data; changing wire types can make an old reader treat it as unknown.
- Renaming a field preserves the binary encoding but can break JSON-mapping consumers.

## Further reading
- [Protocol Buffers: Language guide (proto3)](https://protobuf.dev/programming-guides/proto3/)
