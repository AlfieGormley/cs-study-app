---
id: nsec-zero-trust-access
title: Resource access with zero trust
level: intermediate
minutes: 3
summary: Network location alone grants no trust in the zero trust model.
sourceLesson: nsec-firewalls
---

Segmentation provides network boundaries. Zero trust adds resource access decisions based on identity, device context and policy, with monitoring that can change those decisions over time.

## Zero trust

Traditional design is **castle and moat**: hard perimeter, soft inside. In this simplified perimeter-only model, internal location grants broad trust; real perimeter designs can also enforce internal controls. That model fails when:

- An attacker gets one foothold inside (phishing, a vendor, a stolen VPN password).
- Staff work from home, cafés and phones, and data lives in SaaS and the cloud, so there is no single inside.

**Zero trust** (NIST SP 800-207) rejects trust based solely on network location. Its core ideas:

1. **Evaluate access to each resource** using subject and device identity and policy. NIST describes per-session access and ongoing reevaluation, not a requirement to make the user perform fresh MFA for every HTTP request.
2. **Check the device**: is it managed, patched and encrypted?
3. **Least privilege**: limit the resources and operations accessible for the task.
4. **Monitor and reevaluate**: collect relevant security telemetry and restrict or revoke access as risk changes. Shorter sessions limit some stolen-token exposure but do not automatically expire a stolen password or private key.

Google's **BeyondCorp** is an influential published implementation example, described in its 2014 paper. Employees reach internal applications through an **identity-aware proxy** on the public internet; being in a Google office grants nothing extra. Between services, **mutual TLS** can authenticate service identities, with authorisation enforced separately; a service mesh is one implementation option (the TLS units).

> [!warning] Zero trust is not "no firewalls"
> Zero trust adds identity checks; it does not remove network controls. Segmentation still limits blast radius when an identity is stolen, and an exposed management port is still exposed. Buying a product labelled "zero trust" while leaving a flat network behind it changes little.

## Pitfalls

- **Rule sprawl**: thousands of rules nobody dares delete. Tag each rule with an owner and a ticket, and review hits; a rule with zero hits for a year is a candidate for removal.
- **Any-any rules** added "temporarily" during an incident.
- **Forgotten paths**: management interfaces, backup networks and monitoring agents often bypass the segmentation everything else respects.
- **Trusting the VPN** as if it were the office (the tunnel and VPN units).
- **IPv6**: a reachable IPv6 path can bypass IPv4-only filtering when a service listens on IPv6 and no other control prevents it.

> [!note] Content omitted after review
> No ranking of the most common firewall errors, universal default-policy adoption rate or single zero-trust deployment recipe is supplied: the review has no representative measurement establishing those generalisations.

## Key takeaways
- Network location alone grants no trust in the zero trust model.
- Identity, device context and least privilege inform access and reevaluation.
- Review alternate paths, including IPv6, management networks and VPN access.

## Further reading
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [BeyondCorp: A New Approach to Enterprise Security — Google Research](https://research.google/pubs/beyondcorp-a-new-approach-to-enterprise-security/)
- [Control traffic to resources using security groups — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Control subnet traffic with network ACLs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Simple ruleset for a workstation — nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Simple_ruleset_for_a_workstation)
- [Firewall (computing) — Wikipedia](https://en.wikipedia.org/wiki/Firewall_(computing))
