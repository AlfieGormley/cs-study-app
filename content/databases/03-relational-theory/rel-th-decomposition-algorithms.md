---
id: rel-th-decomposition-algorithms
title: BCNF decomposition and 3NF synthesis
level: intermediate
minutes: 5
sourceLesson: rel-th-normal-forms
summary: What BCNF decomposition and 3NF synthesis guarantee, and how to choose when they conflict.
---

## The BCNF decomposition algorithm

1. Find a non-trivial dependency, holding within the current table, whose left side is not a superkey of that table.
2. Split the table in two: the left side together with everything it determines (within the table), and the left side together with all the remaining attributes.
3. Repeat on each part until every part is in BCNF.

```formula reference
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
In words: put the offending left side with everything it determines in one part, and the same left side with everything else in the other; the two parts share exactly that left side.
```

Each split shares exactly the offending left side, and that left side determines the whole first part, so by the two-part test every step gives a lossless join.

Take a five-attribute relation where A fixes B, B fixes C, and C together with D fixes E. Its only candidate key is A with D.

1. A fixes B, but A is not a key. Split into the A part (A with what it determines: A, B, C) and the rest (A, D, E).
2. Inside the A, B, C part, B fixes C but B is not a key there (A is). Split into (B, C) and (A, B).
3. The A, D, E part has key A with D, and its only non-trivial rule is that A with D fixes E. It is already in BCNF.

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

All three parts, (B, C), (A, B) and (A, D, E), are in BCNF and the decomposition is lossless-join, but the original rule that C and D together fix E is lost. No part contains C, D and E together, and the rules that hold within the parts (A fixes B, B fixes C, A with D fixes E) cannot derive it: starting from C and D, nothing fires. To enforce that rule now, you would have to check a join.

## The 3NF synthesis algorithm

3NF can always be reached **losslessly while preserving every FD**. The synthesis algorithm builds on Bernstein (1976); the extra key relation in step 3, which guarantees the lossless join, comes from later refinements of his method, notably Biskup, Dayal and Bernstein (1979):

1. Compute a minimal FD cover of the given dependencies.
2. Make one relation for each left side in the cover, containing that left side and everything the cover says it determines.
3. If no relation contains a candidate key of the original relation, add one relation that is just such a key.
4. Drop any relation whose attributes are a subset of another's.

On the same five-attribute example, the three rules are already a minimal cover. One relation per rule gives (A, B), (B, C) and (C, D, E). None of them contains the key A with D, so step 3 adds a fourth relation, (A, D), to tie the parts together.

Result: (A, B), (B, C), (C, D, E) and (A, D). Every original rule lives inside one relation, so each can be enforced by that relation's own key; the key relation makes the decomposition lossless-join; and here each part happens to be in BCNF too. Compare the BCNF result above, which lost the rule that C with D fixes E.

## Choosing between 3NF and BCNF

| | 3NF | BCNF |
|---|---|---|
| Lossless join | always | always |
| FDs preserved | always | not always |
| Redundancy | a little possible | none from FDs |

Check the actual dependencies rather than assuming a frequency of overlapping keys. Many ordinary schemas can reach BCNF while preserving the required FDs; when those goals clash, the choices are:

- Stay in 3NF and accept some redundancy, enforcing the dependencies locally; keys alone may not express every local FD.
- Go to BCNF and enforce the lost FD another way: a trigger or application protocol that checks the joined rule, with locking or a serialisable transaction so two transactions running at the same time cannot both pass the check. PostgreSQL has no general declarative cross-table assertions, and a naive check-then-write can race with another transaction.

## Key takeaways

- BCNF decomposition preserves lossless reconstruction but can lose dependencies.
- 3NF synthesis uses a minimal FD cover and adds a candidate-key relation when needed.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
