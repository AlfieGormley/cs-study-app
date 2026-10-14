---
id: dist-truetime-commit-wait
title: TrueTime and Spanner commit wait
level: intermediate
minutes: 4
summary: Use a bounded time interval and commit wait to explain external consistency.
sourceLesson: dist-time-ordering
---

HLCs handle uncertain physical time with causal ordering and read restarts. Spanner instead bounds that uncertainty and waits it out before making a transaction visible.

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
In words: TrueTime never claims an exact time; it says "the physical time is somewhere in this window", and the window is about twice the error bound wide.
```

Physical time is guaranteed to be inside the interval. ε isn't fixed: it grows between synchronisations with the time masters (to allow for local drift) and shrinks after each one. If the time masters become unreachable, ε keeps growing, and Spanner gets **slower** (longer commit waits) rather than incorrect.

### Commit wait

To commit a transaction, Spanner:

1. picks a timestamp no earlier than `TT.now().latest`, also respecting participant prepare timestamps and prior timestamp order,
2. waits until `TT.now().earliest > s`,
3. then makes the commit visible.

```
   commit timestamp
       |
 [--ε--|--ε--]
       |<-wait->|
                commit visible
```

After the wait, `s` is definitely earlier than true current time. Any transaction that starts later in physical time will get a larger timestamp. That's how Spanner gets **external consistency** (strict serializability) with timestamp ordering.

For a simple illustrative case, assume the timestamp is the top of the interval and the uncertainty stays roughly constant. The cost is the wait itself: and the wait ends when the bottom of the interval has passed it, which takes about the interval's full width:

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
| NTP wire timestamp | No | 64 bits |
| Lamport | No | 1 integer |
| Vector | Yes | One integer per process |
| HLC | No | Implementation-dependent |
| TrueTime | Bounded interval | 2 timestamps |

## Key takeaways
- TrueTime returns earliest and latest possible current times, with an uncertainty bound that grows between synchronisations.
- Spanner chooses a commit timestamp and waits until the earliest possible time has passed it before exposing the commit.
- A wider uncertainty interval lengthens commit waits; replication can overlap the wait.

## Further reading
- [Spanner: Google's Globally-Distributed Database (OSDI 2012)](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf)
- [Living without atomic clocks (Cockroach Labs)](https://www.cockroachlabs.com/blog/living-without-atomic-clocks/)
