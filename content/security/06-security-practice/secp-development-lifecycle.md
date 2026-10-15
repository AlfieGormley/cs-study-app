---
id: secp-development-lifecycle
title: Security throughout development
level: basic
minutes: 3
sourceLesson: secp-secure-sdlc
summary: Match security activities to each stage of development and distinguish application requirements from process maturity.
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

You do not have to invent the process. **Microsoft's Security Development Lifecycle** (made mandatory internally in 2004, after Bill Gates's 2002 "Trustworthy Computing" memo) is one prominent large-scale example; no claim of historical priority is made here. The **NIST Secure Software Development Framework** (SP 800-218) recommends practices; **OWASP SAMM** provides an explicit maturity model for assessing them.

## Key takeaways
- Place security work throughout requirements, design, implementation, testing, release and operation.
- Earlier discovery preserves context and can avoid rework, without a universal cost multiplier.
- ASVS describes application controls; SAMM describes the maturity of organisational practices.

## Further reading
- [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)
- [OWASP SAMM model](https://owaspsamm.org/model/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [Microsoft SDL history](https://download.microsoft.com/download/c/e/f/cefb7bf3-de0c-4dcb-995a-c1c69659bf49/sdlprogressreport.pdf)
