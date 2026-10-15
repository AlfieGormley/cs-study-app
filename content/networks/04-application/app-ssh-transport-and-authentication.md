---
id: app-ssh-transport-and-authentication
title: "SSH transport, host trust and authentication"
level: advanced
minutes: 4
sourceLesson: app-ntp-ssh-grpc
summary: "SSH establishes a protected transport, authenticates users and then multiplexes useful channels."
---

## SSH: three protocols in a stack

SSH (RFCs 4251 to 4254) runs over **TCP port 22** and is really three protocols layered on top of each other:

```
+-----------------------------+
| Connection: channels       |
|  (shell, exec, sftp, -L)   |
+-----------------------------+
| User authentication        |
|  (publickey, password)     |
+-----------------------------+
| Transport: key exchange,   |
|  encryption, integrity     |
+-----------------------------+
| TCP                        |
+-----------------------------+
```

### Transport layer

1. Both sides send a **version string** in plaintext, such as `SSH-2.0-OpenSSH_9.6`.
2. Both send **KEXINIT** listing supported algorithms in preference order: key exchange, host key types, ciphers, message authentication codes, compression. Negotiation generally follows client preference among mutually supported choices, subject to compatibility rules between key-exchange and host-key algorithms.
3. **Key exchange**: an ephemeral Diffie-Hellman exchange, these days `curve25519-sha256` or a post-quantum hybrid. OpenSSH 9.0 made `sntrup761x25519-sha512@openssh.com` the default, and OpenSSH 10.0 switched to `mlkem768x25519-sha256`.
4. The server **signs** the exchange hash with its **host key**. The client checks that key against `~/.ssh/known_hosts`. Without a preconfigured trusted host key or host-certificate authority, a first connection can prompt for **trust on first use** (TOFU). Independently checking the fingerprint avoids blindly trusting that first peer.
5. Session keys are derived from the shared secret and the exchange hash. The first exchange hash becomes the permanent **SSH session ID**.

After the version strings, SSH already uses the **binary packet protocol**; initial key-exchange packets are unencrypted. `NEWKEYS` activates the negotiated protection. The base packet structure is:

```
uint32  packet_length
byte    padding_length
byte[]  payload
byte[]  random padding (>= 4)
byte[]  MAC (or AEAD tag)
```

In the base RFC 4253 format, packet length including its four-byte length field but excluding the message authentication code is aligned to the cipher block size or 8 bytes, whichever is larger. Negotiated AEAD/Encrypt-then-MAC formats alter some framing and authentication details. Padding provides limited length hiding. Modern ciphers such as `chacha20-poly1305@openssh.com` and AES-GCM are AEADs, so integrity comes from the cipher's tag. Each direction tracks an implicit **SSH sequence number**. Base RFC 4253 MACs and some negotiated modes use that counter; SSH AES-GCM instead uses its IV-based invocation counter (RFC 5647). Integrity protection normally detects invalid packet manipulation, but the handshake interaction below exposed an exception for affected modes.

> [!warning] Terrapin (2023)
> Sequence numbers were not reset after the handshake. With affected encryption modes (notably ChaCha20-Poly1305 or CBC with Encrypt-then-MAC), an on-path attacker could inject a message during the unencrypted phase and delete one afterwards, keeping the counts consistent, and so silently strip extension negotiation. The fix, "strict KEX", resets sequence numbers at NEWKEYS and forbids stray messages during the handshake; both client and server must support it.

### User authentication

Within the encrypted transport, the client requests the `ssh-userauth` service and tries methods: **publickey**, password, keyboard-interactive (for OTPs). For publickey, the client signs a blob containing the **SSH session ID**, so a captured signature can't be replayed on another connection. A server talking to an attacker in the middle would have a different session ID, so the signature would not verify.

**Agent forwarding** (`ssh -A`) lets a remote host ask your local agent to sign for you. A privileged attacker on that host can request signatures through an unconstrained forwarded agent while it remains accessible. Confirmation, destination and hardware constraints can limit use; forwarding does not normally reveal the private key itself. `ProxyJump` (`ssh -J`) is safer for hopping through bastions: the end-to-end session is negotiated from your laptop.

## Key takeaways
- SSH establishes a protected transport, authenticates users and then multiplexes useful channels.
- Host-key trust and session-bound public-key authentication solve different impersonation and replay problems.

## Further reading
- [RFC 5647: SSH AES-GCM](https://www.rfc-editor.org/rfc/rfc5647)
- [RFC 4253](https://www.rfc-editor.org/rfc/rfc4253)
- [RFC 4252](https://www.rfc-editor.org/rfc/rfc4252)
- [OpenSSH 10.0 release](https://www.openssh.com/txt/release-10.0)
- [Terrapin original research](https://terrapin-attack.com/)
