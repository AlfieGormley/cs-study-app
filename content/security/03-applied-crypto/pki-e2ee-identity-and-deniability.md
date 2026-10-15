---
id: pki-e2ee-identity-and-deniability
title: Messaging identities and deniable tags
level: advanced
minutes: 2
sourceLesson: pki-e2ee
summary: Shared-key tags alone are not transferable proof that one particular peer authored a message.
---

End-to-end encryption keeps message-content keys at the communicating endpoints. Signal’s protocol family uses uploaded prekeys to start sessions and ratcheting keys to protect ongoing conversations.

## Deniability

For the pairwise shared-key authentication illustrated here, a valid tag authenticates the message to a peer who knows they did not create it, assuming uncompromised keys. Either holder could compute the tag, so it alone is not transferable proof of authorship. This is narrower than a claim about all messaging transcripts, group-signature schemes or legal evidence.

> [!note] Content gap
> Legal conclusions about screenshots or deniability are omitted because no jurisdiction-specific legal review was performed.

## Who is Bob, really?

All of this protects Alice's conversation with the holder of IK_B. The server decides what IK_B is. A malicious or compelled server could hand Alice its own key and sit in the middle.

- **Safety numbers**: Signal and WhatsApp show a fingerprint derived from both identity keys. Compare it in person or scan a QR code, and a substituted key shows up as a mismatch.
- **Key-change warnings**: when a contact's identity key changes (new phone, or an attack), the app warns.
- **Key transparency**: auditable key directories can expose inconsistent key views when clients verify proofs and the design's monitoring/witness assumptions hold. WhatsApp described its deployment in 2023. Transparency does not by itself prove the real-world owner of a first-seen key or make all substitutions impossible.

## Key takeaways
- Shared-key tags alone are not transferable proof that one particular peer authored a message.
- Safety-number comparison authenticates the compared identity keys when done over a trusted channel.
- Key transparency detects specified inconsistent directory behaviour under its proof and monitoring assumptions.

## Further reading
- [X3DH specification — Signal](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet specification — Signal](https://signal.org/docs/specifications/doubleratchet/)
