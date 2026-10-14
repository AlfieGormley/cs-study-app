---
id: net-anycast-connections-capacity
title: "Anycast connection state and edge routing"
level: advanced
minutes: 3
summary: "Plan route withdrawal, inherited traffic and stable-edge routing without promising seamless connection migration."
sourceLesson: net-global-traffic
---
A stable IP is useful during failures, but it does not preserve connection state or distribute inherited traffic evenly. Separate the anycast edge from the region-routing decision behind it.

### Anycast's caveats

- **"Nearest" by BGP isn't always nearest by latency.** ISP peering choices can send a user in Paris to a PoP in Amsterdam or even further.
- **Route changes can break TCP.** If BGP shifts mid-connection, packets start arriving at a different site that has no state for that connection, and it resets. For short HTTP requests this is rare and tolerable; for long-lived connections it hurts. QUIC doesn't escape this either, since the new site has no keys for the connection. Operators keep routes stable and use connection-aware L4 layers.
- **Withdrawing a site sends its traffic to the next-nearest sites,** not evenly everywhere. Taking down a big PoP can overload its neighbours, so capacity planning has to consider who inherits each site's users.
- **Anycast is usually only the front door.** Stateless UDP (DNS) is the ideal fit. For TCP services, operators terminate connections at the anycast edge and use ordinary unicast routing behind it.
- **Capacity control is coarse.** You can't directly say "send 30% to London". Operators shape it with route withdrawals, AS-path prepending or BGP communities, all blunt tools.

### Combining them

Many large systems use **anycast to the edge, then private routing to regions**:

```
User --anycast--> nearest edge PoP
        (TLS terminates here)
              |
         private backbone
              |
       chosen origin region
  (by latency, health, capacity)
```

The edge picks the origin region per request with up-to-date health data, which avoids DNS caching entirely for the region decision.

A fast-failover objective requires more than an anycast address. Health detection, edge policy, client connection timeouts and reconnect behaviour determine when a failed long-lived connection reaches a healthy region. Test those together; the technique removes a DNS re-resolution dependency, not every outage delay.

## Key takeaways

- A route change can send connection packets to a site without their state or QUIC keys.
- A withdrawn PoP’s traffic follows routing catchments, so nearby survivors can overload.
- A stable anycast edge can choose healthy origin regions; clients still need tested detection and reconnect behaviour.

## Further reading

- [Operation of anycast services (RFC 4786)](https://www.rfc-editor.org/rfc/rfc4786)
- [What is AWS Global Accelerator?](https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html)
