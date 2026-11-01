---
id: sys-tagging-layers
title: Memory tags and layered protection
level: advanced
minutes: 4
sourceLesson: sys-mitigations
summary: MTE checks suitably configured tagged accesses at sixteen-byte granularity.
---

## Memory tagging

**Arm MTE** associates four-bit allocation tags with 16-byte granules of suitably configured memory and compares them with pointer tags on checked accesses. When the allocator frees and reuses memory, it can give the granules a new tag; a stale pointer still carries the old one, so a checked access through it mismatches and is reported. Software must arrange tagging and retagging; hardware does not infer every object lifetime.

Four bits give only 16 possible tags, so detection is probabilistic. If a freed granule were retagged by a uniform, independent choice among all 16, a stale pointer's old tag would still match about one time in 16 (6.25%), and that access would go unnoticed. Android's documentation correspondingly describes a uniform detection probability of about 93% for its randomised-tag setting. That figure describes one comparison in this simple model, not a real exploit success rate: actual allocator policies can exclude values or retag differently, some accesses are unchecked, and an overflow that stays inside one 16-byte granule never crosses a tag boundary. In synchronous mode a mismatch is reported at the access; asynchronous mode can allow execution to continue before reporting.

> [!analogy] Real-world analogy: coloured wristbands at an event
> At a festival, each area's entrance checks that your wristband colour matches the area's colour. When an area is cleared and reopened for a new session, it gets a new colour, so people still wearing the old band are turned away.
>
> **How it maps:** An area is a 16-byte granule of memory and its colour is the allocation tag. The wristband is the tag carried in the pointer. Clearing and reopening the area is free and reuse with retagging; a stale band is a dangling pointer.
>
> **Where it stops:** With only 16 colours, the new colour sometimes happens to match an old band, so some stale accesses get through. Entrances can be unstaffed (unchecked accesses), wandering within one area is never checked (an overflow inside one granule), and in asynchronous mode the steward reports the problem after you are already inside.

Allocator hardening also narrows some failure modes. glibc safe-linking encodes selected singly linked free-list pointers; it does not prevent all heap corruption. Chrome BackupRefPtr, one MiraclePtr implementation, quarantines eligible allocations while tracked `raw_ptr` references remain. Untracked raw aliases and unsupported allocations are outside that guarantee.

## Summary table

| Mitigation | Checks or restricts | Remaining risk |
|---|---|---|
| Canary | Some protected stack overwrites | Leak, non-linear write |
| DEP/NX | Fetch from NX pages | Code reuse |
| ASLR | Predicting selected addresses | Info leak |
| Full RELRO | Writes to the protected GOT | Other pointers |
| Type-based forward CFI | Invalid indirect-call targets | Unintended allowed target |
| Shadow stack | Covered modified returns | Unprotected code or disabled enforcement |
| MTE | Some invalid tagged accesses | Tag match or unchecked boundary |

> [!note] Defence in depth
> Combine protections and fix the source bug. Data-only corruption, information disclosure and failures outside what the enabled protections cover remain possible. Extra vulnerabilities are sometimes needed to turn a bug into an attack, but a mitigation does not force every attacker to find another bug.

Every row in the table detects or restricts what happens *after* a memory-safety bug. Only removing the bug, by fixing it or by writing the code in a memory-safe language, removes the corruption itself. Mitigations still matter for the C and C++ that remains and for `unsafe` or foreign code inside memory-safe programs.

## Key takeaways
- MTE checks suitably configured tagged accesses at sixteen-byte granularity.
- Four-bit tags make detection probabilistic: under a uniform retagging model a stale tag still matches about one time in sixteen.
- Mitigations restrict exploitation; fixing bugs or using memory-safe languages removes the corruption itself.

## Further reading
- [Memory Tagging Extension — Linux](https://docs.kernel.org/arch/arm64/memory-tagging-extension.html)
- [Memory Tagging Extension — Android](https://source.android.com/docs/security/test/memory-safety/arm-mte)
- [BackupRefPtr — Chromium](https://chromium.googlesource.com/chromium/src/+/main/base/memory/raw_ptr.md)
