---
id: fp-runtime-tail-guarantees
title: Runtime guarantees for tail calls
level: intermediate
minutes: 3
sourceLesson: fp-recursion-tail-calls
summary: Tail-call support is a language, compiler and runtime contract.
---

Tail-call support is a language, compiler and runtime contract. This unit develops that mechanism using the earlier units as prerequisites.

## Which languages actually do it?

| Language | Tail calls eliminated? |
|---|---|
| Scheme | Yes, required by the standard |
| GHC Haskell, OCaml, Erlang | Tail calls can be eliminated; lazy retained work still matters |
| Scala, Kotlin | Direct self-recursion only |
| Clojure | Only via explicit `recur` |
| JavaScript | Specified for eligible strict-mode calls; engine-dependent |
| Python | No, by design |
| Java, C# | Not guaranteed |
| C, C++ | Often at `-O2`; not guaranteed |

- **Scheme** made proper tail calls part of the language definition, so a tail-call chain need not accumulate caller continuations. Other retained data and argument computation can still grow. Erlang and Elixir servers run forever as tail-recursive loops.
- **JavaScript** added proper tail calls in ES2015 (strict mode only). WebKit documents JavaScriptCore support. Do not assume portable engine support: verify your target runtime. A complete current engine-support matrix is omitted because it was not reliably established in this review.
- **Python** deliberately does not. Guido van Rossum argued that TCO loses stack traces, and that Python programmers should write loops.
- The JVM has no general tail-call instruction, so Scala and Kotlin compile self-recursive tail calls into loops at compile time. Scala does this automatically (`@tailrec` makes the compiler fail if it can't); Kotlin needs the `tailrec` modifier. Clojure makes you write `recur` so the compiler can check it.

## Key takeaways
- Tail-call support is a language, compiler and runtime contract.
- Verify the actual target rather than relying on tail-recursive appearance.

## Further reading
- [Scheme](https://standards.scheme.org/corrected-r7rs/r7rs-Z-H-5.html)
- [Webkit Tail](https://webkit.org/blog/6240/ecmascript-6-proper-tail-calls-in-webkit/)
- [Guido Tail](https://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html)
- [Clojure Recur](https://clojure.org/reference/special_forms)
- [Scala Tail](https://www.scala-lang.org/api/2.13.16/scala/annotation/tailrec.html)
- [Kotlin Tail](https://kotlinlang.org/docs/functions.html)
- [Erlang Functions](https://www.erlang.org/doc/system/eff_guide_functions.html)
