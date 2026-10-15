---
id: nsec-segmentation-boundaries
title: Application inspection and segmentation
level: intermediate
minutes: 3
summary: An open HTTPS port does not identify the application behind it.
sourceLesson: nsec-firewalls
---

A firewall can inspect protocol content when it is available, while segmentation limits where traffic can go. Use both to ask which resources remain reachable after a compromise.

## Beyond ports: application-layer firewalls

Port 443 tells you almost nothing in a world where everything is HTTPS. **Next-generation firewalls** (NGFWs) identify the application, user and sometimes the content. **Web application firewalls** (WAFs) sit in front of HTTP services and block patterns such as SQL injection.

Reading encrypted HTTP content requires authorised decryption, such as TLS termination or interception with a trust anchor accepted by the client. Some application identification instead uses exposed metadata; installing a root certificate alone does not intercept traffic. Interception breaks certificate pinning, adds a high-value target and can weaken TLS if the middlebox is poorly implemented. It is a trade-off, not a free upgrade.

## Segmentation

A **flat network**, where every machine can reach every other machine, means one compromised laptop can probe every server. An attacker may **move laterally** from the initial foothold toward other resources.

> [!example] The Target breach (2013)
> A March 2014 Senate staff analysis described an apparent path from compromised HVAC-vendor credentials into sensitive network areas. It cited Target's confirmation that around 40 million payment-card accounts were exposed. The report explicitly relied on then-available reports and expert analysis, not a completed public forensic reconstruction. Its segmentation lesson is to restrict supplier access to necessary resources rather than grant broad internal reachability.

Segmentation draws internal boundaries:

```
  Internet
     |
 [edge firewall]
     |
   DMZ: web, mail  ----x---- no direct path
     |                      to databases
 [internal firewall]
     |
 +---+--------+-----------+
 | App tier   | DB tier   | Corp LAN
 +------------+-----------+
```

- A **DMZ** holds internet-facing services, so a compromised web server is still outside the internal network.
- **VLANs and subnets** separate departments, guest Wi-Fi, IoT devices and management interfaces.
- **Microsegmentation** goes down to individual workloads: each service can talk only to the specific services it needs, typically enforced on the host or by the hypervisor rather than by a central box.

The design question is always **blast radius**: if this machine falls, what else can the attacker reach? Each allowed path is a possible route for lateral movement.

## Key takeaways
- An open HTTPS port does not identify the application behind it.
- Inspecting encrypted HTTP requires appropriate decryption and introduces trust costs.
- Segmentation restricts the paths available after one workload is compromised.

## Further reading
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [BeyondCorp: A New Approach to Enterprise Security — Google Research](https://research.google/pubs/beyondcorp-a-new-approach-to-enterprise-security/)
- [Control traffic to resources using security groups — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Control subnet traffic with network ACLs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Simple ruleset for a workstation — nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Simple_ruleset_for_a_workstation)
- [Firewall (computing) — Wikipedia](https://en.wikipedia.org/wiki/Firewall_(computing))
