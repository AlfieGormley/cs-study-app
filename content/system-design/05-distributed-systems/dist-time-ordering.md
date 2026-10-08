---
id: dist-time-ordering
title: Time and ordering
level: intermediate
minutes: 12
summary: Why wall clocks lie, how NTP works, and how Lamport clocks, vector clocks, hybrid logical clocks and TrueTime order events.
---

Many distributed problems boil down to "which happened first?". Which write wins? Did this message cause that one? Is this lease still valid? On one machine the answer comes from a single clock. Across machines there is no shared clock, so you need to be careful about what "first" even means.

## Physical clocks and their problems

Each server has two kinds of clock:

| Clock | Use | Behaviour |
|---|---|---|
| Time-of-day | Timestamps | Can jump back or forward |
| Monotonic | Measuring durations | Only moves forward |

In Linux these are `CLOCK_REALTIME` and `CLOCK_MONOTONIC`. Rule one: **never measure a timeout with the time-of-day clock**. An NTP step can make an elapsed time negative.

### Drift and skew

Quartz crystals run slightly fast or slow, and it varies with temperature. Typical drift is 10 to 200 parts per million (ppm): a clock with 200 ppm drift gains or loses up to 200 microseconds every second.

To see what that means over a day, multiply the drift rate by the time that passes:

```formula
Δ = r × t
Δ = 0.0002 × 86,400 s
Δ ≈ 17 s
where
Δ: delta, the total error the clock builds up, in seconds (s)
r: the drift rate as a fraction; 200 ppm means 200 parts per million, which is 200 / 1,000,000 = 0.0002
t: the time that passes without correction, in seconds; one day is 24 × 60 × 60 = 86,400 s
s: second
≈: approximately equal to (the exact value is 17.28 s)
In words: a clock that drifts by 200 parts per million is off by about 17 seconds after a day if nothing corrects it.
```

This assumes the drift rate stays constant; in reality it wanders with temperature, so it's a bound rather than a prediction. A 10 ppm clock would build up less than a second a day.

**Skew** is the difference between two clocks at one moment. Two clocks that drift in opposite directions grow apart at the sum of their rates.

### NTP

The Network Time Protocol syncs a client with servers arranged in strata (stratum 0 is an atomic clock or GPS; stratum 1 servers attach to it, and so on). A client estimates offset from a round trip:

```
client            server
 t0 |--request--->|
    |             | t1 (receive)
    |             | t2 (send)
 t3 |<--reply-----|
```

The client records when it sent the request and when the reply arrived (on its own clock); the server records when it received the request and when it sent the reply (on its clock). From those four timestamps NTP works out two things: how long the messages spent on the network, and how far apart the two clocks are.

```formula
δ = (t_3 − t_0) − (t_2 − t_1)
θ = ((t_1 − t_0) + (t_2 − t_3)) / 2
where
δ: delta, the round-trip network delay: total time on the wire, both directions, in milliseconds (ms)
θ: theta, the estimated offset: how far the server's clock is ahead of the client's, in ms (negative means the server is behind)
t_0: the client's clock reading when it sent the request
t_1: the server's clock reading when the request arrived
t_2: the server's clock reading when it sent the reply
t_3: the client's clock reading when the reply arrived
ms: millisecond, one thousandth of a second
In words: the delay is the whole round trip minus the time the server spent holding the request; the offset is the average of the two one-way clock differences, which cancels out the network delay if both directions take equally long.
```

Why the offset formula works: the difference t_1 − t_0 is the offset plus the outbound travel time, and t_2 − t_3 is the offset minus the return travel time. Adding them and halving cancels the travel time, but only when both directions take the same time.

