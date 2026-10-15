---
id: comp-longest-match
title: "Longest matches and keyword boundaries"
level: basic
minutes: 3
sourceLesson: comp-lexing
summary: "Maximal munch chooses the longest token; flex breaks equal-length ties by rule order."
---

Token boundaries must be decided before the parser can apply an operator. Longest match compares token candidates at the same input position; it does not search ahead for whichever token makes the whole program valid. The Calc NAME rule and keyword lookup from the previous unit avoid splitting a keyword prefix off a longer identifier.

## Maximal munch

What should `letter` lex as? It starts with `let`, but it is obviously the name `letter`. Lexers follow the **maximal munch** (longest match) rule: always take the longest lexeme that forms a valid token.

Our lexer gets this right by matching the general NAME pattern first, which greedily eats `letter`, and only *then* checking a keyword table. `in1` likewise lexes as one NAME, not keyword `in` followed by `1`.

> [!warning] Python's `re` is not longest-match
> Python's alternation is **leftmost-first**: `=|==` matched against `==` returns `=`, because the first alternative that works wins. Lexer generators like flex choose the *longest* match across all rules. With `re`, you must order alternatives so longer operators come first (`==|=`).

Maximal munch has famous consequences. In C, `x---y` lexes as `x -- - y`, because the lexer grabs `--` greedily before the parser gets a say. Before C++11, `vector<vector<int>>` was a syntax error because `>>` lexed as the shift operator.

Ties between rules of equal length are broken by **rule order**: in flex, the rule listed first wins. That is how `let` becomes a keyword rather than a NAME when both match exactly three characters.

## Key takeaways
- Maximal munch chooses the longest token; flex breaks equal-length ties by rule order.
- Python alternation chooses its first successful alternative, so put longer operators first.

## Further reading
- [Scanning — Crafting Interpreters](https://craftinginterpreters.com/scanning.html)
- [Python regular-expression matching](https://docs.python.org/3/library/re.html)
- [NFA simulation and backtracking — Russ Cox](https://swtch.com/~rsc/regexp/regexp1.html)
- [Longest matching and rule order — flex](https://westes.github.io/flex/manual/Matching.html)
- [Scanner performance and backup — flex](https://westes.github.io/flex/manual/Performance.html)
- [docs.rs — regex](https://docs.rs/regex/latest/regex/)
- [tc39.es — ecmascript-language-lexical-grammar.html](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html)
