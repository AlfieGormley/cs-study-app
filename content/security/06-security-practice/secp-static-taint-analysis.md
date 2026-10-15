---
id: secp-static-taint-analysis
title: Static analysis and SQL data flow
level: basic
minutes: 3
sourceLesson: secp-secure-sdlc
summary: Trace untrusted values into SQL text and see why parameter binding changes the risk.
---

A static scanner examines code without executing it. For an injection finding, the important question is which argument contains untrusted data: SQL grammar and bound parameter values have different roles. This unit follows the same input through unsafe string construction and a parameterised query.

## SAST: reading the code

**Static application security testing (SAST)** analyses source code (or bytecode) without running it. Tools include Semgrep, CodeQL, SonarQube and, for Python, Bandit.

The simplest SAST tools match patterns: "flag any call to `eval`". Better tools do **taint analysis**. They track data from **taint sources** (things an attacker controls) to **taint sinks** (dangerous operations), and raise an alert if tainted data reaches a sink without passing through a **sanitising function** (one that makes data safe for that sink, such as escaping or validation).

```
 source        propagation       sink
 request.args -> name -> q -> execute()
                    ^
           no sanitiser on path
               => ALERT
```

Here is vulnerable code that a suitably configured taint rule can flag:

```python
from flask import request
import sqlite3

def search():
    # Input is attacker-controlled data.
    name = request.args.get("name")
    db = sqlite3.connect("shop.db")
    # Input becomes SQL grammar here.
    q = ("SELECT * FROM items "
         f"WHERE name = '{name}'")
    return db.execute(q).fetchall()
```

The fix is a parameterised query, which keeps the data separate from the SQL grammar entirely:

```python
    # Keep input separate from SQL grammar.
    q = "SELECT * FROM items WHERE name = ?"
    return db.execute(q, (name,)).fetchall()
```

Bandit's B608 documentation illustrates a finding in this form; exact output and confidence depend on code shape and tool version:

```
>> Issue: [B608:hardcoded_sql_expressions]
   Possible SQL injection vector through
   string-based query construction.
   Severity: Medium   Confidence: Low
```

Note the "Confidence: Low". Bandit only sees that a string containing SQL keywords was built by formatting; it does not know whether `name` came from a user. A taint-tracking tool such as CodeQL, or a Semgrep taint rule, can be more precise:

```
rules:
  - id: flask-sqli
    languages: [python]
    severity: ERROR
    message: SQL built from request data
    mode: taint
    pattern-sources:
      - pattern: flask.request.$X
    pattern-sinks:
      - patterns:
          - pattern: $DB.execute($Q, ...)
          - focus-metavariable: $Q
```

This local teaching rule focuses the sink on the *query* argument, so bound data in a separate parameter argument is not expected to create this SQL-text finding. Its positive and negative examples must be checked with the installed Semgrep version; a passing fixture does not establish complete coverage of Flask input or every SQL API.

### Strengths and limits of SAST

- **Runs early and fast**, on every pull request, before anything is deployed.
- **Identifies code locations**, helping developers investigate findings; modelled paths and reported locations still need review.
- **Covers code paths tests never reach**, by reasoning about paths without executing them, but practical analyses approximate behavior and may miss paths or flows.
- **False positives.** It cannot always tell whether a value is really attacker-controlled or already validated. Noisy tools get ignored.
- **False negatives.** It struggles with things that are not visible in code: misconfigured servers, logic flaws ("a user can approve their own expense claim"), or data flowing through reflection, queues and other services.

## Key takeaways
- A taint model tracks sources, propagation, sinks and context-specific sanitisers.
- Parameter binding keeps input separate from the SQL grammar.
- Static findings depend on the rule and program model; both false positives and missed flows remain possible.

## Further reading
- [Semgrep taint analysis](https://semgrep.dev/docs/writing-rules/data-flow/taint-mode/overview)
- [Bandit B608 SQL construction](https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html)
- [Python SQLite parameter binding](https://docs.python.org/3/library/sqlite3.html)
