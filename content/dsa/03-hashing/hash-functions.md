---
id: hash-functions
title: Hash functions
level: intermediate
minutes: 11
summary: What makes a good hash function, the division and multiplication methods, polynomial string hashing, universal hashing, and how hash flooding attacks forced languages to randomise their hashes.
---

A hash table is only as good as its hash function. Feed it keys that the function spreads evenly and every bucket holds about one key. Feed it keys that the function clumps together and the table turns into a slow list.

This lesson covers what "good" means, the classic ways to build a hash, and how languages responded differently to hash-flooding attacks after 2011.

## What a table hash needs

A hash function maps a key of any size to a fixed-size integer. For a hash table it must be:

1. **Deterministic.** The same key always gives the same hash, at least within one run of the program.
2. **Consistent with equality.** If `a == b`, then `hash(a) == hash(b)`.
3. **Uniform.** Keys spread evenly over the output range, *including* the patterned keys real programs produce: sequential IDs, multiples of 1,000, strings sharing a long prefix.
4. **Fast.** It runs on every lookup, so a few nanoseconds matters.

A good hash also has the **avalanche** property: flipping one input bit flips about half the output bits. That stops similar keys (`user1`, `user2`) landing in nearby slots.

Table hashes are not cryptographic hashes. SHA-256 is designed to make finding two inputs with the same output computationally infeasible, and pays for that in speed. A table only needs a good spread, so it uses fast non-cryptographic functions such as MurmurHash, xxHash or wyhash, or a keyed function such as SipHash when attackers control the keys (see below).

## From hash to bucket: the division method

The simplest way to turn an integer key k into one of m buckets is:

```
h(k) = k mod m
```

It is fast, but the choice of m matters enormously. Take keys that are all multiples of 8 (common for memory addresses and aligned sizes):

```
keys:      8  16  24  32  40  48  56  64
mod 16:    8   0   8   0   8   0   8   0
mod 13:    8   3  11   6   1   9   4  12
```

With m = 16, the keys use only 2 of 16 buckets. With m = 13, they spread over 8 different buckets. When m is a power of two, `k mod m` just keeps the low bits of k, so any pattern in the low bits goes straight into the bucket index. The textbook advice is to choose m as a **prime not close to a power of two**.

## The multiplication method

Primes are awkward: the table cannot double neatly, and a variable divisor may require division; compilers can optimize division by known constants. The **multiplication method** lets m be a power of two:

```
h(k) = floor(m * frac(k * A))
```

Here `frac` takes the fractional part and A is a constant between 0 and 1. Knuth suggests A ≈ (√5 − 1)/2 ≈ 0.618, the golden ratio's fractional part.

In integer arithmetic this becomes **Fibonacci hashing**: multiply by a large odd constant and keep the *top* bits.

```python
def fib_hash(k, p):
    if not 0 <= p <= 32:
        raise ValueError("p out of range")
    # 2**32 / golden ratio
    A = 2654435769
    return ((k * A) % 2**32) >> (32 - p)
```

For a table of 2⁴ = 16 buckets, the multiples of 8 above map to 15, 14, 13, 12, 11, 10, 9, 8: all different. This fixed 32-bit mapping improves this example; it is not a universal collision or avalanche guarantee. Inputs differing by 2**32 collide because the product is reduced modulo 2**32.

## Hashing strings: polynomial hashes

A string is a sequence of characters c₀, c₁, …, cₙ₋₁. A naive hash adds the character codes, but then every anagram collides: `"listen"` and `"silent"` both sum to 655.

A **polynomial hash** weights each position by a power of a base p:

```
h(s) = c0*p^(n-1) + c1*p^(n-2)
       + ... + c(n-1)     (mod M)
```

Computed with Horner's rule, it needs one multiply and one add per character:

```python
def poly_hash(s, p=31, M=10**9 + 9):
    h = 0
    for ch in s:
        h = (h * p + ord(ch)) % M
    return h

poly_hash("abc")
# 97*31^2 + 98*31 + 99 = 96354
```

Java String.hashCode uses base 31 over UTF-16 code units, with signed 32-bit overflow. Python ord iterates Unicode code points, so the code above differs for supplementary characters even with M = 2**32.

Polynomial hashes also **roll**: you can slide a fixed-length window along a string, removing the leftmost character and adding a new one in O(1). That is the idea behind the Rabin–Karp substring search.

> [!warning] Small moduli collide sooner than you think
> Under an independent uniform-hash model for n distinct strings mapped into M values, gives a collision with probability about 1 − e^(−n²/2M). With M ≈ 10⁹ and n = 100,000 strings, that is about 99%. If you compare strings by hash alone, use a 64-bit modulus or two independent hashes, and confirm matches with a real comparison.

