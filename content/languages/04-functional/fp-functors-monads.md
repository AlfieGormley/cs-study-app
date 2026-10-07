---
id: fp-functors-monads
title: Functors and monads, explained practically
level: intermediate
minutes: 13
summary: What map and flatMap really do, why "a value in a box" is a useful pattern, and how Optional, Result, lists, Promises and async/await are all the same idea in disguise.
---

Monads have a reputation for being impossible to explain. The reputation is undeserved. If you've written `user?.address?.city` in JavaScript, chained `.then()` on a Promise, used Rust's `?` operator or written a list comprehension with two `for` clauses, you've used related chaining patterns. These are useful analogies, not a claim that every listed API satisfies all monad laws.

This lesson skips the category theory. It starts from a practical problem, builds the two tools that solve it (`map` and `flat_map`) and then shows the same two tools turning up all over everyday code.

## The problem: values with baggage

Plenty of functions don't return a plain value. They return a value **plus something extra**:

| Returns | The extra bit |
|---|---|
| `Optional[User]` | might be missing |
| `Result[int, str]` | might be an error |
| `list[Route]` | could be 0, 1 or many |
| `Promise<Response>` | eventual fulfillment or rejection; may already be settled |

Call these wrapped values **boxes**. The box carries the value and its baggage together, which makes the possibility of absence explicit; language and tooling determine whether it must be handled.

The cost is that every time you want to do something with the value inside, you have to open the box, check the baggage, do the work and put the result back. Do that five times in a row and you get the familiar staircase:

```python
user = find_user(uid)
if user is not None:
    team = find_team(user)
    if team is not None:
        lead = find_lead(team)
        if lead is not None:
            return lead.email
return None
```

Every step is the same three moves. Functors and monads are just names for **writing those moves once**, inside the box type, so callers don't repeat them.

## Functors: boxes you can map over

Here's a minimal optional box in Python:

```python
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
Some(3).map(lambda x: x + 1).map(str)
# Some('4')
Nothing.map(lambda x: x + 1)
# Nothing
```

That's all a **functor** is: a box type with a sensible `map`. You know several already:

- **Lists**: `map(f, xs)` applies `f` to every element and keeps the list shape.
- **Optionals**: Java's `Optional.map`, Rust's `Option::map`, Swift's `Optional.map`.
- **Promises**: `p.then(f)` where `f` returns a plain value.
- **Dictionaries' values**, **trees**, **parsers**: anything where "apply this to what's inside" makes sense.

A lawful functor obeys identity (mapping id preserves the value) and composition (mapping f then g equals mapping g after f). For these container examples, **preserving shape** is a useful intuition. Treat the illustrative Python boxes as values, with pure callbacks and no external mutation. Mapping over a 3-item list gives a 3-item list. Mapping over `Nothing` gives `Nothing`. Mapping the do-nothing function `lambda x: x` gives back the same box. If a "map" quietly dropped elements or turned errors into successes, you couldn't refactor code that uses it safely.

## Where map runs out

Now try the staircase. `find_team` itself returns a `Maybe`, because a user might have no team:

```python
find_user(1).map(find_team)
# Some(Some({'lead': 2}))
```

A box inside a box. `map` boxes whatever `f` returns, and `f` already returned a box. Chain a third step and you'd have three layers, each needing its own unwrap.

The same nesting appears with every box type:

| Box | `map` with a box-returning `f` |
|---|---|
| list | list of lists |
| Optional | Optional of Optional |
| Result | Result of Result |
| Promise-like wrapper with a separate map | nested wrapper; JavaScript then instead auto-flattens |

What we want is "map, then squash the two layers into one". That operation has many names: `flat_map`, `flatMap`, `and_then`, `bind`, `SelectMany`, `>>=`, and in JavaScript, `then`.

## Monads: boxes you can chain

Add `flat_map` to the class:

```python
    def flat_map(self, f):
        if not self.ok:
            return self
        # f already returns a box
        return f(self.value)
```

