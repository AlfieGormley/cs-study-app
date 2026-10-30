---
id: hash-function-universal
title: Universal hashing and adversary assumptions
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: Picking the hash function at random bounds collisions for any keys chosen independently of that choice, but not for an attacker who adapts to it.
---

Any *fixed* hash function has bad inputs. Universal hashing answers this by choosing the function at random when the table is created, so no particular set of keys is bad in advance.

## Universal hashing

There are infinitely many possible keys and only m buckets (m being the table size), so infinitely many keys share some bucket under any fixed function. That proves colliding inputs exist; it does not prove they are easy to find.

**Universal hashing** picks the function at random from a family (a large set of possible hash functions) when the table is created. A family is universal if, for any two distinct keys you name in advance, a randomly chosen member puts them in the same bucket no more often than a truly random bucket choice would:

```formula essential
Pr[h(x) = h(y)] ≤ 1 / m
where
Pr[…]: "the probability that …", a number from 0 (never) to 1 (always)
h: the hash function, picked at random from the family when the table is created
x: one key
y: a second key, different from x
m: the number of buckets
≤: "is at most"
In words: whichever two different keys you name in advance, the randomly chosen function puts them in the same bucket with probability at most 1 in m. With 1,000 buckets, that is at most 0.1%.
```

The probability is over the random choice of h, not over the keys. That is the whole point: even a fixed, worst-case set of keys gets short chains on average, provided the keys were chosen without knowing which function was picked and the load factor stays bounded.

The classic Carter–Wegman family for integer keys picks two random numbers when the table is created: multiply the key by the first, add the second, take the remainder by a fixed prime larger than any key, then the remainder by the table size. Each pair of random numbers is a different member of the family.

```formula reference
h(k) = ((ak + b) mod p) mod m
where
h(k): the bucket index for key k, from 0 to m − 1
k: a non-negative integer key smaller than p
a: a multiplier picked at random from 1 to p − 1 when the table is created
b: an offset picked at random from 0 to p − 1
p: a fixed prime number larger than every possible key
m: the number of buckets
mod: "modulo", the remainder after whole-number division
In words: multiply by a random number, add another random number, take the remainder by a prime, then by the table size. Changing the two random numbers gives a different function from the same family.
```

> [!analogy] Real-world analogy: a seating plan drawn after the guest list
> A wedding organiser fixes the guest list first, then draws table numbers at random. However awkward the guest list, it is unlikely that any two particular guests end up at the same table more often than chance.
>
> **How it maps:** the guests are the keys, chosen before the draw; the random draw is picking h from the family; "two particular guests at the same table" is the pairwise collision bound.
>
> **Where it stops:** if a guest could see the seating plan and then invite friends to fill their own table, chance no longer applies. That is an attacker who adapts to the outcome, and the universal-hashing guarantee does not cover it.

The guarantee covers a fixed key set chosen before the random function, including a hostile one. An attacker who can watch the table's behaviour and choose later keys accordingly needs a separate analysis; keeping a and b secret is not, on its own, that proof.

## Key takeaways
- The probability is over the random function choice, not the keys.
- Pairwise collision bounds apply to distinct keys chosen independently of the function.
- An attacker who chooses keys after seeing the table's behaviour needs a separate analysis.

## Further reading
- [Universal hashing — Wikipedia](https://en.wikipedia.org/wiki/Universal_hashing)
