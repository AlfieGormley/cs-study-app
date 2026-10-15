---
id: secp-build-system-trust
title: Supply chains and the SolarWinds build
level: intermediate
minutes: 3
sourceLesson: secp-supply-chain
summary: See how a clean repository can produce a signed malicious build.
---

Applications can include many transitive dependencies beyond the ones developers select directly; actual counts vary by project. Add the compiler, the CI system, the base container image and the build scripts, and the code you wrote is a small island in a sea of code you trust without reading.

**Supply-chain attacks** target that sea. Instead of breaking into one hardened company, the attacker compromises something many companies consume, and lets the victims install the payload themselves. The attacker gets reach, and the payload arrives signed, trusted and through the front door.


## Where the chain can break

```
 source ─> build ─> package ─> consumer
   │         │         │          │
 rogue    tampered  hijacked  typosquat,
 commit   builder   registry  confusion,
                    account   vulnerable
                              dependency
```

Each arrow is a trust relationship. Three real incidents show three different links failing.

## SolarWinds: the build system (2020)

SolarWinds Orion is network-monitoring software used by thousands of large organisations, including US government departments. Attackers, later attributed by the US and UK governments to Russia's foreign intelligence service (SVR), got into SolarWinds' build environment.

They did not commit malicious code to the repository, where developers might notice it. Instead they planted a tool that CrowdStrike later named **SUNSPOT** on the build server. It watched for the `MsBuild.exe` build-engine process building Orion, swapped one source file (`InventoryManager.cs`) for a backdoored version for the duration of the build, then put the original back.

The result, **SUNBURST**, was compiled into a legitimate DLL, **signed with SolarWinds' own code-signing certificate**, and shipped in Orion updates from around March to June 2020. SolarWinds initially estimated fewer than 18,000 customers might have installed affected versions. The backdoor waited roughly two weeks before calling home, and the attackers then picked a much smaller set of high-value targets for follow-on intrusion.

Lessons:

- **Code signing binds content to a signing key; it does not prove the actual builder or that the content is safe.** The signature was genuine.
- **Source review is not enough.** The source in git was clean; the build was not.
- The build system is production infrastructure and needs production-grade security.

## Key takeaways
- Source, builder, registry and consumer are separate trust boundaries.
- SUNSPOT changed source during the Orion build; SUNBURST arrived in signed updates.
- A valid signature binds content to a key and does not establish that the build or software is safe.

## Further reading
- [CrowdStrike SUNSPOT analysis](https://www.crowdstrike.com/blog/sunspot-malware-technical-analysis/)
- [Mandiant SUNBURST analysis](https://cloud.google.com/blog/topics/threat-intelligence/evasive-attacker-leverages-solarwinds-supply-chain-compromises-with-sunburst-backdoor)
- [UK attribution of SolarWinds compromise](https://www.gov.uk/government/news/russia-uk-exposes-russian-involvement-in-solarwinds-cyber-compromise)
