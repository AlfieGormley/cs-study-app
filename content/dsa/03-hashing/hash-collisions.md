---
id: hash-collisions
title: Collision resolution
level: intermediate
minutes: 13
summary: Separate chaining versus open addressing, linear and quadratic probing, double hashing, tombstones for deletion, and how Robin Hood hashing and Swiss tables tame probe lengths.
---

However good the hash function, two keys will eventually want the same bucket. For independent uniform bucket choices, with 23 keys in 365 buckets the chance of at least one collision is already over 50% (the birthday paradox). So the real design question for a hash table is not *whether* collisions happen but *what to do* when they do.

There are two families of answer. **Separate chaining** lets a bucket hold many keys. **Open addressing** keeps one key per slot and, on a collision, looks for another slot in the same array.

## Separate chaining

Each bucket holds a small collection, usually a linked list, of every key that hashed there.

```
idx  bucket
 0   -> [k7]
 1   (empty)
 2   -> [k2] -> [k9] -> [k4]
 3   -> [k5]
```

- **Insert**: hash, then add to that bucket's list (after checking the key is not already there).
- **Look up**: hash, then scan that one list.
- **Delete**: unlink the node. Nothing else in the table is affected.

Under simple uniform hashing and uniformly selected stored keys, with load factor α = n/m, the average chain has α keys. An unsuccessful lookup scans a whole chain (about 1 + α steps counting the bucket itself); a successful one scans about half a chain plus one (around 1 + α/2).

Chaining is simple and degrades gracefully: α can go above 1 and the table still works, just more slowly. Its costs are memory and locality. Every entry is a separate heap node with a `next` pointer, and following pointers means cache misses: often the dominant cost on modern CPUs.

Java's `HashMap`, C++'s `std::unordered_map` and many textbook tables use chaining.

## Open addressing

All keys live directly in the array, one per slot. To insert, you follow a **probe sequence** h(k, 0), h(k, 1), h(k, 2), … until you find an empty slot. A lookup follows the same sequence until it finds the key or hits an empty slot (which proves the key is absent).

Because everything is in one contiguous array, open addressing is compact and cache-friendly. The catch: α must stay below 1, and performance falls off sharply as it approaches 1.

### Linear probing

Try the next slot, then the next:

```
h(k, i) = (h(k) + i) mod m
```

Example: m = 7, h(k) = k mod 7. Insert 10, 17, 24, 3, 5 (home slots 3, 3, 3, 3, 5):

```
slot  0   1   2   3   4   5   6
      5   .   .   10  17  24  3
```

Four keys wanted slot 3 and spilled into 4, 5 and 6. Then 5, whose home was slot 5, found 5 and 6 taken and wrapped round to slot 0. Any key hashing anywhere into slots 3 to 6 now has to walk to the end of this run.

That is **primary clustering**: occupied runs grow, and a longer run is more likely to be hit and so grows faster. For random uniform home positions in the classical insertion model, without arbitrary tombstone churn, the asymptotic expected probe counts are:

| α | Hit | Miss |
|---|---|---|
| 0.50 | 1.5 | 2.5 |
| 0.75 | 2.5 | 8.5 |
| 0.90 | 5.5 | 50.5 |

The formulas are ½(1 + 1/(1−α)) for a successful search and ½(1 + 1/(1−α)²) for an unsuccessful one. Going from 75% full to 90% full makes the modeled probe count about six times larger; this is not a wall-clock benchmark.

Despite clustering, linear probing can perform well at moderate load because nearby probes benefit from locality; measure the implementation and workload.

### Quadratic probing

Jump by growing amounts so runs do not merge so readily:

```
h(k, i) = (h(k) + c1*i + c2*i^2) mod m
```

This removes primary clustering but leaves **secondary clustering**: keys with the same home slot still follow the identical sequence. Quadratic probing also may not visit every slot. For h+i² modulo an odd prime m, the first (m+1)/2 probes are distinct, guaranteeing a free slot when fewer than that many slots are occupied. Arbitrary choices of c1 and c2 do not have this guarantee. A popular variant uses triangular numbers, h + i(i+1)/2, which visits every slot when m is a power of two.

### Double hashing

Use a second hash to choose the step size:

```
h(k, i) = (h1(k) + i * h2(k)) mod m
```

Keys with the same home slot now usually follow different sequences, reducing clustering when the two hashes distribute keys well; keys sharing both hashes still share a sequence. Two rules: h2(k) must never be 0 (or you probe the same slot forever), and it must be coprime with m so the sequence can reach every slot. For prime m, require h2 mod m != 0; for power-of-two m an odd h2 suffices.

Same keys with h2(k) = 5 − (k mod 5):

```
slot  0   1   2   3   4   5   6
      .   5   .   10  24  3   17
```

17 jumps 3 slots to slot 6, and 24 steps 1 slot to slot 4, rather than all queuing behind 10. The price is computing a second hash and losing the cache locality of linear steps.

## Deletion and tombstones

Deletion is where open addressing gets subtle. In the linear-probing table above, suppose you delete 17 by setting slot 4 back to empty. A lookup for 24 starts at slot 3 (10, not a match), moves to slot 4, finds it empty, and concludes 24 is absent. Wrong: 24 sits in slot 5.

The fix is a **tombstone**: a special marker meaning "deleted, keep probing".

- **Lookups** skip over tombstones.
- **Inserts** may reuse the first tombstone they pass, but must still probe on to an empty slot to be sure the key is not already further along.

Here `get` and `delete` are methods of a table class whose _probe(key) yields at most one complete cycle of slot indices in probe order:

