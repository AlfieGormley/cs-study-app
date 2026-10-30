---
id: sep-function-abstraction
title: Separate intention from implementation
level: basic
minutes: 3
summary: Extract a function when its name explains intention better than the implementation.
sourceLesson: sep-clean-code
---

A reader skimming a function wants to know *what* it achieves before deciding whether to read *how*. This lesson is about shaping functions so that the what is visible.

## Functions

### Do one thing

Robert C. Martin's *Clean Code* puts it as: a function should do one thing, do it well, and do only that. A practical test: can you describe it in one sentence without "and"? If you can extract a meaningful sub-function from it with a name that isn't just a restatement, it was doing more than one thing.

Martin Fowler offers a sharper rule: **separate intention from implementation**. If you have to read a block of code to work out *what* it does, extract it into a function named after the what. Then the length of the function matters much less than whether its name tells the truth.

> [!note] A contested rule
> How far to decompose is genuinely disputed. John Ousterhout (*A Philosophy of Software Design*) argues that "one thing" gives little guidance on when to stop, and that many tiny, *shallow* functions make readers jump around without hiding much. He prefers *deep* functions: a simple interface over substantial behaviour. Martin, in a published debate with Ousterhout, says he would rather err towards decomposition. Use the reader's effort as the test, not a rule.

### One level of abstraction

Mixing high-level steps with low-level detail makes a function hard to skim.

```python
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
- [Martin Fowler: Function Length](https://martinfowler.com/bliki/FunctionLength.html)
- [Ousterhout and Martin: A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
