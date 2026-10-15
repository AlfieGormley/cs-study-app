---
id: secp-release-component-inventory
title: Release inventories and SBOMs
level: intermediate
minutes: 3
sourceLesson: secp-supply-chain
summary: Use a component inventory to find candidate deployments without confusing a name match with a vulnerability verdict.
---

When a dependency advisory appears, responders first need to locate the software that may include the component. A per-release inventory narrows that search, provided its generation scope and metadata are reliable. The small example below reports candidates; it deliberately does not implement a vulnerability resolver.

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

> [!note] Content gap
> Universal timings for answering inventory questions and relative incident-frequency claims are omitted because no comparable measurement dataset was available.

## Key takeaways
- An SBOM records components and their metadata for a particular release.
- A component-name match is a candidate, not proof of an affected version or reachable exploit.
- Advisory ranges, package identity, backports and runtime configuration still matter.

## Further reading
- [CISA SBOM](https://www.cisa.gov/sbom)
- [CycloneDX specification](https://cyclonedx.org/specification/overview/)
- [Apache Log4j advisories](https://logging.apache.org/log4j/2.x/security.html)
