---
id: secp-release-component-inventory
title: Release inventories and vulnerability priorities
level: intermediate
minutes: 5
sourceLesson: secp-supply-chain
summary: Use a component inventory to find candidate deployments, then rank advisories with severity, exploitation evidence and your own exposure.
---

When a dependency advisory appears, responders first need to locate the software that may include the component. A per-release inventory narrows that search, provided its generation scope and metadata are reliable. Then they need an order of work, because a real scan usually reports far more advisories than a team can fix at once. The small example below reports candidates; it deliberately does not implement a vulnerability resolver.

## Component inventory

A **software bill of materials (SBOM)** is a machine-readable component inventory whose completeness depends on generation scope and metadata quality, in **SPDX** or **CycloneDX** format. US Executive Order 14028 (May 2021) pushed SBOMs into federal procurement. With SBOMs stored per release, "where do we run Log4j?" becomes a query:

```python
import json

def check(path):
    with open(path) as f:
        sbom = json.load(f)
    # No component list gives no candidates.
    for c in sbom.get("components", []):
        # Name alone cannot establish a CVE.
        if c.get("name") != "log4j-core":
            continue
        # Candidates, not CVE verdicts.
        ver = c.get("version", "unknown")
        print(path, ver)
```

This simplified CycloneDX-style inventory lists candidate components, not vulnerability verdicts. Match full package identity and version against the applicable advisory, including backport branches and prereleases; then assess configuration/reachability. A blanket `<2.17.1` check would misclassify backported fixes and later advisories.

> [!analogy] Real-world analogy: a food recall and the ingredients list
> A supplier recalls one batch of peanuts. A manufacturer that keeps an ingredients record for every product batch can list which products might contain them within minutes; one without records has to test its whole warehouse.
>
> **How it maps:** The ingredients record is the per-release SBOM, the recalled batch is the advisory's affected package and version range, and listing possible products is the candidate query above.
>
> **Where it stops:** A recall notice names exact batches, and an ingredients list is usually complete. Software advisories have backports and conditions, and an SBOM is only as complete as the tool that generated it, so a match is a candidate to check, not a verdict.

> [!note] Content gap
> Universal timings for answering inventory questions and relative incident-frequency claims are omitted because no comparable measurement dataset was available.

## From candidates to a priority order

A scanner might report hundreds of advisories across your releases. Three public signals answer different questions, and none of them knows your systems:

| Signal | Question it answers | Watch out for |
|---|---|---|
| CVSS v4.0 Base (CVSS-B) | How severe is the flaw technically? | Severity, not your risk |
| EPSS | How likely is exploitation activity soon? | A population estimate |
| CISA KEV | Has it been exploited in the wild? | Absence is not safety |

- **CVSS** (Common Vulnerability Scoring System, maintained by FIRST) rates a flaw from 0.0 to 10.0. Vendors and the NVD usually publish only the Base score, which v4.0 labels **CVSS-B**; the specification says it measures severity and should not be used alone to assess risk. Consumers can add **Threat metrics** (exploit maturity: attacked, proof-of-concept available or unreported) and **Environmental metrics** (how the flaw matters in their own system), labelled CVSS-BT, CVSS-BE or CVSS-BTE.
- **EPSS** (Exploit Prediction Scoring System, also from FIRST) publishes, every day, a probability from 0 to 1 that exploitation activity for a CVE will be observed in the next 30 days, plus a percentile against all scored CVEs. Most CVEs score close to zero. FIRST advises against multiplying EPSS by CVSS: a probability times a severity rank has no clear meaning.
- **KEV** (CISA's Known Exploited Vulnerabilities catalog) lists CVEs with reliable evidence of exploitation in the wild and a clear remediation, such as a vendor update. CISA urges every organisation to prioritise these. US federal civilian agencies must fix them within set deadlines; since June 2026 that duty sits in Binding Operational Directive (BOD) 26-04, which replaced BOD 22-01 and also weighs asset exposure, exploit automation and technical impact.

Then add what only you know: is the vulnerable component actually deployed, reachable from the internet, running with high privilege or near sensitive data? A sensible, illustrative order is:

1. Known-exploited (KEV-listed or seen in your own logs) on reachable systems: patch or mitigate now.
2. High EPSS or exploit code available, with high severity, on exposed systems: next.
3. The rest by severity and exposure, in the normal patch cycle, with re-checks as EPSS and KEV change.

Every rule like this makes mistakes in both directions. A CVE missing from KEV may simply not have been reported yet, and an EPSS score can change overnight when exploit code appears.

## Key takeaways
- An SBOM records components and their metadata for a particular release.
- A component-name match is a candidate, not proof of an affected version or reachable exploit.
- Advisory ranges, package identity, backports and runtime configuration still matter.
- CVSS-B measures severity, EPSS estimates near-term exploitation likelihood and KEV records exploitation already seen.
- Rank work with those signals plus your own exposure; known exploitation on reachable systems comes first.

## Further reading
- [CISA SBOM](https://www.cisa.gov/sbom)
- [CycloneDX specification](https://cyclonedx.org/specification/overview/)
- [Apache Log4j advisories](https://logging.apache.org/log4j/2.x/security.html)
- [CVSS v4.0 specification](https://www.first.org/cvss/v4-0/specification-document)
- [Using EPSS (FIRST)](https://www.first.org/epss/using-epss)
- [CISA KEV catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
