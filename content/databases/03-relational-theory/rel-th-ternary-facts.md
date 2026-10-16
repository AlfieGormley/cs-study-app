---
id: rel-th-ternary-facts
title: Preserving three-way facts
level: advanced
minutes: 3
sourceLesson: rel-th-er-modelling
summary: Preserving three-way facts, with explicit examples and the conditions that make the reasoning valid.
---

## Ternary relationships

Some facts involve three entities at once: *supplier S supplies part P to project J*. It is tempting to replace this with three binary relationships, but that loses information.

```
Supplies(S, P, J):
S1 P1 J2
S1 P2 J1
S2 P1 J1
```

Project into the three pairs and join them back:

```formula
SP = π S,P (Supplies)
PJ = π P,J (Supplies)
SJ = π S,J (Supplies)
SP ⋈ PJ ⋈ SJ ⊋ Supplies
where
Supplies: the relation of three-way facts, with attributes S (supplier), P (part) and J (project)
S, P, J: the supplier, part and project attributes
π: projection: keep only the listed attributes, removing duplicate relational tuples
SP, PJ, SJ: the three two-attribute tables a designer might use instead
⋈: natural join: match relational tuples on the attributes they share
⊋: is a proper superset of: contains every relational tuple of the right side and at least one more
In words: rejoining the three pairs gives back all three real rows plus at least one invented one.
```

The join returns four rows: the three real ones and an extra one, `S1 P1 J1`. Each pair in it is true (S1 supplies P1 to someone; P1 goes to J1; S1 supplies J1), but S1 never supplied P1 to J1. Without a business rule guaranteeing reconstruction from the pairs, keep a three-way table with all three foreign keys. The displayed counterexample shows that the proposed join dependency does not hold. Join dependencies are the territory of 5NF; merely having three entities does not establish one, and some specially constrained ternary relationships can be decomposed safely.

## What each pair forgets

The supplier/part projection remembers that S1 supplies P1 somewhere, but forgets the project. The part/project projection remembers that P1 goes to J1 from someone, but forgets the supplier. The supplier/project projection remembers that S1 supplies something to J1, but forgets the part. None of the three remembered pairs says that S1 supplies P1 to J1. Their join nevertheless constructs it because every pair matches.

All original triples survive projection and rejoining: each carries three genuine pairs. The failure is additional triples, so the decomposition is called lossy even though its join has more rows. Information about which combinations were absent has been lost.

Before choosing binary tables, ask whether the business explicitly permits a triple whenever those three pairwise facts hold. If yes, the join dependency may be an intended rule. If no, neither a diagram with three binary lines nor three independent foreign keys can recover the original three-way meaning.

## Key takeaways

- Pairwise projections can forget which triples were actually true.
- Only a justified join dependency permits reconstructing three-way facts from pairs.

## Further reading

- [Chen: The Entity-Relationship Model (1976)](https://openlib.org/home/krichel/courses/lis512/readings/chen76theentity-relationship.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
