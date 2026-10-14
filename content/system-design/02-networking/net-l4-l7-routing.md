---
id: net-l4-l7-routing
title: "L4, L7 and direct server return"
level: intermediate
minutes: 3
summary: "Choose a traffic layer for packet forwarding, request routing and response bandwidth."
sourceLesson: net-load-balancers
---
A load balancer sits in front of a pool of servers and decides which one handles each connection or request. It gives you three things at once:

- **Scale:** add servers behind one address.
- **Availability:** stop sending traffic to servers that fail.
- **Operability:** drain, deploy and replace servers without users noticing.

Choosing a load balancer is mostly about two questions: *at which layer does it work*, and *how does it choose a server*?

## L4 vs L7

```
        L4 (transport)
Client --TCP/UDP--> LB --> backend
  sees: IPs, ports, protocol

        L7 (application)
Client --HTTP--> LB --> backend
  sees: path, headers, cookies,
        method, gRPC service
```

| | L4 | L7 |
|---|---|---|
| Unit balanced | Connection / flow | Request |
| Sees | IP, port | URL, headers, body |
| TLS | Usually passthrough | Terminates |
| Work | Packet forwarding | HTTP parsing and proxying |
| Examples | AWS NLB, Maglev, Katran | AWS ALB, Envoy, NGINX |

**L4 load balancers** forward packets based on the 5-tuple (source IP/port, destination IP/port, protocol). They're extremely fast and protocol-agnostic: they work for databases, MQTT, SMTP, anything over TCP or UDP. Google's Maglev and Meta's Katran use software packet forwarding designed for high throughput; their achieved rates depend on hardware, packet sizes and configuration. Some use **direct server return (DSR)**: responses go straight from the backend to the client, bypassing the balancer, which matters because responses are usually much bigger than requests.

**L7 load balancers** terminate the client's connection, parse HTTP, and open (or reuse) separate connections to backends. That costs more CPU but enables:

- Routing by path or host (`/api` → API service, `/img` → image service).
- Per-request balancing of multiplexed HTTP/2 and gRPC.
- Retries, timeouts, header rewriting, auth, rate limiting, compression.
- Detailed metrics per route and status code.

> [!tip] The common layering
> Large deployments often stack both: an L4 tier (anycast + ECMP across many machines) spreads connections over a fleet of L7 proxies, which then do the smart per-request work. The L4 tier is simple and scales; the L7 tier is flexible.

## Key takeaways

- L4 forwards transport flows; L7 understands HTTP requests and can route by path or headers.
- Direct server return lets large responses bypass an L4 balancer.
- Layering an L4 fleet ahead of L7 proxies separates connection distribution from application policy.

## Further reading

- [Application Load Balancer overview (AWS)](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Maglev (Google Research)](https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/)
