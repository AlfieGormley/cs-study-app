---
id: hash-function-flooding
title: Hash flooding and runtime randomisation
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: When a client chooses keys, collisions become a security and latency concern.
---

When an untrusted client chooses the keys, collisions stop being bad luck and become an attack. This lesson shows how such attacks work and how language runtimes defend against them.

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

**SipHash** (Aumasson and Bernstein, 2012) is a fast keyed function designed for exactly this job: it mixes a secret 128-bit key into every hash, so without that key an attacker should not be able to predict which inputs collide. Python switched to it for `str` and `bytes` in 3.4 (PEP 456, using SipHash-2-4), and from 3.11 common CPython builds default to the slightly faster SipHash-1-3; `sys.hash_info.algorithm` shows what your build uses. Rust's standard `HashMap` currently defaults to SipHash-1-3 too, though its documentation says that may change.

> [!analogy] Real-world analogy: a sorting office with a public rule
> A sorting office puts each parcel in a bin chosen by a published rule based on the address. A prankster who knows the rule can address ten thousand parcels so they all land in one bin, and that bin's clerk grinds to a halt. If the office changes to a secret rule each morning, the prankster can no longer aim.
>
> **How it maps:** the published rule is a fixed public hash such as Java's `String.hashCode`, the overloaded bin is one long chain, and the secret daily rule is a keyed hash like SipHash with a per-process random key.
>
> **Where it stops:** the secret only helps while it stays secret and the function resists analysis. It does nothing about a prankster who simply sends a huge number of parcels, so size limits are still needed, and some keys (such as Python integers) are not randomised at all.

> [!note] Consequences of randomisation
> In Python, `hash("abc")` differs between runs unless you set the `PYTHONHASHSEED` environment variable. Never store `hash()` results in files or send them between processes.

Integers are not randomised. On common 64-bit CPython builds, a non-negative integer hashes to its remainder after dividing by the prime 2⁶¹ − 1 (`sys.hash_info.modulus`), and a negative integer to minus the hash of its magnitude. So small integers hash to themselves, and 2⁶¹ hashes to 1. One special case: CPython never returns −1 as a hash, because −1 signals an error inside the interpreter, so `hash(-1) == -2` and `hash(-1) == hash(-2)`. Hash randomisation therefore does nothing for integer keys an attacker controls; other defences, such as limits on input size, still matter.

## Key takeaways
- Public deterministic hashes can let attackers construct expensive collision chains.
- Keyed hashing and per-process randomisation make predicting collisions harder.
- Python integer hashes remain deterministic, and built-in hash results are unsuitable for persisted placement.

## Further reading
- [Denial of Service via Algorithmic Complexity Attacks (Crosby and Wallach, USENIX Security 2003)](https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf)
- [PEP 456: Secure and interchangeable hash algorithm](https://peps.python.org/pep-0456/)
