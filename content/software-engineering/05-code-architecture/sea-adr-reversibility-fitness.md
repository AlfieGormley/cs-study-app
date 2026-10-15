---
id: sea-adr-reversibility-fitness
sourceLesson: sea-adr-evolution
title: Reversible decisions and fitness functions
level: advanced
minutes: 5
summary: Match review effort to reversibility and turn architectural properties into executable checks.
---

An ADR preserves why a choice was made. Next decide how much care that choice needs, and which properties automated checks must preserve while the system changes.

## Reversible and irreversible decisions

Not every decision deserves the same care. Jeff Bezos's 2015 shareholder letter split them into **Type 1** (one-way doors, consequential and hard to reverse) and **Type 2** (two-way doors, which you can walk back through).

| Decision | Door |
|---|---|
| Name of an internal helper | Two-way |
| Choice of logging library behind an adapter | Two-way |
| Public library API at 1.0 | One-way-ish |
| Main database for 10 years of data | One-way-ish |
| Splitting into separately deployed services | One-way-ish |

Two consequences for architecture:

1. **Spend ADR and review effort on one-way doors.** Make two-way decisions quickly.
2. **Turn one-way doors into two-way ones** where you can. Putting the database behind a repository port, or a vendor SDK behind an adapter, can reduce call-site changes, but the cost of migrating also depends on data and semantic compatibility. Much of good architecture is buying reversibility.

The related idea of the **last responsible moment** says to delay irreversible decisions until you have the most information, but no later, since not deciding is also a decision.

## Evolutionary architecture

Neal Ford, Rebecca Parsons and Patrick Kua's *Building Evolutionary Architectures* defines an evolutionary architecture as one that supports **guided, incremental change** across multiple dimensions. The key word is *guided*: change is constant, but some properties must be protected while it happens.

### Fitness functions

A **fitness function** is an objective, preferably automated, check of an architectural characteristic. Rather than hoping the layering survives, you test for it.

Examples:

| Characteristic | Fitness function |
|---|---|
| Layering | import-linter contract in CI |
| No cycles | Acyclic import check |
| Latency | p99 latency under 0.2 seconds in a load test |
| Dependency hygiene | No package more than 1 major version behind |
| Bundle size | Fail if over 250 KB gzipped |

A fitness function can be an ordinary test:

```python
import ast
import pathlib

def imports(path):
    # Inspect syntax without executing code.
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Skip relative imports in this
            # demo.
            if node.level == 0:
                yield node.module or ""
        elif isinstance(node, ast.Import):
            for a in node.names:
                yield a.name

def test_domain_has_no_framework():
    banned = ("flask", "sqlalchemy")
    root = pathlib.Path("shop/domain")
    files = list(root.rglob("*.py"))
    # An empty search must not silently
    # pass.
    assert files, "no domain files found"
    for f in files:
        for mod in imports(f):
            # Compare whole top-level names.
            top = mod.split(".")[0]
            bad = top in banned
            assert not bad, f"{f}: {mod}"
```

This small example checks direct absolute import statements, requires at least one source file, and matches the top-level package exactly. It does not resolve relative or dynamic imports and can include imports guarded by TYPE_CHECKING. A dedicated tool like import-linter also follows indirect chains, which is why it's usually the better choice. The point is that architecture rules become executable and fail the build like any other bug.

## Key takeaways
- Spend greater care on costly, hard-to-reverse decisions.
- Adapters can reduce call-site changes but cannot guarantee an easy data or semantic migration.
- A fitness function checks an architectural property rather than merely describing it.
- A direct-import AST check has explicit limits; dedicated tools can follow indirect dependencies.

## Further reading
- [2015 Letter to Shareholders — Amazon](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/whitepapers/approved/executive-insights/2015-letter-to-shareholders.pdf)
- [Building Evolutionary Architectures — authors’ site](https://evolutionaryarchitecture.com/)
- [Import Linter: contract types](https://import-linter.readthedocs.io/en/stable/contract_types/)
- [ast — Python documentation](https://docs.python.org/3/library/ast.html)