The only difference from `map` is the last line: `f` returns a box, so we return it as-is instead of wrapping it again. Now the staircase is flat:

```python
(find_user(uid)
    .flat_map(find_team)
    .flat_map(find_lead)
    .map(lambda u: u.email))
```

Each step runs only if the previous one produced a value. The first `Nothing` short-circuits the rest of the chain, exactly like the nested `if`s, but the checking lives in one place.

A **monad** provides two operations satisfying the laws below; a box is an intuition, since state and continuation monads need not be containers:

1. **wrap**: put a plain value into a box (`Some(x)`, `[x]`, `Ok(x)`, `Promise.resolve(x)`). Haskell calls it `return` or `pure`.
2. **flat_map**: run a box-returning function on the contents and keep a single layer of box.

That's it. Every monad is a functor too, because `map(f)` is just `flat_map` followed by wrapping `f`'s result.

> [!tip] The one-sentence version
> A monad lets you write a sequence of steps that each return a boxed value, and the box type decides what "and then" means: stop on missing, stop on error, try every option, or wait.

## The same pattern, five times

The power of the idea is that **"and then" means something different for each box**, but the code shape is identical.

### Optional: stop when something's missing

Kotlin, Swift, C# and JavaScript build it into syntax:

```javascript
const city = user?.address?.city;
```

`?.` behaves like short-circuit chaining for null/undefined; it is an analogy to optional bind, not a literal generic flat_map method. In Rust, `user.and_then(|u| u.address)`; in Java, `opt.flatMap(User::getAddress)`.

### Result: stop on the first error, keep the message

`Optional` tells you *that* something failed. `Result` (Haskell calls it `Either`) tells you *why*:

```python
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
fn load(p: &str) -> Result<Cfg, Error> {
    let text = fs::read_to_string(p)?;
    let cfg = parse(&text)?;
    Ok(cfg)
}
```

Here each `?` means "if this is an Err, convert the error as required and return it; otherwise unwrap the Ok". The schematic load function assumes compatible Cfg, Error, fs and parse definitions. That's `flat_map` written as a postfix operator.

### List: try every possibility

For lists, `flat_map` means "for each item, produce zero or more results, and collect them all in one flat list":

```python
def flat_map(xs, f):
    return [y for x in xs for y in f(x)]

flat_map([1, 2, 3], lambda x: [x, x * 10])
# [1, 10, 2, 20, 3, 30]
```

Returning `[]` drops an item, returning `[x]` keeps it, returning several items fans out. A list comprehension with two `for` clauses is chained `flat_map`:

```python
[(x, y) for x in [1, 2] for y in "ab"]
# [(1,'a'), (1,'b'), (2,'a'), (2,'b')]
```

JavaScript has `Array.prototype.flatMap`; C# LINQ calls it `SelectMany`; Spark has `rdd.flatMap`.

### Promise: wait, then continue

`then` is `flat_map` for "not here yet". If the callback returns another Promise, `then` waits for it and you get a flat `Promise<T>`, not a Promise of a Promise:

```javascript
fetch(url)
  .then(r => r.json())  // returns Promise
  .then(data => data.items.length);
```

And `async`/`await` is the same chain written as straight-line code. Each `await` is "flat_map the rest of the function onto this Promise".

```javascript
const r = await fetch(url);
const data = await r.json();
return data.items.length;
```

### Haskell's do-notation

Haskell generalises that trick to **every** monad. `do` blocks are sugar for a chain of `>>=` (bind, i.e. `flat_map`):

```haskell
leadEmail uid = do
  user <- findUser uid
  team <- findTeam user
  lead <- findLead team
  return (email lead)
```

The same chaining shape works when all three functions use a compatible monad: Maybe, Either String, list or IO. The box type decides what each `<-` does. Scala's `for` comprehensions and F#'s computation expressions do the same job.

## The rules, in plain words

There are three "monad laws". You'll rarely write them down, but they're what make refactoring chains safe:

