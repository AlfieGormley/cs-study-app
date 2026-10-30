---
id: sep-knowledge-abstractions
title: Share knowledge without inventing the wrong abstraction
level: intermediate
minutes: 4
summary: DRY targets knowledge that must change together, rather than identical text.
sourceLesson: sep-dry-kiss-yagni
---

Three short slogans shape a huge amount of everyday design argument. Each is useful. Each is also routinely misquoted, and the misquoted versions can do real damage of their own. This lesson starts with DRY.

| Slogan | Expands to | Warns against |
|---|---|---|
| DRY | Don't repeat yourself | Scattered knowledge |
| KISS | Keep it simple | Needless complexity |
| YAGNI | You aren't gonna need it | Speculative features |

## DRY: it's about knowledge, not text

Andy Hunt and Dave Thomas coined DRY in *The Pragmatic Programmer* (1999):

> Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.

Note the word **knowledge**. DRY is not "never have two similar-looking lines of code". It is "never have two places that must be kept in step by hand".

### Real duplication

```python
# signup.py
if len(password) < 12:
    raise WeakPassword()

# reset.py
if len(password) < 10:
    raise WeakPassword()
```

There is one business rule ("minimum password length") with two representations, and they have already drifted apart. That is exactly what DRY targets:

```python
# passwords.py: one home for the rule
MIN_LENGTH = 12

def check(password):
    if len(password) < MIN_LENGTH:
        raise WeakPassword()
```

DRY applies well beyond code: a database schema and an ORM model, an API and its documentation, a config value copied into three YAML files. Generating one from the other (or deriving both from a single source) keeps them in step.

### Accidental duplication

```python
def vat(price):
    return round(price * 0.2, 2)

def staff_discount(price):
    return round(price * 0.2, 2)
```

The code is identical, but the knowledge isn't. VAT is set by government; the staff discount is set by HR. They will change for different reasons at different times. Merging them into `twenty_percent(price)` couples two unrelated rules, and the first time one changes, someone adds a parameter to tell them apart.

> [!tip] The DRY question
> Don't ask "do these look the same?" Ask "if one of these changed, would the other *have* to change too?" Only a yes means duplication.

## The wrong abstraction

Sandi Metz's widely cited post puts it bluntly: **duplication is far cheaper than the wrong abstraction**. The lifecycle she describes:

1. A developer sees duplication and extracts a shared function.
2. A new requirement *almost* fits, so someone adds a parameter and an `if`.
3. Repeat. The function grows flags and branches serving different callers.
4. Nobody dares to touch it, because every caller depends on a different path.

```python
def export(rows, fmt, legacy=False,
           skip_header=False, eu=False,
           for_finance=False):
    ...
```

The fix she recommends is counter-intuitive: **inline the abstraction back into each caller**, delete the paths each caller doesn't use, and then look for the real shared idea, if there is one.

### The rule of three

A heuristic attributed to Don Roberts and popularised by Martin Fowler's *Refactoring*: the first time, just write it. The second time, wince but duplicate. The **third** time, refactor. By then you have three examples, which is usually enough to see what is truly common and what varies.

## Key takeaways
- DRY targets knowledge that must change together, rather than identical text.
- Unrelated business rules should remain free to change independently.
- Flags can signal a wrong abstraction; inline and reconsider what is actually shared.

## Further reading
- [Hunt and Thomas: DRY](https://media.pragprog.com/titles/tpp20/dry.pdf)
- [Sandi Metz: The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- [Rule of three (computer programming)](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming))
