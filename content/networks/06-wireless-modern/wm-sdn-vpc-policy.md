---
id: wm-sdn-vpc-policy
title: Stateful groups, stateless ACLs and VPC connections
level: intermediate
minutes: 3
summary: Valid security-group tracking permits replies without a separate reverse rule, subject to other controls.
sourceLesson: wm-sdn
---

AWS gives a VPC two packet-filtering layers that look similar but behave very differently: one remembers connections and one does not. Mixing them up is a common cause of outages, as is assuming that connected VPCs can reach each other through a middle one.

## Security groups versus NACLs

| | Security group | Network ACL |
|---|---|---|
| Applies to | interface | subnet |
| State | stateful | stateless |
| Rules | allow only | allow and deny |
| Evaluation | all rules | in order, first match |

For an allowed tracked TCP connection, security-group state permits response traffic without a separate reverse-direction rule, while tracking remains valid. Other controls, including NACLs and routing, still apply. A NACL is **stateless**, so you must also allow the return traffic, which goes to the client's **ephemeral port** (typically somewhere in 1024–65535). Forgetting the outbound ephemeral rule on a custom NACL is a common outage.

Security groups can also reference other security groups: an eligible rule such as “allow TCP 5432 from app-servers” identifies associated interfaces rather than copying that group’s rules. Referencing depends on supported VPC relationships and path behaviour; middleboxes can change which source identity/address is applicable.

## Connecting VPCs

- **VPC peering** connects two VPCs privately. It is **not transitive**: if A peers with B and B with C, A cannot reach C through B.
- **Transit Gateway** is a regional hub that many VPCs and VPN connections attach to, with its own route tables.
- **PrivateLink** exposes one service from a VPC as an interface endpoint in another, without full routed peering between both address spaces. Connectivity is limited to the supported service/resource endpoint model; PrivateLink has additional endpoint types beyond this introductory interface-endpoint example.

> [!warning] Overlapping CIDRs
> VPC peering requires non-overlapping CIDRs. Other architectures may handle overlap with translation or service endpoints, but ordinary routing cannot unambiguously use duplicate destination ranges without additional context. Teams that give every VPC `10.0.0.0/16` by default discover this when they need to connect them, and renumbering a live VPC is painful. Allocate ranges centrally from day one.

## Key takeaways
- Valid security-group tracking permits replies without a separate reverse rule, subject to other controls.
- A stateless NACL needs both directions and uses the first matching numbered rule.
- VPC peering is non-transitive and requires non-overlapping address ranges.

## Further reading
- [Control traffic with security groups — AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Network ACLs — AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
