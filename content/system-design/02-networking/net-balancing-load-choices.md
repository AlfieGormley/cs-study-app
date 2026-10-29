---
id: net-balancing-load-choices
title: "Request cost and two-choice balancing"
level: intermediate
minutes: 4
summary: "Choose between rotation, load tracking and random sampling when request costs vary."
sourceLesson: net-load-balancers
---
An equal request count does not imply equal load. Start with a workload model, then decide how much live state and coordination the balancing policy needs.

## Balancing algorithms

### Round robin

Send each new request to the next server in turn. Simple, requiring only rotation state rather than load measurements, and fair **if every request costs the same and every server is identical**. Neither is usually true.

**Weighted round robin** gives bigger servers proportionally more traffic: each server's share is its weight divided by the sum of all weights. With weights 2:1:1, the big server gets half the requests and each smaller one a quarter. Weights express capacity you configured, not load you measured.

### Least connections / least outstanding requests

Send to the server with the fewest active connections (or in-flight requests). This adapts automatically: a server stuck on slow requests accumulates connections and gets fewer new ones.

It needs the balancer to track state per backend, which is easy for one balancer but approximate when there are many balancer instances, each seeing only its own traffic.

### Random, and the power of two choices

Pure random spreads load evenly *on average*, but some servers get unlucky streaks. The **power of two choices** fixes this almost for free:

1. Pick **two** servers at random.
2. Send the request to the one with fewer outstanding requests.

Work by Azar and colleagues, popularised by Michael Mitzenmacher's analysis, showed that this shrinks the worst server's load dramatically. The classic thought experiment sends as many requests as there are servers and asks how loaded the busiest server ends up.

```formula reference
L_1 ≈ ln(n) / ln(ln(n))
L_d ≈ ln(ln(n)) / ln(d)
where
L_1: the load on the busiest server, in requests, when each request goes to one server chosen at random
L_d: the same when each request samples d servers at random and joins the least loaded of them
n: the number of servers, and also the number of requests sent
d: how many servers each request samples; 2 for the power of two choices
ln: the natural logarithm, a function that grows very slowly
≈: approximately; these are the leading terms of how the load grows, with high probability, ignoring constant terms
In words: with one random choice the busiest server's load grows a little more slowly than the logarithm of the fleet size; with two choices it grows only like the logarithm of a logarithm, which barely moves even as the fleet grows a thousand-fold. A third choice improves this only by a constant factor.
```

These are asymptotic results for an idealised model, so read them as a statement about how imbalance *grows*, not as predictions for your fleet. The practical message: almost all the benefit comes from the second sample, and sampling more servers adds little.

It also avoids the **herding** problem of global least-connections, where every balancer sees the same "least loaded" server and they all pile on at once. Envoy's `LEAST_REQUEST` policy (which samples two hosts by default) and NGINX's `random two least_conn` use this idea. Select the desired policy explicitly; defaults and weighted-host behaviour depend on the Envoy configuration/API being used.

## Key takeaways

- Round robin balances counts; weights adapt server shares but do not measure current work.
- Least-outstanding-request policies adapt to slow work but have incomplete views across many balancers.
- Two random choices reduce imbalance and herding; the balls-into-bins formulas are asymptotic illustrations.

## Further reading

- [Supported load balancers (Envoy)](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers)
- [Power of two choices (HAProxy)](https://www.haproxy.com/blog/power-of-two-load-balancing)
