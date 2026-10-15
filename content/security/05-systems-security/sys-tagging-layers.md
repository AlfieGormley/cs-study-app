---
id: sys-tagging-layers
title: Memory tags and layered protection
level: advanced
minutes: 4
sourceLesson: sys-mitigations
summary: MTE checks suitably configured tagged accesses at sixteen-byte granularity.
---

## Memory tagging

**Arm MTE** associates four-bit allocation tags with 16-byte granules of suitably configured memory and compares them with pointer tags on checked accesses. Software must arrange tagging and retagging; hardware does not infer every object lifetime. Four bits give 16 possible tags. Suppose a freed granule is retagged by an explicitly uniform, independent choice among all 16, and a stale pointer keeps its old tag:

```formula
T = 2^4 = 16
P_match = 1 / T
P_match = 1 / 16 = 0.0625 = 6.25%
where
T: the number of distinct tag values
2^4: 4 copies of 2 multiplied together, because each tag is 4 bits
P_match: the probability that the new tag happens to equal the stale pointer's tag, so the bad access is not caught
%: per cent, parts per hundred
In words: with 16 equally likely tags, a stale pointer's tag still matches about one time in 16, roughly 6%.
```

That probability describes one comparison in this simple model, not a real exploit success rate. Actual allocator policies, unchecked accesses and same-granule overflows change what is caught. In synchronous mode a mismatch is reported at the access; asynchronous mode can allow execution to continue before reporting.

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

> [!note] Content omitted after review
> Universal ASLR defaults, platform-wide deployment rates, fixed exploit costs and guaranteed crash or prevention rates are omitted because this review did not establish the necessary versioned measurements. MTE and CET hardware enforcement were not exercised in this review.

## Key takeaways
- MTE checks suitably configured tagged accesses at sixteen-byte granularity.
- A one-in-sixteen match follows only from the explicitly uniform independent retagging model.
- Tagging and allocator hardening restrict some failure modes; combine supported defences and repair source bugs.

## Further reading
- [Memory Tagging Extension — Linux](https://docs.kernel.org/arch/arm64/memory-tagging-extension.html)
- [Memory Tagging Extension — Android](https://source.android.com/docs/security/test/memory-safety/arm-mte)
- [BackupRefPtr — Chromium](https://chromium.googlesource.com/chromium/src/+/main/base/memory/raw_ptr.md)
