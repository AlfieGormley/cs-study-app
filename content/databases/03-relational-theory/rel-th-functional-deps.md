---
id: rel-th-functional-deps
title: Functional dependencies, closure and keys
level: intermediate
minutes: 14
summary: What a functional dependency really claims, Armstrong's axioms, the attribute-closure algorithm, finding every candidate key, and computing a minimal cover.
---

Normalisation, the subject of the next lesson, can sound like a list of rules to memorise. It is not. The normal forms 2NF, 3NF and BCNF are defined using **functional dependencies** (FDs); higher forms also involve multivalued or join dependencies. Once you can reason about FDs, normal forms become mechanical checks.

This lesson gives you the tools: what an FD means, how to derive new FDs from known ones, the closure algorithm, and how to use it to find keys.

## What a functional dependency says

For attribute sets X and Y of a relation R, the FD **X → Y** ("X determines Y") means:

> Any two tuples that agree on X must also agree on Y.

Take a spreadsheet of enrolments that someone has imported as one table:

```
sid  sname  cid  ctitle      grade
 1   Ada    DB   Databases    A
 1   Ada    OS   Op Systems   B
 2   Ben    DB   Databases    C
```

The business rules give these FDs:

- `sid → sname`: a student id identifies one name.
- `cid → ctitle`: a course code identifies one title.
- `{sid, cid} → grade`: one grade per student per course.

An FD is a **constraint on every legal state**, exactly like a key. You get it from the domain, not from the data.

> [!warning] Data can refute an FD, never prove one
> If two rows share a `cid` but have different titles, `cid → ctitle` is false (or the data is dirty). But if today's rows all happen to have unique surnames, that does not make `surname → anything` a rule. Data-profiling tools that "discover" FDs find candidates that a human must confirm.

### Trivial and non-trivial FDs

X → Y is **trivial** if Y ⊆ X, for example `{sid, cid} → sid`. Trivial FDs hold in every relation and tell you nothing. The interesting ones are non-trivial.

### Keys are FDs too

A set K is a **superkey** of R exactly when K → R, that is, K determines every attribute. Here `{sid, cid}` determines sname, ctitle and grade, so it is a superkey, and since neither attribute alone determines everything, it is a candidate key.

## Armstrong's axioms

Given some FDs, which others must also hold? William Armstrong gave three inference rules in 1974. For attribute sets X, Y, Z:

1. **Reflexivity**: if Y ⊆ X then X → Y.
2. **Augmentation**: if X → Y then XZ → YZ.
3. **Transitivity**: if X → Y and Y → Z then X → Z.

(XZ means X ∪ Z.) The rules are **sound** (they never derive a false FD) and **complete** (every FD that logically follows can be derived with them). Three useful rules follow from them:

- **Union**: X → Y and X → Z give X → YZ.
- **Decomposition**: X → YZ gives X → Y and X → Z.
- **Pseudotransitivity**: X → Y and WY → Z give WX → Z.

> [!warning] The left side does not decompose
> X → YZ splits into X → Y and X → Z. But XY → Z does **not** give X → Z. Grade depends on student *and* course together, not on either alone.

The set of all FDs implied by F is written **F⁺**. It can be exponentially large, so in practice you never list it. You compute closures of attribute sets instead.

## The attribute-closure algorithm

The **closure** X⁺ is the set of all attributes that X determines under F. The algorithm is a fixpoint loop:

1. Start with result = X.
2. Find any FD L → R in F with L ⊆ result. Add R to result.
3. Repeat until nothing changes.

```python
def closure(attrs, fds):
    result = set(attrs)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in fds:
            if lhs <= result \
               and not rhs <= result:
                result |= rhs
                changed = True
    return result

F = [({'A'}, {'B'}),
     ({'B'}, {'C'}),
     ({'C', 'D'}, {'E'})]
print(sorted(closure({'A'}, F)))
# ['A', 'B', 'C']
print(sorted(closure({'A', 'D'}, F)))
# ['A', 'B', 'C', 'D', 'E']
```

Trace {A, D}⁺ for R(A, B, C, D, E) with F = {A → B, B → C, CD → E}:

| Step | FD used | Result |
|---|---|---|
| start | | A D |
| 1 | A → B | A B D |
| 2 | B → C | A B C D |
| 3 | CD → E | A B C D E |

Each pass adds at least one attribute or stops, so the loop makes at most |R| attribute-adding passes plus a final no-change pass: polynomial time, and fast in practice.

### Three jobs for closure

1. **Does F imply X → Y?** Yes exactly when Y ⊆ X⁺. Does F imply AD → E? {A, D}⁺ contains E, so yes. Does F imply A → E? A⁺ = {A, B, C}, so no.
2. **Is X a superkey?** Yes exactly when X⁺ = R.
3. **Are F and G equivalent?** Yes if every FD in G follows from F, and every FD in F follows from G.

