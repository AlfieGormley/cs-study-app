---
id: adv-rabin-karp-costs
title: Hash candidates, prefix fingerprints and modulo
level: advanced
minutes: 3
summary: Candidate verification adds a cost per matching window, including genuine matches.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

## Candidate verification and substring fingerprints

Equal strings always have equal hashes, but different strings can produce a **hash collision**. A hash match is only a candidate and must be confirmed by comparing characters.

For C candidate windows, the shown all-occurrences implementation costs O(n + m + mC). Here n is text length and m is pattern length. Hashing advances in constant work per slide, but each candidate may create a pattern-length slice and compare it.

Genuine matches also count as candidates. A repetitive text can trigger verification at almost every start even with no collisions. If the pattern is at most half the text length, the resulting worst case can be O(nm). Expected linear claims need assumptions controlling both false positives and genuine matches.

> [!note] Fixed hashes need a threat model
> A fixed public base and modulus do not justify a numeric collision probability for arbitrary inputs. Choosing a prime modulus alone does not make adversarially chosen strings behave like independent random hashes.

## Porting negative remainders

- **Negative modulo**: in C or Java, `(h - x) % M` can be negative. For positive M, Python's `%` returns a non-negative result, which hides this bug until you port the code. For this fixed modulus near one billion, a sufficiently wide integer type can safely add the modulus before reducing again. For arbitrary fixed-width values, the intermediate addition must also avoid overflow:

For example, reducing negative seven with modulus eleven gives negative seven in Java but four in Python. These represent the same remainder class, yet ordinary equality says they differ. In Java, `((a % M) + M) % M` normalises a remainder for positive `M`, provided the intermediate addition fits. Apply the same representation consistently to pattern and window hashes.

## Key takeaways

- Candidate verification adds a cost per matching window, including genuine matches.
- Normalise negative remainders so equivalent hashes compare equal when porting.

## Further reading
- [String hashing — cp-algorithms](https://cp-algorithms.com/string/string-hashing.html)
