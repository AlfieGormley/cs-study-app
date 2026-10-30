---
id: cache-redis-hash-slot-routing
title: Route and migrate Redis Cluster hash slots
level: advanced
minutes: 3
summary: Use hash tags for multi-key commands and distinguish permanent MOVED redirects from temporary ASK redirects.
sourceLesson: cache-distributed
---

Redis Cluster keeps a fixed slot space and assigns slots to primaries. Clients track ownership while keys migrate, rather than changing the key-to-slot formula when nodes are added.

### Redis Cluster: hash slots

Redis Cluster uses a fixed set of **16,384 hash slots**. Each key's slot comes from a checksum of the key (or of its hash tag, below), and the slot number never depends on how many nodes there are:

```formula reference
slot = CRC16(key) mod 16384
where
slot: the hash slot number, from 0 to 16,383
CRC16: a 16-bit cyclic redundancy check, a fast checksum function that turns the key into a number from 0 to 65,535; Redis uses the XMODEM variant
key: the cache key, or only the part inside {} when the key contains a hash tag
mod: modulo, the remainder after whole-number division; written % in code
16384: the fixed number of slots, 2 to the power 14
In words: checksum the key and take the remainder after dividing by 16,384 to get its slot. Adding nodes changes which node owns a slot, never which slot a key is in.
```

Each primary owns a set of slots. Adding a node means **migrating some slots** to it, key by key, while the cluster keeps serving. Clients cache the slot map and send each command straight to the right node.

- If a client uses an out-of-date map, the node replies `MOVED <slot> <host:port>`: the slot now lives elsewhere *permanently*, so the client updates its map.
- While a slot is mid-migration, a key that has already moved gets an `ASK` redirect: the client retries that one command on the target node (preceded by `ASKING`) but does *not* update its map, because the migration hasn't finished.

A fixed slot count is what makes this cheap. Moving a node's share means reassigning a few thousand slot numbers, not recomputing a ring for every key.

Multi-key operations (`MGET`, transactions, Lua) only work if all keys are in the same slot. **Hash tags** force that: only the part inside `{}` is hashed, so `{user:42}:profile` and `{user:42}:cart` share a slot.

> [!warning] Hash tags create hot slots
> Putting too much under one tag (`{global}:...`) piles all of it on a single node, recreating the bottleneck you sharded to escape.

## Key takeaways
- Redis Cluster hashes keys into 16,384 slots; ownership changes by migrating slots and their keys.
- MOVED updates a client’s ownership map; ASK redirects one command during migration and requires ASKING.
- Hash tags place related keys together for multi-key operations, but a large tag can concentrate load on one shard.

## Further reading
- [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
