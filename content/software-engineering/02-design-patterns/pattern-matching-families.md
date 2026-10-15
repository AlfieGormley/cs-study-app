---
id: pattern-matching-families
title: Abstract factories for matching families
level: basic
minutes: 3
sourceLesson: pattern-creational
summary: One factory centralises a matching family of related products.
---

## Abstract Factory pattern

### The problem

You need to create **families** of related objects that must match. A dark-theme button must go with a dark-theme scrollbar; a PostgreSQL connection must go with a PostgreSQL query compiler.

### The structure

```
        UIFactory
   +button()  +menu()
      ^             ^
      |             |
  MacFactory     WinFactory
  MacButton      WinButton
  MacMenu        WinMenu
```

If the client obtains every part from one correctly implemented factory, the family stays consistent. The pattern itself does not prevent bypassing the factory or a faulty implementation.

### In Python

```python
class DarkTheme:
    def button(self, label):
        return f"[{label}] on black"

    def text(self, s):
        return f"{s} in white"

class LightTheme:
    def button(self, label):
        return f"[{label}] on white"

    def text(self, s):
        return f"{s} in black"

def render(theme):
    # Get both parts from the same family.
    return [theme.button("OK"),
            theme.text("Saved")]

print(render(DarkTheme()))
# ['[OK] on black', 'Saved in white']
```

No base class is needed; duck typing does the job. Add an ABC or `typing.Protocol` if you want type checkers to verify each theme has every method.

### When not to use it

- When there's only one family, or the parts don't actually need to match.
- When families change often. Adding a new *kind* of part (say, `slider()`) means changing every factory.

### In real libraries

- **Java's `javax.xml.parsers.DocumentBuilderFactory`** picks an XML parser implementation at run time and hands out matching builders.
- **Database drivers and dialects** are close cousins: SQLAlchemy picks a dialect from the URL, and that dialect supplies the matching type compiler, SQL compiler and DB-API module.

## Key takeaways
- One factory centralises a matching family of related products.
- A new family is easy to add; a new product kind affects each factory.
- Family consistency relies on correct implementation and callers using that factory.

## Further reading
- [Design Patterns — publisher catalogue](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610)
- [Using SELECT statements — SQLAlchemy documentation](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)
