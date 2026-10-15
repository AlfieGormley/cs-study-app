---
id: comp-lr-actions
title: "LR shift/reduce actions and conflicts"
level: intermediate
minutes: 3
sourceLesson: comp-parsing
summary: "LR tables select shifts and reductions using states and lookahead."
---

## Bottom-up: LR parsing

Recursive descent is **top-down**: it starts from `expr` and predicts what comes next. **LR** parsers work **bottom-up**: they read tokens onto a stack (a shift action) and, when the top of the stack matches the right-hand side of a rule, replace it with the rule's nonterminal (a reduction). Together these are **shift-reduce parsing**. The trace below uses the left-recursive grammar written in arrow notation, where `→` means "can be built from" and `|` separates alternatives. E stands for expression, T for term and F for factor:

```
E → E + T | T
T → T * F | F
F → NUM
```

In the trace, `$` is an end-of-input marker, so the parser can tell when the tokens run out:

```
stack      input      action
           2+3*4$     shift
2          +3*4$      reduce F
F          +3*4$      reduce T
T          +3*4$      reduce E
E          +3*4$      shift
E+         3*4$       shift
E+3        *4$        reduce F
E+F        *4$        reduce T
E+T        *4$        shift (see *)
E+T*       4$         shift
E+T*4      $          reduce F
E+T*F      $          reduce T->T*F
E+T        $          reduce E->E+T
E          $          accept
```

The key moment is `E+T` with `*` next. Reducing `E+T` to `E` would compute `2 + 3` first, which is wrong. The parser's lookahead says *shift*, so `3 * 4` is grouped first. A generator such as **yacc** or **GNU Bison** precomputes these decisions into a table from the grammar (usually **LALR(1)**, look-ahead LR with one token of lookahead: a compact form of LR).

When a generated parse table has multiple possible actions for a state/lookahead, the generator reports a **conflict**. The famous one is the **dangling else**: in `if a if b s1 else s2`, does `else` belong to the inner or outer `if`? Bison reports a shift/reduce conflict and, by default, shifts, attaching `else` to the nearest `if`, which is what C and Java specify.

## LL versus LR

| | LL (top-down) | LR (bottom-up) |
|---|---|---|
| Usually | Hand-written | Generated |
| Left recursion | Naive recursive descent must rewrite | Supported |
| Grammars | Smaller class | Larger class |
| Errors | Easy to tailor | Harder |

Every LL(1) grammar is LR(1), but not the reverse, so LR is strictly more powerful. In practice the power rarely matters, because real recursive descent parsers cheat: they peek further ahead, backtrack in a few places, or consult the symbol table.

## Key takeaways
- LR tables select shifts and reductions using states and lookahead.
- Default Bison shift resolution attaches a dangling else to the nearest unmatched if.

## Further reading
- [Parsing expressions — Crafting Interpreters](https://craftinginterpreters.com/parsing-expressions.html)
- [eli.thegreenplace.net — parsing-expressions-by-precedence-climbing](https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing)
- [CPython’s PEG parser — PEP 617](https://peps.python.org/pep-0617/)
- [www.gnu.org — Algorithm.html](https://www.gnu.org/software/bison/manual/html_node/Algorithm.html)
- [www.gnu.org — Shift_002fReduce.html](https://www.gnu.org/software/bison/manual/html_node/Shift_002fReduce.html)
- [tree-sitter.github.io — tree-sitter](https://tree-sitter.github.io/tree-sitter/)
