---
id: dist-gossip-rumour-spread
title: Gossip rounds and the slow tail
level: advanced
minutes: 3
summary: Explain random-peer dissemination and why reaching the last nodes takes longer than ideal doubling.
sourceLesson: dist-crdts-gossip
---

Replicas need to exchange CRDT state and membership information. Gossip spreads that information through local random contacts rather than one all-cluster broadcast coordinator.

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
doubling: the ideal case
```

The doubling picture is the optimistic phase. Because peers are picked at random, more and more messages land on nodes that already know, and the last few uninformed nodes take a while to be hit. For ideal synchronous push gossip on a complete graph, starting from one informed node with independent uniform peer choices, reliable delivery and fanout 1 (each informed node tells one peer per round), the leading terms of the asymptotic expected round count are:

```formula
r ≈ log_2(N) + ln(N)
r ≈ log_2(1,000) + ln(1,000)
r ≈ 10 + 6.9 ≈ 17
where
r: the number of gossip rounds until every node knows
N: the number of nodes in the cluster; here 1,000
log_2: the base-2 logarithm: how many times you double 1 to reach N; this counts the doubling phase
ln: the natural logarithm (base e ≈ 2.718); this counts the slow tail of finding the last few nodes
≈: approximately equal to
In words: about log₂N rounds to reach most nodes by doubling, plus about ln N more to mop up the stragglers.
```

With one round per second, the leading-term estimate for a 1,000-node cluster is about 17 seconds, before the asymptotic constant and implementation effects. This is an estimate, not a completion deadline. Push-pull (where uninformed nodes also *ask* random peers) finishes the tail much faster. Either way the number of rounds grows with the logarithm of the cluster size, written O(log N): doubling the cluster adds only about one or two rounds.

At fixed fanout, each informed node initiates a constant number of contacts per round. Incoming contacts fluctuate, and bytes transferred depend on the metadata and state size; constant fanout is not constant bandwidth. Gossip tolerates node and message loss naturally. CRDT merges pair well with gossip because they're idempotent and order-insensitive.

## Key takeaways
- Gossip periodically exchanges state with random peers, avoiding a central dissemination server.
- Early spread resembles doubling; repeated contacts with informed peers create a slower tail.
- The push fanout-one round estimate is asymptotic, and CRDTs tolerate repeated, reordered state exchange.

## Further reading
- [Rumour-spreading models and bounds (Doerr, Friedrich and Sauerwald)](https://hpi.de/friedrich/docs/publications/2008/SODA_a.pdf)
- [Gossip protocol (Wikipedia)](https://en.wikipedia.org/wiki/Gossip_protocol)
- [HashiCorp memberlist (SWIM implementation)](https://github.com/hashicorp/memberlist)
