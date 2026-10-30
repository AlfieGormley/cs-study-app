---
id: test-mutant-boundaries
sourceLesson: test-flaky-coverage-mutation
title: Use mutations to discover missing boundary checks
level: advanced
minutes: 3
summary: Mutation testing asks whether tests distinguish deliberate code changes.
---

Coverage tells you where code ran. Mutation testing changes that code deliberately and asks whether a test notices. A missed boundary is a useful example of the extra information it supplies.

## Mutation testing

Coverage asks "did the tests run this code?" **Mutation testing** asks the question you actually care about: "if this code were wrong, would a test fail?"

The tool makes many small changes to your code, called **mutants**, one at a time, and runs the tests against each:

- `>=` becomes `>`, `<`, `<=` or `==`
- `+` becomes `-`, `and` becomes `or`
- a constant `18` becomes `19` or `17`
- `return x` becomes `return None`; a condition becomes `True`

If some test fails, the mutant is **killed**: your tests noticed the change. If all tests pass, the mutant **survived**: the suite did not detect that change; it may be a meaningful missed fault, an equivalent change or outside the required behaviour.

The **mutation score** summarises a run as the share of mutants your tests killed. Conceptually it leaves out **equivalent mutants**, which behave exactly like the original so no test could ever kill them (examined in the next unit). Tools cannot generally tell which mutants are equivalent, so until a human marks them, a reported score may count them as survivors and read lower than the suite deserves. Tools also differ in what they count, for example mutants on lines no test runs. Treat the score as a pointer to survivors worth reading, not as a grade.

> [!analogy] Real-world analogy: planting typos to test a proofreader
> To check how careful a proofreader is, an editor quietly plants a few typos in a manuscript and counts how many come back marked.
>
> **How it maps:** The planted typos are mutants, the proofreader is the test suite, a marked typo is a killed mutant and an unmarked one has survived. Each surviving typo shows a kind of mistake the reader does not notice, just as a surviving `age > 18` shows the suite never checks age 18.
>
> **Where it stops:** A mutation tool plants one small mechanical change at a time and re-runs the relevant tests for each, which is why it is expensive. And some "typos" are acceptable alternative spellings: an equivalent mutant changes the code but not its behaviour, so no test should fail.

### A surviving mutant

```python
def can_rent(age):
    return age >= 18

def test_adult():
    assert can_rent(30)

def test_child():
    assert not can_rent(10)
```

Coverage is 100%. Now mutate:

| Mutant | 30 | 10 | Result |
|---|---|---|---|
| `age > 18` | T | F | survives |
| `age >= 19` | T | F | survives |
| `age >= 17` | T | F | survives |
| `age < 18` | F | T | killed |
| `True` | T | T | killed |

Three mutants survive, all at the boundary. The tests cannot tell 18 from 17 or 19. One more test kills all three:

```python
def test_boundary():
    # Exact lower endpoint must be allowed.
    assert can_rent(18)
    # The adjacent excluded value must fail.
    assert not can_rent(17)
```

`age > 18` fails on 18, `age >= 19` fails on 18, `age >= 17` fails on 17. This is the boundary-testing advice from the earlier boundary-testing unit, discovered mechanically.

Counting only the five mutants in the table, none of which is equivalent, the suite killed 2 of 5 before the boundary test and all 5 after it, while line coverage was 100 % both times. That gap is exactly what mutation testing adds to coverage.

## Key takeaways
- Mutation testing asks whether tests distinguish deliberate code changes.
- Surviving mutants may indicate a missed fault, equivalence or behaviour outside the contract.
- Inputs at 17 and 18 distinguish boundary changes that tests at 10 and 30 miss.

## Further reading
- [Mutation testing basics — PIT](https://pitest.org/quickstart/basic_concepts/)
- [State of Mutation Testing at Google — Google Research](https://research.google/pubs/state-of-mutation-testing-at-google/)
- [mutmut documentation](https://mutmut.readthedocs.io/)