## Universal hashing

Any *fixed* hash function has a bad input. There are infinitely many keys and only m buckets, so some m-way pile of keys all share a bucket. This proves colliding inputs exist; it does not prove they can be found efficiently.

**Universal hashing** defends against this by choosing the function at random from a family when the table is created. A family H is universal if, for any two distinct keys x and y:

```
Pr[ h(x) = h(y) ] <= 1/m
```

over the random choice of h. For a fixed key set chosen independently of the random function, pairwise collision bounds give expected short chains at bounded load.

The classic Carter–Wegman family, for integer keys smaller than a prime p:

```
h(k) = ((a*k + b) mod p) mod m

a picked at random in 1..p-1
b picked at random in 0..p-1
```

The expectation is over your random choice, not over the keys, so it covers a fixed adversarial key set chosen before the random function. Adaptive queries need a separate adversary analysis; keeping a and b secret alone is not that proof.

## Hash flooding attacks

In 2003, Crosby and Wallach showed that you could slow a server to a crawl by sending keys that all collide in its hash table: an **algorithmic complexity attack**. Inserting n colliding keys costs O(n²).

In December 2011, at the 28C3 conference, Alexander Klink and Julian Wälde showed it working against PHP, Java, Python, Ruby and ASP.NET web stacks. Web frameworks parse POST parameters into a hash table automatically, so a single request could carry tens of thousands of colliding parameter names.

Java's string hash made colliding keys trivial to generate:

```
"Aa".hashCode() == 2112
"BB".hashCode() == 2112
```

Any string built from these two blocks collides with every other one of the same length: `"AaAa"`, `"AaBB"`, `"BBAa"` and `"BBBB"` all hash to 2,031,744. Thirty blocks gives 2³⁰ (about a billion) colliding keys.

Languages responded in several ways:

| Defence | Example |
|---|---|
| Random seed per process | Python 3.3+, Ruby, Perl |
| Keyed hash function | SipHash: Python, Rust |
| Cap request parameters | PHP `max_input_vars` |
| Tree-shaped buckets | Java 8 `HashMap` |

**SipHash** (Aumasson and Bernstein, 2012) is a fast keyed function designed for exactly this job: without the secret 128-bit key, predicting collisions without the secret key is intended to be computationally difficult. Python switched to it for `str` and `bytes` in 3.4 (PEP 456), and common CPython builds default to SipHash-1-3 from 3.11; inspect sys.hash_info.algorithm for the actual build. Rust's default `HashMap` hasher is also SipHash-1-3.

> [!note] Consequences of randomisation
> In Python, `hash("abc")` differs between runs unless you set `PYTHONHASHSEED`. Never store `hash()` results in files or send them between processes. Integers are not randomised: for an integer n, let P = sys.hash_info.modulus (commonly 2**61 - 1 on 64-bit builds). Compute abs(n) % P, negate for n < 0, then replace -1 with -2. For example hash(-1) == -2.

## Hashing in distributed systems

Hashing also decides which server stores a key in a sharded cache or database. The naive `hash(key) mod N` can move many keys when N changes; doubling N moves about half under uniform hashing, while changing N to N+1 moves about N/(N+1), which is why distributed systems use **consistent hashing**. That is covered in the System Design subject.

## Key takeaways
- A table hash must be deterministic, consistent with equality, uniform on real (patterned) data, and fast; it does not need to be cryptographic.
- `k mod m` leaks low-bit patterns when m is a power of two; use a prime m, or multiply by a constant and take the high bits (Fibonacci hashing).
- Polynomial hashing weights characters by position, so anagrams need not collide, though collisions remain; rolling updates use O(1) fixed-width arithmetic operations per shift.
- Universal hashing gives expected collision bounds for key sets independent of the random function.
- Hash flooding sends colliding keys to make inserts O(n²); keyed, randomised hashes like SipHash are the standard defence.

## Further reading
- [Hash function — Wikipedia](https://en.wikipedia.org/wiki/Hash_function)
- [Universal hashing — Wikipedia](https://en.wikipedia.org/wiki/Universal_hashing)
- [String hashing — cp-algorithms](https://cp-algorithms.com/string/string-hashing.html)
- [Denial of Service via Algorithmic Complexity Attacks (Crosby and Wallach, USENIX Security 2003)](https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf)
- [PEP 456: Secure and interchangeable hash algorithm](https://peps.python.org/pep-0456/)
- [SipHash — Wikipedia](https://en.wikipedia.org/wiki/SipHash)
