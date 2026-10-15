---
id: type-domain-models
title: Representing valid domain states
level: intermediate
minutes: 3
sourceLesson: type-adts-pattern-matching
summary: Explicit state alternatives tie required data to each valid state.
---

Sum types connect each state to exactly the data it needs. Their design value becomes clearer when compared with independent flags and optional fields.

## Make illegal states unrepresentable

Yaron Minsky's slogan from Jane Street sums up the design use. Compare two models of a network connection:

```ts
// 2 × 2 × 2 = 8 shapes (each optional
// field present or absent), most nonsense
type Conn = {
  connected: boolean;
  sessionId?: string;
  error?: string;
};

// three explicit state alternatives
type Conn2 =
  | { state: "idle" }
  | { state: "live"; sessionId: string }
  | { state: "failed"; error: string };
```

With the first, nothing stops `connected: false` with a `sessionId`, and every reader has to guess. With the second, narrowing to the live alternative guarantees a session id under the checked type. TypeScript structural typing can still admit additional properties; this is not runtime validation or a guarantee of exact object shape. Related advice: **parse, don't validate**. Turn raw input into a precise type once at the boundary, and the rest of the code can rely on it.

## The expression problem

ADTs and classes make opposite things easy. Philip Wadler named this the **expression problem** (1998):

| | Add a new operation | Add a new variant |
|---|---|---|
| ADT + match | Easy: one new function | Edit every match |
| Classes | Edit every class | Easy: one new class |

With an `Expr` ADT, adding `prettyPrint` is one function; adding `Div` touches `eval`, `prettyPrint` and every other match (and the compiler lists them). With an `Expr` class hierarchy it's the reverse. Choose ADTs when the set of cases is stable and operations grow, as in compilers and protocol messages.

## Pitfalls

- **Wildcard catch-alls.** A `_ =>` arm silences exhaustiveness checking, so a new variant is silently handled by the default. Prefer listing cases.
- **Order of arms.** A general pattern above a specific one makes the specific one unreachable. Rust and GHC warn about this.
- **Boolean blindness.** `process(true, false)` says nothing. An enum like `Mode::DryRun` makes intent explicit.
- **Unwrapping everywhere.** `.unwrap()` and Haskell's `fromJust` turn `None` back into a crash, undoing the point of `Option`.
- **Python's `match` isn't `switch`.** A bare name in a `case` binds a new variable rather than comparing against an existing one. `case RED:` matches anything; use `case Color.RED:`.

## Key takeaways
- Explicit state alternatives tie required data to each valid state.
- ADTs favour adding operations; class hierarchies favour adding variants in the simple expression-problem comparison.
- Catch-alls, blind booleans and unconditional unwrapping weaken the design benefits.

## Further reading
- [Jane Street: Effective ML revisited](https://blog.janestreet.com/effective-ml-revisited/)
- [Alexis King: Parse, don’t validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
- [Wadler: The expression problem](https://homepages.inf.ed.ac.uk/wadler/papers/expression/expression.txt)
- [The Rust Book: Pattern syntax](https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html)
