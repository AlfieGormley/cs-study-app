---
id: net-session-affinity-draining
title: "Session affinity and graceful draining"
level: intermediate
minutes: 3
summary: "Keep deploys and scaling from trapping sessions or synchronising client reconnects."
sourceLesson: net-load-balancers
---
Scaling and deployments change which servers exist. Keeping session correctness independent of a particular backend and moving long-lived clients gradually makes those changes easier to absorb.

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
- Watch for **connection limits and warm-up**: some managed balancers scale gradually, so a sudden 10× spike (a launch, a television advert) can outrun them. Pre-warming or load testing helps.

A WebSocket can outlive the entire drain window. Do not wait for thousands of such connections to reach the same removal deadline: close them gradually during the window and make clients reconnect with exponential backoff and random jitter. Spreading server closes and client retries prevents a synchronised reconnect spike; the suitable batch size and window depend on spare fleet capacity.

## Key takeaways

- Stickiness can preserve local state but creates uneven load, fragile failover and slower scaling.
- Drain new work away and let existing work finish; long-lived sockets need an explicit reconnect plan.
- Run resilient balancer topology and test connection limits and sudden load growth.

## Further reading

- [Sticky sessions (AWS)](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/sticky-sessions.html)
- [Deregistration delay and target attributes (AWS)](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-target-group-attributes.html)
- [Retry with backoff pattern (AWS Prescriptive Guidance)](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html)
