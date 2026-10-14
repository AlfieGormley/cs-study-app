---
id: hash-function-universal
title: Universal hashing and adversary assumptions
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: Randomising the choice of hash function gives a probabilistic guarantee for keys chosen independently of that choice.
---

Randomising the choice of hash function gives a probabilistic guarantee for keys chosen independently of that choice. It does not promise that every chosen function has short chains on every input.

## Universal hashing

Any *fixed* hash function has a bad input. There are infinitely many keys and only m buckets (m being the table size), so infinitely many keys share some bucket. This proves colliding inputs exist; it does not prove they can be found efficiently.

**Universal hashing** defends against this by choosing the function at random from a family (a large set of possible hash functions) when the table is created. A family is universal if, for any two distinct keys, a randomly chosen member collides on them no more often than a truly random bucket choice would:

```formula
Pr[h(x) = h(y)] ≤ 1 / m
Pr[h(x) = h(y)] ≤ 1 / 1000 = 0.1%
where
Pr[…]: "the probability that …", a number from 0 (never) to 1 (always)
h: the hash function, picked at random from the family when the table is created
x: one key
y: a second key, different from x
m: the number of buckets, here 1,000
≤: "is at most"
In words: whichever two different keys you name in advance, the randomly chosen function puts them in the same bucket with probability at most 1 in m; with 1,000 buckets, at most 0.1%.
```

The probability is over the random choice of h, not over the keys. For a fixed key set chosen independently of the random function, these pairwise bounds give short chains on average while the load factor stays bounded.

The classic Carter–Wegman family works for integer keys smaller than a chosen prime:

```formula
h(k) = ((a k + b) mod p) mod m
h(8) = ((3 × 8 + 4) mod 17) mod 6
h(8) = (28 mod 17) mod 6 = 11 mod 6 = 5
where
h(k): the bucket index for key k, from 0 to m − 1
k: a nonnegative integer key smaller than p; here 8
a: a multiplier picked at random from 1 to p − 1 when the table is created; here 3
b: an offset picked at random from 0 to p − 1; here 4
p: a prime number larger than every possible key; here 17
m: the number of buckets; here 6
mod: "modulo", the remainder after whole-number division; 28 mod 17 = 11
In words: multiply the key by a random number, add another random number, take the remainder by a prime, then the remainder by the table size; with a = 3 and b = 4, key 8 lands in bucket 5.
```

Each choice of a and b is a different hash function, so the family has the product of the prime and one less than the prime as its member count. The expectation is over your random choice, not over the keys, so it covers a fixed adversarial key set chosen before the random function. Adaptive queries need a separate adversary analysis; keeping a and b secret alone is not that proof.

## Key takeaways
- The probability is over the random function choice, not the keys.
- Pairwise collision bounds apply to distinct keys chosen independently of the function.
- An adaptive adversary requires a separate analysis.

## Further reading
- [Universal hashing — Wikipedia](https://en.wikipedia.org/wiki/Universal_hashing)
