---
id: para-imperative-declarative
title: Imperative vs declarative
level: basic
minutes: 10
summary: Telling the machine how versus telling it what, why SQL, React and Kubernetes are declarative, and where the abstraction leaks.
---

A **programming paradigm** is a style of organising programs: what the basic building blocks are and how you combine them. It is not the same thing as a language. Most languages support several paradigms, and the same problem can be written in very different styles in one language.

The most fundamental split is between **imperative** and **declarative** programming.

- **Imperative**: you give the computer a sequence of commands that change its state, step by step. You describe *how*.
- **Declarative**: you describe the result you want, and something else works out the steps. You describe *what*.

> [!example] Two ways to get a coffee
> Imperative: "Walk to the counter, take a cup, put it under the spout, press the button, wait 30 seconds, add 20 ml of milk."
> Declarative: "A flat white, please." The barista decides the steps, and may do them in a better order than you would.

## Imperative programming

Imperative programming mirrors how the hardware works. A CPU has memory and registers, and it executes instructions one after another, each one reading and writing that state. This is the **von Neumann** model, and assembly language is imperative in its purest form.

The core ingredients are:

- **State**: variables whose values change over time.
- **Assignment**: `x = x + 1` is a command, not an equation.
- **Sequence**: statement two runs after statement one, and order matters.
- **Control flow**: `if`, loops and jumps decide which statement runs next.

**Procedural programming** (C, Pascal, early Python scripts) is imperative code organised into procedures. **Structured programming**, pushed by Edsger Dijkstra's 1968 letter *Go To Statement Considered Harmful*, restricts control flow to sequence, selection (`if`) and iteration (loops). The Böhm–Jacopini theorem (1966) showed those three are enough to express any computable function, so `goto` is never strictly necessary.

Here is an imperative solution to a small task: *sum the squares of the even numbers in a list*.

```python
nums = [3, 4, 7, 10, 1]
total = 0
for n in nums:
    if n % 2 == 0:
        total = total + n * n
print(total)   # 16 + 100 = 116
```

To understand it you mentally run it: `total` starts at 0, becomes 16, then 116. The program's meaning lives in the changing state.

## Declarative programming

A declarative program states the relationship between input and output and leaves the execution strategy to a runtime, compiler or engine.

The same task in a declarative style:

```python
total = sum(n * n for n in nums
            if n % 2 == 0)
```

```sql
SELECT COALESCE(SUM(n * n), 0)
FROM nums
WHERE n % 2 = 0;
```

```haskell
total = sum [n * n | n <- nums, even n]
```

```javascript
const total = nums
  .filter(n => n % 2 === 0)
  .map(n => n * n)
  .reduce((a, b) => a + b, 0);
```

There is no loop counter and no accumulator you update by hand. You say *which* numbers and *what* to do with them.

Declarative languages are everywhere, often not recognised as programming languages at all:

| Language | You declare | Engine decides |
|---|---|---|
| SQL | The rows you want | Join order, indexes |
| HTML/CSS | Structure, style | Layout, painting |
| Regex | A pattern | Matching algorithm |
| Make | Targets, deps | What to rebuild |
| Terraform | Infrastructure | API calls to make |

Functional programming (lesson 3) and logic programming (lesson 4) are the two big declarative *general-purpose* families.

## Why declarative code can be faster

Giving up control of *how* sounds like it would make code slower. Often the opposite is true, because the engine is free to choose a better strategy than you would.

A SQL query does not say "loop over the orders table, then for each row look up the customer". The database's **query planner** looks at table sizes, indexes and statistics and picks a plan: perhaps a hash join, perhaps an index scan, perhaps a parallel scan across 8 workers. If you add an index tomorrow, the planner may use it to accelerate suitable queries without rewriting them; an index does not guarantee a faster plan.

```
  SQL text
     |
     v
  parser -> planner -> executor
             ^   (chooses join order,
             |    index, parallelism)
        statistics
```

The same idea appears elsewhere:

- A Java parallel stream `list.parallelStream().mapToInt(f).sum()` can split work across cores because you never said "in this order, one at a time".
- A spreadsheet can use dependencies to avoid unnecessary recalculation; volatile formulas and full recalculation modes are exceptions.
- Haskell's compiler can fuse `map f (map g xs)` into a single pass with no intermediate list.

The general principle: the **less you over-specify**, the more freedom the system has to optimise.

## Declarative UI and desired state

Two of the most influential modern systems are declarative at heart.

**React** describes a user interface as a function of state. Instead of "find the button, change its text, hide the spinner" (the jQuery style), you write what the UI should look like *for a given state*:

```javascript
function Cart({ items }) {
  return items.length === 0
    ? <p>Your cart is empty</p>
    : <p>{items.length} items</p>;
}
```

React compares the new description with the previous one and computes DOM updates needed by its reconciliation model. Components normally describe output rather than mutate React-managed DOM directly, although refs provide imperative escape hatches.

