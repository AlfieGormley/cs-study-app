---
id: auto-regex-automaton-engines
title: How automaton engines control repeated work
level: advanced
minutes: 3
sourceLesson: auto-regex-engines
summary: Set simulation merges equivalent active states, while lazy DFAs cache reachable subsets.
---

In this unit, m is the compiled pattern size and n is the input length. Bounds concern one search, with input and pattern measured in the chosen engine’s units.

## How automaton engines avoid it

RE2, Go regexp and Rust regex prevent unrestricted repeated exploration for their supported single searches. Implementations can combine several methods, including bounded memoized path exploration. The main ideas:

1. **Thompson NFA simulation** (the earlier NFA and Thompson-construction units): track the set of active states. O(m) per character, where m is the compiled pattern size.
2. **Pike VM**: the same, but each active matching state carries its capture-group positions, with a priority order so results match Perl's leftmost-first semantics.
3. **Lazy DFA**: cache subset-construction states as they are discovered. A cached transition can be followed with a table lookup; the transition reuse fraction is workload-dependent. RE2 bounds the cache's memory; if it fills too often, it falls back to the NFA.
4. **Literal prefilters**: scan for a required fixed string (say `ERROR` in `ERROR.*timeout`) with fast substring search, and only run the automaton near hits.

Go's documentation states the guarantee directly: matching is "guaranteed to run in time linear in the size of the input". Rust's says searches are worst case O(m · n), with m the pattern size and n the input length.

### The price

Features that are not regular, or are expensive to simulate, are left out:

- **Backreferences** like `(\w+) \1`. General backreferences can express non-regular languages, although individual backreference patterns can still be regular; `^(..+)\1+$` on a string of a's matches exactly when the length is composite. General backreferences cannot be implemented by ordinary finite automata. This does not mean every individual backreference pattern is slow or non-regular.
- **Lookaround** (`(?=...)`, `(?<=...)`) is unsupported in RE2, Go and Rust's `regex`. .NET's NonBacktracking mode also excludes lookarounds and backreferences.
- **Atomic groups and possessive quantifiers** can change which strings match. They have meaning beyond a particular execution algorithm: PCRE2’s DFA-style matcher supports them with documented semantics. RE2, Go and Rust regex omit this syntax.

Linear time is per search. Rust's documentation notes that iterating over **all** matches can be O(m · n²) in the worst case, where m is the compiled pattern size including counted-repeat expansion and n is the input length in bytes: up to n searches, each linear. And large patterns cost memory: counted repetition of a Unicode class, such as `\w{200}`, compiles to a big automaton, which is why these libraries enforce size limits on compiled patterns.

## Key takeaways
- Set simulation merges equivalent active states, while lazy DFAs cache reachable subsets.
- Supported syntax and per-search guarantees matter; iterating all matches can have a different bound.

## Further reading
- [Go regexp matching guarantee](https://pkg.go.dev/regexp)
- [Rust regex guarantees](https://docs.rs/regex/latest/regex/)
- [Russ Cox: matching in the wild](https://swtch.com/~rsc/regexp/regexp3.html)
