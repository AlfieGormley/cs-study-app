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

Quartz crystals run slightly fast or slow, and it varies with temperature. Typical drift is 10 to 200 parts per million.

- 200 ppm × 86,400 s = **17 s per day** if never corrected.
- **Skew** is the difference between two clocks at one moment.

### NTP

The Network Time Protocol syncs a client with servers arranged in strata (stratum 0 is an atomic clock or GPS; stratum 1 servers attach to it, and so on). A client estimates offset from a round trip:

```
client            server
 t0 |--request--->|
    |             | t1 (receive)
    |             | t2 (send)
 t3 |<--reply-----|

delay  = (t3 - t0) - (t2 - t1)
offset = ((t1 - t0) + (t2 - t3)) / 2
```

The offset formula assumes the network delay is **symmetric**. If the outbound path is slow and the return fast, the estimate is wrong by half the asymmetry. Typical accuracy: around 1 ms on a good LAN, tens of ms over the internet, and much worse under congestion. AWS and Google offer leap-smeared, GPS-backed time services that do better (sub-millisecond, with bounds).

NTP corrects a clock by **slewing** (running it slightly fast or slow) for small offsets and **stepping** (jumping) for large ones. Steps are what make clocks go backwards.

> [!warning] Last-write-wins with skewed clocks
> Node A's clock is 100 ms fast. A client writes v1 on A at A-time 10.100 (real 10.000). 50 ms later a client writes v2 on B at B-time 10.050 (real 10.050). LWW keeps v1 because 10.100 > 10.050, silently discarding the genuinely later write. This is a well-known hazard in Cassandra and other last-write-wins stores: any two writes closer together than the clock skew can be ordered wrongly.

## Happens-before

Lamport's 1978 paper defined order without clocks. Event *a* **happens before** *b* (written a → b) if:

1. a and b are on the same process and a comes first, or
2. a is sending a message and b is receiving that message, or
3. there's an event c with a → c and c → b (transitivity).

If neither a → b nor b → a, the events are **concurrent** (a ∥ b). Concurrent doesn't mean simultaneous; it means neither could have influenced the other.

## Lamport clocks

Each process keeps an integer counter `L`.

- Before every local event or send: `L = L + 1`; attach `L` to sends.
- On receive with timestamp `t`: `L = max(L, t) + 1`.

```
 P1        P2        P3
 1 a
 2 send--->3 recv
           4 b
           5 send--->6 recv
 3 c                 7 d
```

Guarantee: if a → b then L(a) < L(b). Break ties with process id to get a **total order** consistent with causality. That's enough for things like a totally ordered mutex queue.

Limitation: the converse fails. L(c)=3 < L(b)=4 but c and b are concurrent. **A Lamport timestamp can't tell you whether two events are concurrent.**

Read the guarantee the right way round:

- L(a) < L(b): a *might* have happened before b, or they might be concurrent.
- L(a) = L(b) on different processes: they are **definitely concurrent**, because causally related events always have different timestamps.
- L(a) > L(b): a did **not** happen before b. Either b happened before a, or they're concurrent.

### Logical clocks you already use

Many systems contain a Lamport-style counter under another name: Raft's **term**, Paxos's **ballot number**, Kafka's **leader epoch**, ZooKeeper's **zxid**. Each is a number that only goes up and is carried on messages, so a node that sees a higher one knows its own information is out of date. Lesson 6 uses exactly this property for fencing tokens.

## Vector clocks

A vector clock keeps one counter **per process**. For N processes, each holds `V[1..N]`.

- Local event or send: `V[i] += 1`; attach V to sends.
- Receive V': `V[j] = max(V[j], V'[j])` for all j, then `V[i] += 1`.

Compare two vectors:

- V ≤ W if every entry of V ≤ the matching entry of W.
- V → W (happened before) if V ≤ W and V ≠ W.
- If W ≤ V and W ≠ V, W happened before V.
- Distinct events are **concurrent** only when neither vector is component-wise less than or equal to the other.

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

Rules on a send or local event, with physical time `pt`:

```
l' = max(l, pt)
if l' == l: c = c + 1
else:       c = 0
l = l'
```

On receive of `(lm, cm)`, take the max of `l`, `lm` and `pt`, and set c accordingly (incrementing from whichever input matched).

Properties:

- Respects happens-before like a Lamport clock (and, like one, can't detect concurrency).
- Stays within the clock-skew bound ε of real time, so timestamps are human-meaningful.
- Can use compact fixed-size encodings; exact timestamp widths depend on the implementation.

CockroachDB and YugabyteDB use HLCs for MVCC timestamps. CockroachDB adds a **maximum clock offset** (500 ms by default) and an "uncertainty interval": if a read sees a value whose timestamp is within that window above the read timestamp, it can't tell whether it happened before the read, so it restarts the read at a higher timestamp. A node that detects its clock is too far from the rest of the cluster shuts itself down rather than risk violating the bound.

## TrueTime and Spanner

Google Spanner takes the opposite approach: make physical time trustworthy by **bounding the uncertainty**. Each data centre has GPS receivers and atomic clocks. The TrueTime API returns an interval:

```
TT.now() -> [earliest, latest]
error bound ε: 1-7 ms in the 2012 paper
```

Real time is guaranteed to be inside the interval, which is about 2ε wide. ε isn't fixed: it grows between synchronisations with the time masters (to allow for local drift) and shrinks after each one. If the time masters become unreachable, ε keeps growing, and Spanner gets **slower** (longer commit waits) rather than incorrect.

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

After the wait, `s` is definitely in the past on every clock. Any transaction that starts later in real time will get a larger timestamp. That's how Spanner gets **external consistency** (strict serializability) with timestamp ordering, at the cost of waiting about 2ε per commit, typically a few milliseconds.

> [!tip] The trade-off in one line
> Spanner spends money on hardware to make ε small, then waits it out. CockroachDB, on commodity clocks with bigger ε, avoids waiting on writes but sometimes restarts reads instead.

## Summary comparison

| Clock | Detects concurrency? | Size |
|---|---|---|
| Physical (NTP) | No, and can be wrong | 64 bits |
| Lamport | No | 1 integer |
| Vector | Yes | N integers |
| HLC | No | Implementation-dependent |
| TrueTime | Bounded interval | 2 timestamps |

## Key takeaways
- Use monotonic clocks for durations; time-of-day clocks drift, get stepped by NTP and can go backwards.
- NTP gives roughly millisecond accuracy on a LAN and assumes symmetric delay; skew makes last-write-wins lose data.
- Happens-before is defined by process order and messages; events with no such path are concurrent.
- Lamport clocks give a total order consistent with causality but can't detect concurrency; vector clocks can, at O(N) size.
- Hybrid logical clocks combine physical time and counters; CockroachDB uses them with an uncertainty interval.
- Spanner's TrueTime bounds clock error and uses commit wait to achieve external consistency.

## Further reading
- [Time, Clocks, and the Ordering of Events (Lamport, 1978)](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- [Vector clock (Wikipedia)](https://en.wikipedia.org/wiki/Vector_clock)
- [Logical Physical Clocks and Consistent Snapshots (HLC paper)](https://cse.buffalo.edu/tech-reports/2014-04.pdf)
- [Spanner: Google's Globally-Distributed Database (OSDI 2012)](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf)
- [Living without atomic clocks (Cockroach Labs)](https://www.cockroachlabs.com/blog/living-without-atomic-clocks/)
- [Network Time Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Network_Time_Protocol)
