---
id: lin-string-immutable-sharing
title: Immutable strings and sharing
level: basic
minutes: 3
sourceLesson: lin-strings
summary: Rebinding a variable leaves other aliases pointing at the old string.
---

A string represents a sequence of text units. Many implementations store those units in an array, but strings come with two complications that trip up beginners and experienced engineers alike:

1. In most modern languages they are **immutable**: you can never change one, only make a new one.
2. A "character" is not as simple as it sounds. How many bytes it takes depends on the **character encoding**.

Both have real performance and correctness consequences.

## Immutability

In Python, Java, JavaScript, C# and Go, a string object can never be modified after it is created.

```python
s = "hello"
s[0] = "H"      # TypeError: 'str' object
                # does not support item
                # assignment
s = "H" + s[1:] # builds a new string
```

Operations that look like modification (`upper()`, `replace()`, `+`) return an immutable string value and leave the original contents alone; an implementation may reuse an existing object when the result is unchanged. A variable can be re-pointed at a new string, but any other variable still pointing at the old one sees no change.

```python
s = "hello"
t = s
s += " world"
print(t)        # hello
```

> [!analogy] Real-world analogy: Bookmarks in printed editions
> Two readers keep bookmarks in the same printed edition of a guidebook. When the publisher corrects it, they print a new edition; nobody rewrites the old pages. A reader who switches to the new edition sees the change, and the other reader's bookmark still sits in the old edition.
>
> **How it maps:** The printed edition is the string object, and each bookmark is a variable holding a reference. `s += " world"` prints a new edition and moves only `s`'s bookmark, so `t` still reads `"hello"`.
>
> **Where it stops:** A runtime may hand several readers the very same copy through interning, and CPython can sometimes extend a string in place when no other reference exists, because nobody could observe the difference. Unlike a print run, making a new string costs time proportional to its length.

C++ std::string and Rust String are mutable growable buffers with separate borrowed-view types, std::string_view and &str. C char arrays can be mutable but C does not provide those ownership/view types.

### Why make strings immutable?

- **Safe as hash keys.** A dict or HashMap stores a key in a bucket chosen by its hash. If the key could change, it would sit in the wrong bucket forever. Immutable strings can also **cache** their hash: Python and Java compute it once and store it.
- **Free sharing.** Many variables, threads or data structures can point at the same string with no copying and no locks, because nobody can change it.
- **Interning.** Identical literals can share one object. Java interns string literals; CPython interns many identifiers and short strings.
- **Security.** A checked string value cannot change through an alias. This does not prevent the file, permissions or other external resource named by it from changing between check and use.

Changing the text generally requires producing another value; allocation and copying may be optimized when observable immutability is preserved.

## Key takeaways
- Rebinding a variable leaves other aliases pointing at the old string.
- Immutability enables stable hash keys; external resources can still change.

## Further reading
- [Python built-in types: text sequences](https://docs.python.org/3/library/stdtypes.html)
- [String interning — Wikipedia](https://en.wikipedia.org/wiki/String_interning)
