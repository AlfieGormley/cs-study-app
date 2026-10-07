---
id: wm-sdn
title: Software-defined networking, OpenFlow and cloud VPCs
level: intermediate
minutes: 15
summary: Separating the control plane from the data plane, how OpenFlow match-action tables work, how overlays like VXLAN virtualise the network, and how a cloud VPC's subnets, route tables, security groups and NACLs actually behave.
---

Every router and switch does two jobs. The **data plane** forwards packets: look up the destination, pick an output port, perform the configured forwarding operation in hardware or software, at implementation-dependent rates. The **control plane** decides what the forwarding tables should contain: run OSPF or BGP, compute routes and program forwarding state. MAC learning can also be implemented locally in the data plane.

Traditionally both live in every box, and the network's behaviour emerges from hundreds of devices running distributed protocols, with management that may itself be automated. **Software-defined networking** (SDN) pulls the control plane out into software running on servers, which exposes programmable control interfaces to forwarding devices. Some architectures retain distributed routing and local decision-making.

Cloud virtual networks are a practical application of programmable networking. AWS and Google Cloud use the term VPC; Azure calls its corresponding construct a virtual network (VNet). Their scopes and firewall models differ.

## The SDN architecture

```
  apps: TE, firewall, load balancer
          | northbound API (REST etc.)
   +------+---------------------+
   |   controller (logically    |
   |   centralised, replicated) |
   +------+---------------------+
          | southbound API
          | (OpenFlow, P4Runtime)
  [switch]  [switch]  [switch]
   data plane: match -> action
```

Three ideas:

1. **Separation.** Forwarding behaviour and its policy/control logic can be programmed separately. Local failover, learning and hybrid routing may remain.
2. **Logically central control.** A controller can coordinate a broader view than one device, though observations can be incomplete or stale. Logical centralisation does not require one server or guarantee that a particular implementation is replicated.
3. **Programmability.** Network behaviour is software, so it can be versioned, tested and changed through APIs rather than by logging into boxes.

## OpenFlow: match-action tables

**OpenFlow** came out of Stanford around 2008 as an influential early SDN control protocol. A switch holds **flow tables**. Each entry has:

- **Match fields**: ingress port, Ethernet source/destination and type, VLAN, IP source/destination (with masks), IP protocol, TCP/UDP ports, and more.
- **Priority**: when several entries match, the highest priority wins.
- **Instructions and actions**: instructions can apply/write actions or go to a higher-numbered table. Actions can output or modify packets. Dropping follows from ending processing without an output action; `Goto-Table` is an instruction, not an output action.
- **Counters**: packets and bytes matched, which the controller can read.
- **Timeouts**: an idle timeout (remove if unused) and a hard timeout (remove regardless).

### Tracing a flow table

```
prio  match                  action
300   tcp dst=10.0.0.5:22    drop
200   ip  dst=10.0.0.5       out:2
100   ip  dst=10.0.0.0/24    out:3
0     (anything)             controller
```

| Packet | Matches | Result |
|---|---|---|
| TCP to 10.0.0.5:22 | 300, 200, 100, 0 | drop |
| TCP to 10.0.0.5:443 | 200, 100, 0 | port 2 |
| UDP to 10.0.0.9 | 100, 0 | port 3 |
| TCP to 192.168.1.1 | 0 | controller |

Multiple entries can match; priority decides. The priority-0 catch-all is a **table-miss** entry. In OpenFlow 1.3, if no table-miss entry is installed, unmatched packets are dropped by default; the exact miss behaviour depends on the OpenFlow version and table configuration.

### Reactive versus proactive

- **Reactive**: with a suitable miss rule, a first packet can generate a controller notification and an entry installation. The controller must also arrange forwarding of the original buffered/unbuffered packet when needed. Flexible, but the first packet pays a round trip to the controller, and a flood of new flows can overwhelm it.
- **Proactive**: the controller pre-installs all entries it can compute from the topology and policy. This avoids that reactive setup dependency for covered traffic. Wildcard/aggregate rules can cover many flows without storing one entry per connection.

Wildcard tables may use **TCAM**, while exact-match tables and other stages can use SRAM or different structures. Table size, width, pipeline stages and supported operations are hardware-specific constraints; OpenFlow does not require every table to be TCAM or every lookup to take one cycle.

### Beyond OpenFlow

