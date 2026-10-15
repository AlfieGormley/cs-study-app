---
id: fp-result-errors
title: Optional and Result error chains
level: intermediate
minutes: 3
sourceLesson: fp-functors-monads
summary: Result chains preserve the first error and skip later success callbacks.
---

Result chains preserve the first error and skip later success callbacks. This unit develops that mechanism using the earlier units as prerequisites.

## The same pattern, five times

The power of the idea is that **"and then" means something different for each box**, but the code shape is identical.

## Optional: stop when something's missing

Kotlin, Swift, C# and JavaScript build it into syntax:

```javascript
// Guard each nullable access in the chain.
const city = user?.address?.city;
```

`?.` behaves like short-circuit chaining for null/undefined; it is an analogy to optional bind, not a literal generic flat_map method. In Rust, `user.and_then(|u| u.address)`; in Java, `opt.flatMap(User::getAddress)`.

## Result: stop on the first error, keep the message

`Optional` tells you *that* something failed. `Result` (Haskell calls it `Either`) tells you *why*:

```python
# An Err bypasses later success callbacks.
class Result:
    def __init__(self, value, ok):
        self.value, self.ok = value, ok

    def flat_map(self, f):
        if not self.ok:
            return self
        return f(self.value)

    def __repr__(self):
        tag = "Ok" if self.ok else "Err"
        return f"{tag}({self.value!r})"

def Ok(v): return Result(v, True)
def Err(e): return Result(e, False)

def parse(s):
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"not a number: {s}")

def positive(n):
    if n > 0:
        return Ok(n)
    return Err("must be > 0")

parse("4").flat_map(positive)
# Ok(4)
parse("-2").flat_map(positive)
# Err('must be > 0')
parse("abc").flat_map(positive)
# Err('not a number: abc')
```

This is sometimes called **railway-oriented programming**: two tracks, success and failure, and once you're on the failure track every later step is skipped.

Rust makes it look like ordinary code with the `?` operator:

```rust
// Propagate read or parse errors early.
fn load(p: &str) -> Result<Cfg, Error> {
    let text = fs::read_to_string(p)?;
    let cfg = parse(&text)?;
    Ok(cfg)
}
```

Here each `?` means "if this is an Err, convert the error as required and return it; otherwise unwrap the Ok". The schematic load function assumes compatible Cfg, Error, fs and parse definitions. That's `flat_map` written as a postfix operator.

## Key takeaways
- Result chains preserve the first error and skip later success callbacks.
- Rust question-mark propagation also performs the required error conversion.

## Further reading
- [Rust Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)
- [Rust Question](https://doc.rust-lang.org/reference/expressions/operator-expr.html)
- [Railway](https://fsharpforfunandprofit.com/rop/)
- [Java Optional](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html)
