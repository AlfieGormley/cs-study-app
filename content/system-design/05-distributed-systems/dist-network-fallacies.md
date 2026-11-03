---
id: dist-network-fallacies
title: The eight fallacies and the cost of latency
level: basic
minutes: 3
summary: Recognise hidden network assumptions and calculate the cost of sequential remote calls.
sourceLesson: dist-why-hard
---

A local-looking API call may cross a network with real latency and operational boundaries. The eight fallacies are a checklist for finding those hidden assumptions.

## The eight fallacies of distributed computing

Peter Deutsch and colleagues at Sun Microsystems listed the false assumptions that newcomers make. Each one causes real outages.

| Fallacy | What goes wrong |
|---|---|
| The network is reliable | Lost requests, half-done operations |
| Latency is zero | Chatty APIs become slow over a WAN |
| Bandwidth is infinite | Large payloads saturate links |
| The network is secure | Unencrypted internal traffic is sniffed |
| Topology doesn't change | Hard-coded IPs break on failover |
| There is one administrator | Conflicting configs, firewalls |
| Transport cost is zero | Serialisation CPU, cross-AZ fees |
| The network is homogeneous | Mixed MTUs, protocols, versions |

> [!example] Latency is not zero
> A page that makes 50 sequential calls to a service in the same data centre (0.5 ms round trip) spends 25 ms on the network. Move that service to another region (80 ms round trip) and the same page takes 4 seconds. Nothing in the code changed.

When calls are made one after another (sequentially), each one waits for a full round trip before the next can start, so the network time is simply the number of calls multiplied by the round-trip time:

```formula reference
T = n × RTT
where
T: the total time the page spends waiting on the network, in milliseconds (ms)
n: the number of sequential calls the page makes
RTT: round-trip time, how long one request takes to reach the service and its reply to come back, in milliseconds (ms)
ms: millisecond, one thousandth of a second
In words: calls made one after another each pay a full round trip, so the network wait grows in step with both the number of calls and the distance to the service.
```

This ignores the time the service spends doing the work, which adds on top. It only holds for sequential calls: calls made in parallel overlap, so 50 parallel calls cost roughly one round trip, not fifty.

## Key takeaways
- Reliability, latency, bandwidth, security, topology, administration, cost and homogeneity are all assumptions to check.
- Sequential calls pay one round trip each; moving a chatty service across regions can dominate its runtime.
- Parallel calls overlap network waits; the service's own work time remains an additional cost.

## Further reading
- [Fallacies of distributed computing (Wikipedia)](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing)
- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
