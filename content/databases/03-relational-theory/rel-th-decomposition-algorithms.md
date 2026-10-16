---
id: rel-th-decomposition-algorithms
title: BCNF decomposition and 3NF synthesis
level: intermediate
minutes: 5
sourceLesson: rel-th-normal-forms
summary: BCNF decomposition and 3NF synthesis, with explicit examples and the conditions that make the reasoning valid.
---

## The BCNF decomposition algorithm

1. Find a non-trivial dependency whose determinant is not a superkey of the current schema. The card calls that determinant X and the current heading S. Replace the current schema with the two parts shown.
2. Repeat until every relation is in BCNF.

```formula
S_1 = X⁺ ∩ S
S_2 = X ∪ (S − X⁺)
S_1 ∩ S_2 = X
where
S: the relation being split, as a set of attributes
X: the left side of an FD that violates BCNF in S
X⁺: the attribute closure of X under the dependencies projected onto the current schema S; equivalently compute the original attribute closure then intersect with S
∩: intersection: attributes in both
∪: union: attributes in either
−: difference: attributes of S that X does not determine
S_1: X plus everything in S that X determines
S_2: X plus everything else in S
In words: put X with what it determines in one part, and X with the rest in the other.
```

Each split shares exactly X, and X determines the whole first part, so every step gives a lossless join. In the five-attribute example below, A fixes B, B fixes C, and C together with D fixes E. Its only candidate key is the pair A and D:

```formula
A⁺ = {A, B, C}
A⁺ ∩ ABCDE = ABC
A ∪ (ABCDE − A⁺) = ADE
B⁺ ∩ ABC = BC
B ∪ (ABC − B⁺) = AB
where
A, B, C, D, E: the attributes of R; R itself is the set ABCDE
ABCDE, ABC, ADE, BC, AB: sets of attributes written as letters side by side, e.g. ABC = {A, B, C}
A⁺, B⁺: attribute closures under F = {A → B, B → C, CD → E}; B⁺ = {B, C}
{ }: a set
∩, ∪, −: intersection, union and difference of attribute sets
In words: A → B breaks BCNF (A is not a key), so ABCDE splits into ABC and ADE. Inside ABC, B → C breaks it (B is not a key), so ABC splits into BC and AB. ADE only has AD → E, and AD is its key.
```

The same split sequence as a schema sketch, with names grouping attributes:

```diagram
Full heading
  |  split on A
  +-- A B C
  |     |  split on B
  |     +-- B C
  |     +-- A B
  +-- A D E
```


All three are in BCNF and the decomposition is lossless-join, but the original rule that C and D together fix E is lost. The combined projected FDs cannot derive it: starting from C and D adds nothing in the local dependency union, so E is not reached.

## The 3NF synthesis algorithm

3NF can always be reached **losslessly while preserving every FD**. The synthesis algorithm (Bernstein, 1976):

1. Compute a minimal FD cover of F.
2. Make one relation for each left side X, containing X and everything it determines in the cover.
3. If no relation contains a candidate key of R, add one that is just a key.
4. Drop any relation that is a subset of another.

The original three dependencies are already a singleton-right-side minimal FD cover. Use that cover for the same five-attribute example:

```formula
A → B gives R_1 = AB
B → C gives R_2 = BC
CD → E gives R_3 = CDE
{A, D}⁺ = ABCDE gives R_4 = AD
where
A, B, C, D, E: the attributes of R
→: functionally determines
CD: the set {C, D}
R_1, R_2, R_3: one relation per FD of the minimal FD cover
AB, BC, CDE, AD, ABCDE: sets of attributes, letters side by side
{A, D}⁺: the attribute closure of {A, D}; it is everything, so AD is a candidate key
R_4: the extra relation holding just the key, added because AD is in none of R_1 to R_3
In words: one table per dependency, plus a table holding a key to tie them together.
```

Result: AB, BC, CDE, AD. Every FD lives in one relation, the key relation AD makes the decomposition lossless-join, and here each part happens to be in BCNF too.

## Choosing between 3NF and BCNF

| | 3NF | BCNF |
|---|---|---|
| Lossless join | always | always |
| FDs preserved | always | not always |
| Redundancy | a little possible | none from FDs |

Check the actual dependencies rather than assuming a frequency of overlapping keys. Many ordinary schemas can reach BCNF while preserving the required FDs; when those goals clash, the choices are:

- Stay in 3NF and accept some redundancy, enforcing the dependencies locally; keys alone may not express every local FD.
- Go to BCNF and enforce the lost FD another way, such as a trigger, a carefully synchronised trigger or application protocol that checks the joined rule. PostgreSQL ordinary views do not provide general declarative cross-table assertions; a naive check-then-write can race with another transaction.

## Key takeaways

- BCNF decomposition preserves lossless reconstruction but can lose dependencies.
- 3NF synthesis uses a minimal FD cover and adds a candidate-key relation when needed.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
