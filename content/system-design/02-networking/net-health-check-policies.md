---
id: net-health-check-policies
title: "Detection delay and health policy"
level: intermediate
minutes: 3
summary: "Budget failed requests during detection and choose checks and fail-open behaviour deliberately."
sourceLesson: net-load-balancers
---
A balancer’s availability claim depends on what it measures and what it does when healthy capacity disappears. Separate the detection model from the policy used after detection.

## Health checks

A balancer must know which backends can take traffic.

- **Active checks:** the balancer probes each backend, e.g. `GET /healthz` every 5–10 s. Mark a backend unhealthy after a set number of consecutive failures (the *unhealthy threshold*, say 2–3), and healthy again after a set number of consecutive successes (the *healthy threshold*).
- **Passive checks (outlier detection):** watch real traffic; eject a backend that returns, say, 5 consecutive 5xx errors (Envoy's default) or times out, for a cool-off period.

Active checks can discover a dead server independently of user traffic, but requests may still fail before the next checks detect it; passive checks catch servers that answer `/healthz` happily but fail real requests. Use both. Do the detection maths for active checks:

```formula
t_detect ≈ interval × threshold
t_detect ≈ 10 s × 3 = 30 s
where
t_detect: the worst-case time a dead server keeps receiving traffic before active checks remove it, in seconds (s)
interval: the time between one health-check probe and the next, in seconds; here 10 s
threshold: the unhealthy threshold: how many failed probes in a row mark a backend unhealthy; here 3
s: second
≈: approximately (probe timeouts add a little more)
In words: if the server dies just after a passing probe, it takes three more probes, 10 s apart, before the balancer stops sending it traffic.
```

So with a 10 s interval and 3 failures to mark unhealthy, a dead server can receive traffic for up to about 30 s. At 200 requests per second to that server, that's about 6,000 failed requests.

What should `/healthz` check? This is where teams get burned:

- **Too shallow** (just "process is up"): a server whose database pool is exhausted keeps getting traffic and returning errors.
- **Too deep** (checks the database, cache and three downstream services): when the shared database blips, *every* backend fails its health check at once, the balancer removes them all, and a partial outage becomes a total one.

> [!warning] Fail open
> A configurable availability trade-off: if too many backends are unhealthy, some balancers route to all of them anyway. This can help when checks are misleading or healthy capacity is insufficient, but it can also send traffic to truly broken hosts; disable fail-open where serving such responses is unacceptable. Envoy calls this the *panic threshold* (default 50%). Whether partial service is preferable to rejection depends on the workload and the kinds of errors it could return. Similarly, separate **liveness probes** ("restart me") from **readiness probes** ("don't send me traffic right now"), as Kubernetes does.

## Key takeaways

- Combine active probes with passive outlier detection; neither observes every failure immediately.
- Probe interval and failure threshold determine the simplified worst-case detection window.
- Deep shared-dependency checks can remove every backend; fail-open and readiness policies need explicit decisions.

## Further reading

- [Target group health checks (AWS)](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [Panic threshold (Envoy)](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/panic_threshold)
