---
id: sep-function-abstraction
title: Separate intention from implementation
level: basic
minutes: 3
summary: Extract a function when its name explains intention better than the implementation.
sourceLesson: sep-clean-code
---

Readable functions expose intention, make calls unambiguous and preserve the behaviour callers already rely on.

## Functions

### Do one thing

A function should do one thing, do it well, and do only that. A practical test: can you describe it in one sentence without "and"? If you can extract a meaningful sub-function from it with a name that isn't just a restatement, it was doing more than one thing.

Fowler offers a sharper rule: **separate intention from implementation**. If you have to read a block of code to work out *what* it does, extract it into a function named after the what. Then the length of the function matters much less than whether its name tells the truth.

### One level of abstraction

Mixing high-level steps with low-level detail makes a function hard to skim.

```python
# Accumulate line totals before persistence.
# Before: three levels of detail mixed
def checkout(cart, user):
    total = 0
    for item in cart.items:
        total += item.price * item.qty
    if user.country == "GB":
        total *= 1.2
    conn = psycopg.connect(DSN)
    conn.execute(
        "INSERT INTO orders ...", (total,))
    smtplib.SMTP("mail").sendmail(...)
```

```python
# Each collaborator owns its own detail.
# After: reads like a summary
def checkout(cart, user):
    total = add_tax(cart.subtotal(), user)
    order = orders.save(user, total)
    notifier.order_placed(order)
    return order
```

These checkout fragments illustrate organisation; the tax rule and service calls are placeholders, not a complete tax or transaction implementation. The "after" version tells a story at one altitude. The details still exist, but each lives in a function where it is the main subject.

## Key takeaways
- Extract a function when its name explains intention better than the implementation.
- Keep orchestration at one level of abstraction.
- Function length is a heuristic; extra indirection needs to earn its place.

## Further reading
- [FunctionLength](https://martinfowler.com/bliki/FunctionLength.html)
- [pyguide](https://google.github.io/styleguide/pyguide.html)
