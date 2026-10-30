---
id: rel-th-attribute-fixpoint
title: Computing attribute closure
level: intermediate
minutes: 3
sourceLesson: rel-th-functional-deps
summary: Attribute closure: start from what you know, keep applying dependencies until nothing new appears.
---

## The attribute-closure algorithm

An **attribute closure** collects every attribute determined by a chosen starting set under the given FD basis. Compute it with a fixpoint loop:

1. Start with the requested attribute set as the result.
2. Find any given FD whose whole left side is already in the result. Add its right side to the result.
3. Repeat until nothing changes.

Because the set only ever grows, and it can never grow beyond the relation's attributes, the loop must stop. The final set is the attribute closure of the starting set: exactly the attributes it determines.

> [!analogy] Real-world analogy: cooking from a well-stocked cupboard
> You start with some ingredients and a recipe book. Any recipe whose ingredients you all have can be made, and what you make (pastry, a sauce) unlocks further recipes. Keep going until no recipe gives you anything new: that is everything you can produce.
>
> **How it maps:** Your starting ingredients are the starting attribute set, each recipe is a dependency (all of its left side must be present), and what you can eventually produce is the attribute closure. A recipe needing two ingredients waits until you have both, just as a two-attribute left side does.
>
> **Where it stops:** Cooking uses up ingredients and a recipe can fail. Deriving an attribute consumes nothing and always succeeds, and the order in which you apply rules cannot change the final set.

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

Trace the attribute closure of A and D together for a relation with attributes A to E and the three dependencies in the code (A fixes B, B fixes C, C with D fixes E). The first dependency adds B to the known A and D. The second then adds C; with C and D available, the third adds E. A sequential Python pass can fire a later rule using an attribute added earlier in that same pass. Applying the rules in simultaneous rounds instead takes a different route but reaches the same final set.

Textbooks, and the later units here, write the attribute closure of a set with a superscript plus:

```formula reference
{A, D}⁺ = {A, B, C, D, E}
where
{A, D}⁺: the attribute closure of the set {A, D}: every attribute that A and D together determine under the given dependencies. A superscript plus after an attribute set always means its attribute closure
A, B, C, D, E: the attributes of the relation in the trace
{ }: a set of attributes
In words: the attribute closure of A and D together is the whole heading, so A and D together form a superkey of this relation.
```

Each pass of the loop either adds at least one attribute or changes nothing and stops. So the number of passes is at most one per attribute, plus a final pass that finds nothing new, and each pass checks every dependency once. The algorithm runs in polynomial time and is fast in practice, which is why it, rather than listing every implied dependency, is the everyday tool.

## Key takeaways

- Start from known attributes and apply every available FD until a full pass adds nothing.
- The order of firing does not matter: every schedule reaches the same final set.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Functional dependency, including attribute closure (Wikipedia)](https://en.wikipedia.org/wiki/Functional_dependency)
