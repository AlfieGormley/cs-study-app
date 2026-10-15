---
id: fp-maybe-mapping
title: Mapping values with absence
level: intermediate
minutes: 5
sourceLesson: fp-functors-monads
summary: An optional wrapper centralises handling of present and absent values.
---

Monads have a reputation for being impossible to explain. The reputation is undeserved. If you've written `user?.address?.city` in JavaScript, chained `.then()` on a Promise, used Rust's `?` operator or written a list comprehension with two `for` clauses, you've used related chaining patterns. These are useful analogies, not a claim that every listed API satisfies all monad laws.

This lesson skips the category theory. It starts from a practical problem, builds the two tools that solve it (`map` and `flat_map`) and then shows the same two tools turning up all over everyday code.

## The problem: values with baggage

Plenty of functions don't return a plain value. They return a value plus something extra:

| Returns | The extra bit |
|---|---|
| `Optional[User]` | might be missing |
| `Result[int, str]` | might be an error |
| `list[Route]` | could be 0, 1 or many |
| `Promise<Response>` | eventual fulfillment or rejection; may already be settled |

Call these wrapped values **wrapped values**. The box carries the value and its baggage together, which makes the possibility of absence explicit; language and tooling determine whether it must be handled.

The cost is that every time you want to do something with the value inside, you have to open the box, check the baggage, do the work and put the result back. Do that five times in a row and you get the familiar staircase:

```python
# Each absent value skips later lookups.
user = find_user(uid)
if user is not None:
    team = find_team(user)
    if team is not None:
        lead = find_lead(team)
        if lead is not None:
            return lead.email
return None
```

Every step is the same three moves. Functors and monads are just names for writing those moves once, inside the box type, so callers don't repeat them.

## Functors: boxes you can map over

Here's a minimal optional box in Python:

```python
# map preserves the missing-value branch.
class Maybe:
    def __init__(self, value, ok):
        self.value = value
        self.ok = ok

    def __repr__(self):
        if not self.ok:
            return "Nothing"
        return f"Some({self.value!r})"

    def map(self, f):
        if not self.ok:
            return self
        return Some(f(self.value))

def Some(v): return Maybe(v, True)
Nothing = Maybe(None, False)
```

`map` says: "if there's a value, apply `f` to it and box the result; if not, stay empty". The caller never writes the `if`:

```python
# An absent value skips the callback.
Some(3).map(lambda x: x + 1).map(str)
# Some('4')
Nothing.map(lambda x: x + 1)
# Nothing
```

For these examples, a **functor** is a type constructor with a `map` obeying the identity and composition laws below. The box picture helps with containers; function and other functors need not be literal containers. You know several already:

- **Lists**: `map(f, xs)` applies `f` to every element and keeps the list shape.
- **Optionals**: Java's `Optional.map`, Rust's `Option::map`, Swift's `Optional.map`.
- **JavaScript promises**: `p.then(f)` gives a related mapping pattern when callbacks return ordinary non-thenable values. Arbitrary thenables and observable scheduling need additional care; this is an analogy, not an unrestricted functor instance.
- Dictionaries' values, **trees**, **parsers**: anything where "apply this to what's inside" makes sense.

A lawful functor obeys two **functor laws**, identity and composition:

```formula
map(id, m) = m
map(g ∘ f, m) = map(g, map(f, m))
where
map: the box type's map operation: apply a function to what's inside and keep the box
m: any box value, such as Some(3), Nothing or a list
id: the identity function, which returns its argument unchanged: id(x) = x
f, g: any two pure functions on the contents
∘: function composition: (g ∘ f)(x) = g(f(x)), read "g after f"
In words: mapping the do-nothing function changes nothing, and mapping f and then g in two passes gives the same result as mapping "g after f" in one pass.
```

For example, mapping "add 1" over [1, 2, 3] gives [2, 3, 4], and mapping "double" over that gives [4, 6, 8]; mapping the single function "add 1, then double" over [1, 2, 3] gives the same [4, 6, 8]. For these container examples, preserving shape is a useful intuition. Treat the illustrative Python boxes as values, with pure callbacks and no external mutation. Mapping over a 3-item list gives a 3-item list. Mapping over `Nothing` gives `Nothing`. Mapping the do-nothing function `lambda x: x` gives an equal wrapped value under the stated value semantics; it need not return the identical Python object. If a "map" quietly dropped elements or turned errors into successes, you couldn't refactor code that uses it safely.

## Key takeaways
- An optional wrapper centralises handling of present and absent values.
- A lawful map preserves identity and composition under stated value semantics.

## Further reading
- [Haskell base: functor and monad laws](https://hackage.haskell.org/package/base/docs/Control-Monad.html)
- [Java Optional](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html)
- [Rust Option](https://doc.rust-lang.org/std/option/enum.Option.html)
