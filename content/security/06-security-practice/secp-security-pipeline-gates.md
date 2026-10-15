---
id: secp-security-pipeline-gates
title: Security checks developers can use
level: basic
minutes: 3
sourceLesson: secp-secure-sdlc
summary: Build actionable pipeline gates while retaining human review for business rules and design.
---

Security checks help when someone can act on their results. This unit combines static, dynamic, dependency and secret checks into a practical pipeline, then considers how to handle an existing backlog and business rules that generic tools do not know.

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
3. **Put results where developers work**: as PR comments rather than in a separate dashboard nobody opens.
4. **Use security champions**: one developer per team with extra training, who triages findings and is the first point of contact. This spreads trained first-line support across teams; it does not eliminate specialist review or guarantee a particular improvement.
5. **Keep humans in the loop.** Code review and threat modelling find logic and design flaws that generic scanners may miss without the relevant security requirements and models.

## Common pitfalls

- **Tools as a checkbox.** Running a scanner for compliance and never reading the output adds cost and no security.
- **Treating "no findings" as "secure".** Each tool has blind spots; absence of evidence is not evidence of absence.
- **Security as gatekeeper.** If the security team is a bottleneck that says "no", teams route around it. Paved roads (secure defaults, approved libraries, templates) reduce avoidable friction and can complement risk-based gates.
- **Skipping design.** A generic scanner may miss a non-expiring password-reset token; custom rules, framework checks and targeted dynamic tests can detect some such flaws.

## Key takeaways
- Baseline and triage an existing backlog while escalating severe existing issues.
- Gate actionable new findings, tune rules and put results where developers work.
- Human review identifies business requirements that can become custom checks and targeted tests.
- Choose initial automation to match the stated risks rather than treating package counts as a risk measurement.

## Further reading
- [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final)
- [OWASP Security Champions Guide](https://owasp.org/www-project-security-champions-guide/)
- [Semgrep documentation](https://semgrep.dev/docs/)
