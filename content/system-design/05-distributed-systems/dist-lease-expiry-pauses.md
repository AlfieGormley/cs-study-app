---
id: dist-lease-expiry-pauses
title: Lease expiry and the paused holder
level: advanced
minutes: 5
summary: Time a lease conservatively while recognising why client-side checks cannot ensure exclusive action.
sourceLesson: dist-leases-locks
---

Many systems need exactly one actor doing something at a time: one scheduler running cron jobs, one primary database, one worker processing a given file. On a single machine you'd take a mutex. Across machines, it's much harder, because the holder can crash, pause or be cut off while holding it.

## Locks are really leases

A distributed lock that never expires is useless: if the holder crashes, nobody can ever take it. Lease-based services use an expiry or session timeout to recover ownership automatically after failure; some systems instead require explicit recovery of persistent locks. A lock with a timeout is a **lease**: "you own this for the next 10 seconds, renew it if you want to keep it."

```
client A        lock service
  |--acquire----->|  lease 10 s
  |<--granted-----|
  |  ... work ... |
  |--renew------->|  every ~3 s
  |<--ok----------|
```

The holder renews well before expiry (often at a third of the lease). If it crashes, renewals stop and the lease expires, letting someone else take over.

### Why use a lease for leader election?

Leader election is a lock on the role "leader". Kubernetes controllers use a `Lease` object (in the `coordination.k8s.io` API, stored in etcd behind the API server); HDFS and HBase use ZooKeeper ephemeral nodes; AWS describes the same pattern with DynamoDB conditional writes in its Builders' Library.

Choosing the lease duration is a trade-off:

| Lease | Pro | Con |
|---|---|---|
| Short (2 s) | Fast failover | False expiry on GC/network blips |
| Long (60 s) | Few false failovers | Long outage if holder dies |

## The fundamental problem: the holder doesn't know it lost

A lease expiry is decided by the lock service's clock. The holder only *believes* it holds the lease, based on its own sense of time. Process pauses break that belief:

```
A            lock svc        storage
|--acquire-->|
|<--ok, 10s--|
| GC pause...
|            | lease expires
|            |<--acquire-- B
|            |---ok-------> B
|            |       B writes ->|
| ...resumes |
|--write (thinks it holds)----->|
          CORRUPTION
```

Checking "do I still hold the lease?" right before writing doesn't help: the pause can happen *between* the check and the write. Network delays do the same: A's write can sit in a TCP buffer and arrive after B's.

> [!warning] You can't fix this on the client
> Any client-side check is a check-then-act race. The only safe place to reject a stale holder is the resource being protected.

### Holder-side hygiene still matters

Client checks can't make a lease *safe*, but they make trouble rarer, and getting them wrong makes it common:

- **Start the clock before you ask.** Record the monotonic time just *before* sending the acquire request, and count the lease from then. The service starts its countdown when it grants, which is later, so the holder's view expires first.
- **Use the monotonic clock**, never the time-of-day clock, so an NTP step can't extend the lease.
- **Leave a margin for clock rate drift.** Two machines don't need synchronised clocks for leases, but clock-rate error must stay within the protocol's assumed bound. Stop acting a little before your local expiry.

Put together, the holder works out its own deadline like this:

```formula
t_stop = t_send + T_lease − m
t_stop = 0.0 s + 10 s − 0.5 s = 9.5 s
where
t_stop: the time, on the holder's monotonic clock, after which it must stop acting as the lease holder
t_send: the holder's monotonic clock reading just before it sent the acquire request; here 0.0 s
T_lease: the lease duration the service granted; here 10 seconds (s)
m: a safety margin for clock rate drift and processing delays; here 0.5 s
s: second
In words: count the lease from before you asked, not from when the answer arrived, and stop a little early.
```

Worked example: the request takes 300 ms to arrive, so the service grants at 0.3 s and its lease runs to 10.3 s. The reply takes another 300 ms. Counting from the reply would let the holder act until 10.6 s, after the service has already given the lease away. Counting from the send, with the margin, the holder stops at 9.5 s, safely first. This assumes the two clocks run at nearly the same rate; it does nothing about a pause that strikes between checking the deadline and acting.

## Key takeaways
- A lease expires unless renewed, trading failover speed against false expiry during pauses and delays.
- A holder can pause between checking its lease and acting, so a client check cannot make the resource safe.
- Count from before acquisition on a monotonic clock and leave a drift margin; that hygiene does not eliminate check-then-act races.

## Further reading
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Leader election in distributed systems (AWS Builders' Library)](https://aws.amazon.com/builders-library/leader-election-in-distributed-systems/)
- [ZooKeeper recipes: locks and leader election](https://zookeeper.apache.org/doc/current/recipes.html)
- [Leases (Kubernetes docs)](https://kubernetes.io/docs/concepts/architecture/leases/)
