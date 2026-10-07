---
id: dist-leases-locks
title: Leader election, leases and distributed locks
level: advanced
minutes: 14
summary: Why every distributed lock is really a lease, how fencing tokens stop stale holders doing damage, and the Redlock debate.
---

Many systems need exactly one actor doing something at a time: one scheduler running cron jobs, one primary database, one worker processing a given file. On a single machine you'd take a mutex. Across machines, it's much harder, because the holder can crash, pause or be cut off while holding it.

## Locks are really leases

A distributed lock that never expires is useless: if the holder crashes, nobody can ever take it. So every practical distributed lock has a timeout. A lock with a timeout is a **lease**: "you own this for the next 10 seconds, renew it if you want to keep it."

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
- **Leave a margin for clock rate drift.** Two machines don't need synchronised clocks for leases, but their clocks must run at roughly the same *rate*. Stop acting a little before your local expiry.

## Fencing tokens

The fix, described in the Chubby paper and popularised by Martin Kleppmann: every time the lock service grants the lock, it also returns a **fencing token**, a number that strictly increases with each grant.

- The client sends the token with every request to the protected resource.
- The resource remembers the highest token it has seen and **rejects** any request with a lower one.

```
A gets lock, token 33
A pauses
lease expires
B gets lock, token 34
B writes (34)  -> storage: max=34 OK
A wakes, writes (33)
               -> storage: 33<34 REJECT
```

Once the resource has accepted a higher token, it rejects lower-token writes. Acquisition alone does not notify the resource: register the new epoch before reading or acting on state when the protocol requires that boundary.

### Where tokens come from

| System | Natural fencing token |
|---|---|
| etcd | Lock key's `create_revision` or `mod_revision` |
| ZooKeeper | `zxid` or znode `cversion`/sequence number |
| Raft/Paxos | The term or ballot number |
| Database | A version column updated with each grant |

Raft's **term** is itself a fencing token: followers reject `AppendEntries` from a leader with a lower term. That's why stale Raft leaders can't corrupt the log.

### The catch

The resource has to cooperate. A database can do it with a conditional update:

```
UPDATE jobs
SET owner = 'B', token = 34
WHERE id = 7 AND token <= 34;
```

The `<=` lets the current holder write repeatedly with the same token, while any lower (stale) token matches no rows. Check the affected row count: zero means you've been fenced off.

The check must also happen in **one consistent place**. If the "resource" is three asynchronously replicated copies that each track their own highest token, a stale write can still succeed on a copy that hasn't yet seen the newer token. A single leader or a linearizable conditional write does the job; independent replicas don't.

An S3 bucket, a payment API or an email server generally won't check your token. For those, you need idempotency (so a duplicate is harmless) or you must accept the risk.

## Efficiency locks versus correctness locks

Kleppmann distinguishes two purposes:

- **Efficiency**: avoid doing the same work twice (e.g. two workers both regenerating a report). An occasional double run wastes money but is harmless.
- **Correctness**: two holders would corrupt data, double-charge or lose updates.

For efficiency, a simple single-node Redis lock (`SET key token NX PX 10000`) is perfectly fine. For correctness, you need a consensus-backed lock service *and* fencing at the resource.

Even an efficiency lock needs a careful **release**. A plain `DEL key` is wrong: if your lease expired during a pause and someone else acquired the lock, you'd delete *their* lock. Release only if the value is still your random token, atomically, with a small Lua script:

```
if redis.call("get", KEYS[1])
   == ARGV[1] then
  return redis.call("del", KEYS[1])
end
return 0
```

## Redlock and why it's controversial

Redlock is an algorithm proposed by Salvatore Sanfilippo (antirez), Redis's creator, for a lock that survives a Redis node failing. It uses N independent Redis masters (typically 5), with no replication between them:

1. Get the current time T1.
2. Try `SET resource token NX PX ttl` on all 5 instances, with a short per-node timeout.
3. Get the time T2. The lock is held if a majority (≥ 3) succeeded **and** T2 − T1 < ttl.
4. The validity time is ttl − (T2 − T1) − clock drift allowance.
5. On failure, release on all instances.

### Kleppmann's critique (2016)

1. **No fencing tokens.** Redlock returns a random value, not a monotonically increasing number, so a resource can't tell an old holder from a new one. Process pauses still cause two holders, as in the diagram above.
2. **It depends on timing assumptions.** Safety relies on bounded network delay, bounded pauses and clocks that don't jump. If a Redis node's clock jumps forward (NTP step, admin change), its key expires early:

```
C1 locks A, B, C   (3 of 5)
C's clock jumps forward
  -> C expires C1's key
C2 locks C, D, E   (3 of 5)
Both C1 and C2 think they hold it
```

A node crashing and restarting without persisted keys (or with `fsync` every second) has the same effect.

His conclusion: Redlock is too heavy for efficiency locks (one Redis is fine) and not safe enough for correctness locks (use ZooKeeper or etcd with fencing).

### Antirez's response

Antirez argued that:

- the random token can be used for compare-and-set at the resource in some cases;
- Redlock's step 3 detects long delays *during acquisition*;
- clock jumps can be avoided operationally by slewing rather than stepping, so the timing assumptions are reasonable;
- every lock with auto-release has the GC pause problem, including ZooKeeper's.

The last point is true, and it's exactly why fencing tokens are the real answer: they make safety independent of timing. Redlock's problem is that it doesn't produce one.

> [!tip] Practical guidance
> For efficiency only, a single Redis `SET NX PX` is fine. For correctness, use etcd, ZooKeeper or Consul, *plus* fencing tokens at the resource, *plus* idempotency where the resource can't check tokens. Or partition work by key, as Kafka consumer groups do, and enforce sequencing or fencing at external storage so a stale consumer cannot reorder writes during a rebalance.

## Key takeaways
- Any distributed lock that can auto-expire is a lease; holders must renew, and lease length trades failover speed against false expiry.
- A holder can't reliably know it has lost the lease, because pauses and delays can strike between check and act.
- Fencing tokens (monotonically increasing per grant) let the protected resource reject stale holders, making safety independent of timing. The check must happen in one consistent place.
- Holders should time leases from before the request, on the monotonic clock, and release locks only if they still own them.
- etcd revisions, ZooKeeper zxids and Raft terms all serve as fencing tokens.
- Distinguish efficiency locks (single Redis is fine) from correctness locks (consensus plus fencing).
- Redlock lacks fencing tokens and relies on bounded clocks and pauses, which is why Kleppmann argued it is unsafe for correctness.

## Further reading
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Is Redlock safe? (antirez's reply)](http://antirez.com/news/101)
- [Distributed locks with Redis (Redis docs)](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/)
- [Leader election in distributed systems (AWS Builders' Library)](https://aws.amazon.com/builders-library/leader-election-in-distributed-systems/)
- [ZooKeeper recipes: locks and leader election](https://zookeeper.apache.org/doc/current/recipes.html)
- [Leases (Kubernetes docs)](https://kubernetes.io/docs/concepts/architecture/leases/)
