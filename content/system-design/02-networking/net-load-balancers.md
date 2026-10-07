---
id: net-load-balancers
title: "Load balancers: L4 vs L7, algorithms and health checks"
level: intermediate
minutes: 15
summary: How load balancers spread traffic, the difference between L4 and L7, which algorithm to pick and why, and how health checks and sticky sessions go wrong.
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
| Speed | Millions of pps | Lower, more CPU |
| Examples | AWS NLB, Maglev, Katran | AWS ALB, Envoy, NGINX |

**L4 load balancers** forward packets based on the 5-tuple (source IP/port, destination IP/port, protocol). They're extremely fast and protocol-agnostic: they work for databases, MQTT, SMTP, anything over TCP or UDP. Google's Maglev and Meta's Katran handle millions of packets per second per machine in software. Some use **direct server return (DSR)**: responses go straight from the backend to the client, bypassing the balancer, which matters because responses are usually much bigger than requests.

**L7 load balancers** terminate the client's connection, parse HTTP, and open (or reuse) separate connections to backends. That costs more CPU but enables:

- Routing by path or host (`/api` → API service, `/img` → image service).
- Per-request balancing of multiplexed HTTP/2 and gRPC.
- Retries, timeouts, header rewriting, auth, rate limiting, compression.
- Detailed metrics per route and status code.

> [!tip] The common layering
> Large deployments often stack both: an L4 tier (anycast + ECMP across many machines) spreads connections over a fleet of L7 proxies, which then do the smart per-request work. The L4 tier is simple and scales; the L7 tier is flexible.

## Balancing algorithms

### Round robin

Send each new request to the next server in turn. Simple, requiring only rotation state rather than load measurements, and fair **if every request costs the same and every server is identical**. Neither is usually true.

**Weighted round robin** gives bigger servers proportionally more traffic (e.g. weights 2:1:1).

### Least connections / least outstanding requests

Send to the server with the fewest active connections (or in-flight requests). This adapts automatically: a server stuck on slow requests accumulates connections and gets fewer new ones.

It needs the balancer to track state per backend, which is easy for one balancer but approximate when there are many balancer instances, each seeing only its own traffic.

### Random, and the power of two choices

Pure random spreads load evenly *on average*, but some servers get unlucky streaks. The **power of two choices** fixes this almost for free:

1. Pick **two** servers at random.
2. Send the request to the one with fewer outstanding requests.

Work by Azar and colleagues, popularised by Michael Mitzenmacher's analysis, showed this dramatically shrinks the maximum load compared with one random choice. Throwing *n* requests at *n* servers, the busiest server's load drops from roughly `log n / log log n` to about `log log n`: an exponential improvement. Going from two choices to three helps only a little more; almost all the gain comes from the second choice.

It also avoids the **herding** problem of global least-connections, where every balancer sees the same "least loaded" server and they all pile on at once. Envoy's `LEAST_REQUEST` policy (which samples two hosts by default) and NGINX's `random two least_conn` use this idea. Select the desired policy explicitly; defaults and weighted-host behavior depend on the Envoy configuration/API being used.

### Hashing and consistent hashing

Sometimes you *want* the same key to go to the same server: for example, routing by user ID to a server that has that user's data cached.

Naive hashing (`hash(key) % N`) breaks when N changes: going from 10 to 11 servers remaps about **91%** of keys, destroying every cache at once.

**Consistent hashing** places servers and keys on a ring; each key goes to the next server clockwise:

```
        S1
     /      \
  k3          k1
  |            |
  S3          S2
     \      /
        k2
k1 -> S2, k2 -> S3, k3 -> S1
```

Adding or removing a server only moves the keys in its arc, about **1/N** of them. Each server gets many **virtual nodes** on the ring (say 100–200) so the load evens out. Variants include **rendezvous (HRW) hashing** and Google's **Maglev hashing**, which builds a lookup table for fast, near-even assignment with minimal disruption. Consistent hashing is covered in more depth in the partitioning lessons; here, its job is cache affinity.

### Choosing

