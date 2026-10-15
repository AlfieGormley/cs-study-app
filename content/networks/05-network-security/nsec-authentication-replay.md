---
id: nsec-authentication-replay
title: Authentication and replay protection
level: basic
minutes: 3
summary: An encrypted channel to an impostor still exposes data to that impostor.
sourceLesson: nsec-threats
---

A passive observer reads traffic; an active attacker may relay it or resend an earlier valid message. The objective here is to distinguish peer authentication from message freshness.

## Man-in-the-middle

A **man-in-the-middle (MITM)** attacker sits between two parties, relaying and possibly altering traffic while each side believes it is talking directly to the other. An unmitigated MITM can threaten confidentiality, integrity and authentication; correctly authenticated encryption can prevent reading or modifying protected content even when traffic is relayed.

```
 Normal:
 Alice ------------------------> Bank

 MITM:
 Alice ----> Mallory ----> Bank
   "I am the Bank"  "I am Alice"
```

Ways to get in the middle:

- **ARP spoofing** on a LAN: tell the victim "the gateway's IP is at my MAC address".
- **Rogue Wi-Fi access points** ("evil twins", the wireless units).
- **DNS spoofing**: make the domain resolve to the attacker's IP.
- **BGP hijacking**: an unauthorised announcement may redirect traffic in networks that accept and select it.

Encryption alone does not stop MITM. If Alice does a key exchange with Mallory, she has a perfectly encrypted channel to the attacker. What stops MITM is **authentication**: Alice must verify she is talking to the real bank. In TLS that is the certificate check (the TLS units). This is why clicking through a certificate warning is so dangerous.

## Replay

In a **replay attack** the attacker captures a valid message and sends it again later. They do not need to read or change it.

> [!example] A replayed payment
> A client sends an encrypted, signed message: "pay merchant £50". The attacker cannot read it, but captures it and sends it ten more times. If the server only checks the signature, it pays out £550.

The signature is valid every time, because it is the same message. The defence is to make each message usable **once**:

- **Nonces**: include a unique value in the authenticated request; atomically reject reuse in the relevant session or account.
- **Timestamps**: an authenticated timestamp can limit the timestamp validity interval, but a replay inside that window still needs duplicate detection. Clock and expiry rules must be defined.
- **Sequence numbers**: authenticate counters and track accepted values. An ordered channel can require the next counter; an IPsec-style anti-replay window can accept unseen out-of-order packets while rejecting duplicates and packets that are too old. TLS early data has separate replay caveats (the TLS units).

## Key takeaways
- An encrypted channel to an impostor still exposes data to that impostor.
- Preventing replay needs authenticated freshness information and receiver state.
- A timestamp bounds age; duplicate detection handles reuse inside that bound.

## Further reading
- [UDP-Based Amplification Attacks — CISA](https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks)
- [RFC 2827 (BCP 38): Network Ingress Filtering](https://www.rfc-editor.org/rfc/rfc2827)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [Amplification Hell: Revisiting Network Protocols for DDoS Abuse (NDSS 2014)](https://www.ndss-symposium.org/ndss2014/programme/amplification-hell-revisiting-network-protocols-ddos-abuse/)
- [February 28th DDoS incident report — GitHub blog](https://github.blog/news-insights/company-news/ddos-incident-report/)
- [Understanding the Mirai Botnet (USENIX Security 2017)](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/antonakakis)
