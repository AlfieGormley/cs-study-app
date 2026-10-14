---
id: hash-prob-bloom-membership
title: Bloom filters: negative proof and maybe results
level: advanced
minutes: 3
sourceLesson: hash-probabilistic
summary: A Bloom filter is a prefilter, not a replacement for authoritative membership.
---

A Bloom filter is a prefilter, not a replacement for authoritative membership. The append-only contract is what makes a negative answer conclusive for the represented snapshot.

An exact hash set of a billion 20-byte keys needs tens of gigabytes. Often you do not need an exact answer. "Is this key *possibly* on disk?", "roughly how often has this IP appeared?" and "about how many unique visitors today?" can be answered in kilobytes or megabytes if you accept a small, known error.

The three structures in this part of the module rely on the same idea: a good hash function makes its output look random, so you can reason about collisions with probability, and then size the structure to make errors as rare as you like.

| Structure | Answers | Error |
|---|---|---|
| Bloom filter | "is x in the set?" | false positives only |
| Count-Min Sketch | "how many times x?" | overestimates with nonnegative updates and no overflow |
| HyperLogLog | "how many distinct?" | ± a few % |



## Bloom filters

A **Bloom filter** (Burton Bloom, 1970) is a bit array of m bits, all 0, plus k hash functions that each map an item to one of the m positions.

- **Add x**: run x through all k hash functions and set each of the k bits they pick to 1.
- **Query x**: if *any* of those k bits is 0, x was definitely never added. If all are 1, x was *possibly* added. Its probability of membership also depends on how often queried items are actually members.

```
m = 16, k = 3
add "cat": bits 2, 7, 11
add "dog": bits 4, 7, 13

idx  0123456789012345
     0010100100010100

query "eel": bits 2, 4, 13 -> all 1
             -> "maybe" (false positive)
query "fox": bits 3, 7, 11 -> bit 3 is 0
             -> "definitely not"
```

"eel" was never added, but other items happened to set all of its bits. That is a **false positive**. There are never **false negatives**: an added item's bits stay set, because nothing ever clears a bit.

```python
from hashlib import sha256

class Bloom:
    def __init__(self, m, k):
        if type(m) is not int or m <= 0:
            raise ValueError("positive m")
        if type(k) is not int or k <= 0:
            raise ValueError("positive k")
        self.m, self.k = m, k
        # 1 bool per bit (real ones pack)
        self.bits = [False] * m

    def _idx(self, item):
        d = sha256(item.encode()).digest()
        h1 = int.from_bytes(d[:8])
        h2 = int.from_bytes(d[8:16]) | 1
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item):
        for j in self._idx(item):
            # Shared bits are never cleared.
            self.bits[j] = True

    def __contains__(self, item):
        return all(self.bits[j]
                   for j in self._idx(item))
```

Computing k separate hashes would be slow. The `h1 + i*h2` trick, due to Kirsch and Mitzenmacher, derives all k positions from two hashes with the same asymptotic false-positive probability under the paper's model; this does not promise identical finite-filter accuracy. The odd step is coprime to power-of-two m, but not to every composite m.

> [!note] Evidence gap
> The previously claimed measured 0.84% rate is omitted: no benchmark dataset, query sample or reproducible measurement accompanied it. The formulas below are modelled estimates, not measurements of this implementation.

## Key takeaways
- An append-only filter has no false negatives for its represented snapshot.
- All queried bits set means maybe, requiring an authoritative check when correctness demands it.
- The two-hash implementation illustrates positions without certifying finite-filter error.

## Further reading
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Bloom filter — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
- [Less hashing, same performance](https://www.eecs.harvard.edu/~michaelm/postscripts/rsa2008.pdf)
