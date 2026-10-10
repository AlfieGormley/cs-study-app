---
id: rel-th-functional-deps
title: Functional dependencies, closure and keys
level: intermediate
minutes: 18
summary: What a functional dependency really claims, Armstrong's axioms, the attribute-closure algorithm, finding every candidate key, and computing a minimal cover.
---

Normalisation, the subject of the next lesson, can sound like a list of rules to memorise. It is not. The normal forms 2NF, 3NF and BCNF are defined using **functional dependencies** (FDs); higher forms also involve multivalued or join dependencies. Once you can reason about FDs, normal forms become mechanical checks.

This lesson gives you the tools: what an FD means, how to derive new FDs from known ones, the attribute-closure algorithm, and how to use it to find keys.

A note on notation used throughout. Attributes are often single capital letters, and a relation's heading is written `R(A, B, C)`: relation R with attributes A, B and C. Letters written side by side denote a *set* of attributes, so **AB** means the set {A, B}. Every symbol is defined again in each formula card.

## What a functional dependency says

For attribute sets X and Y of a relation R, the FD written with an arrow, "X → Y" and read "X determines Y", means:

> Any two tuples that agree on X must also agree on Y.

```formula
X → Y
for all t_1, t_2 in R:
  t_1[X] = t_2[X] gives t_1[Y] = t_2[Y]
where
X, Y: sets of attributes of R; each may be a single attribute or several
→: "functionally determines": the condition on the next two lines holds in every legal state of R
R: the relation (table) the dependency is about
t_1, t_2: any two tuples (rows) of R
t_1[X], t_2[X]: the values the tuple has for the attributes in X; t_1[Y] and t_2[Y] likewise for Y
In words: whenever two rows have the same X values, they must have the same Y values. Knowing X pins down Y.
```

Take a spreadsheet of enrolments that someone has imported as one table:

```
sid  sname  cid  ctitle      grade
 1   Ada    DB   Databases    A
 1   Ada    OS   Op Systems   B
 2   Ben    DB   Databases    C
```

The business rules say a student id identifies one name, a course code identifies one title, and there is one grade per student per course. As FDs:

```formula
sid → sname
cid → ctitle
{sid, cid} → grade
where
→: functionally determines: rows equal on the left side are equal on the right side
sid: the student id
sname: the student's name
cid: the course code
ctitle: the course title
grade: the grade the student got on that course
{ }: a set of attributes; {sid, cid} means "sid and cid together"
In words: the id fixes the name, the code fixes the title, and only the pair (student, course) fixes the grade.
```

An FD is a **constraint on every legal state**, exactly like a key. You get it from the domain, not from the data.

> [!warning] Data can refute an FD, never prove one
> If two rows share a `cid` but have different titles, the FD from `cid` to `ctitle` is false (or the data is dirty). But if today's rows all happen to have unique surnames, that does not make surname a determinant of anything. Data-profiling tools that "discover" FDs find candidates that a human must confirm.

### Trivial and non-trivial FDs

An FD is a **trivial FD** if its right side is part of its left side. Trivial FDs hold in every relation and tell you nothing. The interesting ones are non-trivial.

```formula
Y ⊆ X
{sid} ⊆ {sid, cid}
{sid, cid} → sid
where
X, Y: sets of attributes
→: functionally determines
⊆: "is a subset of": every attribute in Y is also in X (Y may equal X)
sid, cid: the student-id and course-code attributes
{ }: a set of attributes
In words: X → Y is called trivial exactly when Y ⊆ X. A set of attributes always determines any part of itself, so {sid, cid} → sid is true in every relation and says nothing.
```

### Keys are FDs too

A set K is a **superkey** of R exactly when K determines every attribute of R:

```formula
K → R
{sid, cid} → sname, ctitle, grade
where
K: a set of attributes of R
→: functionally determines
R: here, the set of all attributes of the relation R
sid, sname, cid, ctitle, grade: the attributes of the enrolment table above
{ }: a set of attributes
In words: K is a superkey when knowing K's values fixes every other value in the row.
```

Here `{sid, cid}` determines sname, ctitle and grade, so it is a superkey. Neither attribute alone determines everything, so it is also a **candidate key**: a superkey with nothing that can be removed.

## Armstrong's axioms

Given some FDs, which others must also hold? William Armstrong gave three inference rules in 1974. For attribute sets X, Y and Z:

