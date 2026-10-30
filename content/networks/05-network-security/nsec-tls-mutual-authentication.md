---
id: nsec-tls-mutual-authentication
title: Mutual TLS and service authorisation
level: intermediate
minutes: 3
summary: Full certificate-based mTLS proves possession of both server and client private keys.
sourceLesson: nsec-tls
---

The certificate handshake so far authenticated the server. A service-to-service connection can also require a client certificate. This unit tracks where that proof ends and where application authorisation begins.

## Mutual TLS

In a full server-certificate TLS handshake, the client need not supply a certificate and may authenticate at the application layer later. For certificate-based **mutual TLS (mTLS)**, the server requests a client certificate and the client supplies Certificate and CertificateVerify when authenticating. PSK resumption does not repeat these certificate messages.

```
Server: {CertificateRequest} ...
Client: {Certificate}
        {CertificateVerify}
        {Finished}
```

Where it is used:

- **Service-to-service** traffic in zero trust designs (the earlier firewall and segmentation units). Configured service meshes can issue workload certificates and apply mTLS. For example, Istio uses SPIFFE-style identities and separate authentication/authorisation policies; permissive modes and unenrolled workloads require attention.
- **APIs** for banks and payment networks, IoT devices and internal admin tools.

Trade-offs and pitfalls:

- You usually run a **private CA**, and must issue, rotate and revoke certificates for every client. Automation is the whole game.
- A certificate proves **who** the caller is, not **what** they may do. You still need authorisation: "service `checkout` may call `POST /charge`".
- TLS terminated at a load balancer ends the mTLS there; the backend must trust the balancer to pass on the verified identity, usually in a header that clients must be prevented from setting themselves.

## Key takeaways
- Full certificate-based mTLS proves possession of both server and client private keys.
- Identity authentication and permission to perform an operation are separate decisions.
- When a trusted proxy terminates mTLS, protect the identity it forwards to the backend.

## Further reading
- [RFC 9846: TLS 1.3, client authentication](https://www.rfc-editor.org/rfc/rfc9846.html)
- [Istio security concepts](https://istio.io/latest/docs/concepts/security/)
