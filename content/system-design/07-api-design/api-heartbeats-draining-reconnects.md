---
id: api-heartbeats-draining-reconnects
title: Heartbeats, draining and reconnect budgets
level: advanced
minutes: 3
summary: Keep persistent connections alive and rebalance or deploy without overwhelming reconnect dependencies.
sourceLesson: api-real-time
---

A fleet with enough memory can still fail during deploys: reconnecting clients consume authentication and handshake capacity. Plan for connection turnover as well as steady state.

## Load balancing

- The load balancer must support the `Upgrade` and long-lived connections. L7 balancers such as NGINX, Envoy and AWS ALB do. Set idle timeouts generously (AWS ALB's default is 60 s) and send **heartbeats** (ping/pong) every ~30 s, so that idle connections aren't culled by the balancer or by NAT devices along the way.
- Heartbeats also detect *dead* connections. A phone that loses signal doesn't send a TCP close, so without pings the server can hold a "connected" socket for a client that vanished minutes ago.
- Balancing happens at **connect** time only. If you add servers, existing connections stay where they are, so new servers initially receive only new or reconnected clients. Use least-connections balancing, and consider a maximum connection age (say, a few hours, with jitter) so the fleet rebalances itself gradually.

## Deploys and reconnect storms

Restarting a gateway drops every connection on it at once. If 200,000 clients all reconnect immediately, they hammer the auth service and the remaining gateways.

- **Drain gracefully**: stop accepting new connections, then close existing ones gradually over minutes.
- **Clients reconnect with exponential backoff and jitter**.
- **Resume, don't replay everything**: the client sends its last-seen message id or sequence number, and the server sends only what was missed.

## Managed options

If you don't want to run this yourself: AWS API Gateway WebSocket APIs, Azure Web PubSub, Ably, Pusher. They hold the connections and give your backend a simple "send to connection id" API.

If each reconnect makes one auth call, the drain cannot close connections faster than the spare authentication throughput can accept them. Divide the connections being moved by spare calls per second to obtain an ideal minimum drain duration, then allow extra time for variability and simultaneous fleet work.

## Key takeaways
- Heartbeat cadence must suit idle timeouts and also detects clients that vanished.
- New servers receive new connections; existing connections require gradual reconnection to rebalance.
- Drain gradually within auth capacity, and use client backoff and jitter.
- Resume from last-seen identities and consider managed gateways when operating the fleet is unnecessary.

## Further reading
- [Slack engineering: Real-time messaging](https://slack.engineering/real-time-messaging/)
- [Discord: How Discord scaled Elixir to 5,000,000 concurrent users](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users)
- [AWS: Load balancer idle timeout](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-load-balancer-attributes.html)