1. **Reflexivity**: a set determines any subset of itself.
2. **Augmentation**: adding the same attributes to both sides keeps an FD true.
3. **Transitivity**: if X determines Y and Y determines Z, then X determines Z.

```formula
Y ⊆ X gives X → Y
X → Y gives XZ → YZ
X → Y and Y → Z gives X → Z
where
X, Y, Z: sets of attributes of one relation
⊆: is a subset of: every attribute of Y is in X
→: functionally determines
XZ, YZ: sets written side by side are combined: XZ means X ∪ Z, the attributes of X together with those of Z
∪: union: everything in either set
In words: line 1 is reflexivity, line 2 is augmentation and line 3 is transitivity.
```

The rules are **sound** (they never derive a false FD) and **complete** (every FD that logically follows can be derived with them). Three useful rules follow from them: the **union rule**, the **decomposition rule** and **pseudotransitivity**.

```formula
X → Y and X → Z gives X → YZ
X → YZ gives X → Y and X → Z
X → Y and WY → Z gives WX → Z
where
W, X, Y, Z: sets of attributes of one relation
→: functionally determines
YZ, WY, WX: combined sets, for example YZ = Y ∪ Z
∪: union: everything in either set
In words: union merges right sides that share a left side; decomposition splits a right side apart; pseudotransitivity chains two FDs when extra attributes W are needed on the second one's left.
```

> [!warning] The left side does not decompose
> A right side can be split, but a left side cannot. Grade depends on student *and* course together, not on either alone.

```formula
XY → Z ⇏ X → Z
{sid, cid} → grade ⇏ sid → grade
where
X, Y, Z: sets of attributes
XY: X ∪ Y, the two sets combined
∪: union
→: functionally determines
⇏: "does not imply": the left FD can hold while the right one fails
sid, cid, grade: the student-id, course-code and grade attributes
{ }: a set of attributes
In words: knowing that X and Y together determine Z tells you nothing about X alone. One student has several grades, one per course.
```

The set of all FDs implied by a set F is written **F⁺** (F with a superscript plus):

```formula
X → Y in F⁺ when F ⊨ X → Y
where
F: the set of FDs you were given
F⁺: the FD closure of F: every FD that follows logically from F, including the trivial ones
X, Y: sets of attributes
→: functionally determines
⊨: "logically implies": every relation state that satisfies all of F also satisfies X → Y
In words: F⁺ is everything you can derive from F with Armstrong's axioms.
```

F⁺ can be exponentially large, so in practice you never list it. You compute closures of attribute sets instead.

## The attribute-closure algorithm

The **attribute closure** of X, written X⁺, is the set of all attributes that X determines under F. The algorithm is a fixpoint loop:

1. Start with result = X.
2. Find any FD in F whose whole left side is already inside result. Add its right side to result.
3. Repeat until nothing changes.

```formula
result_0 = X
result_{k+1} = result_k ∪ M
  for any L → M in F with L ⊆ result_k
X⁺ = result_k when result_{k+1} = result_k
where
X: the attribute set whose attribute closure you want
X⁺: the attribute closure of X: every attribute X determines under F
F: the set of FDs
L → M: one FD in F, with left side L and right side M
result_0, result_k, result_{k+1}: the set built so far: at the start, after k steps, and after one more step
k: the step number, 0, 1, 2, ...
∪: union: add M's attributes to the set
⊆: is a subset of: every attribute of L is already in the result
→: functionally determines
In words: keep firing any FD whose left side you already have, adding its right side, until no FD adds anything new. What you have then is X⁺.
```

The same algorithm in Python, with a set of letters standing for attributes:

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

Trace the attribute closure of {A, D} for R(A, B, C, D, E):

```formula
F = {A → B, B → C, CD → E}
{A, D}⁺ = {A, B, C, D, E}
where
R: a relation with five attributes, A, B, C, D and E
A, B, C, D, E: the attributes of R
F: the FDs that hold on R
CD: the set {C, D}
→: functionally determines
{ }: a set
{A, D}⁺: the attribute closure of {A, D}: everything A and D together determine
In words: starting from A and D, the three FDs fire in turn and reach every attribute.
```

| Step | FD used | Result |
|---|---|---|
| start | | A D |
| 1 | A → B | A B D |
| 2 | B → C | A B C D |
| 3 | CD → E | A B C D E |

