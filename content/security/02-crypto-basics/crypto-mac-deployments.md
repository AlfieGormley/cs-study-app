---
id: crypto-mac-deployments
sourceLesson: crypto-macs
title: Webhooks, shared verifier keys and AEAD tags
level: intermediate
minutes: 3
summary: Every holder of an HMAC verification secret can also mint valid tags.
---

A MAC is only one part of a protocol. The following applications show why key distribution, message format and replay controls still matter.

## Where you meet MACs

- **Webhooks.** GitHub sends `X-Hub-Signature-256: sha256=<hex>`, an HMAC-SHA256 of the body using a secret you configured. Stripe's `Stripe-Signature` header signs a timestamp plus the body, so receivers can reject events outside an accepted time window. Preventing duplicate effects within that window also requires replay/idempotency handling.
- **AWS Signature Version 4.** SigV4-authenticated requests use HMAC-SHA256; AWS also supports other authentication paths, including asymmetric SigV4a. The signing key is derived by chaining HMACs over the date, region and service, so a leaked derived key is limited in scope.
- **JWTs with HS256.** The token's signature is HMAC-SHA256 under a shared secret. Anyone who can verify can also mint tokens, which is fine inside one service but wrong when many parties only need to verify.
- **Session cookies.** Frameworks such as Django and Flask provide signed-cookie mechanisms. Their session-storage choices differ; do not assume every default session cookie contains a signed copy of the session data.
- **Inside AEAD.** AES-GCM uses GHASH and ChaCha20-Poly1305 uses Poly1305. ChaCha20-Poly1305 derives a one-time Poly1305 key for each nonce. GCM reuses a GHASH subkey derived from the AES key and combines its result with a nonce-dependent mask; GHASH alone is not a complete secure MAC. Both modes require their specified nonce discipline.

> [!analogy] Real-world analogy: Checking a stamp by owning the stamp
> Imagine an office where the only way to check that a document carries the official stamp is to own a copy of that stamp and press it beside the original to compare. Every checking desk now holds a stamp, so any desk can also stamp documents of its own.
>
> **How it maps:** The stamp is the HMAC secret. Verifying an HMAC tag means recomputing it, which needs the same key that creates tags. Handing an HS256 secret to twelve verifying services hands all twelve the power to mint tokens. A signature scheme is like giving each desk a way to recognise the stamp without owning it: services verify with a public key that cannot sign.
>
> **Where it stops:** A good look at a physical stamp might help someone forge one, whereas a public key gives no feasible way to produce signatures. And a MAC is not weak because many parties use it; the risk is only that every key holder is equally trusted to create tags.

## Key takeaways
- Every holder of an HMAC verification secret can also mint valid tags.
- Webhook formats and AEAD constructions have their own exact authenticated inputs.

## Further reading
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
