---
id: nsec-vpn-access-boundaries
title: VPN access without broad internal trust
level: advanced
minutes: 3
summary: A remote-access VPN creates a network path, not unlimited authority.
sourceLesson: nsec-vpns
---

A VPN can protect traffic across an untrusted path while still granting too much access at its destination. The relevant question is what a stolen remote-access identity can reach after login.

Consider an employee who needs only one internal dashboard. If VPN membership permits access to every database and administration interface, encryption has protected a much broader path than the employee needs. Restrict the reachable resources or use a suitable identity-aware application proxy; the precise design depends on the application and administration requirements.

## VPNs in a security architecture

A remote-access VPN puts a device "on the network", which is exactly the location-based trust the earlier firewall and segmentation units warned about. Stolen VPN credentials or vulnerabilities in exposed VPN gateways can give attackers a way in. Internet-facing VPN gateways therefore require restricted administration, monitoring and timely fixes.

> [!note] Content gap
> A vendor-by-vendor list of recently exploited VPN vulnerabilities and an incident-frequency claim are omitted here because the individual advisories and a comparable incident dataset were not verified.

Good practice:

- MFA for remote access, and certificate-based device authentication.
- Prioritise fixes for known exploitation and high-risk exposed vulnerabilities; follow the applicable vendor advisory and incident response process.
- Treat VPN users as a separate, segmented zone, not as the office LAN.
- Prefer per-application access (identity-aware proxies) for most users, and keep network-level VPNs for site-to-site links and administrators.

> [!note] Content omitted after review
> A universal WireGuard/IPsec code-size comparison, protocol popularity ranking and fixed tunnel-MTU defaults are not asserted: implementation versions, options and path configurations were not specified for those claims. The earlier tunnel units instead give explicit header-budget models.

## Key takeaways
- A remote-access VPN creates a network path, not unlimited authority.
- Segment remote users and combine identity, device authentication and least privilege.
- Patch and monitor exposed VPN endpoints according to verified advisories.

## Further reading
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
- [RFC 4303: IP Encapsulating Security Payload (ESP)](https://www.rfc-editor.org/rfc/rfc4303)
- [WireGuard: Next Generation Kernel Network Tunnel (whitepaper)](https://www.wireguard.com/papers/wireguard.pdf)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