Each pass of the loop either adds at least one attribute or changes nothing and stops, so the number of passes is bounded by the number of attributes:

```formula
N_pass ≤ |R| + 1
where
N_pass: the number of times the loop goes through all the FDs
|R|: the number of attributes of R (5 in the trace above)
≤: is at most
In words: at most one adding pass per attribute, plus a final pass that finds nothing to add. Each pass checks every FD once, so the whole algorithm runs in polynomial time and is fast in practice.
```

### Three jobs for attribute closure

1. **Does F imply a given FD?** Compute the attribute closure of its left side and check that the right side is inside it.
2. **Is X a superkey?** Yes exactly when its attribute closure is every attribute of R.
3. **Are F and G equivalent?** Yes if every FD in G follows from F, and every FD in F follows from G.

```formula
F ⊨ X → Y iff Y ⊆ X⁺
X⁺ = R
F ≡ G iff F⁺ = G⁺
{A, D}⁺ = ABCDE, so F ⊨ AD → E
A⁺ = {A, B, C}, so F ⊭ A → E
where
F, G: two sets of FDs over the same relation
X, Y: sets of attributes
→: functionally determines
⊨: logically implies; ⊭: does not imply
⊆: is a subset of
X⁺: the attribute closure of X under F
R: here, the set of all attributes of the relation (A, B, C, D, E in the example, with F = {A → B, B → C, CD → E})
≡: equivalent: F and G imply exactly the same FDs
F⁺, G⁺: the closures of F and G: every FD each one implies
A⁺, {A, D}⁺: the closures of A and of {A, D} under F
A, B, C, D, E: the attributes of R
ABCDE, AD: the sets {A, B, C, D, E} and {A, D}
In words: line 1: F implies X → Y exactly when every attribute of Y is in the attribute closure of X ("iff" means "if and only if"). Line 2: X is a superkey exactly when its attribute closure is all of R. Line 3: F and G are equivalent exactly when they imply the same FDs. In the example, A and D together reach E, so AD → E follows from F; A alone only reaches A, B and C, so A → E does not.
```

In practice you test equivalence FD by FD: compute each FD's left-side attribute closure under the other set, rather than ever listing F⁺.

## Finding candidate keys

A **candidate key** is a superkey with no unnecessary attributes:

```formula
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
In words: X determines everything, and no smaller part of X does.
```

Searching every subset is exponential, but two observations prune it hard:

- An attribute that **never appears on any right-hand side** cannot be derived, so it must be in **every** key.
- An attribute that appears **only on right-hand sides** is always derivable, so it is in **no** key.

> [!example] One key
> Take R(A, B, C, D, E) with the FDs A → B, B → C and CD → E. A and D never appear on a right side, so every key contains both. The attribute closure of {A, D} is all five attributes, so **AD is the only candidate key**.

> [!example] Several keys
> Take R(A, B, C, D) with the FDs AB → C, C → D and D → A. B is never on a right side, so B is in every key. B alone only reaches itself, so add one more attribute. AB, BC and BD each reach all four attributes, as the card below shows.
>
> Candidate keys: **AB, BC, BD**. Every attribute is **prime** (belongs to some candidate key), a fact the 3NF test in the next lesson cares about.

```formula
F = {AB → C, C → D, D → A}
B⁺ = {B}
{A, B}⁺ = {A, B, C, D}
{B, C}⁺ = {A, B, C, D}
{B, D}⁺ = {A, B, C, D}
where
A, B, C, D: the attributes of R
F: the FDs that hold on R
AB: the set {A, B}
→: functionally determines
B⁺, {A, B}⁺, {B, C}⁺, {B, D}⁺: attribute closures under F
{ }: a set
In words: AB uses AB → C then C → D; BC uses C → D then D → A; BD uses D → A then AB → C. Each reaches everything, and B alone does not, so all three are minimal.
```

A relation with n attributes can have exponentially many candidate keys, and deciding whether a given attribute is prime is NP-complete. Real schemas are small enough that this rarely matters, but it is why textbooks warn that the 3NF test is harder than it looks.

## Minimal cover

Two FD sets can say the same thing with different amounts of redundancy. A **minimal cover** (also called a canonical cover) is an equivalent set where:

1. Every right side is a single attribute.
2. No left side has an **extraneous** attribute (one you could drop and still derive the FD).
3. No FD is **redundant** (derivable from the others).

