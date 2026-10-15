---
id: compu-grammar-ambiguity
title: Ambiguity and disambiguation
level: basic
minutes: 5
summary: An ambiguous grammar gives some string more than one parse tree.
sourceLesson: compu-cfg
---

## Ambiguous grammars

An **ambiguous grammar** is one in which some string has two or more different parse trees. The tempting short grammar for arithmetic is ambiguous:

```formula
E → E "+" E | E "*" E | "id"
where
E: the start variable for an expression
→: may be rewritten as
|: separates alternatives
"+", "*": addition and multiplication terminal tokens
"id": a terminal identifier token
In words: Both operators combine arbitrary expressions at the same grammar level, leaving their relative grouping unspecified.
```

`id + id * id` now has two trees: one groups `(id + id) * id`, the other `id + (id * id)`. The grammar alone leaves grouping unspecified; a parser needs an additional disambiguation policy or an unambiguous grammar.

The problem gets worse with length. Each parse tree picks one operator as the root; the operands to its left and to its right are then grouped independently. That gives a recurrence (a formula defined in terms of smaller cases of itself):

```formula
T(1) = 1
T(n) = Σ T(k) × T(n − k)
       for k = 1, …, n − 1 and n ≥ 2
T(n) = C(n − 1)
C(m) = (2m)! / ((m + 1)! × m!)
where
T(n): the number of parse trees for an expression with n operands (the ids)
n: the number of operands, 1 or more
k: how many operands sit left of the root operator, from 1 to n − 1
Σ: capital sigma: add up the term after it for every listed value of k
C(m): the m-th Catalan number, a famous counting sequence 1, 1, 2, 5, 14, 42, …
m: the position in the Catalan sequence, starting at 0
!: factorial: the product of all whole numbers from 1 up to that number, so 4! = 24 (and 0! = 1)
≥: is at least
In words: count the trees by trying every operator as the root and multiplying the ways to group each side; the totals are the Catalan numbers.
```

For four operands, the recurrence and closed form agree:

```formula
T(4) = T(1)T(3) + T(2)T(2) + T(3)T(1)
T(4) = 2 + 1 + 2 = 5
C(3) = 6! / (4! × 3!) = 720 / 144 = 5
where
T(n): the number of parse trees for an expression with n operands
C(m): the Catalan number at nonnegative index m
n: the positive number of operands
m: the nonnegative Catalan index
!: factorial; the product of positive integers up to the argument, with zero factorial equal to one
In words: Trying each root split produces five trees; the third-index Catalan number is also five.
```

For one through seven operands the sequence is 1, 1, 2, 5, 14, 42, 132. Ratios between neighbouring terms approach four; 132 divided by 42 is already about 3.1. This short recursive count confirms it:

```python
from functools import lru_cache

@lru_cache(None)
def trees(n):          # n operands
    if n == 1:
        return 1
    # split into left k and right n-k
    return sum(trees(k) * trees(n - k)
               for k in range(1, n))

print([trees(n) for n in range(1, 8)])
# [1, 1, 2, 5, 14, 42, 132]
```

The famous real-world case is the **dangling else**:

```formula
S → "if" C "then" S
  | "if" C "then" S "else" S
  | "other"
where
S: the start variable for statements
C: a variable standing for a condition
→: may be rewritten as
|: separates alternatives
"if", "then", "else": terminal keyword tokens
"other": a terminal standing for a statement of another kind
In words: An if statement may omit its else branch or include one, so nesting can leave else attachment ambiguous.
```

In `if a then if b then x else y`, does `else y` belong to the inner or the outer `if`? C, C++ and Java all resolve it by convention: the `else` binds to the nearest eligible unmatched `if`. Parser generators such as yacc and Bison report this as a *shift/reduce conflict* and resolve it by shifting, which gives the same answer.

> [!warning] Ambiguous grammars versus ambiguous languages
> You can usually remove grammar ambiguity by rewriting the grammar (as the E/T/F grammar does). But some context-free *languages* are **inherently ambiguous**: every context-free grammar for them is ambiguous. A standard example consists of an a block, then a b block, then a c block, where either the first two or the last two block lengths agree. In the obvious union grammar, strings with all three lengths equal have two leftmost derivations. That observation alone does not prove inherent ambiguity: the theorem rules out every equivalent unambiguous CFG, not just this construction. Deciding whether an arbitrary CFG is ambiguous is also undecidable; a full proof of these results is beyond this lesson.

## Key takeaways

- An ambiguous grammar gives some string more than one parse tree.
- Rewriting can remove grammar ambiguity in many cases; an inherently ambiguous language has no equivalent unambiguous CFG.
- Dangling else conventionally attaches to the nearest eligible unmatched if.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
- [GNU Bison: dangling else and shift/reduce conflicts](https://github.com/akimd/bison/blob/master/doc/bison.texi)
- [Koechlin: inherent ambiguity and why equivalent grammars cannot always fix it](https://drops.dagstuhl.de/storage/00lipics/lipics-vol250-fsttcs2022/LIPIcs.FSTTCS.2022.41/LIPIcs.FSTTCS.2022.41.pdf)
