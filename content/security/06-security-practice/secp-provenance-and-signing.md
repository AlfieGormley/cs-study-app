---
id: secp-provenance-and-signing
title: Build provenance, signing and updates
level: intermediate
minutes: 3
sourceLesson: secp-supply-chain
summary: Apply provenance and signer policies while keeping dependencies patched.
---

An inventory says what was included. Provenance describes how an artifact was produced, and a verified signature can authenticate an expected signing identity. Each needs a consumer policy and has limits: authentic evidence can still describe a malicious input or a vulnerable component.

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
- **Log4Shell** was a genuine bug; SLSA provenance does not diagnose that vulnerability; SBOMs and SCA help locate candidate affected components.

### Signing

**Sigstore** (with its `cosign` tool) supports CI signing artefacts with short-lived certificates tied to an OIDC identity ("built by this GitHub Actions workflow in this repo"), and records signatures in a public transparency log. npm and PyPI now support provenance attestations based on this. Remember SolarWinds: signing tells you *who*, so verify the identity is the one you expect.

> [!analogy] Real-world analogy: a certificate of origin from a named factory
> An importer accepts goods only with a certificate of origin stamped by the factory's inspector, naming the factory, the production line and the batch. The importer checks that the stamp is genuine *and* that the named factory is one it has audited.
>
> **How it maps:** The certificate is the provenance statement, the inspector's stamp is the signature, the named factory and line are the builder and source repository, and the importer's list of audited factories is the verification policy that pins the expected identity.
>
> **Where it stops:** A genuine certificate from a stranger's factory is still genuine: Sigstore will happily certify an attacker's own workflow, so checking only that a signature is valid proves almost nothing. And a truthful certificate says where goods were made, not that the recipe was safe: a malicious commit built by the right builder gets accurate provenance.

### Choose and limit dependencies

- Prefer fewer, well-maintained dependencies. **OpenSSF Scorecard** rates projects on branch protection, code review, signed releases and more.
- Let **Dependabot** or **Renovate** raise update PRs, but weigh observation delays for untrusted new releases against the urgency of security fixes; no fixed waiting period guarantees safety.
- Run SCA (`pip-audit`, `npm audit`, Dependabot alerts) in CI.
- Use private registries or proxies, and reserve your internal package names (or use npm scopes such as `@acme/`).

> [!tip] Trade-off: pinning versus patching
> Strict pinning with enforced artifact hashes avoids automatically selecting a different new release, but leaves you on vulnerable old versions unless something prompts an update. Pin *and* automate updates, so changes are deliberate, reviewed and frequent.

## Key takeaways
- SLSA Build levels strengthen provenance and build isolation within their threat model.
- Check the expected source, builder and signing identity; a valid signature alone is insufficient.
- Source review, reproducible builds and component analysis complement provenance.
- Pin packages and hashes, then review automated updates so pinning does not freeze known vulnerabilities forever.

## Further reading
- [SLSA v1.2](https://slsa.dev/spec/v1.2/)
- [Sigstore overview](https://docs.sigstore.dev/)
- [Reproducible build definition](https://reproducible-builds.org/docs/definition/)
- [OpenSSF Scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md)
