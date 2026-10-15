---
id: auto-regex-defences
title: Choosing engines and defending validators
level: advanced
minutes: 3
sourceLesson: auto-regex-engines
summary: Removing ambiguity must preserve the intended full-match language and capture behaviour where needed.
---

## Defences

1. **Use a linear-time engine for untrusted input or untrusted patterns.** Python has the `google-re2` bindings; Java has RE2/J; .NET 7+ has `RegexOptions.NonBacktracking`; V8 described an experimental linear engine and /l flag in a 2021 article; availability depends on runtime version and runtime command-line options, so this is not a portable JavaScript feature. Bound pattern size, compilation resources and input volume even with linear matching.
2. **Remove ambiguity.** `(a+)+` is just `a+`. `(\w+\s?)*` has the same full-match language as `(\w+\s)*\w*`, but in the second form every word must end at a space, so each string can be matched only one way. Captured-group results can differ. Unanchored searches also need separate complexity analysis.
3. **Use atomic groups or possessive quantifiers** where the engine has them. Python 3.11 added both: `(?>a+)+$` and `(a++)+$` eliminate that nested pattern’s repeated splitting because the inner group cannot give back characters. Atomicity does not make every surrounding search safe and can change accepted input.
4. **Bound the input.** Cap field lengths before matching. Reject overlong values rather than validating only a truncated prefix: truncation can hide an invalid suffix.
5. **Set timeouts** where supported: .NET's `Regex` accepts a match timeout. Python's `re` and Java's `java.util.regex` have none built in, so use a killable process or an execution boundary that actually stops the work on deadline. Timing out a waiting thread does not necessarily stop the underlying match.
6. **Test with failing inputs.** Long almost-matches (many a's then a wrong character) are what expose backtracking. Static analysers and fuzzers for ReDoS exist for several languages.
7. **Don't use regex for nested structure.** Formal regular expressions cannot recognise arbitrary nesting. Bounded nesting and richer engine features are different cases; use a suitable parser for general structured formats.

## Choosing an engine

- **Backtracking** is right when you need backreferences or lookaround, patterns are written by your own developers, and inputs are bounded. Check the chosen implementation, input-length caps and required features; developer-authored patterns can also be vulnerable.
- **Automaton-based** is right when patterns or inputs come from users (search boxes, WAF rules, application event log filters, user-supplied validation), when inputs are large (grep over gigabytes), or when predictable scaling matters. This still requires explicit caps on memory and execution time, plus workload testing.

## Key takeaways
- Removing ambiguity must preserve the intended full-match language and capture behaviour where needed.
- Combine suitable engines with bounded resources, failing-input tests and enforceable execution deadlines.

## Further reading
- [Python re: syntax and atomic groups](https://docs.python.org/3/library/re.html)
- [RE2 supported syntax](https://github.com/google/re2/wiki/Syntax)
- [Rust regex guarantees](https://docs.rs/regex/latest/regex/)
