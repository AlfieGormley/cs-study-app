---
id: sepr-refactoring-moves
title: Recognise smells and make small moves
level: basic
minutes: 4
summary: Use code smells to select focused refactorings and preserve arithmetic behaviour.
sourceLesson: sepr-refactoring
---

A safe refactoring starts from the tests and behaviour boundary established in the preceding unit. This unit connects design symptoms to small changes you can verify.

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
Most day-to-day refactoring uses a handful of moves. Here is a function definition for a fictional surcharge. The snippets are partial examples: no order is constructed or invoice called, so executing the definitions prints nothing. A call prints a formatted total; the numeric policy is invented for this exercise.

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

For the supported numeric inputs, the arithmetic and printed output are preserved. This is a fictional country-tagged surcharge, not a VAT implementation or tax guidance. Keep the original accumulation loop: replacing it with `sum` can change floating-point results on Python 3.12 and later. Now each part can be tested and reused, and adding a new country's rate touches one small function.

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
