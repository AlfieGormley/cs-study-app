---
id: nsec-firewalls
title: Firewalls, segmentation and zero trust
level: intermediate
minutes: 13
summary: Stateless and stateful packet filters, how rule order and connection tracking work, cloud security groups versus network ACLs, why flat networks get breached, and what zero trust actually changes.
---

The previous lesson showed why receiving a packet does not, by itself, establish a trustworthy identity. A **firewall** is the first answer to that: a device or piece of software that sits on a boundary and decides, packet by packet or connection by connection, what is allowed through.

The second answer is to have more boundaries. **Segmentation** splits a network into zones so that a compromise in one zone does not hand over all of them. The third answer, **zero trust**, says that network location alone must not grant implicit trust.

This lesson works through all three, from the mechanics of a rule table up to architecture.

## What a firewall decides on

Every firewall matches traffic against a list of **rules**. The more of the packet it understands, the more precise the rules can be:

| Type | Looks at | Example rule |
|---|---|---|
| Stateless filter | Headers of one packet | Drop TCP to port 23 |
| Stateful | Headers plus connection state | Allow replies to my requests |
| Application (L7) | Protocol content | Block HTTP `POST /admin` |

Most rules are written in terms of the **5-tuple**: protocol, source IP, source port, destination IP, destination port. Add the direction (inbound or outbound) and the interface, and you can express most network policy.

### Rule order and default policy

The toy filter below uses **top-to-bottom, first-match evaluation**. Real products differ: AWS security groups combine allow rules, while nftables can continue across chains after an accept verdict. Anything that matches no rule gets the **default policy**, which should be *deny*.

```python
from ipaddress import ip_address, ip_network

RULES = [  # proto, port, source, action
    ("tcp", 22, "10.0.0.0/8", "allow"),
    ("tcp", 443, "0.0.0.0/0", "allow"),
    ("tcp", 22, "0.0.0.0/0", "deny"),
]

def check(proto, port, src):
    addr = ip_address(src)
    for p, dport, net, action in RULES:
        if p != proto or dport != port:
            continue
        if addr in ip_network(net):
            return action  # first match
    return "deny"  # default policy

print(check("tcp", 22, "10.1.2.3"))
print(check("tcp", 22, "203.0.113.9"))
print(check("udp", 53, "10.1.2.3"))
```

This prints `allow`, `deny`, `deny`. SSH from inside `10.0.0.0/8` matches rule 1. SSH from the internet skips rule 1 and hits rule 3. DNS matches nothing and falls through to the default.

Swap rules 1 and 3 and internal SSH breaks too, because the broad deny now matches first. Order bugs and broad rules that shadow narrow ones can contradict the intended policy. Good tooling flags **shadowed rules** that can never match.

> [!tip] Default deny, both ways
> Explicit inbound and outbound allowlists can reduce exposure. Egress restrictions can obstruct some command-and-control and exfiltration paths, but allowed services may still be abused; default-deny adoption is not universal.

## Stateless versus stateful

A **stateless** filter judges each packet alone. That causes a problem with replies. When your web server at port 443 answers a client, the reply goes *to* the client's **ephemeral port**, some random number such as 51,812. A stateless filter needs a rule covering the intended return traffic. For general public clients this often includes a range of destination ephemeral ports; source ports, addresses and protocol flags may further constrain a rule, but do not prove connection state.

A **stateful** firewall keeps a **connection table**. When it sees an allowed outbound SYN, it records the flow. Connection tracking supplies state that filtering rules can match. A known flow is accepted only when the applicable policy permits it:

```
 conntrack table (simplified)
 proto src:port        dst:port   state
 tcp   10.0.0.5:51812  1.2.3.4:443  ESTAB
 udp   10.0.0.5:40001  9.9.9.9:53   REPLIED
```

On Linux this is **conntrack**. This abbreviated nftables input-chain example explicitly accepts established and related traffic:

