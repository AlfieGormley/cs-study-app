---
id: sep-failure-types-contracts
title: Choose how a failure becomes part of the contract
level: advanced
minutes: 4
summary: Distinguish a bug from a domain outcome and from an environmental failure.
sourceLesson: sep-error-handling
---

Most code is written for the happy path. Failure paths deserve explicit design: the timeout nobody expected, the exception swallowed three layers down, the retry storm that turned a blip into an outage.

Good error handling isn't about catching everything. It's about deciding, deliberately, **who** should deal with each failure and **what** they need to know to do it.

## Three kinds of failure

Different failures need different responses. Mixing them up is behind much bad error handling.

| Kind | Example | Right response |
|---|---|---|
| Bug | `None` where a user was expected | Crash loudly, fix the code |
| Expected failure | Card declined, file missing | Handle as normal logic |
| Environmental | Network timeout, disk full | Retry, degrade, or report |

- **Bugs** need diagnosis and correction. Do not silently continue as though the operation succeeded. A service may safely contain a failing request or worker, roll back its changes and report the error; process termination is not always necessary.
- **Expected failures** are part of the domain. "Insufficient funds" isn't exceptional to a bank. These deserve explicit types and handling.
- **Environmental failures** arise outside the immediate operation; some are transient and others need intervention. A brief network interruption might clear up, but a full disk or a revoked credential may persist. Choose retries with backoff, timeouts, fallbacks or circuit breakers at a layer that can decide whether they are appropriate.

## Exceptions versus error values

Languages take two broad approaches.

**Exceptions** (Python, Java, C#) separate the error path from the normal flow. An error propagates up the call stack until something catches it.

- Pro: the happy path reads cleanly, and forgetting to inspect a normal return value does not itself swallow a raised exception. A broad handler or an unobserved background task can still hide a failure.
- Con: the error path is invisible at the call site. Any line might throw, and you can't tell from reading it.

**Error values** (Go's `(value, err)`, Rust's `Result<T, E>`) make failure part of the return type.

```
// Wrap the cause with the failing path.
// Go
f, err := os.Open(path)
if err != nil {
    return fmt.Errorf("open %s: %w",
                      path, err)
}
```

- Pro: every failure point is visible, and Rust normally warns when a `Result` marked `must_use` is discarded. This is a lint, not an unconditional compilation error; code can explicitly discard it, so meaningful handling still needs review.
- Con: more ceremony; in Go nothing stops you ignoring `err` (linters help).

Java adds a twist: **checked exceptions** must be caught or declared (`throws IOException`) by code that can propagate them, which makes failures visible in signatures. In practice many teams found them noisy, wrapping them in unchecked exceptions, and later JVM languages such as Kotlin dropped them. A common guideline from Oracle's own tutorial: use checked exceptions for conditions a caller can reasonably recover from, and unchecked (`RuntimeException`) for programming errors.

In Python, exceptions are the idiom. Use them, but make the expected ones explicit types.

## Key takeaways
- Distinguish a bug from a domain outcome and from an environmental failure.
- Exceptions and result values expose failure in different ways; both still require deliberate handling.
- Java checked exceptions make some failures part of the compile-time contract.

## Further reading
- [Oracle Java tutorial: Unchecked Exceptions, the Controversy](https://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html)
- [The Rust Book: Error Handling](https://doc.rust-lang.org/book/ch09-00-error-handling.html)
- [The Go Blog: Error handling and Go](https://go.dev/blog/error-handling-and-go)
