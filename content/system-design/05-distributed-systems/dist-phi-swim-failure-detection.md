---
id: dist-phi-swim-failure-detection
title: Phi suspicion and SWIM probes
level: advanced
minutes: 4
summary: Interpret model-based heartbeat silence and use indirect probing before declaring membership failure.
sourceLesson: dist-crdts-gossip
---

Gossip can spread membership information, but a node must first decide how suspicious another node’s silence is. Failure detectors supply evidence and thresholds rather than certainty.

## Failure detection

### Heartbeats with a fixed timeout

The simplest detector: if no heartbeat for T seconds, mark dead. Pick T too short and you get false positives under load; too long and real failures go unnoticed. One threshold can't suit every network condition.

### Phi accrual failure detector

Hayashibara et al. (2004), used by Cassandra and Akka, output a **suspicion level φ** instead of a yes/no.

- Each node records recent heartbeat inter-arrival times and models them as a distribution (the original paper uses a normal distribution with the observed mean and variance; Cassandra uses a simpler exponential model).
- From that model it works out how unlikely the current silence is, and turns that into φ:

```formula reference
φ = −log_10(P_later(t))
where
φ: phi, the suspicion level; a plain number with no unit, higher means more suspicious
t: the time since the last heartbeat arrived, in seconds (s)
P_later(t): the probability, according to the model, that a healthy node's next heartbeat would arrive even later than t; between 0 and 1
log_10: the base-10 logarithm: how many times you multiply 10 to reach a number; log_10(0.001) = −3
s: second
In words: φ = 3 means the model gives a healthy node a 1-in-1,000 chance of being this quiet; each extra 1 in φ makes the silence ten times less likely.
```

In Cassandra's exponential model, the probability of a heartbeat being even later falls off exponentially as the silence grows, and φ becomes a straight line:

```formula reference
P_later(t) = e^{−t/μ}
φ = (t / μ) × log_10(e)
where
P_later(t): the modelled chance a heartbeat is later than t
t: the time since the last heartbeat, in seconds (s)
μ: mu, the mean interval between heartbeats, in seconds
e: Euler's number, about 2.718, the base of natural logarithms
log_10(e): the base-10 logarithm of e, about 0.434
φ: phi, the suspicion level (no unit)
s: second
In words: in this model φ grows steadily with silence, at a rate set by the average heartbeat interval; variation in the intervals doesn't enter into it.
```

In other words, φ is the silence measured in average heartbeat intervals, multiplied by a fixed constant of about 0.434. With a 1-second mean interval, this model reaches Cassandra's default threshold of 8 after about 18 seconds of silence. A peer with a longer average interval takes proportionally longer to convict.

| φ | Modelled heartbeat tail probability |
|---|---|
| 1 | 10% |
| 3 | 0.1% |
| 8 | 0.000001% |

The application chooses a threshold (Cassandra's `phi_convict_threshold` defaults to 8). The adaptation depends on the model: Cassandra's exponential detector uses the observed mean interval, so extra variance alone at the same mean does not guarantee later conviction. The tail probability is not a measured false-positive rate.

### SWIM

SWIM (Das, Gupta and Motivala, 2002) is a scalable membership protocol, used in HashiCorp's memberlist (Consul, Nomad, Serf).

> [!analogy] Real-world analogy: asking friends to try a phone number
> You ring a friend and get no answer. Before assuming something has happened to them, you ask two mutual friends to try. If either gets through, the problem was your phone or your line. If nobody gets through, you start to worry, and tell others you are worried, but your friend can still turn up and say "I'm fine".
>
> **How it maps:** Your call is A's direct ping to B, the mutual friends are SWIM's helpers sending ping-req, getting through via a friend is an indirect ack, worrying aloud is gossiping that B is in the **suspect state**, and "I'm fine" is B refuting suspicion with a higher incarnation number.
>
> **Where it stops:** If the friends also fail to get through, that still does not prove your friend has gone; their calls may share the same broken route. SWIM declares a member dead only after a suspicion timeout, and that remains a decision under uncertainty.

```
A             B          C (helpers)
|--ping------>X
| no ack in time
|--ping-req(B)--------->C
               C--ping->B
               C<--ack--B
|<-------ack------------C
B is alive (A's path was bad)
```

1. Each period, A pings one random member B.
2. No ack? A asks a few other members (k of them; HashiCorp's memberlist LAN and WAN configurations use 3 by default) to **ping-req** B on its behalf (indirect probing), which can reveal a problem with A's direct path if a helper succeeds; failed helpers still do not prove B is dead.
3. Still nothing: B is **suspected**, not dead. Suspicion is gossiped; B can refute it by gossiping an incremented **incarnation number**.
4. After a suspicion timeout, B is declared **dead**.

Membership updates **piggyback** on ping and ack messages, so there's no separate broadcast traffic. In the paper's model, expected probe-message load per member and expected time until some healthy member first detects a failure do not grow with group size. Dissemination to the whole group and implementation suspicion timeouts are separate costs. HashiCorp's Lifeguard extensions further reduce false positives from slow, overloaded nodes.

## Key takeaways
- A fixed heartbeat timeout trades recovery speed against false positives; phi reports suspicion under a model of observed heartbeat intervals.
- Cassandra’s exponential model depends on the mean interval, so greater variance alone does not guarantee later conviction.
- SWIM uses indirect probes, a suspicion period and incarnation numbers; a failed direct path is not proof that the node failed.

## Further reading
- [SWIM paper (Das, Gupta, Motivala)](https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/SWIM.pdf)
- [HashiCorp memberlist (SWIM implementation)](https://github.com/hashicorp/memberlist)