| Workload | Good choice |
|---|---|
| Uniform, short requests | Round robin |
| Variable request cost | Least requests / P2C |
| Many LB instances | Power of two choices |
| Cache or session affinity | Consistent hashing |
| Mixed server sizes | Weighted variants |

## Health checks

A balancer must know which backends can take traffic.

- **Active checks:** the balancer probes each backend, e.g. `GET /healthz` every 5–10 s. Mark unhealthy after N consecutive failures (say 2–3); healthy again after M successes.
- **Passive checks (outlier detection):** watch real traffic; eject a backend that returns, say, 5 consecutive 5xx errors (Envoy's default) or times out, for a cool-off period.

Active checks can discover a dead server independently of user traffic, but requests may still fail before the next checks detect it; passive checks catch servers that answer `/healthz` happily but fail real requests. Use both. Do the detection maths: with a 10 s interval and 3 failures to mark unhealthy, a dead server can receive traffic for up to about 30 s.

What should `/healthz` check? This is where teams get burned:

- **Too shallow** (just "process is up"): a server whose database pool is exhausted keeps getting traffic and returning errors.
- **Too deep** (checks the database, cache and three downstream services): when the shared database blips, *every* backend fails its health check at once, the balancer removes them all, and a partial outage becomes a total one.

> [!warning] Fail open
> A configurable availability trade-off: if too many backends are unhealthy, some balancers route to all of them anyway. This can help when checks are misleading or healthy capacity is insufficient, but it can also send traffic to truly broken hosts; disable fail-open where serving such responses is unacceptable. Envoy calls this the *panic threshold* (default 50%). Serving with some errors is better than serving nothing. Similarly, separate **liveness** ("restart me") from **readiness** ("don't send me traffic right now"), as Kubernetes does.

### Graceful draining

When removing a server (deploy, scale-in), stop sending it **new** requests but let in-flight ones finish: AWS calls this *deregistration delay* (default 300 s). Without it, deploys cause bursts of reset connections.

## Sticky sessions

**Session affinity** routes a client's requests to the same backend, typically via a cookie the balancer sets (e.g. `AWSALB`) or by hashing the client IP.

It's useful when servers hold per-user state in memory: a legacy session store, a WebSocket connection, a warm cache. But it costs you:

- **Uneven load.** A few heavy users can pin one server hot.
- **Fragile failover.** When the server dies, its users lose their sessions.
- **Slower scaling.** New servers only get *new* users; existing ones stay put.
- **IP hashing breaks behind NAT:** a whole office or mobile carrier can map to one server.

The usual better answer is to make servers **stateless** and keep session data in a shared store (Redis, a database) or a signed token, so any server can handle any request. Use stickiness for cache affinity, not correctness.

## The balancer itself must not be a single point of failure

- Run balancers in pairs or fleets: active/passive with a floating IP (keepalived/VRRP), or active/active behind ECMP or anycast.
- Managed balancer resilience depends on the product and configured zones; configure the supported multi-zone topology and place backends across failure domains.
- Watch for **connection limits and warm-up**: some managed balancers scale gradually, so a sudden 10× spike (a launch, a TV advert) can outrun them. Pre-warming or load testing helps.

## Key takeaways

- L4 balances connections using IPs and ports; it's fast and protocol-agnostic. L7 balances requests using HTTP details; it's flexible and costs more CPU.
- Round robin assumes uniform requests; least-requests adapts to variable cost; power of two choices gets most of the benefit with little coordination.
- Use consistent hashing when you need key affinity; naive modulo hashing remaps almost everything on resize.
- Health checks should reflect ability to serve without cascading shared-dependency failures; choose fail-open policy deliberately.
- Prefer stateless servers over sticky sessions, and drain connections on removal.

## Further reading

- [Load balancing (computing) (Wikipedia)](https://en.wikipedia.org/wiki/Load_balancing_%28computing%29)
- [Supported load balancers (Envoy docs)](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers)
- [Power of two choices load balancing (HAProxy)](https://www.haproxy.com/blog/power-of-two-load-balancing)
- [Maglev: a fast and reliable software network load balancer (Google Research)](https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/)
- [Load balancing, visualised (Sam Rose)](https://samwho.dev/load-balancing/)
