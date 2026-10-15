---
id: secp-incident-detection-case-studies
title: SolarWinds and Log4Shell detection
level: intermediate
minutes: 3
sourceLesson: secp-detection-response
summary: See how identity anomalies and runtime behaviour complement literal payload matching.
---

Two historical incidents show why a known-file signature or one literal input pattern is incomplete. SolarWinds emerged from investigation of an identity anomaly; Log4Shell payloads changed spelling while the vulnerable lookup behaviour and some runtime effects remained.

## Case study: how SolarWinds was finally caught

SUNBURST was designed to evade detection:

- It waited up to two weeks after installation before doing anything.
- Its traffic imitated the legitimate Orion Improvement Program protocol.
- It checked for security tools and stayed quiet if it found them.
- The follow-on intruders used hostnames matching the victim's naming scheme and IP addresses in the victim's own country.

The campaign spanned months, but installation, follow-on compromise and detection dates differed by organisation; a uniform nine-month dwell time for every customer is not supported. It was the security firm FireEye that eventually noticed, in late 2020, when it found it had been breached itself. In Senate testimony, Kevin Mandia confirmed that an unexpected additional authentication verifier was a tip-off. Details of a particular employee phone call are omitted here because the primary testimony checked does not establish them.

The suspicious identity event helped initiate a much broader investigation; it did not alone establish the whole campaign. FireEye disclosed it on 13 December 2020, and the US CISA issued an emergency directive ordering federal agencies to disconnect Orion.

> [!example] Lesson
> High-value detections are often about **identity and behaviour**, not malware signatures: new MFA devices, impossible travel, a service account logging in interactively, a server talking to a new external domain.

## Case study: detecting Log4Shell

Log4Shell was disclosed on 9 December 2021. Cloudflare saw the first exploitation attempt **nine minutes** later, and found scanning as early as 1 December, eight days before disclosure.

Defenders' first reflex was a rule matching `${jndi:` in request logs. Attackers adapted within hours, using Log4j's own lookup syntax to disguise the string:

```
${${lower:j}ndi:ldap://...}
${${::-j}${::-n}${::-d}${::-i}:...}
${${env:X:-j}ndi:...}
```

These examples illustrate nested/default lookups that can construct `jndi` without containing the literal `${jndi:` pattern in raw input. The environment-default example assumes X is absent; runtime configuration matters. Cloudflare's advice was to treat *any* `${` in input as suspicious. Better still were detections higher up the pyramid:

- **Egress**: unexpected outbound LDAP/RMI connections may be useful warning signs. Restrict unnecessary egress according to the application baseline; some applications legitimately use these protocols, and these blocks do not cover every exploit/exfiltration path.
- **Process behaviour**: a Java process spawning `sh`, `curl` or `powershell`.
- **DNS**: lookups of unusual subdomains from servers (many scanners used DNS callbacks).

And remember the payload can arrive through *any* logged field, not just HTTP: usernames, email subjects, even device names. String-matching on the web tier would never see those.

## Key takeaways
- An unexpected authentication verifier was an investigative clue rather than proof of the whole SolarWinds campaign.
- Nested Log4j lookups can evade a literal raw-input pattern.
- Patching addresses the vulnerable implementation; egress and process detections add path-specific coverage.
- Logged fields outside the web edge also matter.

## Further reading
- [SolarWinds Senate testimony](https://www.govinfo.gov/content/pkg/CHRG-117shrg45485/html/CHRG-117shrg45485.htm)
- [Mandiant SUNBURST analysis](https://cloud.google.com/blog/topics/threat-intelligence/evasive-attacker-leverages-solarwinds-supply-chain-compromises-with-sunburst-backdoor)
- [Cloudflare Log4Shell observations](https://blog.cloudflare.com/exploitation-of-cve-2021-44228-before-public-disclosure-and-evolution-of-waf-evasion-patterns/)
- [Apache Log4j advisories](https://logging.apache.org/log4j/2.x/security.html)
