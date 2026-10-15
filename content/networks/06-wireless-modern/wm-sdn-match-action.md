---
id: wm-sdn-match-action
title: OpenFlow tables and reactive flow setup
level: intermediate
minutes: 3
summary: Highest matching priority selects an OpenFlow entry; instructions and actions have distinct roles.
sourceLesson: wm-sdn
---

This unit focuses on OpenFlow tables and reactive flow setup. It builds on the earlier units in this module; the examples below state their additional assumptions.

## OpenFlow: match-action tables

**OpenFlow** came out of Stanford around 2008 as an influential early SDN control protocol. A switch holds **flow tables**. Each entry has:

- **Match fields**: ingress port, Ethernet source/destination and type, VLAN, IP source/destination (with masks), IP protocol, TCP/UDP ports, and more.
- **Priority**: when several entries match, the highest priority wins.
- **Instructions and actions**: instructions can apply/write actions or go to a higher-numbered table. Actions can output or modify packets. Dropping follows from ending processing without an output action; `Goto-Table` is an instruction, not an output action.
- **Counters**: packets and bytes matched, which the controller can read.
- **Timeouts**: an idle timeout (remove if unused) and a hard timeout (remove regardless).

## Tracing a flow table

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

## Reactive versus proactive

- **Reactive flow setup**: with a suitable miss rule, a first packet can generate a controller notification and an entry installation. The controller must also arrange forwarding of the original buffered/unbuffered packet when needed. Flexible, but the first packet pays a round trip to the controller, and a flood of new flows can overwhelm it.
- **Proactive flow setup**: the controller pre-installs all entries it can compute from the topology and policy. This avoids that reactive setup dependency for covered traffic. Wildcard/aggregate rules can cover many flows without storing one entry per connection.

Wildcard tables may use **TCAM**, while exact-match tables and other stages can use SRAM or different structures. Table size, width, pipeline stages and supported operations are hardware-specific constraints; OpenFlow does not require every table to be TCAM or every lookup to take one cycle.

## Beyond OpenFlow

OpenFlow fixed the set of headers a switch could match. **P4** (2014) lets you program the parser and match-action pipeline itself, within the target’s parser, pipeline, memory and action capabilities. P4 cannot make fixed hardware implement arbitrary unsupported operations. **Open vSwitch** (OVS) brought flow-table forwarding into software on hypervisors, on hosts; SDN also has hardware and other software implementations.

## Key takeaways
- Highest matching priority selects an OpenFlow entry; instructions and actions have distinct roles.
- Reactive setup consumes control resources; proactive rules cover traffic without that first-packet dependency.

## Further reading
- [OpenFlow — Wikipedia](https://en.wikipedia.org/wiki/OpenFlow)
- [P4 Language Consortium](https://p4.org/)
- [OpenFlow Switch Specification 1.3.5](https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.3.5.pdf)
- [P4 language specification1.2.4](https://p4.org/wp-content/uploads/sites/53/p4-spec/docs/P4-16-v1.2.4.html)
