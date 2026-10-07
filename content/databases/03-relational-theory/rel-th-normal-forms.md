---
id: rel-th-normal-forms
title: Normal forms from 1NF to BCNF
level: intermediate
minutes: 16
summary: Update anomalies and why they happen, 1NF, 2NF, 3NF and BCNF defined through functional dependencies, lossless and dependency-preserving decomposition, and the BCNF and 3NF algorithms worked by hand.
---

Normalisation is the process of splitting a badly structured relation into smaller ones so that **each fact is stored once**. When a fact is stored in many rows, the copies can disagree unless additional constraints or coordinated writes keep them consistent.

Each normal form forbids one kind of redundancy, defined precisely with the functional dependencies from the previous lesson. The informal summary, due to Bill Kent (1983), is that every non-key attribute should depend on "the key, the whole key, and nothing but the key".

## The problem: anomalies

A shop imports its order spreadsheet as a single table:

```
OrderLine
oid pid odate  cid cname pname  price qty
 10 P1  03-01  C7  Ann   Bolt   0.20  50
 10 P2  03-01  C7  Ann   Nut    0.10  50
 11 P1  03-02  C9  Raj   Bolt   0.20  10
```

The business rules, as FDs:

- `oid → odate, cid` (an order has one date and one customer)
- `cid → cname`
- `pid → pname, price` (this shop sets one current price per product)
- `{oid, pid} → qty`

The only candidate key is `{oid, pid}`. Three kinds of trouble follow.

1. **Update anomaly.** Ann changes her name. It is stored on every line of every order she has placed, and an update that misses one leaves the data contradicting itself.
2. **Insertion anomaly.** You cannot record a new product until someone orders it, because `oid` is part of the key and cannot be NULL.
3. **Deletion anomaly.** Delete order 11, Raj's only order, and you lose the fact that customer C9 is called Raj.

All three come from FDs whose left side is not a key: the table is storing facts about customers and products inside rows about order lines.

## First normal form (1NF)

A relation is in 1NF when every attribute value is **atomic**: a single value from its domain, with no repeating groups.

```
Not 1NF
oid  products
 10  "P1:50, P2:50"
```

Ordinary column constraints and joins do not directly represent the individual items; parsing expressions or custom constraints are more complex than storing a row per item. The fix is one row per product per order, as in OrderLine above.

> [!note] What counts as atomic?
> Atomicity is relative to how you use the data. A date has parts, and a Postgres `text[]` or `jsonb` column holds structure, yet both can be fine if the database never needs to query or constrain the inside separately. The practical test: if you need to filter, join or enforce a rule on a part, it should be its own attribute or row. A list of tags you only ever display is fine as an array; a list of order lines is not.

## Second normal form (2NF)

A relation is in 2NF when it is in 1NF and **no non-prime attribute depends on part of a candidate key**. (A **prime** attribute is one that belongs to some candidate key.)

2NF only matters when a key is composite. OrderLine's key is `{oid, pid}`, and:

- `oid → odate, cid, cname` depends on part of the key.
- `pid → pname, price` depends on the other part.

Both are **partial dependencies**. Fix them by moving each one into its own relation:

```
Order(oid, odate, cid, cname)
Product(pid, pname, price)
Line(oid, pid, qty)
```

## Third normal form (3NF)

A relation is in 3NF when, for every non-trivial FD X → A that holds in it, **either X is a superkey or A is prime**.

`Order(oid, odate, cid, cname)` is in 2NF (its key `oid` is a single attribute) but still repeats Ann's name on every order. The cause is a **transitive dependency**: `oid → cid` and `cid → cname`. `cid` is not a superkey of Order and `cname` is not prime, so 3NF is violated. Split again:

```
Order(oid, odate, cid)
Customer(cid, cname)
Product(pid, pname, price)
Line(oid, pid, qty)
```

Now every FD's left side is a key of its relation. Ann's name lives in one row, products can exist before anyone orders them, and deleting an order loses nothing else.

> [!warning] Price is a different fact
> `pid → current_price` can hold in every database state even when prices change over time. It does not imply `pid → price_paid` across historical order lines. In a real shop, the price charged on an order is a separate fact from the current list price: `{oid, pid} → price_paid`. Store it on `Line`. That is not denormalisation; it is modelling a time-dependent fact correctly. Normalising away the price paid is a classic bug that silently rewrites old invoices.

## Boyce–Codd normal form (BCNF)

A relation is in BCNF when, for every non-trivial FD X → Y that holds in it, **X is a superkey**. BCNF drops 3NF's escape clause "or A is prime".

3NF and BCNF differ only when a relation has overlapping candidate keys. The classic example: each teacher teaches one course, and each student has one teacher per course.

```
Teaching(student, course, teacher)
  {student, course} → teacher
  teacher → course
Keys: {student, course}, {student, teacher}
```

- `teacher → course`: `teacher` is not a superkey, so **BCNF fails**.
- But `course` is prime (it is in the key `{student, course}`), so **3NF holds**.