```python
EMPTY, TOMB = object(), object()

def get(self, key):
    for i in self._probe(key):
        k = self.keys[i]
        if k is EMPTY:
            raise KeyError(key)
        if k is not TOMB and k == key:
            return self.vals[i]
    raise KeyError(key)

def delete(self, key):
    for i in self._probe(key):
        k = self.keys[i]
        if k is EMPTY:
            raise KeyError(key)
        if k is not TOMB and k == key:
            self.keys[i] = TOMB
            return
    raise KeyError(key)
```

> [!warning] Tombstones pile up
> Tombstones count against the load for lookups, since searches must walk past them, but they hold no data. A table with heavy insert and delete churn can fill with tombstones, making misses slow even though it holds few live keys. Implementations track them and rebuild the table (rehash live keys into a fresh array) when they pass a threshold. In CPython 3.14 ordinary combined dicts, GIL-enabled builds can reuse dummy index slots; dense entry holes are generally compacted on rebuild. Free-threaded builds do not reuse dummy index slots, and popitem can trim the dense entry tail.

With linear probing there is an alternative: **backward-shift deletion**. After emptying a slot, scan forward and move back any key that could legally sit in the gap, until you reach an empty slot. No tombstones, at the cost of more work per delete.

## Robin Hood hashing

Linear probing's average is fine, but its *variance* is the problem: some unlucky keys end up dozens of slots from home. Robin Hood hashing (Celis, Larson and Munro, 1985) evens this out by "taking from the rich and giving to the poor".

The insertion fragment requires a nonempty table with a free slot and a key not already stored; a complete map must handle duplicate updates and grow before exhausting capacity. Each key's **probe distance** is how far it sits from its home slot. While inserting, if the incoming key has travelled further than the resident of the current slot, they swap: the incoming key takes the slot and the displaced, "richer" key carries on probing.

```python
def rh_insert(slots, key, home):
    # slots hold (key, dist) or None
    m = len(slots)
    i, d = home % m, 0
    while True:
        cur = slots[i]
        if cur is None:
            slots[i] = (key, d)
            return
        if cur[1] < d:  # resident richer
            slots[i] = (key, d)
            key, d = cur  # carry it on
        i = (i + 1) % m
        d += 1
```

Insert D (home 2), then A, B and C (all home 0):

```
plain linear    A0  B1  D0  C3
robin hood      A0  B1  C2  D1
               (key + probe distance)
```

C reaches slot 2 having travelled 2; D there has travelled 0, so C takes the slot and D moves on to slot 3. The total distance is the same (4), but the worst case drops from 3 to 2. Robin Hood hashing can reduce probe-distance variance; worst-case lookup remains O(n) under adversarial collisions.

It also speeds up misses. Probing for an absent key, you can stop as soon as you meet a resident whose distance is smaller than your current distance: had your key been present, it would have displaced that resident. Deletion usually uses backward shifting.

Rust's standard `HashMap` used Robin Hood hashing until 2019 (Rust 1.36), when it switched to a Swiss table.

## Modern designs: Swiss tables

Google's **Swiss tables** (Abseil `flat_hash_map`, presented in 2017) are open addressing with a twist. Alongside the slots is an array of one-byte **control bytes**, each holding "empty", "deleted" or 7 bits of the key's hash. On Abseil's SSE path, a lookup loads 16 control bytes and uses SIMD instructions to compare all 16 against the key's 7 bits in a single step, only touching the slots that match. Tables run at up to 7/8 full while lookups stay fast.

Rust (via the `hashbrown` crate) and, since Go 1.24, Go's built-in map use Swiss-table designs; Go uses eight-slot groups, so Swiss-table designs do not all probe 16 slots.

Another option is **cuckoo hashing**, where each key has two possible slots and inserts evict residents to their alternative slot. The classic two-hash, single-slot, no-stash version checks at most two candidate slots; insertion can trigger rehashing. Bucketed or stashed variants have different lookup bounds.

## Choosing between them

| | Chaining | Open addressing |
|---|---|---|
| Load factor | can exceed 1 | must stay below 1 |
| Memory | node + pointer each | one flat array |
| Cache behaviour | pointer chasing | contiguous |
| Delete | trivial | tombstones or shifting |
| Near full | slows gently | slows sharply |

Chaining is the safer general-purpose choice when keys are large or the load is unpredictable, and it lets you swap the chain for a tree (Java 8, next lesson). Open addressing can offer good locality and low overhead at controlled load; actual speed depends on key size, hash cost and workload.

## Key takeaways
- Chaining stores colliding keys in per-bucket lists; it is simple, tolerates α > 1 and makes deletion trivial, but costs pointers and cache misses.
- Open addressing probes for another slot in the same array; linear probing suffers primary clustering, quadratic probing secondary clustering, and double hashing reduces shared probe paths with suitably distributed hashes.
- Linear-probing misses cost about ½(1 + 1/(1−α)²) probes: 2.5 at α = 0.5 but 50.5 at α = 0.9.
- Deleting in open addressing needs tombstones (or backward shifting); otherwise lookups stop early and lose keys.
- Robin Hood hashing swaps keys to equalise probe distances, reducing variance without removing linear worst cases; some Swiss-table implementations compare 16 metadata bytes at once.

## Further reading
- [Open addressing — Wikipedia](https://en.wikipedia.org/wiki/Open_addressing)
- [Linear probing — Wikipedia](https://en.wikipedia.org/wiki/Linear_probing)
- [Double hashing — Wikipedia](https://en.wikipedia.org/wiki/Double_hashing)
- [Hash table: Robin Hood hashing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Robin_Hood_hashing)
- [Swiss tables design notes — Abseil](https://abseil.io/about/design/swisstables)
- [Cuckoo hashing — Wikipedia](https://en.wikipedia.org/wiki/Cuckoo_hashing)
