---
id: wm-debug-symptoms-and-ping
title: A repeatable debugging method and careful ping use
level: advanced
minutes: 3
summary: Define the endpoint, error, timing and scope before testing a cause.
sourceLesson: wm-debugging
---

“The network is down” or “the network is slow” needs a precise symptom before it can guide diagnosis. Good network debugging is mostly method: pin down the symptom, find which layer and which part of the path it lives in, and test a hypothesis with the right tool.

Start with a repeatable method and use ping as one limited end-to-end measurement. The following units add path, DNS, timing and packet evidence before examining recurring failure patterns.

## The method

1. **Define the symptom precisely.** Which client, which destination (hostname, IP, port), what error, what timing? "Checkout API calls from the London office take 3 s instead of 200 ms since 14:05" is debuggable. "It's slow" is not.
2. **Scope it.** One user or everyone? One region, ISP, Wi-Fi network, or all? IPv4 and IPv6? Always or intermittent? Scope tells you where to look.
3. **Ask what changed.** Deploys, config pushes, certificate renewals, DNS changes, firewall rules. Correlate changes with evidence; a recent change is a hypothesis, not proof of cause.
4. **Walk the layers, bottom up**, until something fails:

| Layer | Question | Tools |
|---|---|---|
| Link | Interface up? Errors? Signal? | `ip link`, RSSI |
| IP | Address, route, gateway? | `ip addr`, `ip route` |
| Name | Does it resolve correctly? | `dig` |
| Transport | Does the port connect? | `nc`, `curl` |
| TLS | Does the handshake work? | `openssl s_client` |
| App | Right response, how fast? | `curl -w`, logs |

5. **Divide the path.** Test from the client, from a host near the server, and from somewhere in between. A difference narrows hypotheses, but source-specific policy, different DNS answers or server treatment can also explain it.
6. **Change one thing at a time** and re-measure against a baseline.

> [!tip] Refused or timed out?
> An immediate **connection refusal** commonly reflects a TCP reset or an explicit rejection reported by the stack. It does not prove the intended host generated the response. A **timeout** means the operation did not finish within its deadline; loss, filtering, routing, overload, peer behaviour and an unsuitable deadline are possible causes. Capture and endpoint evidence distinguish them.

## ping: reachability and RTT

`ping` sends ICMP echo requests and reports round-trip time and loss.

```
$ ping -c 5 10.0.3.7
64 bytes from 10.0.3.7: time=0.41 ms
...
5 packets transmitted, 5 received
rtt min/avg/max/mdev =
  0.38/0.42/0.47/0.03 ms
```

Read it carefully:

- Many networks block or deprioritise ICMP. No reply does not prove the host is down; try a TCP connect too.
- High **mdev**, the standard deviation of sampled RTTs, indicates variability. Queueing is one possible cause, alongside scheduling, path changes and measurement effects.
- Run it for a while (`-c 100`) when hunting intermittent loss; five probes cannot reliably estimate a 1% loss probability. Even 100 probes have substantial sampling uncertainty, and ICMP behaviour may differ from the application.

## Key takeaways
- Define the endpoint, error, timing and scope before testing a cause.
- ICMP outcomes and sampled RTT variation are evidence with protocol and sampling limits.

## Further reading
- [The USE Method — Brendan Gregg](https://www.brendangregg.com/usemethod.html)
- [Linux ping manual](https://man7.org/linux/man-pages/man8/ping.8.html)
