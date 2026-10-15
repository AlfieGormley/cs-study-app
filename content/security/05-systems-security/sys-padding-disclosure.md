---
id: sys-padding-disclosure
title: Initialised fields do not define padding
level: intermediate
minutes: 3
sourceLesson: sys-memory-bugs
summary: Indeterminate automatic values are not a reliable source of old bytes.
---

## Uninitialised memory

An uninitialised automatic value is indeterminate in C11/C17, and many uses have undefined behaviour. Do not assume it reliably returns old bytes. Separately, copying a raw structure across a trust boundary can disclose struct padding. Initialising members with `{0}` is not a portable guarantee that padding remains zero after member stores. Encode named fields into an explicitly defined byte representation instead of transmitting `sizeof(struct)` bytes.

Consider a structure with a one-byte flag followed by an eight-byte integer. Under an ABI that aligns the integer at offset eight and gives the whole structure sixteen bytes, offsets one through seven are padding. Writing both members establishes their values; it does not establish a portable representation for those seven extra bytes. That layout is an explicit example, not a promise about every platform.

A safe interface defines which fields leave the component and how each is encoded. Copy the named values into a byte format with documented sizes and byte order; do not use the compiler's whole structure layout as the protocol. This also avoids exposing layout changes when the compiler, architecture or type definitions change.

A kernel-to-user copy is a useful example of a trust boundary: user-space code should receive only the documented response, not incidental internal bytes. User-address checking and memory initialisation solve different problems. A valid destination address does not make unintended source padding safe to disclose.

## Key takeaways
- Indeterminate automatic values are not a reliable source of old bytes.
- Member assignments do not define portable structure-padding contents.
- Encode named fields into a defined representation before crossing a trust boundary.

## Further reading
- [C11 committee draft: objects and library contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [CWE-200: information exposure — MITRE](https://cwe.mitre.org/data/definitions/200.html)