**Kubernetes** continuously reconciles declared desired state, such as three Pod replicas, against observed state. When replicas disappear its controllers attempt to restore them, subject to capacity and scheduling constraints. **Terraform** also declares desired infrastructure, but normally refreshes and reconciles during explicit plan/apply runs; it is not a continuously running self-healing controller. Imperative scripts can also run repeatedly and inspect state if programmed to do so.

> [!tip] Declarative surface, imperative engine
> Declarative systems are almost always built on imperative code. The SQL planner, React's reconciler and Kubernetes controllers are imperative programs. The paradigm describes the layer you work with, not what happens all the way down.

A useful goal of desired-state operations is **idempotence** under stable inputs and provider behavior: applying the same declaration twice gives the same result as applying it once. Written as a formula, an operation is idempotent when:

```formula
f(f(s)) = f(s)
where
f: an operation applied to a system, such as "ensure 3 replicas exist"
s: the state of the system before the operation, such as how many replicas are running
f(s): the state after applying the operation once
f(f(s)): the state after applying it a second time, straight after the first
In words: an operation is idempotent when doing it again changes nothing more than doing it once did.
```

Running "ensure 3 replicas" ten times still leaves 3 replicas: from 0 running, the first run gives 3 and every later run finds 3 and does nothing. Running "start 3 containers" ten times leaves 30, because each run adds 3 more (0, then 3, then 6, ...), so applying it twice does not give the same state as applying it once. The idea only holds while nothing else changes the system between runs.

## It's a spectrum

"Imperative" and "declarative" are not two boxes; they are relative. A comprehension is more declarative than a `for` loop, but less declarative than SQL, because you still chose the data structure and evaluation order.

A useful test: **how much of the execution order and intermediate state is visible in your code?** The more there is, the more imperative it is.

## Trade-offs and pitfalls

Declarative code is usually shorter, has fewer places for bugs to hide (no off-by-one loop counter, no forgotten reset of an accumulator), and expresses intent directly. But the abstraction leaks.

- **Performance cliffs.** You do not control the plan, so when the engine picks badly, things get dramatically slower. A missing index or stale statistics can turn a 5 ms query into a 50-second full-table scan, and the SQL text looks identical.
- **The "how" sneaks back in.** Real systems grow escape hatches: SQL index hints, React's `useMemo`, or explicit Terraform dependency declarations. You end up needing to know the engine's internals anyway.
- **Debugging is indirect.** There is no line to put a breakpoint on inside a SQL query. You read `EXPLAIN` output or a React profiler instead.
- **Expressiveness limits.** Pure SQL cannot easily express "loop until converged". SQL implementations offer procedural extensions; recursive CTEs also express iteration declaratively and can handle some convergence problems.
- **Imperative is sometimes clearer.** A complex algorithm with early exits, such as a state machine for parsing, is often easiest to read as explicit steps.

> [!warning] An ORM's N+1 trap
> ORMs let you write `for order in orders: print(order.customer.name)`, which looks like simple attribute access. Each `.customer` may fire a separate query, so 1,000 orders cause 1,001 round trips. The declarative-looking code hid an imperative cost. Eager loading with an appropriate join or batch query can avoid those per-object queries.

The name "N+1" comes from counting the queries: one to load the list, then one more per item in it.

```formula
Q = 1 + N
Q = 1 + 1000 = 1001
where
Q: the total number of database queries (round trips) the loop makes
N: the number of orders loaded, here 1,000
In words: one query fetches the orders, then each order triggers one extra query for its customer.
```

At even 1 ms per round trip, 1,001 queries spend about a second just waiting on the database. Eager loading brings the count down to 1 or 2 queries however many orders there are.

## Key takeaways
- Imperative code describes *how*: a sequence of state-changing commands, mirroring the von Neumann machine.
- Declarative code describes *what*: the desired result, leaving execution strategy to an engine.
- SQL, HTML/CSS, regex, Make, React and Kubernetes manifests are all declarative; functional and logic programming are declarative general-purpose paradigms.
- Not specifying the "how" lets engines optimise: query planners, parallel streams, loop fusion.
- Kubernetes controllers reconcile continuously; Terraform usually reconciles on explicit runs. Idempotence depends on operation semantics, not on the paradigm label alone.
- The abstraction leaks: performance cliffs, escape hatches and indirect debugging are the price.

## Further reading
- [Imperative programming — Wikipedia](https://en.wikipedia.org/wiki/Imperative_programming)
- [Declarative programming — Wikipedia](https://en.wikipedia.org/wiki/Declarative_programming)
- [Go To Statement Considered Harmful — Dijkstra (EWD215)](https://www.cs.utexas.edu/~EWD/transcriptions/EWD02xx/EWD215.html)
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/current/using-explain.html)
- [Kubernetes controllers — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/controller/)
