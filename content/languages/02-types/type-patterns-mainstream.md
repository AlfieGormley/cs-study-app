---
id: type-patterns-mainstream
title: Exhaustive patterns in everyday languages
level: intermediate
minutes: 3
sourceLesson: type-adts-pattern-matching
summary: TypeScript narrows discriminated unions; a never assignment detects missing cases.
---

A sum-type model needs a reliable way to inspect alternatives. These examples revisit the same circle-or-rectangle shape in three languages; radius, width and height are numeric field values, and each area function returns square units when the inputs use one consistent length unit.

## Sum types in other languages

### TypeScript: discriminated unions

A union of object types that share a literal **variant tag** field:

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number };

function area(s: Shape): number {
  // The tag narrows available fields.
  switch (s.kind) {
    case "circle":
      return Math.PI * s.r ** 2;
    case "rect":
      return s.w * s.h;
    default: {
      // New variants break this check.
      const gone: never = s;
      return gone;
    }
  }
}
```

Checking `s.kind` **narrows** `s` in each branch. In `default`, every case has been removed, so `s` has type `never`. Add a `"triangle"` member and the assignment to `never` fails to compile: a hand-made exhaustiveness check.

### Python: dataclasses and `match`

Python 3.10 added structural pattern matching. This version uses `typing.assert_never`, so the full example requires Python 3.11 or later:

```python
import math
from dataclasses import dataclass
from typing import assert_never

@dataclass
class Circle:
    r: float

@dataclass
class Rect:
    w: float
    h: float

Shape = Circle | Rect

def area(s: Shape) -> float:
    # Extract the fields for this variant.
    match s:
        case Circle(r=r):
            return math.pi * r * r
        case Rect(w=w, h=h):
            return w * h
        case _:
            # Static missing-case check;
            # raises if actually reached.
            assert_never(s)
```

Python itself does not statically check exhaustiveness. Without a matching arm execution continues after the match; the shown catch-all arm instead calls `assert_never`, which raises at runtime. But mypy and Pyright narrow `s` in each case, and `typing.assert_never` (3.11+) makes a missing case a type error.

A bare name in a Python case is a **capture pattern**, not a comparison with an existing variable. `case RED:` binds the matched value to a local name; use a dotted constant such as `case Colour.RED:` or a literal such as `case "red":` when comparing values. An unguarded capture that matches everything must be the last case; a guard can allow later cases to remain reachable.

### Java: sealed interfaces and records

Java 17 added `sealed` types and Java 21 finalised pattern matching for `switch` and record patterns:

```java
sealed interface Shape
    permits Circle, Rect {}
record Circle(double r)
    implements Shape {}
record Rect(double w, double h)
    implements Shape {}

static double area(Shape s) {
  // The sealed variants cover the switch.
  return switch (s) {
    case Circle c ->
        Math.PI * c.r() * c.r();
    case Rect(double w, double h) ->
        w * h;
  };
}
```

No `default` is needed, because the compiler knows the permitted implementations. A null selector still throws `NullPointerException` unless a `case null` handles it.

## Key takeaways
- TypeScript narrows discriminated unions; a never assignment detects missing cases.
- Python capture patterns bind names; assert_never supports static exhaustiveness checks.
- Java 21 combines sealed types, records and switch patterns; null still needs deliberate handling.

## Further reading
- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [PEP 636: Pattern matching tutorial](https://peps.python.org/pep-0636/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [JEP 441: Pattern matching for switch](https://openjdk.org/jeps/441)
- [JEP 440: Record patterns](https://openjdk.org/jeps/440)
