---
id: test-property-strategies
sourceLesson: test-tdd-property
title: Design useful properties and reach difficult inputs
level: intermediate
minutes: 4
summary: Use round-trip properties, test oracles, test invariants, idempotence and metamorphic relations for different contracts.
---

A property test needs both a truthful rule and generators that reach useful cases. Assume `from hypothesis import given, example, assume` and `from hypothesis import strategies as st` for the API examples below. `User` stands for an application class with an `age` constructor argument.

### Strategies

A **Hypothesis strategy** describes how to generate values:

- `st.integers(min_value=0)`, `st.floats(allow_nan=False)`, `st.text()`, `st.booleans()`
- `st.lists(st.integers(), max_size=50)`, `st.dictionaries(...)`, `st.tuples(...)`
- `st.sampled_from(["GBP", "EUR"])`, `st.builds(User, age=st.integers(0, 120))`
- `.map(...)` and `.filter(...)` to transform; `assume(cond)` inside a test to discard unsuitable inputs.

### Finding good properties

"What property?" is the hard part. Common patterns:

| Pattern | Example |
|---|---|
| Round-trip property | Decode the encoded value; recover the original |
| Test oracle | Fast implementation agrees with simple reference |
| Test invariant | sort keeps length and items |
| Idempotence | Repeating the operation changes nothing |
| Metamorphic | Add a restrictive filter: no new results |

The first and fourth rows are mathematical statements about functions. Written as maths, they say what must hold for every generated input:

```formula
decode(encode(x)) = x   for all x
f(f(x)) = f(x)   for all x
where
x: any input the generator produces, for example a string or a list
encode: a function that converts a value into another form, such as Python value to JSON text
decode: the function that reverses encode, such as JSON text back to a Python value
f: the function under test, for example one that trims spaces from both ends of a string
In words: decoding what you encoded gives back the original, and applying an idempotent function a second time changes nothing.
```

For example, trimming `"  hi "` gives `"hi"`, and trimming `"hi"` again still gives `"hi"`, so trimming is idempotent. Doubling a number is not: 3 becomes 6, then 12. The round-trip property rule holds only for inputs the encoder represents faithfully and that compare equal to themselves. The float `NaN` ("not a number") fails the second condition: it is not equal even to itself, so the decoded copy never compares equal to the original, and such inputs are usually excluded from the strategy.

Python’s `json.dumps` returns JSON text as a `str`, and `json.loads` reads it back. Acyclic JSON-native values within recursion and memory bounds can recover the original value after encoding and decoding: string-keyed dictionaries, lists, strings, booleans, `None`, supported integers and finite floats. Tuples instead decode as lists, and non-string dictionary keys can change. With the unchanged default formatting, serialising a decoded serialisation is stable for this restricted domain.

The **test oracle** pattern used for `merge` is particularly strong: a simple, obviously correct implementation (here `sorted`) checks a fast, clever one.

## Limits of property-based testing

Generation is strategy-guided, not uniform random sampling, and can be deterministic under the CI profile or explicit settings. The default `max_examples=100` limits satisfying generated cases in a successful search, not necessarily all calls including rejected inputs and shrinking. Some bugs need rare inputs.

A run-length encoder that writes `"aaab"` as `"3a1b"`, with a decoder that reads one digit then one character, breaks on any run of 10 or more (it treats `0` as the character for a one-character run, leaving `a` unmatched). The round-trip property is useful, but a generic text strategy is not a guarantee of reaching long repeated runs. Generate such runs deliberately and pin the known counterexample. No measured rate of finding a failure is asserted here.

Remedies:

- Design strategies that reach the interesting region (small alphabets, boundary values, long runs).
- Pin known-tricky cases with `@example("a" * 10)`, which runs in the explicit-example phase (enabled by default) before generated inputs.
- Raise `max_examples` for important properties, perhaps in a nightly run.

Property tests also run slower than single examples and need more thought to write. They complement example tests rather than replace them: examples document specific expectations clearly, properties hunt for what you forgot.

> [!example] Stateful testing
> Hypothesis can also generate *sequences of operations* (add, remove, query) against a system and a simple model of it, checking they agree after every step. This is how bugs in caches, databases and data structures that only appear after a particular series of calls get found.

## Key takeaways
- Use round-trip properties, test oracles, test invariants, idempotence and metamorphic relations for different contracts.
- A generic strategy may miss rare regions; deliberately generate interesting shapes.
- Pin known cases with explicit examples and keep example tests alongside properties.

## Further reading
- [Hypothesis documentation](https://hypothesis.readthedocs.io/en/latest/)
- [What is property-based testing? — Hypothesis](https://hypothesis.works/articles/what-is-property-based-testing/)
- [Useful property patterns — Hypothesis](https://hypothesis.works/articles/what-is-property-based-testing/)
- [JSON encoding and decoding — Python docs](https://docs.python.org/3/library/json.html)
