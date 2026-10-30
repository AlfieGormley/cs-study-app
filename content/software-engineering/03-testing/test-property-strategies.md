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

Here are the round-trip and idempotence rows as Hypothesis tests. The strategy builds the JSON-native values Python's `json` module can represent faithfully:

```python
import json

# JSON scalars: NaN and infinity are
# excluded (NaN != NaN), and integers
# kept to a 64-bit range.
i64 = st.integers(-2**63, 2**63 - 1)
finite = st.floats(allow_nan=False,
                   allow_infinity=False)
scalars = (st.none() | st.booleans()
           | i64 | finite | st.text())
# Nest them in lists and str-keyed dicts.
values = st.recursive(
    scalars,
    lambda inner: st.lists(inner)
    | st.dictionaries(st.text(), inner))

@given(values)
def test_json_round_trip(x):
    # Decoding the encoding gives x back.
    assert json.loads(json.dumps(x)) == x

@given(st.text())
def test_strip_is_idempotent(s):
    # A second strip changes nothing.
    once = s.strip()
    assert once.strip() == once
```

Both pass. Trimming `"  hi "` gives `"hi"`, and trimming `"hi"` again still gives `"hi"`, so trimming is idempotent. Doubling a number is not: 3 becomes 6, then 12.

A round-trip property holds only for inputs the encoder represents faithfully and that compare equal to themselves. The float `NaN` ("not a number") fails the second condition: it is not equal even to itself, so the decoded copy never compares equal to the original, which is why the strategy excludes it. Tuples would also fail: `json` decodes them as lists. Choosing the input domain is part of writing the property. Over this domain, two further rules also hold: `json.dumps` always returns a `str`, and with the default formatting unchanged, encoding a decoded value again reproduces the same text (`dumps(loads(dumps(x))) == dumps(x)`).

The **test oracle** pattern used for `merge` is particularly strong: a simple, obviously correct implementation (here `sorted`) checks a fast, clever one.

## Limits of property-based testing

Generation is strategy-guided, not uniform random sampling, and can be deterministic under the CI profile or explicit settings. The default `max_examples=100` limits satisfying generated cases in a successful search, not necessarily all calls including rejected inputs and shrinking. Some bugs need rare inputs.

A run-length encoder that writes `"aaab"` as `"3a1b"`, with a decoder that reads one digit then one character, breaks on any run of 10 or more: `"10a"` is misread as one `"0"`, and the decoder then trips over a stray `a`. The round-trip property is the right rule, but a generic text strategy rarely produces ten identical characters in a row, so the test can pass run after run. Generate such runs deliberately and pin the known counterexample:

```python
# Build strings from runs of 1 to 15
# repeated characters.
runs = st.lists(st.tuples(
    st.sampled_from("ab"),
    st.integers(1, 15)))
texts = runs.map(lambda rs: "".join(
    ch * n for ch, n in rs))

@example("a" * 10)
@given(texts)
def test_rle_round_trip(s):
    assert decode(encode(s)) == s
```

Here `encode` and `decode` are the codec under test. A smaller alphabet alone helps less than you might expect: random two-letter text still seldom contains a run of ten.

Remedies:

- Design strategies that reach the interesting region (boundary values, duplicates, long runs).
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
- [JSON encoding and decoding — Python docs](https://docs.python.org/3/library/json.html)
