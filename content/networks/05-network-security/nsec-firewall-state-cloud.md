---
id: nsec-firewall-state-cloud
title: Connection state and cloud return traffic
level: intermediate
minutes: 4
summary: Connection state lets policy recognise reply traffic but consumes finite memory.
sourceLesson: nsec-firewalls
---

Rule order is only part of a firewall’s behaviour. A packet may be a reply in an existing flow, or a new attempt requiring another state entry. This unit follows that distinction into AWS subnet and interface controls.

## Stateless versus stateful

A **stateless** filter judges each packet alone. That causes a problem with replies. When your web server at port 443 answers a client, the reply goes *to* the client's **ephemeral port**, some random number such as 51,812. A stateless filter needs a rule covering the intended return traffic. For clients anywhere on the internet this often includes a range of destination ephemeral ports; source ports, addresses and protocol flags may further constrain a rule, but do not prove connection state.

A **stateful** firewall keeps **a connection table**. When it sees an allowed outbound SYN, it records the flow. Connection tracking supplies state that filtering rules can match. A known flow is accepted only when the applicable policy permits it:

```
 conntrack table (simplified)
 proto src:port        dst:port   state
 tcp   10.0.0.5:51812  1.2.3.4:443  ESTAB
 udp   10.0.0.5:40001  9.9.9.9:53   REPLIED
```

On Linux this is **conntrack**. This abbreviated nftables input-chain example explicitly accepts established and related traffic:

```nftables
table inet filter {
  chain input {
    type filter hook input priority 0;
    policy drop;
    ct state established,related accept
    ct state invalid drop
    iif "lo" accept
    tcp dport 22 ip saddr 10.0.0.0/8 accept
    tcp dport { 80, 443 } accept
  }
}
```

The `inet` family covers both IPv4 and IPv6; the `ip saddr` condition is specifically IPv4. A new IPv6 SSH attempt matches neither the IPv4 SSH allow rule nor the web-port rules and falls through to drop.

This is an input-chain fragment, not a complete deployment ruleset: it omits IPv6 neighbour discovery, router advertisements, other required ICMP handling, and forwarding and outbound policy. Blindly applying it can break connectivity. UDP and ICMP tracking uses protocol-specific tuples and timeouts; a UDP reply does not establish application-level authentication.

### The cost of state

State is memory, and memory can run out. The connection table is itself a DoS target: a SYN flood or many short UDP flows can fill it, after which the firewall drops new connections, including legitimate ones. Timeouts matter too. Linux keeps an idle established TCP entry for five days by default, while many cloud load balancers and NAT gateways drop idle flows after minutes, which is why long-lived idle connections mysteriously die unless they send keepalives.

## Firewalls in the cloud

AWS is a good case study because it gives you both kinds side by side:

| | Security group | Network ACL |
|---|---|---|
| Applies to | Network interface | Subnet |
| State | Stateful | Stateless |
| Rules | Allow only | Allow and deny |
| Evaluation | All rules together | Numbered order, first match |

Because NACLs are stateless, you must explicitly allow return traffic to ephemeral ports (AWS suggests 1024 to 65535). Forgetting the outbound ephemeral rule is a classic cause of "the security group is open but nothing works".

Security groups can also reference *other security groups*: "allow port 5432 from members of `sg-web`". Within supported AWS connectivity arrangements, the reference resolves to associated interfaces' private addresses and updates automatically as interfaces join or leave the group. It is a network policy reference, not cryptographic proof of application identity; traffic through a middlebox can require different rules.

## Key takeaways
- Connection state lets policy recognise reply traffic but consumes finite memory.
- AWS security groups combine stateful allow rules; NACLs are ordered and stateless.
- Return ports and idle timeouts matter even when the service port is open.

## Further reading
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [BeyondCorp: A New Approach to Enterprise Security — Google Research](https://research.google/pubs/beyondcorp-a-new-approach-to-enterprise-security/)
- [Control traffic to resources using security groups — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Control subnet traffic with network ACLs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Simple ruleset for a workstation — nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Simple_ruleset_for_a_workstation)
- [Firewall (computing) — Wikipedia](https://en.wikipedia.org/wiki/Firewall_(computing))
