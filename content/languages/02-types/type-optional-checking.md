---
id: type-optional-checking
title: TypeScript and Python checking limits
level: advanced
minutes: 3
sourceLesson: type-gradual-soundness
summary: Type assertions and Python casts provide no runtime validation.
---

The previous unit distinguished dynamic types from safe top types. These TypeScript and Python examples show where optional static checking leaves runtime behaviour unchanged.

## TypeScript: unsound by design

TypeScript's design goals list "apply a sound or provably correct type system" as an explicit **non-goal**. It prefers to accept common JavaScript idioms. The known holes:

| Hole | Example |
|---|---|
| `any` | `const n: number = JSON.parse(s)` |
| Type assertions | `x as User`, `y!` |
| Covariant arrays | `Dog[]` used as `Animal[]` |
| Method bivariance | Method parameters permit both directions |
| Unchecked indexing | `xs[10]` is `T`, not `T \| undefined` |

The indexing one surprises people:

```ts
const xs: number[] = [];
// The unchecked read actually yields
// undefined despite the declared number.
const n: number = xs[0];
n.toFixed(2);
// TypeError: Cannot read properties
// of undefined
```

The checker typed `xs[0]` as `number`; at run time it's `undefined`. The `noUncheckedIndexedAccess` option makes index results `T | undefined`, but it's **not** part of `strict`, and can require explicit handling of missing indexed values.

And because TypeScript **erases** all types when emitting JavaScript, the emitted type annotations add no runtime enforcement. Ordinary JavaScript operations can still perform their normal runtime checks. A wrong `as` cast or an API returning an unexpected shape just flows on until something crashes, possibly far away.

## Python: hints, checked separately

PEP 484 (Python 3.5, 2015) defined type hints, but **the interpreter does not enforce them**; it retains annotation metadata and may evaluate annotations when introspected. Checking is done by a separate tool: mypy, Pyright, Pyre or others. The same program can be fine under one and rejected by another.

```python
import json
from typing import Any

def load() -> Any:
    # JSON decodes to a string, not an int.
    return json.loads('"42"')

def double(n: int) -> int:
    # Strings repeat when multiplied by 2.
    return n * 2

# Any lets the string cross this boundary.
# The output is 4242, not numeric 84.
print(double(load()))
```

mypy accepts this, because `Any` is consistent with `int`. It prints `4242`: the string `"42"` repeated twice.

Python-specific holes and defaults to know:

- **Unannotated functions are skipped.** By default mypy doesn't type-check the body of a function with no annotations, and treats its parameters as `Any`. `--check-untyped-defs` (included in `--strict`) changes that.
- **`cast(T, x)`** does nothing at run time; it just tells the checker to trust you.
- **`# type: ignore`** silences a line.
- **Missing stubs.** Imports lacking usable type information can produce missing-stub diagnostics or `Any`, depending on checker configuration and whether implementation analysis is available.

Because the hints are real objects at run time (`typing.get_type_hints`), libraries can enforce them where it matters. Pydantic validates data against annotated models when it's parsed; tools like `beartype` and `typeguard` check function calls.

## Key takeaways
- Type assertions and Python casts provide no runtime validation.
- Strict TypeScript still omits noUncheckedIndexedAccess; default mypy skips unannotated bodies.

## Further reading
- [TypeScript Handbook: Compatibility and soundness](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)
- [TypeScript compiler options](https://www.typescriptlang.org/tsconfig/)
- [PEP 484: Type hints](https://peps.python.org/pep-0484/)
- [mypy: Command-line options](https://mypy.readthedocs.io/en/stable/command_line.html)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
