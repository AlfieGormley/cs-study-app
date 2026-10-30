---
id: db-consistent-hash-hot-keys
title: Consistent hashing and hot keys
level: advanced
minutes: 3
summary: Limit membership-change movement, colocate Redis keys and mitigate skew that even hashing cannot remove.
sourceLesson: db-partitioning
---

Membership changes and skew are different placement problems. Consistent hashing reduces remapping, while hot keys still need caching, splitting or another workload-specific response.

## Consistent hashing

Place both nodes and keys on a ring of hash values (say 0 to 2⁶⁴). Each key belongs to the first node clockwise from it.

```
            0
        N1 ●
      /       \
  k3 ·         · k1
    |           |
 N3 ●           ● N2
      \       /
        · k2
  k1 → N2, k2 → N3, k3 → N1
```

When a node joins, it takes over keys only from its clockwise neighbour; when one leaves, its keys move to the next node. Only about one node's share of keys moves: going from 10 to 11 nodes moves about 1 key in 11 (about 9%), against about 91% with plain modulo. That is the minimum any scheme can move while keeping every node's share equal.

Plain consistent hashing gives uneven ranges, and a newly added node only relieves one neighbour. The fix is **virtual nodes**: each physical node owns many small points on the ring (Cassandra historically used 256 per node, now 16 by default with a smarter allocation algorithm). Load evens out, and a new node can take small slices from many existing nodes, rather than necessarily every node.

Used by Amazon Dynamo, Cassandra, Riak, and the client-side sharding in many cache libraries (such as memcached clients using the "ketama" scheme). A related approach used by Redis Cluster is a fixed set of **16,384 hash slots** assigned to nodes.

Redis Cluster only allows a multi-key command (`MGET`, a transaction, a Lua script) when all its keys are in the same slot. **Hash tags** make that possible: only the part inside `{...}` is hashed, so `{user42}:cart` and `{user42}:profile` always share a slot.

## Hot spots and skew

Even with perfect hashing, a single hot *key* lands on one partition. A celebrity with 100 million followers, or a viral product during a sale, can overload it.

Mitigations:

- **Key splitting (salting)**: write to `key#0` … `key#9` (random suffix), creating ten logical keys that can spread load; they are not guaranteed to occupy ten physical partitions. Reads gather across those keys. Only do this for the few known-hot keys.
- **Caching** the hot key's reads in front of the database.
- **Adaptive capacity**: DynamoDB automatically shifts capacity to busy partitions and splits them, even isolating frequently accessed items on their own partitions. A single item still can't exceed one partition's limits (about 3,000 RCU / 1,000 WCU per second).

## Key takeaways
- Virtual nodes spread ring ownership and transfers over several physical nodes.
- Redis hash tags keep related keys in one slot for multi-key commands.
- Salting and caching can relieve hot keys; logical salts do not guarantee distinct physical partitions.

## Further reading
- [www.cs.princeton.edu: chash.pdf](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf)
- [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [docs.aws.amazon.com: burst adaptive capacity](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/burst-adaptive-capacity.html)