1. **Wrapping then chaining does nothing extra.** `Some(x).flat_map(f)` is the same as `f(x)`.
2. **Chaining with wrap does nothing.** `m.flat_map(Some)` is the same as `m`.
3. **Grouping doesn't matter.** `m.flat_map(f).flat_map(g)` equals `m.flat_map(lambda x: f(x).flat_map(g))`.

Rule 3 is the useful one in practice: it says you can pull a few steps out into a helper function, or inline one, without changing behaviour. It justifies regrouping lawful chains. Refactoring real async code must also preserve cancellation, exception boundaries and observable microtask scheduling.

## Pitfalls and trade-offs

### JavaScript Promises bend the rules

`then` acts as `map` *or* `flat_map` depending on what the callback returns, and Promises flatten automatically: Promise.resolve(p) returns p itself when p is a Promise whose constructor matches the receiver. Standard, unmodified Promises adopt returned Promises/thenables rather than fulfilling with a nested Promise value. That's convenient, but it breaks rule 1 in an edge case: if `x` is itself a Promise (or any object with a `then` method), `Promise.resolve(x).then(f)` unwraps `x` first, so `f` receives something different from what `f(x)` would. That's why purists say Promises are "not quite" monads.

### Java's Optional.map swallows null

If the function passed to `Optional.map` returns `null`, you get an empty `Optional`, not a box containing `null`. Usually helpful, occasionally surprising when `null` was a meaningful result.

### Different boxes don't stack for free

A function returning `Promise<Result<User, Error>>` has two layers of baggage, and `then` only knows about one. You end up unwrapping the inner `Result` by hand in every step. Haskell solves this with **monad transformers**; most other ecosystems settle for a pragmatic convention, such as "Promises reject on error", or libraries like Effect (TypeScript) and ZIO (Scala).

### Don't force it in Python

Python has no `?` operator or do-notation, so a hand-built `Maybe` class often reads worse than early returns. Use the *idea* (one place that handles absence or errors) rather than the class hierarchy. In Python, the idiomatic version is usually exceptions, `None` checks with early `return`, or generators and comprehensions.

### Exceptions versus Result

Exceptions also short-circuit a sequence of steps, so why bother with `Result`? A Result can expose failure in the return type, but handling enforcement varies: Rust warns on unused Results by default rather than universally rejecting them. Exceptions can also be declared, such as Java checked exceptions and Swift throws. Rust, Go-style error returns and Swift's `throws` all sit at different points on that trade-off.

## Key takeaways
- A **functor** is a box with a `map` that transforms the contents and keeps the shape.
- `map` with a function that itself returns a box gives a box in a box; `flat_map` maps and flattens in one step.
- A **monad** is a box with *wrap* and *flat_map*; the box decides what "and then" means: skip on missing, stop on error, try all options, or wait.
- Optional chaining, Rust ?, comprehensions and async APIs illustrate related chaining patterns, with language-specific laws and effects.
- The laws boil down to "wrapping adds nothing" and "you can regroup steps freely", which is what makes refactoring chains safe.
- Promises auto-flatten, Java's Optional maps `null` to empty, and stacking different boxes needs extra machinery.

## Further reading
- [Monad (functional programming) — Wikipedia](https://en.wikipedia.org/wiki/Monad_(functional_programming))
- [Functors, Applicatives, And Monads In Pictures — Aditya Bhargava](https://www.adit.io/posts/2013-04-17-functors,_applicatives,_and_monads_in_pictures.html)
- [A Fistful of Monads — Learn You a Haskell](https://learnyouahaskell.github.io/a-fistful-of-monads.html)
- [Recoverable Errors with Result — The Rust Book](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)
- [Using promises — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises)
- [Railway Oriented Programming — Scott Wlaschin](https://fsharpforfunandprofit.com/rop/)
- [Primary verification source 1](https://hackage.haskell.org/package/base/docs/Control-Monad.html)
- [Primary verification source 2](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html)
- [Primary verification source 4](https://tc39.es/ecma262/multipage/control-abstraction-objects.html)
- [Primary verification source 5](https://docs.python.org/3/library/functions.html#int)
