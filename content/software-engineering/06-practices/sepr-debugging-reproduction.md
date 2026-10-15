---
id: sepr-debugging-reproduction
title: Observe and reproduce a failure
level: intermediate
minutes: 4
summary: Replace guesses with falsifiable hypotheses, a reliable reproduction and a careful traceback reading.
sourceLesson: sepr-debugging
---

Debugging can consume substantial engineering time. The usual approach is to stare at the code, guess, change something, and rerun. Sometimes it works. When it does not, you can lose a day.

Methodical debugging replaces guessing with a process. A structured investigation can reduce wasted experiments; its benefit depends on the problem.

## Debugging is the scientific method
A bug is a gap between what you expect the program to do and what it actually does. Somewhere, one of your beliefs about the system is false. Debugging is finding which one.

The loop:

1. **Observe**: gather facts. What exactly happens? What did you expect?
2. **Hypothesise**: propose a specific cause. "The cache returns a stale price after an update."
3. **Predict**: if that is true, what else must be true? "Clearing the cache should fix it; the database row should be correct."
4. **Test**: run the experiment that would *disprove* the hypothesis.
5. **Conclude**: keep or discard it, and loop.

Two habits make this work. First, **change one thing at a time**, to make the effect easier to attribute. Second, **write things down**: hypotheses tried, results, commands run. After two hours you will not remember whether you tested with the cache off.

David Agans' book *Debugging* condenses this into nine rules worth memorising (paraphrased here): understand the system; make it fail; quit thinking and look; systematically narrow the search; change one thing at a time; keep an investigation record; check the plug; get a fresh view; and if you didn't fix it, it ain't fixed.

## Step 1: reproduce it
A reliable reproduction provides strong evidence for evaluating a fix; without one, confidence must come from other evidence and remains harder to establish. Aim for a reproduction that is:

- **Reliable**: fails every time, or at a known rate.
- **Fast**: seconds, not a 20-minute deploy.
- **Automated**: ideally a failing test.

Collect everything: the exact error message, the full stack trace, inputs, versions, environment and time. "It's broken" is not a bug report; "POST /orders with an empty basket returns 500 since Tuesday's deploy" is.

### Read the stack trace properly

Python prints frames oldest first and says so: `Traceback (most recent call last)`. The bottom line is the exception; the frame just above it is where it was raised. Work upwards to find the first frame in *your* code, which is usually where the wrong value came from or was passed in.

The following traceback is illustrative, with source filenames and line numbers chosen for the example.

```
Traceback (most recent call last):
  File "app.py", line 30, in handle
    total = order_total(basket)
  File "pricing.py", line 12, in order_total
    return sum(i.price for i in items) / n
ZeroDivisionError: division by zero
```

Here the crash is in `order_total`, but the real question is why `n` was zero, and whether `handle` should have rejected an empty basket before calling it.

## Key takeaways
- Write down observations, hypotheses, experiments and actual results.
- A useful reproduction records inputs, expected and actual behaviour, versions and environment.
- Read the exception and raising frame, then trace the wrong value back through your own code.

## Further reading
- [Python errors and exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Methodical debugging — MIT](https://web.mit.edu/6.031/www/sp21/classes/13-debugging/)
- [The Debugging Book — Andreas Zeller](https://www.debuggingbook.org/)
