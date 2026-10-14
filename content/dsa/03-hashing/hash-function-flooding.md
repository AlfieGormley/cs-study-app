---
id: hash-function-flooding
title: Hash flooding and runtime randomisation
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: When a client chooses keys, collisions become a security and latency concern.
---

When a client chooses keys, collisions become a security and latency concern. A public deterministic table hash offers different protection from a keyed hash or a randomly sampled universal family.

## Hash flooding attacks

In 2003, Crosby and Wallach showed that you could slow a server to a crawl by sending keys that all collide in its hash table: an **algorithmic complexity attack**. Inserting n colliding keys costs O(n²), because each new key is compared with every key already in its chain: 50,000 colliding keys need about 1.25 billion comparisons.

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
> In Python, `hash("abc")` differs between runs unless you set the `PYTHONHASHSEED` environment variable. Never store `hash()` results in files or send them between processes.

Integers are not randomised. CPython hashes an integer by taking its remainder modulo a fixed prime, read from `sys.hash_info.modulus`:

```formula
hash(n) = n mod P          (n ≥ 0)
hash(n) = −(|n| mod P)     (n < 0)
P = 2^61 − 1
hash(2^61) = 2^61 mod P = 1
where
hash(n): the value Python's built-in hash() returns for the integer n
n: the integer being hashed
P: the prime 2^61 − 1 = 2,305,843,009,213,693,951 on common 64-bit builds
mod: "modulo", the remainder after whole-number division
|n|: the absolute value of n, its size without the sign; |−5| = 5
≥: "is greater than or equal to"
<: "is less than"
^: "to the power of"
In words: a non-negative integer hashes to its remainder after dividing by a huge fixed prime, and a negative integer to minus the remainder of its size; so small integers hash to themselves, and 2^61 hashes to 1.
```

One special case: the result −1 is replaced by −2, because −1 signals an error inside CPython. So `hash(-1) == -2`, and `hash(-1) == hash(-2)`.

## Key takeaways
- Public deterministic hashes can let attackers construct expensive collision chains.
- Keyed hashing and per-process randomisation make predicting collisions harder.
- Python integer hashes remain deterministic, and built-in hash results are unsuitable for persisted placement.

## Further reading
- [Denial of Service via Algorithmic Complexity Attacks (Crosby and Wallach, USENIX Security 2003)](https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf)
- [PEP 456: Secure and interchangeable hash algorithm](https://peps.python.org/pep-0456/)
