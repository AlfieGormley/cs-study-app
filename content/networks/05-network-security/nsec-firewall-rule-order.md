---
id: nsec-firewall-rule-order
title: Packet policy and rule order
level: intermediate
minutes: 3
summary: A first-match filter stops at its first matching rule.
sourceLesson: nsec-firewalls
---

The earlier threat units showed why receiving a packet does not, by itself, establish a trustworthy identity. A **firewall** is the first answer to that: a device or piece of software that sits on a boundary and decides, packet by packet or connection by connection, what is allowed through.

The second answer is to have more boundaries. **Network segmentation** splits a network into zones so that a compromise in one zone does not hand over all of them. The third answer, **zero trust**, says that network location alone never grants implicit trust.

This unit focuses on rule matching and its default policy.

## What a firewall decides on

Every firewall matches traffic against a list of **firewall rules**. The more of the packet it understands, the more precise the rules can be:

| Type | Looks at | Example rule |
|---|---|---|
| Stateless filter | Headers of one packet | Drop TCP to port 23 |
| Stateful | Headers plus connection state | Allow replies to my requests |
| Application (L7) | Protocol content | Block HTTP `POST /admin` |

Most rules are written in terms of the **5-tuple**: protocol, source IP, source port, destination IP, destination port. Add the direction (inbound or outbound) and the interface, and you can express most network policy.

### Rule order and default policy

The toy filter below uses **top-to-bottom, first-match evaluation**. Real products differ: AWS security groups combine allow rules, while nftables can continue across chains after an accept verdict. Anything that matches no rule gets **the default policy**, which should be *deny*.

```python
from ipaddress import ip_address, ip_network

RULES = [  # proto, port, source, action
    ("tcp", 22, "10.0.0.0/8", "allow"),
    ("tcp", 443, "0.0.0.0/0", "allow"),
    ("tcp", 22, "0.0.0.0/0", "deny"),
]

def check(proto, port, src):
    addr = ip_address(src)
    # Keep rule order: the first match wins.
    for p, dport, net, action in RULES:
        if p != proto or dport != port:
            # Skip a different service.
            continue
        if addr in ip_network(net):
            return action  # first match
    # No rule matched this packet.
    return "deny"  # default policy

# Compare internal SSH, public SSH and DNS.
print(check("tcp", 22, "10.1.2.3"))
print(check("tcp", 22, "203.0.113.9"))
print(check("udp", 53, "10.1.2.3"))
```

This prints `allow`, `deny`, `deny`. SSH from inside `10.0.0.0/8` matches rule 1. SSH from the internet skips rule 1 and hits rule 3. DNS matches nothing and falls through to the default.

Swap rules 1 and 3 and internal SSH breaks too, because the broad deny now matches first. Order bugs and broad rules that shadow narrow ones can contradict the intended policy. Good tooling flags **shadowed rules** that can never match.

> [!analogy] Real-world analogy: a door supervisor's ordered checklist
> A door supervisor works down a written list and acts on the first line that fits each guest: "staff with a badge: let in", "anyone in football shirts: refuse", "ticket holders: let in". Anyone the list does not mention is refused.
>
> **How it maps:** Each line is a firewall rule, acting on the first line that fits is first-match evaluation, and "refuse anyone not mentioned" is a default-deny policy. If "refuse football shirts" sits above "staff with a badge", a staff member in a football shirt is turned away: the broad rule shadows the narrower one beneath it.
>
> **Where it stops:** A person can use judgement when the list seems wrong; a firewall applies the rules exactly. Real products also differ in how they evaluate rules: AWS security groups have no order at all, and nftables can pass a packet through several chains.

> [!tip] Default deny, both ways
> Explicit inbound and outbound allowlists can reduce exposure. Egress restrictions can obstruct some command-and-control and exfiltration paths, but allowed services may still be abused; default-deny adoption is not universal.

## Key takeaways
- A first-match filter stops at its first matching rule.
- A broad earlier rule can shadow a later specific rule.
- Explicit defaults and outbound controls make permitted paths easier to review.

## Further reading
- [Firewall (computing) — Wikipedia](https://en.wikipedia.org/wiki/Firewall_(computing))
- [Control subnet traffic with network ACLs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Simple ruleset for a workstation — nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Simple_ruleset_for_a_workstation)
