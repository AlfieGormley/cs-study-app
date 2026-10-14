---
id: net-retry-budgets-deadlines
title: "Retry budgets and propagated deadlines"
level: intermediate
minutes: 3
summary: "Calculate retry multiplication and bound duplicate work with budgets, backoff and deadlines."
sourceLesson: net-proxies-gateways-mesh
---
Proxies, gateways, meshes and client libraries can all retry. A retry helps only if its extra work remains safe and affordable when the dependency is already struggling.

## Retries: a feature that can hurt

Every layer here can retry, and that's dangerous. If the gateway makes up to 3 attempts, the mesh sidecar makes up to 3 attempts for each of those, and the app's client makes up to 3 for each of *those*, one failing request becomes **3 × 3 × 3 = 27** attempts on the struggling backend: a **retry storm** that turns an overload into an outage. Because every attempt at an outer layer triggers a full set at the next layer in, the counts multiply:

```formula
A_total = a^L
A_total = 3^3 = 3 × 3 × 3 = 27
A_total = 4^3 = 4 × 4 × 4 = 64
where
A_total: the worst-case number of attempts that reach the innermost backend for one user request
a: the attempts each layer may make: the first try plus its retries; 3 in the first line, 4 in the last
L: the number of layers that retry independently; here 3 (gateway, sidecar and client library)
In words: retries multiply across layers, so the worst case is the attempts per layer raised to the power of the number of layers.
```

Careful with wording: "3 retries" usually means 4 attempts (the first try plus 3 retries), which gives the 64 in the last line.

Rules of thumb:

- Retry at **one** layer (usually closest to the caller), and only for idempotent requests.
- Use **retry budgets** (e.g. retries may add at most 10–20% extra load) and exponential backoff with jitter.
- Set **timeouts** that shrink as you go deeper (or propagate a *deadline* with the request, as gRPC does). If the gateway gives up after 2 s but the service behind it waits 5 s for its database, the inner work carries on for a caller that has already left, and any outer retry piles duplicate work on top.

One rate-based retry budget caps retries per second at a fixed fraction of original request traffic. The calculation below uses that policy. Product accounting differs: Envoy’s retry budget instead limits concurrent retries relative to active and pending requests, with a default percentage of 20% when that budget is configured.

```formula
R_max = b × λ
R_max = 0.2 × 1,000 rps = 200 rps
where
R_max: the most retries per second the budget allows, in requests per second (rps)
b: the retry budget, as a fraction of normal traffic; 0.1 to 0.2 (10–20%) are illustrative choices, not universal defaults
λ: lambda, the normal request rate, in rps; here 1,000 rps
rps: requests per second
In words: with a 20% budget and 1,000 requests per second, at most 200 retries per second are allowed, however many calls fail.
```

Without a budget, retrying every failure once at a 50% failure rate would add 500 rps instead: the extra load grows with the failure rate, exactly when the backend can least afford it.

## Key takeaways

- Independent retry layers multiply attempts; attempts include the initial try.
- One retry layer, bounded budgets and jitter prevent failures from causing uncontrolled extra load.
- Propagate deadlines and cancellation so inner work does not continue for an abandoned caller.

## Further reading

- [Handling overload (Google SRE)](https://sre.google/sre-book/handling-overload/)
- [Deadlines (gRPC)](https://grpc.io/docs/guides/deadlines/)
