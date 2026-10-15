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

If some test fails, the mutant is **killed**: your tests noticed the change. If all tests pass, the mutant **survived**: the suite did not detect that change; it may be a meaningful missed fault, an equivalent change or outside the required behaviour. The **mutation score** summarises a run as the share of mutants your tests killed, leaving out mutants that no test could ever kill (equivalent mutants, examined in the next unit):

```formula
M = K / (T − E) × 100 %
where
M: the mutation score, as a percentage; 100 % means every killable mutant was killed
K: the number of killed mutants (at least one test failed)
T: the total number of mutants the tool generated
E: the number of those mutants judged equivalent: they behave exactly like the original, so no test can kill them
%: per cent, parts per hundred
In words: the mutation score is killed mutants divided by the killable (non-equivalent) mutants.
```

The fraction requires at least one non-equivalent mutant; otherwise there is no killable population to divide by.

Tools cannot generally tell which mutants are equivalent, so until a human marks them, a reported score may divide by all generated mutants and read lower than the true value.

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

Counting only the five mutants in the table, none of which is equivalent, the boundary test moves the mutation score from 40 % to 100 %:

```formula
M_before = 2 / (5 − 0) × 100 % = 40 %
M_after = 5 / (5 − 0) × 100 % = 100 %
where
M_before: the mutation score with only test_adult and test_child, as a percentage
M_after: the mutation score once test_boundary is added
%: per cent, parts per hundred
In words: before, 2 of the 5 mutants were killed (40 %); after adding the boundary test, all 5 are (100 %), while line coverage was 100 % both times.
```

## Key takeaways
- Mutation testing asks whether tests distinguish deliberate code changes.
- Surviving mutants may indicate a missed fault, equivalence or behaviour outside the contract.
- Inputs at 17 and 18 distinguish boundary changes that tests at 10 and 30 miss.

## Further reading
- [Mutation testing basics — PIT](https://pitest.org/quickstart/basic_concepts/)
- [State of Mutation Testing at Google — Google Research](https://research.google/pubs/state-of-mutation-testing-at-google/)
- [mutmut documentation](https://mutmut.readthedocs.io/)