```
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

This is an input-chain fragment, not a complete deployment ruleset: it omits IPv6 neighbour discovery, router advertisements, other required ICMP handling, and forwarding/egress policy. Blindly applying it can break connectivity. UDP and ICMP tracking uses protocol-specific tuples and timeouts; a UDP reply does not establish application-level authentication.

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

Security groups can also reference *other security groups*: "allow port 5432 from members of `sg-web`". Within supported AWS connectivity arrangements, the reference resolves to associated interfaces' private addresses and follows membership changes. It is a network policy reference, not cryptographic proof of application identity; traffic through a middlebox can require different rules.

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

## Zero trust

Traditional design is **castle and moat**: hard perimeter, soft inside. In this simplified perimeter-only model, internal location grants broad trust; real perimeter designs can also enforce internal controls. That model fails when:

- An attacker gets one foothold inside (phishing, a vendor, a stolen VPN password).
- Staff work from home, cafés and phones, and data lives in SaaS and the cloud, so there is no single inside.

**Zero trust** (NIST SP 800-207) rejects trust based solely on network location. Its core ideas:

1. **Evaluate access to each resource** using subject and device identity and policy. NIST describes per-session access and ongoing reevaluation, not a requirement to make the user perform fresh MFA for every HTTP request.
2. **Check the device**: is it managed, patched and encrypted?
3. **Least privilege**: limit the resources and operations accessible for the task.
4. **Monitor and reevaluate**: collect relevant security telemetry and restrict or revoke access as risk changes. Shorter sessions limit some stolen-token exposure but do not automatically expire a stolen password or private key.

Google's **BeyondCorp** is an influential published implementation example, described in its 2014 paper. Employees reach internal applications through an **identity-aware proxy** on the public internet; being in a Google office grants nothing extra. Between services, **mutual TLS** can authenticate service identities, with authorisation enforced separately; a service mesh is one implementation option (lesson 3).

> [!warning] Zero trust is not "no firewalls"
> Zero trust adds identity checks; it does not remove network controls. Segmentation still limits blast radius when an identity is stolen, and an exposed management port is still exposed. Buying a product labelled "zero trust" while leaving a flat network behind it changes little.

## Pitfalls

- **Rule sprawl**: thousands of rules nobody dares delete. Tag each rule with an owner and a ticket, and review hits; a rule with zero hits for a year is a candidate for removal.
- **Any-any rules** added "temporarily" during an incident.
- **Forgotten paths**: management interfaces, backup networks and monitoring agents often bypass the segmentation everything else respects.
- **Trusting the VPN** as if it were the office (lesson 4).
- **IPv6**: a reachable IPv6 path can bypass IPv4-only filtering when a service listens on IPv6 and no other control blocks it.

> [!note] Content omitted after review
> No ranking of the most common firewall errors, universal default-policy adoption rate or single zero-trust deployment recipe is supplied: the review has no representative measurement establishing those generalisations.

## Key takeaways
- Firewall evaluation semantics vary. The toy model is first-match; choose explicit defaults and needed inbound/outbound allowances.
- Stateful firewalls track flows so policy can allow matching replies; the state table is a resource attackers can exhaust.
- AWS security groups are stateful and allow-only; NACLs are stateless and ordered, so they need explicit rules for ephemeral return ports.
- Segmentation limits lateral movement; design each zone around its blast radius.
- Zero trust rejects trust based solely on location, evaluates resource access with identity and device context, and complements network controls.

## Further reading
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [BeyondCorp: A New Approach to Enterprise Security — Google Research](https://research.google/pubs/beyondcorp-a-new-approach-to-enterprise-security/)
- [Control traffic to resources using security groups — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Control subnet traffic with network ACLs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Simple ruleset for a workstation — nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Simple_ruleset_for_a_workstation)
- [Firewall (computing) — Wikipedia](https://en.wikipedia.org/wiki/Firewall_(computing))
