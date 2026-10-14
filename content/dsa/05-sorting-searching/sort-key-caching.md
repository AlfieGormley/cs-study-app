---
id: sort-key-caching
title: Key functions and cached work
level: advanced
minutes: 2
sourceLesson: sort-real-world
summary: A key function is evaluated once per element.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Keys instead of comparators

Python 3 dropped `cmp` in favour of `key`. A key function is called **once per element**: n calls. A comparator is called on every comparison: O(n log n) calls in the worst case for this sort, often fewer on ordered inputs. For a million items that is 1 million versus 20 million calls to an expensive function, such as lower-casing a string or parsing a date.

This is a caller-context excerpt: `rows` contains objects with country and score fields.

```python
# Group countries; rank scores descending.
rows.sort(
    key=lambda r: (r.country, -r.score))
```

This "decorate, sort, undecorate" pattern is known as the **Schwartzian transform** from Perl. Tuple keys give lexicographic multi-field order. When a field cannot be negated (strings in descending order), use `functools.cmp_to_key` or rely on stability.

## Key takeaways
- A key function is evaluated once per element.
- Tuple keys express lexicographic order and avoid repeating expensive transformations in every comparison.

## Further reading
- [Sorting techniques — Python documentation](https://docs.python.org/3/howto/sorting.html)
- [CPython 3.14.0 list-sort design notes](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listsort.txt)
