---
id: rel-th-enumerate-keys
title: Finding every candidate key
level: intermediate
minutes: 4
sourceLesson: rel-th-functional-deps
summary: Finding every candidate key with two pruning rules, and why stopping at the first key misleads normal-form tests.
---

## Finding candidate keys

A **candidate key** is a superkey with no unnecessary attributes: it determines every attribute, and no smaller part of it does.

```formula reference
X⁺ = R
X' ⊂ X gives X'⁺ ≠ R
where
X: the candidate key being tested
X⁺: the attribute closure of X
R: the set of all attributes of the relation
X': any set made by removing at least one attribute from X
⊂: is a proper subset of: contained in X but not equal to it
X'⁺: the attribute closure of X'
≠: is not equal to
In words: a candidate key determines every attribute of the relation, and removing any of its attributes breaks that.
```

Searching every subset is exponential, but two observations prune it hard:

- An attribute that **never appears on any right-hand side** cannot be derived, so it must be in **every** key.
- An attribute that appears **only on right-hand sides**, and in no determinant, is in **no** candidate key: starting with it cannot help derive anything else, so a superkey containing it can derive it from the other attributes. This assumes the stated FDs are the complete constraint basis being analysed.

> [!example] One key
> Use the five-attribute closure example from the preceding unit: A fixes B, B fixes C, and C together with D fixes E. A and D cannot be derived, so every key includes both. Their attribute closure reaches all five attributes; therefore that pair is the only candidate key.

> [!example] Several keys
> In a four-attribute example, A and B together fix C, C fixes D, and D fixes A. B cannot be derived and therefore belongs to every key. B alone reaches only itself; adding any one of A, C or D reaches the whole heading: A with B gives C and then D; B with C gives D and then A; B with D gives A and then C.
>
> The candidate keys are B with A, B with C, and B with D. Every one of the four attributes therefore belongs to some candidate key: each is a **prime attribute**, a fact the 3NF test cares about.

A relation with n attributes can have exponentially many candidate keys. For schemas specified by an FD basis, Lucchesi and Osborn showed that deciding whether a given attribute is prime is NP-complete. Exhaustive enumeration can be practical for a small schema; larger ones may need pruning. This explains why identifying every prime attribute for the 3NF test can be harder than computing one attribute closure.

“Minimal” means minimal under set inclusion, not smallest cardinality among keys. There can be candidate keys of different sizes. When checking minimality of a superkey, it suffices to remove each member in turn: if any proper subset were a superkey, some single-member removal would also be one. Do not stop after finding the first candidate key; prime attributes depend on the union of all of them.

## Key takeaways

- Every key must include attributes that cannot be derived from right sides.
- Check every candidate for inclusion minimality; all candidate keys contribute prime attributes.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Candidate key (Wikipedia)](https://en.wikipedia.org/wiki/Candidate_key)
