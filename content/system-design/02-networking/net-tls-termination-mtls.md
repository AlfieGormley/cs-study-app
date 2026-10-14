---
id: net-tls-termination-mtls
title: "TLS termination and service identity"
level: intermediate
minutes: 3
summary: "Choose edge termination, re-encryption or passthrough and understand mutual TLS lifecycle work."
sourceLesson: net-tls
---
The location that decrypts traffic determines what a load balancer can route on and who holds the private key. For internal connections, encryption and service authentication are separate requirements.

## Where to terminate TLS

"Termination" is where the encrypted connection ends and traffic is decrypted. You have three main patterns:

| Pattern | Where decrypted | Trade-off |
|---|---|---|
| Edge termination | LB / CDN | Simple; internal hop plaintext |
| Re-encryption | LB, then again at app | Encrypts both hops; adds another TLS connection and requires backend authentication policy |
| Passthrough | App server only | LB can't see HTTP (L4 only) |

```
Edge termination:
Client ==TLS==> LB --HTTP--> App

Re-encryption:
Client ==TLS==> LB ==TLS==> App

Passthrough:
Client ==========TLS========> App
           (LB forwards TCP)
```

**Edge termination** is the common default. The load balancer holds the certificate, offloads crypto from app servers, and can inspect HTTP to route by path, add headers like `X-Forwarded-For` and `X-Forwarded-Proto`, and apply a WAF.

But "plaintext inside the network" is increasingly unacceptable. **Zero-trust** designs and the risk of attackers moving laterally inside networks motivate **re-encryption** or **mutual TLS (mTLS)** between services. Validate backend identities as well as encrypting connections; encryption alone does not establish which service you reached. Service meshes automate mTLS so every service gets a certificate and identity.

**Passthrough** is used when the app must hold the key (end-to-end requirements) or needs the raw TLS session (e.g. for client certificates). The load balancer can still route by **SNI**, which is visible in the ClientHello, but can't see paths or headers. **Encrypted Client Hello (ECH)** hides the real SNI inside an encrypted inner ClientHello; an SNI-routing balancer then sees only the outer, public name unless it holds the ECH keys itself.

> [!note] Keys at the edge
> Edge termination on a CDN means a third party holds your private key or terminates on your behalf. For highly sensitive keys, options include short-lived delegated credentials or "keyless" setups where the CDN calls back to your own key server for the signing step.

## mTLS: when the client authenticates too

In normal TLS only the server presents a certificate. In **mutual TLS**, the client does too. That's common for:

- Service-to-service traffic in a mesh (Istio, Linkerd issue a certificate per workload).
- B2B APIs and payment networks.
- IoT devices with a certificate burned in at manufacture.

The hard part isn't the protocol but **certificate lifecycle**: issuing, rotating (at a configured lifetime and renewal interval) and revoking at scale. That's what mesh control planes and tools like SPIFFE/SPIRE automate.

## Key takeaways

- Edge termination enables HTTP routing; re-encryption protects a separate backend connection.
- Authenticate backend identities as well as encrypting their traffic.
- Passthrough can use visible SNI but cannot see HTTP paths; mTLS requires client certificates and lifecycle management.

## Further reading

- [TLS 1.3 (RFC 8446)](https://www.rfc-editor.org/rfc/rfc8446)
- [Encrypted Client Hello (RFC 9849)](https://www.rfc-editor.org/rfc/rfc9849)
- [What is Istio?](https://istio.io/latest/docs/concepts/what-is-istio/)
