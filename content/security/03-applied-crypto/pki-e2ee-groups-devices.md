---
id: pki-e2ee-groups-devices
title: Group encryption and multiple devices
level: advanced
minutes: 2
sourceLesson: pki-e2ee
summary: Device membership and session fan-out need authentication as well as content encryption.
---

Pairwise ratchets work well between two phones. Real messaging has people with several devices and groups of hundreds or thousands, which changes both the cost and the security trade-offs.

## Groups and multiple devices

**Multiple devices**: devices need authenticated membership and protected sessions. Designs differ: Sesame supports per-user or per-device identity keys, and fan-out encrypts for relevant recipient devices. Adding a device need not change the account's identity fingerprint; device enrolment needs its own controls and visibility.

**Small groups**: pairwise sessions for every message would cost O(n) encryptions per message, where n is the number of group members (assuming one device each; multiple devices add further sessions). **Sender Keys** (used by WhatsApp and Signal groups) give each sender a chain key, distributed once over pairwise sessions; messages are encrypted once and fanned out by the server. It has forward secrecy, but weaker post-compromise security: healing requires distributing new sender keys.

**Large groups**: **MLS** (Messaging Layer Security, RFC 9420, 2023) arranges members' keys in a tree (TreeKEM). When a member refreshes their key, they replace the secrets on the path from their leaf to the root and encrypt each new secret once to the neighbouring subtree, instead of once to every member. In a balanced, fully populated tree the path length grows with the logarithm of the group size: each doubling of the group adds only about one node to the path, so a 10,000-member group has a path of at most 14 nodes, against 9,999 messages for pairwise re-keying.

Actual update size and work also depend on blank nodes, resolution sizes and members joining or leaving, so the tree-depth comparison is a best case rather than an unconditional bound on the total work.

## Key takeaways
- Device membership and session fan-out need authentication as well as content encryption.
- Sender Keys reduce repeated encryption but need fresh key distribution to recover from stolen sender chains.
- Balanced MLS tree paths are logarithmic; actual update work also depends on tree state and resolution sizes.

## Further reading
- [RFC 9420: The Messaging Layer Security (MLS) Protocol](https://www.rfc-editor.org/rfc/rfc9420)
- [Sesame specification — Signal](https://signal.org/docs/specifications/sesame/)
