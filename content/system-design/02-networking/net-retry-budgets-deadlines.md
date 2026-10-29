---
id: net-retry-budgets-deadlines
title: "Retry budgets and propagated deadlines"
level: intermediate
minutes: 3
summary: "Predict how layered retries multiply load and bound duplicate work with budgets, backoff and deadlines."
sourceLesson: net-proxies-gateways-mesh
---
Proxies, gateways, meshes and client libraries can all retry. A retry helps only if its extra work remains safe and affordable when the dependency is already struggling.

## Retries: a feature that can hurt

Every layer here can retry, and that's dangerous. Each attempt made by an outer layer triggers a full set of attempts at the next layer in, so the counts multiply rather than add:

```formula reference
A_total = a^L
where
A_total: the worst-case number of attempts that reach the innermost backend for one user request
a: the attempts each layer may make: the first try plus its retries
L: the number of layers that retry independently, such as a gateway, a mesh sidecar and a client library
In words: retries multiply across layers, so the worst case is the attempts per layer raised to the power of the number of retrying layers.
```

If the gateway makes up to 3 attempts, the mesh sidecar up to 3 for each of those, and the app's client up to 3 for each of *those*, one failing request becomes up to 27 attempts on the struggling backend: a **retry storm** that turns an overload into an outage. Watch the wording: "3 retries" usually means 4 attempts (the first try plus 3 retries), and with that setting the same three layers can produce 64.

Rules of thumb:

- Retry at **one** layer (usually closest to the caller), and only for idempotent requests.
- Use **retry budgets** (e.g. retries may add at most 10–20% extra load) and exponential backoff with jitter.
- Set **timeouts** that shrink as you go deeper (or propagate a *deadline* with the request, as gRPC does). If the gateway gives up after 2 s but the service behind it waits 5 s for its database, the inner work carries on for a caller that has already left, and any outer retry piles duplicate work on top.

A **retry budget** breaks the link between failure rate and extra load. Without one, retrying every failure once adds load in proportion to the failures: at 1,000 requests per second and 50% failures that is 500 extra requests per second, and at 100% failures the load doubles, exactly when the dependency can least afford it. A rate-based budget instead caps retries at a fixed fraction of normal traffic (say 20%, so at most 200 per second here), however many calls fail. Products account for budgets differently: Envoy's retry budget, for example, limits *concurrent* retries relative to active and pending requests, with a default of 20% when that budget is configured.

## Key takeaways

- Independent retry layers multiply attempts; attempts include the initial try.
- One retry layer, bounded budgets and jitter prevent failures from causing uncontrolled extra load.
- Propagate deadlines and cancellation so inner work does not continue for an abandoned caller.

## Further reading

- [Handling overload (Google SRE)](https://sre.google/sre-book/handling-overload/)
- [Deadlines (gRPC)](https://grpc.io/docs/guides/deadlines/)
