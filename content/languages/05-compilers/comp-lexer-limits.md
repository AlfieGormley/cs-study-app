---
id: comp-lexer-limits
title: "State explosion, ReDoS and real lexer context"
level: basic
minutes: 5
sourceLesson: comp-lexing
summary: "DFA state counts can grow exponentially; backtracking can instead explode at runtime."
---

## Why DFAs can be a trap, and why backtracking is worse

The subset construction can blow up. The classic example is the language "the third character from the end is `a`", over the two letters `a` and `b`, or in general "the nth character from the end". Its regex is `(a|b)*a(a|b){n-1}`: any run of `a`s and `b`s, then one `a`, then one fewer letter than that distance from the end. An NFA can *guess* which `a` is the one that matters, so it needs only a few states. A DFA cannot guess: it must remember the last n characters it has read, because any of them might turn out to be the one n from the end.

```formula
S_DFA = 2^n
S_NFA = n + 1
where
S_DFA: the number of states in the smallest DFA for the language
S_NFA: the number of states in the simple NFA for the same language
n: how far from the end the required `a` must be (n = 3 means the third character from the end)
2^n: n copies of 2 multiplied together: each of the last n characters is one of 2 letters, and every different history needs its own state
In words: each extra position the DFA must remember doubles its number of states, while the NFA grows by only one state.
```

For the third-character-from-the-end case, the minimal DFA needs 8 states against the NFA’s 4; the twentieth-character-from-the-end case needs 1,048,576 DFA states. Real token patterns are simple, so lexers rarely hit this.

General-purpose regex engines in Python, Perl, Java and JavaScript take a different approach: **backtracking**. It supports features like back-references (`\1`, "match the same text that group 1 matched"), but some patterns take exponential time. Matching `(a+)+$` (one or more groups of one or more `a`s, then `$`, the end of the input) against `"aaa…ab"` fails because of the final `b`, and before Python's `re` can report the failure it tries every way of splitting the `a`s into groups:

```formula
W = 2^{k−1}
W = 2^{29} ≈ 5.4 × 10^8   when k = 30
where
W: the number of ways to split a run of `a`s into one or more non-empty groups; a backtracking engine may try each one before giving up
k: the number of `a` characters in the input
2^{k−1}: k − 1 copies of 2 multiplied together: each of the k − 1 gaps between neighbouring `a`s either is or is not a group boundary
≈: approximately equal to
In words: every extra `a` doubles the number of splits to try, so the matching time grows exponentially with the input length.
```

So 30 `a`s already mean over half a billion splits, and each extra `a` roughly doubles the time. This class of bug, **ReDoS**, has taken down production services. Engines like Google's RE2 and Rust's `regex` crate use automata-based techniques that avoid this exponential backtracking for supported syntax. A single search is linear in input length for a fixed pattern; regex size and repeated-search APIs also affect bounds.

> [!note] Our regex lexer is safe
> Calc's simple alternatives and disjoint starting classes avoid catastrophic ambiguity; its repeats can still backtrack internally. Nested ambiguous repetition is one source of trouble, not the only one.

## Lexers in the real world

- **Generated lexers.** flex turns a spec of regex rules into a table-driven DFA in C. re2c compiles the DFA into direct `goto` code, with performance depending on the generated scanner, target and workload.
- **Hand-written lexers.** GCC, Clang, Go, V8 and CPython (whose C tokenizer is hand-written) all lex by hand: it is not much code, it is fast, and it gives better error messages.
- **Context-sensitive corners.** Python's tokenizer emits `INDENT` and `DEDENT` tokens by keeping a stack of indentation widths, which a pure DFA cannot do. In JavaScript, `/` may start a regex literal or be division, depending on grammatical context, not just the immediately previous token. C's "lexer hack" feeds the symbol table back into the lexer so it can tell a typedef name from a variable.

## Pitfalls

- **Lexing does not validate structure.** `2x` lexes happily as `NUM NAME`; the parser rejects it.
- **Unicode surprises.** In Python, `\d` on a `str` matches any Unicode decimal digit, such as Arabic-Indic `٣`. Use `[0-9]` or `re.ASCII` if your language means ASCII only.
- **Losing positions.** Discarding positions makes precise source locations harder to recover.
- **Keyword lists in the regex.** Writing `let|in|[A-Za-z_]\w*` with Python's `re` lexes `letter` as `let` + `ter`. Match names first, then look keywords up.

## Key takeaways
- DFA state counts can grow exponentially; backtracking can instead explode at runtime.
- Indentation and grammatical context require more than an isolated pure DFA.

## Further reading
- [Scanning — Crafting Interpreters](https://craftinginterpreters.com/scanning.html)
- [Python regular-expression matching](https://docs.python.org/3/library/re.html)
- [NFA simulation and backtracking — Russ Cox](https://swtch.com/~rsc/regexp/regexp1.html)
- [Longest matching and rule order — flex](https://westes.github.io/flex/manual/Matching.html)
- [Scanner performance and backup — flex](https://westes.github.io/flex/manual/Performance.html)
- [docs.rs — regex](https://docs.rs/regex/latest/regex/)
- [tc39.es — ecmascript-language-lexical-grammar.html](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html)
