---
id: sepr-refactoring-moves
title: Recognise smells and make small moves
level: basic
minutes: 4
summary: Use code smells to choose focused refactorings, and check that each move really preserves behaviour.
sourceLesson: sepr-refactoring
---

With a safety net in place (previous lesson), the next questions are where to refactor and which small move to make. Code smells point to the first; a short catalogue of moves answers the second.

## Code smells: when to refactor
A **code smell** is a surface symptom that often (not always) signals a deeper design problem. Some common ones from Fowler's catalogue:

| Smell | Typical fix |
|---|---|
| Long function | Extract Function |
| Duplicated code | Extract, then reuse |
| Feature envy | Move Function |
| Data clumps | Introduce Parameter Object |
| Primitive obsession | Replace Primitive with Object |
| Shotgun surgery | Move related code together |
| Divergent change | Split the module |

Two of these are worth telling apart. **Shotgun surgery** is when one change forces edits in many places. **Divergent change** is the opposite: one module changes for many unrelated reasons. Both are coupling and cohesion problems seen from different directions.

## The core moves
Most day-to-day refactoring uses a handful of moves. Here is a function that adds up an order and applies an invented 20% surcharge for one country (a made-up policy for the exercise, not tax guidance). Calling it prints the formatted total:

```python
def invoice(order):
    total = 0
    # Accumulate in the original order.
    for line in order["lines"]:
        total += line["qty"] * line["price"]
    if order["country"] == "GB":
        total = total * 1.2
    print(f"Total: {total:.2f}")
```

**Extract Function** pulls a coherent piece into a named function. The name documents intent:

```python
def subtotal(lines):
    total = 0
    # Preserve the accumulation order.
    for line in lines:
        total += line["qty"] * line["price"]
    return total

def with_example_charge(amount, country):
    # Apply the fictional GB surcharge.
    if country == "GB":
        return amount * 1.2
    return amount

def invoice(order):
    net = subtotal(order["lines"])
    gross = with_example_charge(
        net, order["country"])
    print(f"Total: {gross:.2f}")
```

The same arithmetic runs in the same order, so the printed total is unchanged. Now each part can be tested and reused, and adding a new country's rate touches one small function.

Notice one deliberate choice: the extracted `subtotal` keeps the original loop. Swapping it for Python's `sum` function looks like a harmless tidy-up, but since Python 3.12 `sum` adds floats with a more accurate algorithm, so the result can differ in the last digits. Summing ten copies of `0.1` gives `0.9999999999999999` with a loop but `1.0` with `sum` on Python 3.12+. A rounded total usually hides that, but an exact comparison or a stored value would not. "Looks equivalent" is not the same as "behaves identically".

Other moves you will use constantly:

- **Rename** (variable, function, class). The cheapest, most valuable refactoring. If you have to read a function's body to know what it does, its name is wrong.
- **Inline Function / Inline Variable**: the reverse of extract, when the indirection no longer earns its keep.
- **Extract Variable**: give a complicated expression a name.
- **Move Function**: put a function next to the data it uses most (the fix for feature envy).
- **Introduce Parameter Object**: `(start, end)` passed everywhere becomes a `DateRange`.
- **Replace Conditional with Polymorphism**: a `match` on type repeated in several places becomes one class per case.
- **Separate Query from Modifier**: a function that both returns a value and changes state is split, so reading never surprises you.

Modern IDEs (IntelliJ, PyCharm, VS Code with a language server) automate rename, extract and move. Automated refactorings are much safer than hand edits because the tool can resolve many references consistently, though dynamic code like `getattr(obj, name)` can still escape it.

## Key takeaways
- A smell suggests investigation, rather than proving that code needs replacement.
- Shotgun surgery spreads one change across modules; divergent change gives one module unrelated reasons to change.
- Extract, rename, move and introduce parameter objects in behaviour-preserving steps.

## Further reading
- [Catalog of Refactorings](https://refactoring.com/catalog/)
- [Python sum changes](https://docs.python.org/3/library/functions.html#sum)
