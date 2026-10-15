---
id: pki-e2ee-limits
title: E2EE endpoints, metadata and backups
level: advanced
minutes: 1
sourceLesson: pki-e2ee
summary: Endpoint malware can read content after decryption even when the transport cryptography works.
---

End-to-end encryption keeps message-content keys at the communicating endpoints. Signal’s protocol family uses uploaded prekeys to start sessions and ratcheting keys to protect ongoing conversations.

## What E2EE does not protect

- **Endpoints.** Spyware like Pegasus reads messages on the phone after decryption. E2EE moves the target to the device.
- **Metadata.** The server still sees who talks to whom, when, from which IP and how often. Signal's **sealed sender** reduces explicit sender identity exposed to the delivery service. Timing, recipient addressing and network observations can still reveal metadata; it is not guaranteed anonymity.
- **Backups.** A chat history backed up to the cloud unencrypted is a copy outside E2EE. WhatsApp added optional end-to-end encrypted backups in 2021.
- **The other person.** A recipient can screenshot or forward anything.
- **Abuse reporting and moderation** have to work without the server seeing content, usually by having the reporting user send messages in themselves.

## Key takeaways
- Endpoint malware can read content after decryption even when the transport cryptography works.
- Sealed sender reduces certain explicit metadata; traffic analysis and recipient observations remain.
- Backups, screenshots and user-submitted abuse reports create separate content disclosures.

## Further reading
- [X3DH specification — Signal](https://signal.org/docs/specifications/x3dh/)
- [Double Ratchet specification — Signal](https://signal.org/docs/specifications/doubleratchet/)
- [The X3DH Key Agreement Protocol — Signal](https://signal.org/docs/specifications/x3dh/)
- [The Double Ratchet Algorithm — Signal](https://signal.org/docs/specifications/doubleratchet/)
- [Quantum Resistance and the Signal Protocol — Signal blog](https://signal.org/blog/pqxdh/)
- [Signal Protocol and Post-Quantum Ratchets — Signal blog](https://signal.org/blog/spqr/)
- [Deploying key transparency at WhatsApp — Meta Engineering](https://engineering.fb.com/2023/04/13/security/whatsapp-key-transparency/)
- [RFC 9420: The Messaging Layer Security (MLS) Protocol](https://www.rfc-editor.org/rfc/rfc9420)
