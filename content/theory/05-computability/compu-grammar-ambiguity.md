---
id: compu-grammar-ambiguity
title: Ambiguity and disambiguation
level: basic
minutes: 3
summary: An ambiguous grammar gives some string more than one parse tree.
sourceLesson: compu-cfg
---

## Ambiguous grammars

An **ambiguous grammar** is one in which some string has two or more different parse trees. The tempting short grammar for arithmetic is ambiguous:

```formula essential
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

Longer expressions can have many groupings. A parser that merely reports “accepted” has not settled which grouping the programmer intended. Test the tree as well as the accepted string. The layered expression/term/factor grammar in the previous lesson fixes this arithmetic ambiguity by giving multiplication its own level and making repeated addition group to the left.

> [!analogy] Real-world analogy: Attaching a phrase
> “I saw the person with binoculars” can describe your viewing equipment or something the other person carried.
>
> **How it maps:** The same sequence of words permits different attachments, just as one token string can have different parse trees.
>
> **Where it stops:** A programming grammar specifies exact permitted trees. Human interpretation also uses context and knowledge beyond grammar.

The famous real-world case is the **dangling else**:

```formula essential
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