## Finding candidate keys

A candidate key is a minimal X with X⁺ = R. Searching every subset is exponential, but two observations prune it hard:

- An attribute that **never appears on any right-hand side** cannot be derived, so it must be in **every** key.
- An attribute that appears **only on right-hand sides** is always derivable, so it is in **no** key.

> [!example] One key
> R(A, B, C, D, E), F = {A → B, B → C, CD → E}.
> A and D never appear on a right side, so every key contains AD. {A, D}⁺ = ABCDE, so **AD is the only candidate key**.

> [!example] Several keys
> R(A, B, C, D), F = {AB → C, C → D, D → A}.
> B is never on a right side, so B is in every key. B⁺ = {B}, so add one more attribute:
> - AB⁺: AB → C, C → D gives ABCD. Key.
> - BC⁺: C → D, D → A gives ABCD. Key.
> - BD⁺: D → A, AB → C gives ABCD. Key.
>
> Candidate keys: **AB, BC, BD**. Every attribute is **prime** (belongs to some candidate key), a fact the 3NF test in the next lesson cares about.

A relation with n attributes can have exponentially many candidate keys, and deciding whether a given attribute is prime is NP-complete. Real schemas are small enough that this rarely matters, but it is why textbooks warn that the 3NF test is harder than it looks.

## Minimal cover

Two FD sets can say the same thing with different amounts of redundancy. A **minimal cover** (also called a canonical cover) is an equivalent set where:

1. Every right side is a single attribute.
2. No left side has an **extraneous** attribute (one you could drop and still derive the FD).
3. No FD is **redundant** (derivable from the others).

Work through F = {A → BC, B → C, A → B, AB → C}:

1. Split right sides: A → B, A → C, B → C, AB → C (the duplicate A → B merges).
2. Extraneous left attributes: in AB → C, is B needed? A⁺ = {A, B, C} already contains C, so B is extraneous. AB → C becomes A → C, a duplicate.
3. Redundant FDs: is A → C derivable from {A → B, B → C}? A⁺ = {A, B, C}, yes. Drop it.

Minimal cover: **{A → B, B → C}**. Four FDs became two, with exactly the same meaning. The 3NF synthesis algorithm in the next lesson starts from a minimal cover, which is why this step matters. Minimal covers are not always unique; different removal orders can give different, equally valid answers.

## Where FDs show up in real systems

- **Keys and UNIQUE constraints** directly enforce key-based dependencies. SQL has no general FUNCTIONAL DEPENDENCY declaration for an arbitrary X → Y; some special dependencies can be enforced with CHECK or exclusion constraints, and others need triggers or schema decomposition. Normalisation avoids storing the same dependent fact in many rows.
- **Postgres uses FDs in GROUP BY.** If you group by a table's primary key, Postgres (since 9.1) lets you select that table's other columns without listing them, because it knows the key determines them:

```sql
SELECT c.id, c.name, COUNT(*)
FROM customer c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id;   -- c.name allowed
```

- **Optimisers use FDs** to drop redundant grouping or sorting columns and to prove that a join cannot multiply rows.
- **Data-quality checks** test FDs over warehouses: `SELECT cid FROM sheet GROUP BY cid HAVING COUNT(DISTINCT ctitle) > 1` finds violations of `cid → ctitle`.

## Common mistakes

- **Reading FDs off sample data.** A coincidence in 50 rows is not a rule.
- **Splitting the left side.** XY → Z does not imply X → Z.
- **Forgetting transitivity.** When asked for keys, compute the closure; do not eyeball it. Chains like D → A, AB → C are easy to miss.
- **Stopping at one key.** A relation can have several candidate keys, and normal-form tests depend on all of them.

## Key takeaways
- X → Y means tuples equal on X are equal on Y, in every legal state. It is a business rule; data can only refute it.
- Armstrong's axioms (reflexivity, augmentation, transitivity) are sound and complete; union and decomposition apply to the right side only.
- The closure X⁺ answers implication (Y ⊆ X⁺), superkey (X⁺ = R) and equivalence questions in polynomial time.
- Attributes never on a right side are in every key; attributes only on right sides are in none. Use this to find all candidate keys quickly.
- A minimal cover removes split, extraneous and redundant parts of F, and is the input to 3NF synthesis.

## Further reading
- [Functional dependency — Wikipedia](https://en.wikipedia.org/wiki/Functional_dependency)
- [Armstrong's axioms — Wikipedia](https://en.wikipedia.org/wiki/Armstrong%27s_axioms)
- [Candidate key — Wikipedia](https://en.wikipedia.org/wiki/Candidate_key)
- [Table expressions and GROUP BY — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-table-expressions.html)
