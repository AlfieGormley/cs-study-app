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

The simplest way to turn an integer key into one of m buckets is to divide by m and keep the remainder:

```formula
h(k) = k mod m
h(40) = 40 mod 13 = 1
where
h(k): the bucket index the hash gives key k, a whole number from 0 to m − 1
k: the integer key being stored, here 40
m: the number of buckets in the table, here 13
mod: "modulo", the remainder after whole-number division; 40 mod 13 = 1 because 40 = 3 × 13 + 1
In words: divide the key by the number of buckets and use the remainder as the bucket number; key 40 in a 13-bucket table goes to bucket 1.
```

It is fast, but the choice of m matters enormously. Take keys that are all multiples of 8 (common for memory addresses and aligned sizes):

```
keys:      8  16  24  32  40  48  56  64
mod 16:    8   0   8   0   8   0   8   0
mod 13:    8   3  11   6   1   9   4  12
```

With m = 16, the keys use only 2 of 16 buckets. With m = 13, they spread over 8 different buckets. When m is a power of two (2, 4, 8, 16, …), k mod m just keeps the low bits of k: 40 is 101000 in binary, and 40 mod 16 = 8 is its last four bits, 1000. So any pattern in the low bits goes straight into the bucket index. The textbook advice is to choose m as a **prime not close to a power of two**.

## The multiplication method

Primes are awkward: the table cannot double neatly, and a variable divisor may require division; compilers can optimise division by known constants. The **multiplication method** lets m be a power of two. Multiply the key by a constant, keep only the part after the decimal point, and scale that up to the table size:

```formula
h(k) = floor(m × frac(k × A))
A = (√(5) − 1) / 2 ≈ 0.618
h(8) = floor(16 × frac(8 × 0.618034))
h(8) = floor(16 × frac(4.944272))
h(8) = floor(16 × 0.944272)
h(8) = floor(15.108) = 15
where
h(k): the bucket index for key k, from 0 to m − 1
k: the integer key, here 8
m: the number of buckets, here 16 (any size works, including powers of two)
A: a constant between 0 and 1; Knuth suggests (√5 − 1)/2 ≈ 0.618, the fractional part of the golden ratio
frac: "fractional part", what is left after removing the whole-number part; frac(4.944) = 0.944
floor: round down to the nearest whole number; floor(15.108) = 15
√: square root; √5 ≈ 2.236
≈: approximately equal to (the value is rounded)
In words: multiply the key by about 0.618, throw away the whole-number part, and scale the leftover fraction (between 0 and 1) up to a bucket number; key 8 lands in bucket 15 of 16.
```

Because every key's fraction is scrambled by the multiplication, the size of the table no longer has to be prime. The method still assumes keys are integers; other keys (strings, tuples) are first turned into integers.

In integer arithmetic this becomes **Fibonacci hashing**: multiply by a large odd constant, keep the low 32 bits of the product, and use the *top* few of those bits as the bucket index (4 bits for a 16-bucket table):

```formula
h(k) = floor((k × A mod 2^32) / 2^(32 − p))
h(8) = floor(4055616968 / 2^28)
h(8) = floor(15.1) = 15
where
h(k): the bucket index for key k, from 0 to 2^p − 1
k: the integer key, here 8
A: the constant 2,654,435,769, which is 2^32 divided by the golden ratio (about 1.618), rounded to an odd number
mod: "modulo", the remainder after division; mod 2^32 keeps the low 32 bits, as a 32-bit unsigned multiply does automatically
p: the number of index bits, so the table has 2^p buckets; here p = 4, giving 16 buckets
floor: round down to a whole number; dividing by 2^(32 − p) and rounding down keeps the top p bits
^: "to the power of"; 2^32 = 4,294,967,296
In words: multiply the key by a fixed odd constant, keep 32 bits of the result, and use its highest p bits as the bucket; key 8 gives bucket 15 of 16, matching the decimal version above.
```

The same calculation in Python, where `%` is mod and `>>` shifts bits right (dividing by a power of two and rounding down):