The redundancy is real: "Smith teaches DB" is repeated for every student Smith teaches.

## Decomposing safely

Splitting a relation has two possible costs, and you should check both.

### Lossless join

A decomposition of R into R1 and R2 is **lossless** if R1 ⋈ R2 always gives back exactly R. If not, the join invents **spurious tuples**. The test for two parts:

> R1 ∩ R2 → R1, or R1 ∩ R2 → R2, must be in F⁺.

In words, the shared attributes must be a superkey of at least one side. Split Teaching badly into `(student, course)` and `(course, teacher)`:

```
student course | course teacher
Ann     DB     | DB     Smith
Bob     DB     | DB     Jones
```

Joining on `course` produces four rows, including `Ann, DB, Jones`, which never happened. `course` determines neither side, so the split is lossy. Split into `(teacher, course)` and `(student, teacher)` instead: the shared attribute `teacher` determines `course`, so it is lossless.

### Dependency preservation

A decomposition **preserves dependencies** if the union of the FDs projected onto its parts implies every FD in F. Enforcing those local dependencies then suffices without checking a join; an original FD can follow transitively across several local dependencies rather than literally fit in one part. The lossless BCNF split of Teaching loses `{student, course} → teacher`: no part contains all three attributes, so nothing stops Ann having two DB teachers.

## The BCNF decomposition algorithm

1. If some relation S has a non-trivial FD X → Y with X not a superkey of S, replace S with **X⁺ ∩ S** and **X ∪ (S − X⁺)**.
2. Repeat until every relation is in BCNF.

Each split shares exactly X, and X determines the whole first part, so every step is lossless. Worked on R(A, B, C, D, E) with F = {A → B, B → C, CD → E}, key AD:

```
ABCDE   A -> B violates (A not a key)
        A+ = ABC
  -> ABC, ADE
ABC     B -> C violates (B not a key)
  -> BC, AB
ADE     only AD -> E: AD is its key, ok

Result: AB, BC, ADE
```

All three are in BCNF and the join is lossless, but **CD → E is lost**: C and E never share a relation with D, so checking it needs a join.

## The 3NF synthesis algorithm

3NF can always be reached **losslessly while preserving every FD**. The synthesis algorithm (Bernstein, 1976):

1. Compute a minimal cover of F.
2. Make one relation for each left side X, containing X and everything it determines in the cover.
3. If no relation contains a candidate key of R, add one that is just a key.
4. Drop any relation that is a subset of another.

Same example. The minimal cover is {A → B, B → C, CD → E}:

```
A -> B    gives AB
B -> C    gives BC
CD -> E   gives CDE
key AD in none of them: add AD

Result: AB, BC, CDE, AD
```

Every FD lives in one relation, the key relation AD makes the join lossless, and here each part happens to be in BCNF too.

## Choosing between 3NF and BCNF

| | 3NF | BCNF |
|---|---|---|
| Lossless | always | always |
| FDs preserved | always | not always |
| Redundancy | a little possible | none from FDs |

In practice most schemas reach BCNF with no loss, because overlapping candidate keys are rare. When they do clash, the usual choices are:

- Stay in 3NF and accept some redundancy, enforcing the dependencies locally; keys alone may not express every local FD.
- Go to BCNF and enforce the lost FD another way, such as a trigger, a constraint on a join view, or application logic.

## Beyond BCNF, briefly

BCNF removes redundancy caused by FDs, but not all redundancy. If an employee has a set of skills and, independently, a set of languages, storing `(emp, skill, language)` forces every skill to be paired with every language. That is a **multivalued dependency** (emp ↠ skill), and **4NF** splits it into `(emp, skill)` and `(emp, language)`. **5NF** handles join dependencies across three or more parts. Both are rare in practice, but the "independent facts in one table" smell is worth recognising.

## Key takeaways
- Anomalies (update, insertion, deletion) come from FDs whose left side is not a key.
- 1NF: atomic values. 2NF: no partial dependence of a non-prime attribute on a candidate key. For non-trivial FDs, 3NF requires a superkey determinant or prime right-hand attribute; BCNF requires a superkey determinant.
- A two-way split is lossless when the shared attributes are a key of one side; otherwise the join creates spurious tuples.
- BCNF decomposition is always lossless but may lose FDs; 3NF synthesis is always lossless and dependency-preserving.
- Model time-dependent facts (price paid versus list price) as their own attributes rather than normalising them away.

## Further reading
- [Database normalization — Wikipedia](https://en.wikipedia.org/wiki/Database_normalization)
- [Third normal form — Wikipedia](https://en.wikipedia.org/wiki/Third_normal_form)
- [Boyce–Codd normal form — Wikipedia](https://en.wikipedia.org/wiki/Boyce%E2%80%93Codd_normal_form)
- [Lossless join decomposition — Wikipedia](https://en.wikipedia.org/wiki/Lossless_join_decomposition)
- [Fourth normal form — Wikipedia](https://en.wikipedia.org/wiki/Fourth_normal_form)
