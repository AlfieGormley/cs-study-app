---
id: rel-th-attribute-fixpoint
title: Computing attribute closure
level: intermediate
minutes: 3
sourceLesson: rel-th-functional-deps
summary: Computing attribute closure, with complete worked examples and local definitions.
---

## The attribute-closure algorithm

An **attribute closure** collects every attribute determined by a chosen starting set under the given FD basis. Compute it with a fixpoint loop:

1. Start with the requested attribute set as the result.
2. Find any FD in F whose whole left side is already inside result. Add its right side to result.
3. Repeat until nothing changes.

```formula
result_0 = X
M_k = ⋃{Y : (L → Y) in F, L ⊆ result_k}
result_{k+1} = result_k ∪ M_k
X⁺ = result_k when result_{k+1} = result_k
where
X: the attribute set whose attribute closure you want
X⁺: the attribute closure of X: every attribute X determines under F
F: the set of FDs
L, Y: left and right attribute sets of an FD in F
M_k: all right-side attributes whose left sides are already available at step k
⋃: union of every set in the collection, including the empty union when none qualifies
result_0, result_k, result_{k+1}: the set built so far: at the start, after k steps, and after one more step
k: the step number, 0, 1, 2, ...
∪: union: add all currently derivable right-side attributes
⊆: is a subset of: every attribute of L is already in the result
→: functionally determines
In words: keep firing any FD whose left side you already have, adding its right side, until no FD adds anything new. What you have then is X⁺.
```

The same algorithm in Python, with a set of letters standing for attributes:

```python
def closure(attrs, fds):
    # Start with the known attributes.
    result = set(attrs)
    changed = True
    while changed:
        changed = False
        # Fire every applicable dependency.
        for lhs, rhs in fds:
            if lhs <= result \
               and not rhs <= result:
                # Add new attributes.
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

The first dependency adds B to the known A and D. The second then adds C; with C and D available, the third adds E. A sequential Python pass can fire a later rule using an attribute added earlier in that same pass. The card uses simultaneous rounds instead: both schedules reach the same least fixed point.

Each pass of the loop either adds at least one attribute or changes nothing and stops, so the number of passes is bounded by the number of attributes:

```formula
N_pass ≤ |R| + 1
where
N_pass: the number of times the loop goes through all the FDs
|R|: the number of attributes of R (5 in the trace above)
≤: is at most
In words: at most one adding pass per attribute, plus a final pass that finds nothing to add. Each pass checks every FD once, so the whole algorithm runs in polynomial time and is fast in practice.
```

## Key takeaways

- Start from known attributes and apply every available FD until a full pass adds nothing.
- Sequential firing and simultaneous rounds reach the same least fixed point.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
