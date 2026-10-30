---
id: hash-function-bucket-bits
title: Hash quality and bucket reduction
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: A full hash and a bucket index are different things; a power-of-two remainder exposes patterns in a key's low bits.
---

A hash table is only as good as its hash function. Feed it keys that the function spreads evenly and every bucket holds about one key. Feed it keys that the function clumps together and the table turns into a slow list.

There are two steps to watch. The hash function turns a key into a large integer, and a second step reduces that integer to a bucket index. Even a valid hash can perform badly if the reduction preserves patterns in the input.

## What a table hash needs

A hash function maps a key of any size to a fixed-size integer. For a hash table it must be:

1. **Deterministic.** The same key always gives the same hash, at least within one run of the program.
2. **Consistent with equality.** If `a == b`, then `hash(a) == hash(b)`.
3. **Uniform.** Keys spread evenly over the output range, *including* the patterned keys real programs produce: sequential IDs, multiples of 1,000, strings sharing a long prefix.
4. **Fast.** It runs on every lookup, so a few nanoseconds matters.

A good hash also has the **avalanche** property: flipping one input bit flips about half the output bits. That stops similar keys (`user1`, `user2`) landing in nearby slots.

Table hashes are not cryptographic hashes. SHA-256 is designed to make finding two inputs with the same output computationally infeasible, and pays for that in speed. A table only needs a good spread, so it uses fast non-cryptographic functions such as MurmurHash, xxHash or wyhash, or a keyed function such as SipHash when attackers control the keys (Hash flooding and runtime randomisation).



## From hash to bucket: the division method

The simplest way to turn an integer key into one of m buckets is the **division method**: divide by m and keep the remainder (written `k mod m`, or `k % m` in Python). Key 40 in a 13-bucket table goes to bucket 1, because 40 = 3 × 13 + 1.

It is fast, but the choice of m matters enormously. Take keys that are all multiples of 8 (common for memory addresses and aligned sizes):

```
keys:      8  16  24  32  40  48  56  64
mod 16:    8   0   8   0   8   0   8   0
mod 13:    8   3  11   6   1   9   4  12
```

With sixteen buckets, the keys use only 2 of 16 buckets. With thirteen buckets, they spread over 8 different buckets.

Why? When m is a power of two (2, 4, 8, 16, …), the remainder is just the key's lowest binary digits: 40 is 101000 in binary, and its remainder after dividing by 16 is its last four bits, 1000, which is 8. Every multiple of 8 ends in three zero bits, so only one of the four kept bits can vary. Any pattern in the low bits goes straight into the bucket index. The textbook advice for the division method is to choose m as a **prime not close to a power of two**; the next lesson shows how other designs keep fast power-of-two sizes by mixing the bits first.

> [!analogy] Real-world analogy: filing by the last digit
> A clerk files invoices in ten trays by the last digit of the invoice number. That works well until the accounts system starts issuing numbers that always end in 0 or 5: two trays overflow and eight sit empty.
>
> **How it maps:** the trays are buckets, "last digit" is reduction by a power of the number base (keeping the low digits), and the 0-or-5 numbering is a pattern in the keys' low bits, like aligned memory addresses that always end in zero bits.
>
> **Where it stops:** the clerk works in decimal, so the low digits are the last decimal digits; a power-of-two table keeps the last binary digits. Choosing a prime number of trays, or scrambling the number before filing, spreads such patterned keys out.

## Key takeaways
- Hashing must respect equality and remain deterministic for the table’s lifetime.
- Power-of-two remainder selection exposes patterns in low bits.
- A cryptographic collision guarantee is different from useful bucket distribution.

## Further reading
- [Hash function — Wikipedia](https://en.wikipedia.org/wiki/Hash_function)
