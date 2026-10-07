---
id: dist-crdts-gossip
title: Conflict resolution, CRDTs and gossip
level: advanced
minutes: 16
summary: Resolving concurrent writes with last-write-wins, version vectors and CRDTs (G-Counter, PN-Counter, OR-Set), and spreading state with gossip, phi accrual and SWIM.
---

Systems that accept writes on several replicas at once (multi-leader, leaderless, offline-first apps, multi-region active-active) will see **concurrent writes** to the same data. They must merge them so that every replica ends up with the same value. This lesson covers how, and how such clusters learn about each other through gossip.

## Detecting conflicts: version vectors

Before you resolve a conflict you need to know one exists. A **version vector** (a vector clock keyed by replica rather than by client) records, for each replica, how many updates from it this version has seen.

```
replica A writes:  {A:1}
replica B writes:  {A:1, B:1}  (saw A's)
replica A writes:  {A:2}       (didn't
                                see B's)
```

Compare `{A:1, B:1}` with `{A:2}`: each is ahead in one entry, so they're **concurrent**. A store like Riak keeps both as **siblings** and returns both to the next reader, who merges them and writes back with a vector that dominates both, `{A:2, B:1}` plus an increment.

If one vector dominates (≥ in every entry), the dominated version is simply obsolete and can be discarded.

## Last-write-wins (LWW)

The simplest resolution: attach a timestamp to every write and keep the highest (ties broken by something deterministic, such as replica id). Cassandra does this per column; DynamoDB global tables do it per item in their default, eventually consistent mode.

It's simple and converges, but it **silently loses data**:

- Two concurrent writes: one is discarded, even though both clients got "success".
- With clock skew, a write that happened later can lose to an earlier one with a faster clock.

```
t=10.000 A: cart = [book]   clock +50ms
t=10.020 B: cart = [pen]    clock ok
stored ts: A=10.050, B=10.020
LWW keeps [book]; [pen] lost
```