Work through F = {A → BC, B → C, A → B, AB → C}:

1. Split right sides: A → B, A → C, B → C, AB → C (the duplicate A → B merges).
2. Extraneous left attributes: in AB → C, is B needed? The attribute closure of A is {A, B, C}, which already contains C, so B is extraneous. AB → C becomes A → C, a duplicate.
3. Redundant FDs: is A → C derivable from A → B and B → C? The attribute closure of A under those two is {A, B, C}, so yes. Drop it.

```formula
F = {A → BC, B → C, A → B, AB → C}
F_1 = {A → B, A → C, B → C, AB → C}
A⁺ = {A, B, C}
F_2 = {A → B, A → C, B → C}
F_3 = {A → B, B → C}
where
A, B, C: attributes
F: the original set of FDs
BC, AB: the sets {B, C} and {A, B}
→: functionally determines
F_1: F after splitting every right side into single attributes
A⁺: the attribute closure of A; it contains C, so B is extraneous in AB → C
F_2: F_1 with AB → C reduced to A → C (now a duplicate, so merged)
F_3: F_2 without A → C, which follows from A → B and B → C by transitivity
{ }: a set
In words: four FDs reduce to two with exactly the same meaning: F_3 is a minimal cover of F.
```

Minimal cover: **{A → B, B → C}**. Four FDs became two, with exactly the same meaning. The 3NF synthesis algorithm in the next lesson starts from a minimal cover, which is why this step matters. Minimal covers are not always unique; different removal orders can give different, equally valid answers.

## Where FDs show up in real systems

- **Keys and UNIQUE constraints** directly enforce key-based dependencies. SQL has no general FUNCTIONAL DEPENDENCY declaration for an arbitrary dependency between two sets of columns; some special dependencies can be enforced with CHECK or exclusion constraints, and others need triggers or schema decomposition. Normalisation avoids storing the same dependent fact in many rows.
- **Postgres uses FDs in GROUP BY.** If you group by a table's primary key, Postgres (since 9.1) lets you select that table's other columns without listing them, because it knows the key determines them:

```sql
SELECT c.id, c.name, COUNT(*)
FROM customer c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id;   -- c.name allowed
```

- **Optimisers use FDs** to drop redundant grouping or sorting columns and to prove that a join cannot multiply rows.
- **Data-quality checks** test FDs over warehouses: `SELECT cid FROM sheet GROUP BY cid HAVING COUNT(DISTINCT ctitle) > 1` finds course codes with more than one title, which are violations of the FD from `cid` to `ctitle`.

## Common mistakes

- **Reading FDs off sample data.** A coincidence in 50 rows is not a rule.
- **Splitting the left side.** Two attributes determining a third together does not imply that either one does alone.
- **Forgetting transitivity.** When asked for keys, compute the attribute closure; do not eyeball it. Chains through two FDs are easy to miss.
- **Stopping at one key.** A relation can have several candidate keys, and normal-form tests depend on all of them.

```formula
XY → Z ⇏ X → Z
D → A and AB → C gives BD → C
where
X, Y, Z: sets of attributes
XY: X ∪ Y, the two sets combined
∪: union
→: functionally determines
⇏: does not imply
A, B, C, D: single attributes
AB, BD: the sets {A, B} and {B, D}
In words: the first line is the left-side mistake; the second is an easily missed chain: D gives A, and then A with B gives C.
```

## Key takeaways
- An FD X → Y means tuples equal on X are equal on Y, in every legal state. It is a business rule; data can only refute it.
- Armstrong's axioms (reflexivity, augmentation, transitivity) are sound and complete; union and decomposition apply to the right side only.
- The attribute closure X⁺ answers implication (is Y inside X⁺?), superkey (is X⁺ all of R?) and equivalence questions in polynomial time.
- Attributes never on a right side are in every key; attributes only on right sides are in none. Use this to find all candidate keys quickly.
- A minimal cover removes split, extraneous and redundant parts of F, and is the input to 3NF synthesis.

## Further reading
- [Functional dependency — Wikipedia](https://en.wikipedia.org/wiki/Functional_dependency)
- [Armstrong's axioms — Wikipedia](https://en.wikipedia.org/wiki/Armstrong%27s_axioms)
- [Candidate key — Wikipedia](https://en.wikipedia.org/wiki/Candidate_key)
- [Table expressions and GROUP BY — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-table-expressions.html)
