---
id: comp-token-model
title: "Tokens, lexemes and regular patterns"
level: basic
minutes: 3
sourceLesson: comp-lexing
summary: "A token carries a classification, source text and usually a source position."
---

Before a compiler can understand `let x = 5 in x * x`, it has to know that `let` is one word, `5` is a number, and the spaces mean nothing. That is the **lexer**'s job (also called a **scanner** or **tokeniser**).

It is the simplest stage of the pipeline, but it touches every character of every file, so it has to be fast. It is also where a surprising number of language design quirks live.

## Tokens, lexemes and kinds

A **lexeme** is a run of characters, such as `in1`. A **token** is a lexeme plus its classification and, usually, its position:

```
Tok(kind='NAME', text='in1', pos=4)
```

Calc chooses grammar branches from the kind (NAME, NUM, +...), while parsing also uses text to create numeric and name nodes: the number's value, or the name to look up.

Calc has five kinds of token:

| Kind | Pattern | Examples |
|---|---|---|
| NUM | `\d+` | `5`, `042` |
| NAME | `[A-Za-z_]\w*` | `x`, `in1` |
| keyword | `let`, `in` | `let` |
| operator | one of `+-*/^()=` | `*` |
| whitespace | `\s+` | discarded |

The patterns are written in regular-expression (regex) notation. Each symbol has a fixed meaning:

| Notation | Matches |
|---|---|
| `\d` | one decimal digit |
| `\w` | one word character: letter, digit or `_` |
| `\s` | one whitespace character |
| `[A-Za-z_]` | one character from the set: here a letter or `_` |
| `+` | the item before it, one or more times |
| `*` | the item before it, zero or more times |
| `{n}` | the item before it, exactly n times |
| `( )` | groups items into one item |

A vertical bar between two patterns means "either one": `let` or `in` is written with a bar between them. So `[A-Za-z_]\w*` reads "a letter or underscore, then any number of word characters".

Every one of these is a **regular expression**. That is no accident: token shapes are almost always **regular languages**, the class of patterns that a finite automaton can recognise using a fixed amount of memory. Nesting, like matching brackets, is *not* regular. That is the parser's problem, not the lexer's.

## Key takeaways
- A token carries a classification, source text and usually a source position.
- Python regex character classes have Unicode behaviour unless restricted.

## Further reading
- [Scanning — Crafting Interpreters](https://craftinginterpreters.com/scanning.html)
- [Python regular-expression matching](https://docs.python.org/3/library/re.html)
- [NFA simulation and backtracking — Russ Cox](https://swtch.com/~rsc/regexp/regexp1.html)
- [Longest matching and rule order — flex](https://westes.github.io/flex/manual/Matching.html)
- [Scanner performance and backup — flex](https://westes.github.io/flex/manual/Performance.html)
- [docs.rs — regex](https://docs.rs/regex/latest/regex/)
- [tc39.es — ecmascript-language-lexical-grammar.html](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html)