LWW is fine when writes are naturally immutable (each key written once, e.g. keyed by UUID) or when losing a concurrent update is acceptable (a user's "last seen" time). For anything like a shopping cart, you need a merge.

> [!example] Dynamo's shopping cart
> The Dynamo paper's cart merged siblings by taking the **union** of items. That never loses an add, but a removed item could reappear if a concurrent sibling still contained it. That's exactly the problem the OR-Set solves.

## CRDTs

A **Conflict-free Replicated Data Type** is a data structure designed so that replicas can be updated independently and **always merge to the same result**, with no coordination and no conflicts to resolve by hand.

State-based CRDTs (CvRDTs) define a `merge` function that is:

| Property | Meaning |
|---|---|
| Commutative | merge(a, b) = merge(b, a) |
| Associative | Grouping doesn't matter |
| Idempotent | merge(a, a) = a |

Those three properties mean replicas can exchange state in any order, any number of times, via any path (gossip), and still converge. That's **strong eventual consistency**: replicas that have received the same updates are in the same state.

There's a fourth condition that's easy to miss: **local updates may only move the state "upwards"**, so that the updated state, merged with the old one, gives the updated state. Formally, states form a *join-semilattice*, merge is the least upper bound, and updates are inflationary. That's why a G-Counter may only increase entries and why a set "remove" is recorded as a tombstone rather than by deleting the element: a deletion would be undone by the next merge with a replica that still has it.

Operation-based CRDTs (CmRDTs) instead broadcast operations. Concurrent operations must commute, and the delivery layer usually has to deliver each operation **exactly once** and in **causal order**. They send less data but need more from the network. Delta-state CRDTs sit in between: they ship only the recently changed part of the state, merged with the same join.

### G-Counter (grow-only counter)

Each replica keeps a vector of counts, one per replica, and only increments its own entry.

- `increment()` on replica i: `P[i] += 1`
- `value()`: sum of all entries
- `merge(X, Y)`: element-wise max

```
A: [A:3, B:0, C:0]  (3 local incs)
B: [A:1, B:2, C:0]  (saw 1 of A's)
merge -> [A:3, B:2, C:0]
value = 5
```

Why max and not sum? Because merging the same state twice must not double count (idempotence). Each entry is only ever increased by its owner, so the max is always the owner's latest value.

### PN-Counter (increment and decrement)

A G-Counter can't decrement: lowering an entry would be undone by max. So use **two** G-Counters: `P` for increments and `N` for decrements.

- `value() = sum(P) − sum(N)`
- `merge` merges P and N separately.

```
A: P=[A:5,B:0] N=[A:1,B:0]
B: P=[A:2,B:3] N=[A:0,B:2]
merge:
P=[A:5,B:3] = 8
N=[A:1,B:2] = 3
value = 5
```

Used for like-counts, stock levels where brief overselling is tolerable, and Redis Enterprise's active-active counters. Note that a PN-Counter can't enforce "never below zero": that's a global invariant needing coordination.

A middle ground is an **escrow** (or bounded) counter: split the available stock between replicas up front (say 60 units to EU, 40 to US). Each replica can decrement its own share without coordination and only needs to talk to others to borrow more. The invariant holds, and coordination happens only near the limit.

### G-Set and 2P-Set

A **G-Set** only grows; merge is union. A **2P-Set** adds a "tombstone" set of removed elements; an element is present if it's in the add-set and not the remove-set. Its flaw: once removed, an element can **never be re-added**.

### OR-Set (observed-remove set)

The OR-Set fixes that. Every `add(x)` attaches a **unique tag** (e.g. replica id + counter). `remove(x)` removes only the tags the remover has **observed**.

```
A: add(milk) tag a1
   -> sync to B
B: remove(milk)  removes {a1}
A: add(milk) tag a2   (concurrent)
merge:
 adds   = {a1, a2}
 removes= {a1}
 milk present (tag a2 survives)
```

Concurrent add and remove resolves to **add wins**, which is usually what users expect (re-adding milk to the shopping list shouldn't be cancelled by someone else's earlier removal). Riak's sets and maps, Redis CRDB sets and Automerge's internals use this idea.

### Beyond sets

- **LWW-Register / MV-Register**: a single value, resolved by timestamp or kept as multiple values.
- **Maps** of CRDTs, recursively.
- **Sequence CRDTs** (RGA, Logoot, Yjs, Automerge) for collaborative text editing, as in many real-time editors.

Costs: metadata grows (tags and tombstones accumulate and need garbage collection). Arbitrary independent updates cannot preserve every invariant; bounded counters can enforce non-negative stock using preallocated rights, as described above.

Garbage collection is the hard part. A tombstone can only be dropped once **every** replica has seen it; otherwise a replica that was offline still holds the old add, and the next merge brings the element back. Knowing that every replica has caught up is itself a coordination problem, the same one behind Cassandra's `gc_grace_seconds` in lesson 4. (Optimised OR-Sets such as Riak's ORSWOT avoid most tombstones by using version vectors, but pay in vector size instead.)

> [!tip] Choosing
> Use a CRDT when merging is semantically clear (counters, sets, collaborative docs) and availability matters more than invariants. Use consensus when you need invariants.

## Gossip protocols

Large clusters (Cassandra, Consul, Riak, ScyllaDB) need every node to learn membership, liveness and metadata without a central server. **Gossip** (epidemic) protocols do this:

1. Every interval (e.g. 1 s), each node picks a random peer (or a few).
2. They exchange state digests and the newer entries (push, pull or push-pull).
3. Information spreads like an infection.

```
round 0: 1 node knows
round 1: 2
round 2: 4
round 3: 8 ...
~log2(N) rounds to reach most
```