OpenFlow fixed the set of headers a switch could match. **P4** (2014) lets you program the parser and match-action pipeline itself, within the target’s parser, pipeline, memory and action capabilities. P4 cannot make fixed hardware implement arbitrary unsupported operations. **Open vSwitch** (OVS) brought flow-table forwarding into software on hypervisors, on hosts; SDN also has hardware and other software implementations.

## Where SDN won

- **Hyperscale WANs.** Google's **B4**, described in a 2013 paper, connects its data centres with a centrally controlled traffic-engineering system. The paper reports high utilisation for its controlled workload and traffic-engineering design. This is a historical deployment result, not a universal target or comparison for every WAN; measurement, failure headroom and traffic priorities matter.
- **Data-centre fabrics.** Controllers configure and monitor large Clos fabrics as one system.
- **Network virtualisation.** Building isolated virtual networks for thousands of tenants on shared hardware. This is the cloud VPC.

## Overlays: virtual networks on a physical fabric

A cloud tenant wants their own private address space (two customers can both use `10.0.0.0/16`), their own subnets and firewall rules, and VMs that move between hosts. An overlay can keep much of this tenant-specific forwarding state out of the transit fabric, though tunnel endpoints and policies still need it.

The answer is an **overlay**: a tunnel endpoint, such as a hypervisor, switch or smart NIC, wraps each tenant packet in an outer packet addressed between physical hosts. The fabric just routes host to host.

**VXLAN** (RFC 7348) is the standard example:

```
| outer Eth | outer IP | UDP | VXLAN | inner
|   14 B    |  20 B    | 8 B |  8 B  | frame
             host A->B  :4789 VNI=24b
```

- The 24-bit **VXLAN Network Identifier** allows about 16 million segments, against 4,094 usable VLAN IDs.
- RFC 7348 recommends deriving the outer UDP source port from inner headers to provide entropy for outer-header ECMP. Actual path use depends on the hash, mapping and traffic.
- With outer IPv4 without options, UDP, VXLAN and untagged inner Ethernet without inner FCS, the outer IP packet contains **50 bytes in addition to the inner IP packet**: 20 + 8 + 8 + 14. Thus a 1,500-byte underlay IP MTU permits at most 1,450 inner IP bytes under these assumptions. Outer Ethernet is outside that IP MTU; tags, outer IPv6 or other encapsulation alter the budget. A tenant MTU of 1,500 instead needs at least 1,550 underlay IP bytes here, not necessarily a 9,000-byte jumbo frame. Getting this wrong produces the classic "small requests work, big ones hang" bug.

Something must know which physical host each virtual address lives on. In VXLAN fabrics, BGP EVPN often distributes that mapping. A cloud provider may use a proprietary distributed virtual-network datapath. Do not infer that every provider uses standard VXLAN or the same per-host architecture; AWS’s VPC behaviour below is an API-level example.

## A cloud VPC, piece by piece

An AWS VPC is a regional logical network supporting IPv4 and/or supported IPv6 configurations. The following describes a conventional private IPv4 example; other clouds have different scoping rules:

- **CIDR block**: e.g. `10.20.0.0/16`. Plan it so it does not overlap anything you may connect it to later (on-premises, other VPCs).
- **Subnets**: each lives in one availability zone. For an ordinary AWS private IPv4 subnet, the first four addresses and the last are reserved. These are offsets from the subnet base, not necessarily addresses ending .0–.3. The VPC DNS resolver is available at the primary VPC CIDR base plus two (and link-local addresses); each subnet’s base-plus-two is reserved, not necessarily its resolver endpoint. AWS does not support subnet broadcast. BYOIP has documented exceptions to the ordinary reservation rule.
- **Route tables**: a subnet is associated with one table, which can be shared by several subnets. A public IPv4 subnet has a direct Internet-gateway route; an instance also needs suitable public addressing, routes and filtering to communicate. Private subnets may use NAT, private connectivity or no Internet route. IPv6 egress uses different mechanisms.
- **Security groups**: attached to instances or network interfaces.
- **Network ACLs**: attached to subnets.

```python
import ipaddress

vpc = ipaddress.ip_network("10.20.0.0/16")
subnets = list(vpc.subnets(new_prefix=20))
for az, net in zip("abc", subnets):
    print(az, net, net.num_addresses - 5)
# a 10.20.0.0/20 4091
# b 10.20.16.0/20 4091
# c 10.20.32.0/20 4091
```

