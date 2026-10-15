---
id: para-relations-unification
title: Relations, queries and unification
level: intermediate
minutes: 3
sourceLesson: para-logic-dataflow
summary: Facts and rules describe relations that queries can use in several modes.
---

Imperative, object-oriented and functional programming dominate everyday code, but two other paradigms quietly power a lot of software: **logic programming**, where you state facts and rules and ask questions, and **dataflow programming**, where a program is a graph through which values flow.

You may never write Prolog for a living. You almost certainly use spreadsheets, build systems, reactive UI frameworks and static analysers, all of which borrow these ideas.

## Logic programming

In logic programming, a program is a set of **Prolog facts** and **Prolog rules** in a form of logic. You run it by asking a **query**, and the system searches for values that make the query true.

**Prolog** (Alain Colmerauer and Philippe Roussel, Marseille, 1972) is the classic language. Here is a small family database:

```prolog
% Direct facts seed the recursive relation.
parent(tom, bob).
parent(bob, ann).
parent(bob, pat).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z),
                  ancestor(Z, Y).
```

Read `:-` as "if" and `,` as "and". Variables start with a capital letter. The two rules say: X is an ancestor of Y if X is a parent of Y, *or* if X is a parent of some Z who is an ancestor of Y.

There is no function called `ancestor` that you call with inputs. You ask questions:

```prolog
?- ancestor(tom, ann).
true.

?- ancestor(tom, Who).
Who = bob ;
Who = ann ;
Who = pat.
```

The same relation answers "is Tom an ancestor of Ann?", "who are Tom's descendants?" and, with `ancestor(Who, pat)`, "who are Pat's ancestors?". The relation itself is not tied to one input/output direction. A particular predicate implementation can still require certain arguments to be bound to terminate or avoid errors; not every Prolog predicate runs safely in every direction.

## Unification

Prolog matches queries against facts and rule heads by **unification**: finding values for variables that make two terms identical.

| Term 1 | Term 2 | Result |
|---|---|---|
| `f(X, b)` | `f(a, Y)` | X = a, Y = b |
| `f(X, X)` | `f(a, b)` | Fails |
| `[H\|T]` | `[1, 2, 3]` | H = 1, T = [2, 3] |

The `[H|T]` pattern splits a list into head and tail, much like pattern matching in Haskell, but unification works in both directions. That lets you run some predicates "backwards":

```prolog
?- append(X, Y, [1, 2]).
X = [],     Y = [1, 2] ;
X = [1],    Y = [2] ;
X = [1, 2], Y = [].
```

`append` was written to join lists, yet here it enumerates every way to *split* one.

## Key takeaways
- Facts and rules describe relations that queries can use in several modes.
- Unification finds consistent bindings across whole terms.

## Further reading
- [SWI-Prolog: a quick start](https://www.swi-prolog.org/pldoc/man?section=quickstart)
- [SWI-Prolog: unification](https://www.swi-prolog.org/pldoc/man?section=unifyspecial)
