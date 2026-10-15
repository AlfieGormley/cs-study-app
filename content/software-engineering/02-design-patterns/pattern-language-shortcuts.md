---
id: pattern-language-shortcuts
title: Patterns as Python language features
level: basic
minutes: 3
sourceLesson: pattern-why
summary: First-class functions make strategies and simple commands small.
---

## Patterns and language features

The GoF wrote for C++ and Smalltalk in the early 1990s. Several of their patterns exist to work around missing language features.

In a 1996 talk, Peter Norvig argued that **16 of the 23** patterns have qualitatively simpler implementations in dynamic languages such as Lisp and Dylan, at least for some of their uses. Some become invisible altogether. The same is largely true of Python:

| Pattern | What Python gives you |
|---|---|
| Strategy | Pass a function |
| Command | Pass a function or closure |
| Iterator | `__iter__`, `__next__`, generators |
| Singleton | A module-level object |
| Factory method | Classes are callables |
| Template method | Often just pass a hook |

Older Java examples often use an interface and explicit classes; Java 8 and later also support lambdas and method references for functional-interface strategies. In Python, `sorted` takes a `key` function, and that *is* the strategy pattern:

```python
words = ["pear", "Fig", "apple"]
print(sorted(words))
# ['Fig', 'apple', 'pear']
# Compare lowercase keys, return words.
print(sorted(words, key=str.lower))
# ['apple', 'Fig', 'pear']
```

(For the ASCII letters here, uppercase F precedes lowercase a and p in code-point order. This is not a universal ordering rule for all Unicode upper- and lowercase letters.)

The pattern has not disappeared. The *problem* (let the caller choose the rule) is still there; the language just makes the *solution* a one-liner. Knowing the pattern still tells you the consequences, for instance that every strategy must accept the same arguments.

## Key takeaways
- First-class functions make strategies and simple commands small.
- A key function changes sorting behaviour while preserving the caller’s interface.
- A short implementation still has the pattern’s constraints and trade-offs.

## Further reading
- [Design Patterns in Dynamic Languages — Peter Norvig](https://www.norvig.com/design-patterns/)
- [Sorting techniques — Python documentation](https://docs.python.org/3/howto/sorting.html)