A `/16` holds sixteen `/20`s, so this plan leaves thirteen spare for private subnets and future growth.

### Security groups versus NACLs

| | Security group | Network ACL |
|---|---|---|
| Applies to | interface | subnet |
| State | stateful | stateless |
| Rules | allow only | allow and deny |
| Evaluation | all rules | in order, first match |

For an allowed tracked TCP connection, security-group state permits response traffic without a separate reverse-direction rule, while tracking remains valid. Other controls, including NACLs and routing, still apply. A NACL is **stateless**, so you must also allow the return traffic, which goes to the client's **ephemeral port** (typically somewhere in 1024–65535). Forgetting the outbound ephemeral rule on a custom NACL is a common outage.

Security groups can also reference other security groups: an eligible rule such as “allow TCP 5432 from app-servers” identifies associated interfaces rather than copying that group’s rules. Referencing depends on supported VPC relationships and path behaviour; middleboxes can change which source identity/address is applicable.

### Connecting VPCs

- **VPC peering** connects two VPCs privately. It is **not transitive**: if A peers with B and B with C, A cannot reach C through B.
- **Transit Gateway** is a regional hub that many VPCs and VPN connections attach to, with its own route tables.
- **PrivateLink** exposes one service from a VPC as an interface endpoint in another, without full routed peering between both address spaces. Connectivity is limited to the supported service/resource endpoint model; PrivateLink has additional endpoint types beyond this introductory interface-endpoint example.

> [!warning] Overlapping CIDRs
> VPC peering requires non-overlapping CIDRs. Other architectures may handle overlap with translation or service endpoints, but ordinary routing cannot unambiguously use duplicate destination ranges without additional context. Teams that give every VPC `10.0.0.0/16` by default discover this when they need to connect them, and renumbering a live VPC is painful. Allocate ranges centrally from day one.

## Trade-offs and failure modes

- **Controller availability.** Controller-loss behaviour is configured: in OpenFlow fail-secure mode retained entries can continue, subject to timeout expiry and other changes. Fail-standalone/hybrid behaviour and preinstalled local failover differ. Replication can improve availability but is not mandated by SDN itself.
- **Consistency during updates.** Changing many switches is not atomic; for a moment some use old rules and some new, which can cause loops or black holes. Techniques include two-phase updates with version tags.
- **Scale of reactive control.** Reactive control consumes controller/channel/table resources. Test its capacity and use aggregate/proactive rules where suitable; no universal flow-rate cutoff or deployment share is assumed here.
- **Debuggability.** A virtual network's state lives in software and hypervisors. Cloud tools like VPC Flow Logs and reachability analysers exist because `traceroute` inside an overlay often tells you little.

## Key takeaways
- SDN exposes programmable control over forwarding; architecture, replication and retained local control vary.
- OpenFlow tables select by priority and execute instructions/actions, with version-specific miss and failure behaviour.
- VXLAN carries a 24-bit VNI over UDP; calculate MTU from the actual outer and inner headers.
- AWS VPC subnet, routing, security-group and NACL rules are provider-specific. Stateful response allowance does not bypass other controls.
- Prepare new paths before using them, and retain old rules until in-flight old-path packets have drained.

> [!note] Evidence limits
> Universal SDN adoption shares, TCAM capacities, controller rate limits and unverified provider-internal datapaths are omitted. Cloud rules and product features must be rechecked against current documentation. This lesson’s arithmetic and table traces are models; no live AWS or OpenFlow fabric was deployed during review.

## Further reading
- [Software-defined networking — Wikipedia](https://en.wikipedia.org/wiki/Software-defined_networking)
- [OpenFlow — Wikipedia](https://en.wikipedia.org/wiki/OpenFlow)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
- [B4: Experience with a Globally-Deployed Software Defined WAN — Google Research](https://research.google/pubs/b4-experience-with-a-globally-deployed-software-defined-wan/)
- [What is Amazon VPC? — AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [Subnet CIDR blocks — AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html)
- [Control traffic with security groups — AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Network ACLs — AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [P4 Language Consortium](https://p4.org/)

- [OpenFlow Switch Specification 1.3.5](https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.3.5.pdf)
- [P4 language specification1.2.4](https://p4.org/wp-content/uploads/sites/53/p4-spec/docs/P4-16-v1.2.4.html)