The doubling picture is the optimistic phase. Because peers are picked at random, more and more messages land on nodes that already know, and the last few uninformed nodes take a while to be hit. For push gossip with fanout 1 the total is about log₂N + ln N rounds: with N = 1,000 that's roughly 10 + 7 ≈ 17 rounds. Push-pull (where uninformed nodes also *ask* random peers) finishes the tail much faster. Either way it's O(log N).

Load per node is constant regardless of cluster size, and gossip tolerates node and message loss naturally. CRDT merges pair well with gossip because they're idempotent and order-insensitive.

## Failure detection

### Heartbeats with a fixed timeout

The simplest detector: if no heartbeat for T seconds, mark dead. Pick T too short and you get false positives under load; too long and real failures go unnoticed. One threshold can't suit every network condition.

### Phi accrual failure detector

Hayashibara et al. (2004), used by Cassandra and Akka, output a **suspicion level φ** instead of a yes/no.

- Each node records recent heartbeat inter-arrival times and models them as a distribution (the original paper uses a normal distribution with the observed mean and variance; Cassandra uses a simpler exponential model).
- φ = −log₁₀(P(a heartbeat arrives later than now)).

| φ | Modelled heartbeat tail probability |
|---|---|
| 1 | 10% |
| 3 | 0.1% |
| 8 | 0.000001% |

The application chooses a threshold (Cassandra's `phi_convict_threshold` defaults to 8). The adaptation depends on the model: Cassandra's exponential detector uses the observed mean interval, so extra variance alone at the same mean does not guarantee later conviction. The tail probability is not a measured false-positive rate.

### SWIM

SWIM (Das, Gupta and Motivala, 2002) is a scalable membership protocol, used in HashiCorp's memberlist (Consul, Nomad, Serf).

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
2. No ack? A asks k other members to **ping-req** B on its behalf (indirect probing), which rules out a problem with A's own link.
3. Still nothing: B is **suspected**, not dead. Suspicion is gossiped; B can refute it by gossiping an incremented **incarnation number**.
4. After a suspicion timeout, B is declared **dead**.

Membership updates **piggyback** on ping and ack messages, so there's no separate broadcast traffic. Per-node load is constant and detection time doesn't grow with cluster size. HashiCorp's Lifeguard extensions further reduce false positives from slow, overloaded nodes.

## Key takeaways
- Version vectors detect concurrent writes; dominated versions are discarded, concurrent ones become siblings to merge.
- Last-write-wins is simple but silently drops concurrent writes and is vulnerable to clock skew; use it only for immutable or unimportant data.
- CRDT merges are commutative, associative and idempotent, and updates only move state upwards in the lattice, giving strong eventual consistency without coordination.
- G-Counter merges with element-wise max; PN-Counter pairs two G-Counters; OR-Set tags each add so concurrent add and remove resolves to add-wins.
- CRDTs cannot preserve arbitrary global invariants under unrestricted updates and can accumulate metadata; garbage-collecting tombstones needs every replica to have caught up. Use consensus (or escrow) where invariants matter.
- Gossip spreads state in O(log N) rounds (about log₂N + ln N for push) with constant per-node load; phi accrual gives adaptive suspicion levels; SWIM adds indirect probes and suspicion with incarnation numbers.

## Further reading
- [Conflict-free replicated data type (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
- [A comprehensive study of CRDTs (Shapiro et al.)](https://hal.inria.fr/inria-00555588/document)
- [crdt.tech: resources and implementations](https://crdt.tech/)
- [CRDTs: the hard parts (Martin Kleppmann)](https://martin.kleppmann.com/2020/07/06/crdt-hard-parts-hydra.html)
- [Version vector (Wikipedia)](https://en.wikipedia.org/wiki/Version_vector)
- [SWIM paper (Das, Gupta, Motivala)](https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/SWIM.pdf)
- [Gossip protocol (Wikipedia)](https://en.wikipedia.org/wiki/Gossip_protocol)
- [HashiCorp memberlist (SWIM implementation)](https://github.com/hashicorp/memberlist)