```python
def fib_hash(k, p):
    if not 0 <= p <= 32:
        raise ValueError("p out of range")
    # 2**32 / golden ratio
    A = 2654435769
    return ((k * A) % 2**32) >> (32 - p)
```

For a table of 2⁴ = 16 buckets, the multiples of 8 above map to 15, 14, 13, 12, 11, 10, 9, 8: all different. This fixed 32-bit mapping improves this example; it is not a universal collision or avalanche guarantee. Inputs differing by 2³² (about 4.3 billion) collide because the product is reduced modulo 2³².

## Hashing strings: polynomial hashes

A string is a sequence of characters, and each character has a numeric code (`a` is 97 in ASCII and Unicode). A naive hash adds the character codes, but then every anagram collides: `"listen"` and `"silent"` both sum to 655.

A **polynomial hash** fixes this by weighting each position by a different power of a base, so the same letters in a different order give a different total:

```formula
h(s) = (c_0 × p^(n−1) + c_1 × p^(n−2)
        + … + c_{n−1}) mod M
h("abc") = 97 × 31^2 + 98 × 31 + 99
h("abc") = 93217 + 3038 + 99 = 96354
where
h(s): the hash of string s, a whole number from 0 to M − 1
s: the string being hashed, here "abc"
n: the number of characters in s, here 3
c_0: the numeric code of the first character (a = 97)
c_1: the numeric code of the second character (b = 98)
c_{n−1}: the code of the last character (c = 99), which gets weight 1
p: the base, a fixed whole number; here 31, a small prime commonly used for text
M: the modulus, a large prime such as 1,000,000,009 (10⁹ + 9) that keeps the result a manageable size
mod: "modulo", the remainder after dividing by M
…: the terms in between follow the same pattern
^: "to the power of"; 31^2 = 961
In words: multiply each character's code by the base raised to a power that falls by one per position, add the results and keep the remainder after dividing by M; "abc" gives 96,354, while "cab" gives 98,244.
```

Because the first character is multiplied by the biggest power, swapping letters changes the total. Collisions can still happen (the remainder after dividing by M has only M possible values), but they no longer follow simple patterns such as anagrams.

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

Java's `String.hashCode` uses base 31 over UTF-16 code units, with signed 32-bit overflow instead of a prime modulus. Python's `ord` gives Unicode code points, so the code above differs from Java for supplementary characters (such as emoji) even with M = 2³².

Polynomial hashes also **roll**: you can slide a fixed-length window along a string, removing the leftmost character and adding a new one in O(1), a constant amount of work however long the window is:

```formula
h_new = (h_old − c_out × p^(n−1)) × p
        + c_in
h_new = (96354 − 97 × 961) × 31 + 100
h_new = 3137 × 31 + 100 = 97347
where
h_new: the hash of the window after sliding one place right, here "bcd"
h_old: the hash of the window before sliding, here h("abc") = 96,354
c_out: the code of the character leaving on the left, here a = 97
c_in: the code of the character entering on the right, here d = 100
p: the base, here 31
n: the window length in characters, here 3, so p^(n−1) = 31^2 = 961
^: "to the power of"
In words: subtract the leaving character's contribution, multiply everything by the base to shift each remaining character up one power, then add the new character with weight 1; "abc" rolls to "bcd" with hash 97,347.
```

With a modulus M, every step is also reduced mod M (adding M first if the subtraction went negative). That is the idea behind the Rabin–Karp substring search, which compares a pattern's hash with every window of a text in expected linear time.

> [!warning] Small moduli collide sooner than you think
> With a 10⁹-sized modulus, 100,000 strings almost certainly contain a collision. If you compare strings by hash alone, use a 64-bit modulus or two independent hashes, and confirm matches with a real comparison.

The estimate comes from the **birthday paradox**: the number of *pairs* of strings grows with the square of the number of strings, so collisions appear long before the hash values run out. Assuming each string's hash behaves like an independent, uniformly random value:

```formula
P ≈ 1 − e^(−n^2 / (2 × M))
P ≈ 1 − e^(−100000^2 / (2 × 10^9))
P ≈ 1 − e^(−5) ≈ 1 − 0.0067 ≈ 0.993
where
P: the probability that at least two of the strings share a hash, from 0 (never) to 1 (certain)
n: the number of distinct strings hashed, here 100,000
M: the number of possible hash values (the modulus), here about 10⁹
e: Euler's number, about 2.718, the base of natural logarithms; e^(−5) ≈ 0.0067
^: "to the power of"
≈: approximately equal to
In words: with 100,000 strings and about a billion possible hashes, the chance of at least one shared hash is about 99%; the chance reaches about 50% once n is a little more than the square root of M.
```

The approximation is good when n is much smaller than M. Real hashes are not perfectly random, and patterned inputs can do worse.

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
h(k) = ((a × k + b) mod p) mod m
h(8) = ((3 × 8 + 4) mod 17) mod 6
h(8) = (28 mod 17) mod 6 = 11 mod 6 = 5
where
h(k): the bucket index for key k, from 0 to m − 1
k: the integer key, smaller than p; here 8
a: a multiplier picked at random from 1 to p − 1 when the table is created; here 3
b: an offset picked at random from 0 to p − 1; here 4
p: a prime number larger than every possible key; here 17
m: the number of buckets; here 6
mod: "modulo", the remainder after whole-number division; 28 mod 17 = 11
In words: multiply the key by a random number, add another random number, take the remainder by a prime, then the remainder by the table size; with a = 3 and b = 4, key 8 lands in bucket 5.
```

Each choice of a and b is a different hash function, so the family has (p − 1) × p members. The expectation is over your random choice, not over the keys, so it covers a fixed adversarial key set chosen before the random function. Adaptive queries need a separate adversary analysis; keeping a and b secret alone is not that proof.

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

## Hashing in distributed systems

Hashing also decides which server stores a key in a sharded cache or database. The naive rule picks server `hash(key) mod N` out of N servers. It works until N changes, because the remainder changes for most keys:

```formula
F ≈ N / (N + 1)
F ≈ 10 / 11 ≈ 0.91
where
F: the fraction of keys that move to a different server when one server is added, from 0 to 1
N: the number of servers before the change, here 10
≈: approximately equal to (it assumes uniformly spread hashes)
In words: going from 10 to 11 servers with mod-N placement moves about 10 keys in every 11, roughly 91% of the data, even though only one server was added.
```

Doubling N moves about half the keys. Either way a large share of a cache is invalidated at once, which is why distributed systems use **consistent hashing**, which moves only about 1/(N + 1) of the keys. That is covered in the System Design subject.

## Key takeaways
- A table hash must be deterministic, consistent with equality, uniform on real (patterned) data, and fast; it does not need to be cryptographic.
- Taking the key's remainder by a power-of-two table size leaks low-bit patterns into the bucket index; use a prime table size, or multiply by a constant and take the high bits (Fibonacci hashing).
- Polynomial hashing weights characters by position, so anagrams need not collide, though collisions remain; rolling updates use O(1) fixed-width arithmetic operations per shift.
- Universal hashing gives expected collision bounds for key sets independent of the random function.
- Hash flooding sends colliding keys so that inserting n of them costs O(n²); keyed, randomised hashes like SipHash are the standard defence.

## Further reading
- [Hash function — Wikipedia](https://en.wikipedia.org/wiki/Hash_function)
- [Universal hashing — Wikipedia](https://en.wikipedia.org/wiki/Universal_hashing)
- [String hashing — cp-algorithms](https://cp-algorithms.com/string/string-hashing.html)
- [Denial of Service via Algorithmic Complexity Attacks (Crosby and Wallach, USENIX Security 2003)](https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf)
- [PEP 456: Secure and interchangeable hash algorithm](https://peps.python.org/pep-0456/)
- [SipHash — Wikipedia](https://en.wikipedia.org/wiki/SipHash)
