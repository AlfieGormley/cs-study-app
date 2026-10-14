---
id: net-balancing-load-choices
title: "Request cost and two-choice balancing"
level: intermediate
minutes: 5
summary: "Choose between rotation, load tracking and random sampling when request costs vary."
sourceLesson: net-load-balancers
---
An equal request count does not imply equal load. Start with a workload model, then decide how much live state and coordination the balancing policy needs.

## Balancing algorithms

### Round robin

Send each new request to the next server in turn. Simple, requiring only rotation state rather than load measurements, and fair **if every request costs the same and every server is identical**. Neither is usually true.

**Weighted round robin** gives bigger servers proportionally more traffic. Each server gets its weight's share of the total:

```formula
share_i = w_i / Σw
share_1 = 2 / (2 + 1 + 1) = 0.5 = 50%
where
share_i: the fraction of requests that server number i receives
w_i: the weight configured for server i; bigger servers get bigger weights
i: which server we mean: 1, 2, 3 and so on
share_1: the share for server 1, the big server with weight 2
Σ: sigma, "the sum of": add up the term after it for every server
w: a server's weight; Σw is all the weights added together, here 2 + 1 + 1 = 4
%: per cent
In words: with weights 2:1:1, the big server gets half the requests and each smaller one gets a quarter.
```

### Least connections / least outstanding requests

Send to the server with the fewest active connections (or in-flight requests). This adapts automatically: a server stuck on slow requests accumulates connections and gets fewer new ones.

It needs the balancer to track state per backend, which is easy for one balancer but approximate when there are many balancer instances, each seeing only its own traffic.

### Random, and the power of two choices

Pure random spreads load evenly *on average*, but some servers get unlucky streaks. The **power of two choices** fixes this almost for free:

1. Pick **two** servers at random.
2. Send the request to the one with fewer outstanding requests.

Work by Azar and colleagues, popularised by Michael Mitzenmacher's analysis, showed this dramatically shrinks the maximum load compared with one random choice. The classic result imagines sending as many requests as there are servers and asks how loaded the busiest server ends up. With high probability:

```formula
L_1 ≈ ln(n) / ln(ln(n))
L_d ≈ ln(ln(n)) / ln(d)
where
L_1: the number of requests on the busiest server when each request goes to one server chosen at random
L_d: the same, when each request samples d servers at random and joins the least loaded of them
n: the number of servers, and also the number of requests sent
d: how many servers each request samples; 2 for the power of two choices
ln: the natural logarithm, a function that grows very slowly: ln(1,000,000) ≈ 13.8
≈: approximately; these are the leading terms of how the load grows, ignoring smaller constant terms
In words: with one random choice the worst server's load grows almost as fast as ln(n); with two choices it grows only like the logarithm of a logarithm, which barely moves.
```

Worked example with a million servers and a million requests:

```formula
L_1 ≈ ln(10^6) / ln(ln(10^6))
L_1 ≈ 13.8 / 2.63 ≈ 5.3
L_2 ≈ ln(ln(10^6)) / ln(2)
L_2 ≈ 2.63 / 0.69 ≈ 3.8
where
L_1: the leading-term estimate of the busiest server's load with one random choice, in requests
L_2: the same estimate with two choices
ln: the natural logarithm; ln(10^6) ≈ 13.8 and ln(2) ≈ 0.69
≈: approximately equal to
In words: at this size the leading terms differ by less than you might expect; the big difference is in how fast each grows as the system gets larger.
```

The real difference is in growth. Increasing the number of servers a thousand-fold barely increases the logarithm of a logarithm. The relevant values are:

```formula
g_small = ln(ln(1,000)) ≈ 1.93
g_large = ln(ln(1,000,000)) ≈ 2.63
ln(2) ≈ 0.69
ln(3) ≈ 1.10
where
g_small: the dimensionless logarithm-of-a-logarithm term for one thousand servers
g_large: the same term for one million servers
ln: the natural logarithm function, applied twice in the growth terms
≈: approximately equal to
In words: a thousand-fold increase in servers moves the growth term only from about 1.93 to 2.63; adding a third choice changes the divisor by a constant factor.
```

That change in how the load grows is the exponential improvement. These are asymptotic results, so treat the exact numbers as illustrations, not predictions. Going from two choices to three divides by the natural logarithm of three instead of the natural logarithm of two, a constant-factor gain; almost all the benefit comes from the second choice.

It also avoids the **herding** problem of global least-connections, where every balancer sees the same "least loaded" server and they all pile on at once. Envoy's `LEAST_REQUEST` policy (which samples two hosts by default) and NGINX's `random two least_conn` use this idea. Select the desired policy explicitly; defaults and weighted-host behavior depend on the Envoy configuration/API being used.

## Key takeaways

- Round robin balances counts; weights adapt server shares but do not measure current work.
- Least-outstanding-request policies adapt to slow work but have incomplete views across many balancers.
- Two random choices reduce imbalance and herding; the balls-into-bins formulas are asymptotic illustrations.

## Further reading

- [Supported load balancers (Envoy)](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers)
- [Power of two choices (HAProxy)](https://www.haproxy.com/blog/power-of-two-load-balancing)
