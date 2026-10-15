---
id: dl-livelock-starvation-retry-collisions
title: Livelock and collision back-off
level: intermediate
minutes: 4
sourceLesson: dl-livelock-starvation
summary: Repeated retry state changes can make no useful progress without a blocked wait cycle.
---

## Livelock

Two people meet in a corridor. Both step left to let the other pass, then both step right, then both step left. Each is responding sensibly to the other, and neither gets anywhere. That's **livelock**: threads keep changing state in response to each other without making progress.

The prevention lessons's try-lock pattern is the classic way to create it:

```python
def polite(first, second):
    while True:
        first.acquire()
        if second.acquire(blocking=False):
            return          # got both
        # Both contenders may retry
        # together.
        first.release()
        # no back-off: retry at once
```

Run `polite(a, b)` and `polite(b, a)` on two cores in perfect lockstep:

```
T1: take a     T2: take b
T1: try b, no  T2: try a, no
T1: drop a     T2: drop b
T1: take a     T2: take b
...forever
```

In this particular repeating schedule neither thread blocks indefinitely, so a blocked-wait cycle detector misses the failure. CPU use can be high. Other schedules may briefly block at `first.acquire()`. The caller must release both locks after a successful return.

Scheduling variation may break this pattern, but it supplies no progress guarantee; repeated collisions can waste CPU and increase latency.

### The fix: break the symmetry

For this symmetric retry pattern, useful ways to improve progress include:

- **Randomised back-off.** Sleep a random time before retrying, so the two sides stop moving in step. Ethernet's original CSMA/CD did exactly this (below).
- **Ordering.** If both threads take `a` before `b`, the problem disappears entirely (the prevention lessons).
- **Priority or tie-breaking.** Let the older or lower-id contender win.

On the original shared-cable Ethernet, two stations that transmit at once garble each other's frames: an **Ethernet collision**. CSMA/CD (carrier-sense multiple access with collision detection) makes each station pick a random wait from a range that doubles after every collision, up to a limit:

```formula
k = min(c, 10)
r ∈ {0, 1, …, 2^k − 1}
t_wait = r t_slot
t_max = (2^3 − 1) × 51.2 µs = 358.4 µs
where
c: how many times this frame has collided so far (1 after the first collision)
min(c, 10): the smaller of c and 10, so the range stops growing after the 10th collision
k: the back-off exponent
r: a whole number of slot times, chosen at random with every value equally likely
∈ {…}: "is one of"; … stands for the whole numbers in between
t_wait: how long the station waits before trying again
t_slot: the slot time, 512 bit times: 51.2 microseconds (µs) on 10 Mb/s Ethernet
t_max: the longest wait after the 3rd collision (c = 3, k = 3), in the example
µs: microseconds, millionths of a second
In words: after each collision the station waits a random number of slot times, and the range of possible waits doubles each time, up to 1,024 possible values (0 to 1,023 slots).
```

So after a third collision a station waits 0 to 7 slots, at most 358.4 µs at 10 Mb/s. After 16 failed attempts it gives up and reports an error. In a simplified two-station model with independent uniform choices and no other interference, choosing the same slot again causes another collision. The probability of equal choices halves with each expanding range until the tenth collision. Real carrier sensing and additional contenders complicate this model.

Raft uses the same trick for leader elections. If two followers time out together, they split the vote and both have to retry. Raft draws each election timeout at random (150–300 ms in the paper’s example) to spread elections and reduce repeated split votes. Timing, network delays and scheduling still affect whether an election succeeds.

## Key takeaways
- Repeated retry state changes can make no useful progress without a blocked wait cycle.
- Ordering or tie-breaking removes symmetric conflicts; randomized back-off reduces synchronized retries.
- Historical shared-medium Ethernet uses bounded binary exponential back-off; full-duplex links do not use CSMA/CD.

## Further reading
- [IEEE 802.3: slot-time interpretation](https://www.ieee802.org/3/interp/interp-1-0397.pdf)
- [Raft: randomised election timers](https://raft.github.io/raft.pdf)
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
