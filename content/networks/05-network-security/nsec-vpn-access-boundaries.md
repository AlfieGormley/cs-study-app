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

Good practice:

- MFA for remote access, and certificate-based device authentication.
- Prioritise fixes for known exploitation and high-risk exposed vulnerabilities; follow the applicable vendor advisory and incident response process.
- Treat VPN users as a separate, segmented zone, not as the office LAN.
- Prefer per-application access (identity-aware proxies) for most users, and keep network-level VPNs for site-to-site links and administrators.

## Key takeaways
- A remote-access VPN creates a network path, not unlimited authority.
- Put remote users in their own network segment and combine identity, device authentication and least privilege.
- Patch and monitor exposed VPN endpoints according to verified advisories.

## Further reading
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