Worked example: the client sends at 100 ms, the server receives at 160 ms and replies at 161 ms, and the reply arrives at 120 ms (each time on its own side's clock):

```formula
δ = (120 − 100) − (161 − 160) = 19 ms
θ = ((160 − 100) + (161 − 120)) / 2
θ = (60 + 41) / 2 = 50.5 ms
where
δ: delta, the round-trip network delay, in milliseconds (ms)
θ: theta, the offset of the server's clock relative to the client's, in ms; positive means the server is ahead
ms: millisecond
In words: the messages spent 19 ms on the network in total, and the server's clock is about 50.5 ms ahead of the client's.
```

The offset formula assumes the network delay is **symmetric**. If the outbound path is slow and the return fast, the estimate is wrong by half the asymmetry:

```formula
e = (d_out − d_back) / 2
e = (15 ms − 4 ms) / 2 = 5.5 ms
where
e: the error in the offset estimate, in milliseconds (ms)
d_out: the real one-way delay from client to server, in ms; here 15 ms
d_back: the real one-way delay from server to client, in ms; here 4 ms
ms: millisecond
In words: NTP can't see how the round trip splits between the two directions, so any imbalance turns into an offset error of half the difference.
```

NTP has no way to notice this error from the timestamps alone. Typical accuracy: around 1 ms on a good LAN, tens of ms over the internet, and much worse under congestion. AWS and Google offer leap-smeared, GPS-backed time services that do better (sub-millisecond, with bounds).

NTP corrects a clock by **slewing** (running it slightly fast or slow) for small offsets and **stepping** (jumping) for large ones. Steps are what make clocks go backwards.

> [!warning] Last-write-wins with skewed clocks
> Node A's clock is 100 ms fast. A client writes v1 on A at A-time 10.100 (real 10.000). 50 ms later a client writes v2 on B at B-time 10.050 (real 10.050). LWW keeps v1 because 10.100 > 10.050, silently discarding the genuinely later write. This is a well-known hazard in Cassandra and other last-write-wins stores: any two writes closer together than the clock skew can be ordered wrongly.

## Happens-before

Lamport's 1978 paper defined order without clocks. It uses two pieces of notation:

```formula
a → b
a ∥ b
where
a: one event, such as a local step, a message send or a message receive on some process
b: another event, possibly on a different process
→: "happens before": a could have influenced b
∥: "is concurrent with": neither a → b nor b → a holds
In words: a → b means information could have flowed from a to b; a ∥ b means no information could have flowed either way.
```

Event *a* **happens before** *b* (a → b) if:

1. a and b are on the same process and a comes first, or
2. a is sending a message and b is receiving that message, or
3. there's an event c with a → c and c → b (transitivity: chains of happens-before also count).

If neither a → b nor b → a, the events are **concurrent** (a ∥ b). Concurrent doesn't mean simultaneous; it means neither could have influenced the other.

## Lamport clocks

Each process keeps a single whole-number counter, L, starting at 0. Two rules update it:

```formula
L_new = L + 1
L_new = max(L, t) + 1
where
L: this process's current Lamport counter, a whole number with no unit
L_new: the counter's value after the event; it is also that event's timestamp
t: the timestamp carried on an incoming message
max: the larger of its inputs, e.g. max(3, 8) = 8
In words: on a local event or a send, add one (and attach the new value to the message); on a receive, jump past both your own counter and the message's timestamp, then add one.
```

The first rule applies before every local event or send; the second on every receive. Worked example: P1's counter is 7 and P2's is 3. P1 sends a message, so its counter becomes 7 + 1 = 8 and the message carries 8. P2 receives it and sets its counter to the larger of 3 and 8, plus one, which is 9. The send (8) comes before the receive (9), as it must.

```
 P1        P2        P3
 1 a
 2 send--->3 recv
           4 b
           5 send--->6 recv
 3 c                 7 d
```

The guarantee Lamport clocks give:

```formula
a → b ⇒ L(a) < L(b)
where
a: an event
b: another event
→: "happens before": a could have influenced b
⇒: "implies": whenever the left side is true, the right side is true too
L(a): the Lamport timestamp of event a
L(b): the Lamport timestamp of event b
In words: if a happened before b, a's timestamp is smaller. It does not work the other way round: a smaller timestamp doesn't prove a happened first.
```

Break ties with process id to get a **total order** consistent with causality. That's enough for things like a totally ordered mutex queue.

Limitation: the converse fails. In the diagram, L(c) is 3 and L(b) is 4, so L(c) < L(b), but c and b are concurrent: no message path links them. **A Lamport timestamp can't tell you whether two events are concurrent.**

Read the guarantee the right way round:

- L(a) < L(b): a *might* have happened before b, or they might be concurrent.
- L(a) = L(b) on different processes: they are **definitely concurrent**, because causally related events always have different timestamps.
- L(a) > L(b): a did **not** happen before b. Either b happened before a, or they're concurrent.

### Logical clocks you already use

Many systems contain a Lamport-style counter under another name: Raft's **term**, Paxos's **ballot number**, Kafka's **leader epoch**, ZooKeeper's **zxid**. Each is a number that only goes up and is carried on messages, so a node that sees a higher one knows its own information is out of date. Lesson 6 uses exactly this property for fencing tokens.

## Vector clocks

A vector clock keeps one counter **per process**. With N processes, each process holds a list of N counters, V[1] to V[N]: its best knowledge of how many events every process has had.

```formula
V_new[i] = V[i] + 1
V_new[j] = max(V[j], V′[j])
where
V: this process's vector clock, a list of N whole-number counters
N: the number of processes
i: this process's own position in the list
j: any position in the list, from 1 to N
V_new: the vector after the update
V′: V-prime, the vector carried on an incoming message
max: the larger of its two inputs
In words: on a local event or a send, add one to your own entry only (and attach the vector to the message); on a receive, take the larger value in every position, then add one to your own entry.
```

For example, if P2's clock is [1, 4, 2] and it receives a message stamped [3, 1, 0], the position-by-position maximum is [3, 4, 2], and adding one to P2's own entry gives [3, 5, 2].

To compare two vector timestamps V and W:

```formula
V ≤ W ⇔ ∀k: V[k] ≤ W[k]
V → W ⇔ V ≤ W ∧ V ≠ W
V ∥ W ⇔ V ≰ W ∧ W ≰ V
where
V: one event's vector timestamp
W: another event's vector timestamp
k: a position in the vectors
∀k: "for every position k"
⇔: "exactly when": the left side holds if and only if the right side holds
∧: "and": both conditions must hold
≤: less than or equal to (for vectors: in every position)
≰: not less than or equal to: some position of the left vector is bigger
≠: not equal: at least one position differs
→: "happened before"
∥: "is concurrent with"
In words: V happened before W when no entry of V is bigger than W's and at least one is smaller; if each vector is bigger somewhere, the events are concurrent.
```

The last case is the one Lamport clocks can't see: distinct events are **concurrent** exactly when neither vector is less than or equal to the other in every position.

```
P1: [1,0,0] a
P1: [2,0,0] send to P2
P2: [2,1,0] recv
P2: [2,2,0] send to P3
P3: [0,0,1] e (before recv)
P3: [2,2,2] recv
P1: [3,0,0] c
```

Is c → [2,2,0]? Compare [3,0,0] vs [2,2,0]: 3 > 2 in one position, 0 < 2 in another. **Concurrent.** Vector clocks can detect that, which is why Dynamo and Riak used them to keep both sibling values instead of silently dropping one.

Cost: one entry per participant. With thousands of clients as writers, vectors bloat, so systems use **version vectors** keyed by replica (not client), or prune old entries (at the risk of false conflicts).

## Hybrid logical clocks (HLC)

HLC (Kulkarni et al., 2014) combines physical time with a logical counter. Each timestamp is a pair `(l, c)`:

- `l` tracks the largest physical time seen,
- `c` is a counter that breaks ties when `l` doesn't advance.

The rule on a send or local event:

```formula
l′ = max(l, pt)
where
l: the HLC's current physical part: the largest physical time this node has seen, in the clock's time units
pt: the node's own physical (wall-clock) time right now, read from its time-of-day clock
l′: l-prime, the new physical part after the event
max: the larger of its inputs
In words: the physical part follows the wall clock, but never goes backwards and never falls behind a time it has already seen.
```

The counter c then decides ties. If l′ is the same as l (the wall clock hasn't moved past what was already seen), c goes up by one; otherwise the physical part has advanced and c resets to 0. As code:

```python
l_new = max(l, pt)
if l_new == l:
    c = c + 1
else:
    c = 0
l = l_new
```

On receive of a message stamped `(lm, cm)`, take the max of `l`, `lm` and `pt`, and set c accordingly (incrementing from whichever input matched).

Properties:

- Respects happens-before like a Lamport clock (and, like one, can't detect concurrency).
- Stays within the maximum clock skew of real time, so timestamps are human-meaningful.
- Can use compact fixed-size encodings; exact timestamp widths depend on the implementation.

CockroachDB and YugabyteDB use HLCs for MVCC timestamps. CockroachDB adds a **maximum clock offset** (500 ms by default) and an "uncertainty interval": if a read sees a value whose timestamp is within that window above the read timestamp, it can't tell whether it happened before the read, so it restarts the read at a higher timestamp.

```formula
r < w ≤ r + Δ_max
where
r: the read's timestamp
w: the timestamp of a value the read finds
Δ_max: delta-max, the maximum clock offset allowed between any two nodes; 500 milliseconds (ms) by default in CockroachDB
ms: millisecond, one thousandth of a second
In words: a value stamped later than the read, but by no more than the maximum clock offset, might really have been written before the read, so the read can't safely ignore it and restarts.
```

Worked example: a read at 10.000 s finds a value written at 10.200 s. The window runs up to 10.000 + 0.500 = 10.500 s, and 10.200 falls inside it, so the read restarts at a timestamp of 10.200 s or above and then includes the value. A value stamped 10.600 s would be outside the window, so the read can treat it as definitely later and ignore it.

A node that detects its clock is too far from the rest of the cluster shuts itself down rather than risk violating the bound.

## TrueTime and Spanner

Google Spanner takes the opposite approach: make physical time trustworthy by **bounding the uncertainty**. Each data centre has GPS receivers and atomic clocks. Instead of a single time, the TrueTime API returns an interval that is guaranteed to contain the true time:

```formula
TT.now() = [earliest, latest]
latest − earliest ≈ 2 × ε
where
TT.now(): the TrueTime call that asks "what time is it?"
earliest: the earliest the true time could be right now
latest: the latest the true time could be right now
ε: epsilon, the error bound: how far the local clock could be from true time in either direction, in milliseconds (ms); it varied between about 1 and 7 ms in the 2012 Spanner paper
≈: approximately equal to
ms: millisecond, one thousandth of a second
In words: TrueTime never claims an exact time; it says "the real time is somewhere in this window", and the window is about twice the error bound wide.
```

Real time is guaranteed to be inside the interval. ε isn't fixed: it grows between synchronisations with the time masters (to allow for local drift) and shrinks after each one. If the time masters become unreachable, ε keeps growing, and Spanner gets **slower** (longer commit waits) rather than incorrect.

### Commit wait

To commit a transaction, Spanner:

1. picks timestamp `s = TT.now().latest`,
2. waits until `TT.now().earliest > s`,
3. then makes the commit visible.

```
     s = latest
       |
 [--ε--|--ε--]
       |<-wait->|
                commit visible
```

After the wait, `s` is definitely in the past on every clock. Any transaction that starts later in real time will get a larger timestamp. That's how Spanner gets **external consistency** (strict serializability) with timestamp ordering.

The cost is the wait itself. The timestamp is chosen at the top of the interval, and the wait ends when the bottom of the interval has passed it, which takes about the interval's full width:

```formula
s = TT.now().latest
TT.now().earliest > s
t_wait ≈ 2 × ε
t_wait ≈ 2 × 4 ms = 8 ms
where
s: the commit timestamp Spanner picks for the transaction
TT.now(): the TrueTime call, which returns an interval [earliest, latest] containing the true time
latest: the top of that interval
earliest: the bottom of that interval
t_wait: the commit wait, how long the commit stays invisible, in milliseconds (ms)
ε: epsilon, TrueTime's current error bound, in ms; here 4 ms
≈: approximately equal to
ms: millisecond, one thousandth of a second
In words: Spanner stamps the commit with the latest possible current time, then waits until even the earliest possible current time is later than that stamp, which takes about twice the error bound.
```

So with ε around 4 ms, each commit waits about 8 ms: a few milliseconds per commit, and longer whenever ε grows. Spanner overlaps this wait with replication, so the real added latency is often smaller.

> [!tip] The trade-off in one line
> Spanner spends money on hardware to make ε small, then waits it out. CockroachDB, on commodity clocks with bigger ε, avoids waiting on writes but sometimes restarts reads instead.

## Summary comparison

| Clock | Detects concurrency? | Size |
|---|---|---|
| Physical (NTP) | No, and can be wrong | 64 bits |
| Lamport | No | 1 integer |
| Vector | Yes | One integer per process |
| HLC | No | Implementation-dependent |
| TrueTime | Bounded interval | 2 timestamps |

## Key takeaways
- Use monotonic clocks for durations; time-of-day clocks drift, get stepped by NTP and can go backwards.
- NTP gives roughly millisecond accuracy on a LAN and assumes symmetric delay; skew makes last-write-wins lose data.
- Happens-before is defined by process order and messages; events with no such path are concurrent.
- Lamport clocks give a total order consistent with causality but can't detect concurrency; vector clocks can, at a size that grows with the number of processes (one counter each).
- Hybrid logical clocks combine physical time and counters; CockroachDB uses them with an uncertainty interval.
- Spanner's TrueTime bounds clock error and uses commit wait to achieve external consistency.

## Further reading
- [Time, Clocks, and the Ordering of Events (Lamport, 1978)](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- [Vector clock (Wikipedia)](https://en.wikipedia.org/wiki/Vector_clock)
- [Logical Physical Clocks and Consistent Snapshots (HLC paper)](https://cse.buffalo.edu/tech-reports/2014-04.pdf)
- [Spanner: Google's Globally-Distributed Database (OSDI 2012)](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf)
- [Living without atomic clocks (Cockroach Labs)](https://www.cockroachlabs.com/blog/living-without-atomic-clocks/)
- [Network Time Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Network_Time_Protocol)
