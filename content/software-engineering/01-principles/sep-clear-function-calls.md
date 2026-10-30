---
id: sep-clear-function-calls
title: Make function calls self-explanatory
level: basic
minutes: 3
summary: Keyword-only arguments prevent silent positional mix-ups.
sourceLesson: sep-clean-code
---

A call site is where most readers meet a function, often without opening its definition. This lesson is about making the call itself say what it does.

A positional call relies on the reader remembering the parameter order. Keyword arguments spell out the mapping. A bare `*` in a Python definition goes further: it requires all following parameters to be passed by name, so a positional attempt raises `TypeError` before the body executes. This prevents swapping equally plausible integers without a visible clue.

### Few parameters, no flag arguments

Each parameter is something a caller must understand and get right. Three positional parameters of the same type are an accident waiting to happen:

```python
# Positions alone hide transfer direction.
transfer(100, 42, 17)  # which is which?
```

Python's keyword-only arguments help:

```python
# The bare * requires names at the call.
def transfer(*, amount, src, dst): ...

transfer(amount=100, src=42, dst=17)
```

A **flag argument** (a boolean that changes what the function does) is often a sign the function does two things:

```python
# Named operations expose the chosen mode.
render(doc, True)       # True what?

# Prefer two named functions
render_preview(doc)
render_print(doc)
```

Fowler's advice is to prefer separate, named functions, with one exception he notes: when the boolean genuinely comes from data (say, a checkbox value passed straight through), a flag can be justified. Keyword-only arguments at least make such a flag readable at the call site.

When many parameters always travel together (`street, city, postcode`), introduce a **parameter object** (`Address`).

## Key takeaways
- Keyword-only arguments prevent silent positional mix-ups.
- A behaviour-changing flag can hide several jobs behind one function name.
- Group parameters that represent one domain value rather than adding unrelated arguments.

## Further reading
- [PEP 3102: Keyword-Only Arguments](https://peps.python.org/pep-3102/)
- [Martin Fowler: Flag Argument](https://martinfowler.com/bliki/FlagArgument.html)
