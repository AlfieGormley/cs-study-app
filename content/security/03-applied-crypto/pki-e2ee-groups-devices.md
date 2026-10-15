---
id: pki-e2ee-groups-devices
title: Group encryption and multiple devices
level: advanced
minutes: 2
sourceLesson: pki-e2ee
summary: Device membership and session fan-out need authentication as well as content encryption.
---

End-to-end encryption keeps message-content keys at the communicating endpoints. Signal’s protocol family uses uploaded prekeys to start sessions and ratcheting keys to protect ongoing conversations.

## Groups and multiple devices

**Multiple devices**: devices need authenticated membership and protected sessions. Designs differ: Sesame supports per-user or per-device identity keys, and fan-out encrypts for relevant recipient devices. Adding a device need not change the account's identity fingerprint; device enrolment needs its own controls and visibility.

**Small groups**: pairwise sessions for every message would cost O(n) encryptions per message, where n is the number of group members (assuming one device each; multiple devices add further sessions). **Sender Keys** (used by WhatsApp and Signal groups) give each sender a chain key, distributed once over pairwise sessions; messages are encrypted once and fanned out by the server. It has forward secrecy, but weaker post-compromise security: healing requires distributing new sender keys.

**Large groups**: **MLS** (Messaging Layer Security, RFC 9420, 2023) arranges members' keys in a tree (TreeKEM), so a balanced populated tree can refresh a path of O(log n) nodes. For a balanced tree:

```formula
L = ⌈log_2(N)⌉
L = ⌈log_2(10,000)⌉ = ⌈13.29⌉ = 14
where
L: the maximum root-to-leaf depth of this balanced binary tree; individual member paths can be shorter
N: the number of members, one per leaf
log_2: logarithm base 2: the power 2 must be raised to (log_2(1,024) = 10)
⌈ ⌉: ceiling: round up to the next whole number
In words: each doubling of the group adds only one level, so a 10,000-member balanced tree has a maximum path depth of 14; this path-depth comparison does not count all update ciphertexts or all membership-change work.
```

Actual update size/work also depends on blank nodes, resolution sizes and members joining or leaving; the tree-depth example is not an unconditional total-cost bound.

## Key takeaways
- Device membership and session fan-out need authentication as well as content encryption.
- Sender Keys reduce repeated encryption but need fresh key distribution to recover from stolen sender chains.
- Balanced MLS tree paths are logarithmic; actual update work also depends on tree state and resolution sizes.

## Further reading
- [X3DH specification — Signal](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet specification — Signal](https://signal.org/docs/specifications/doubleratchet/)
