---
id: secp-xz-release-trust
title: xz-utils and release-only changes
level: intermediate
minutes: 3
sourceLesson: secp-supply-chain
summary: Distinguish trusted source review from checking what a release archive actually builds.
---

A release archive can contain files absent from the corresponding repository snapshot. The 2024 xz-utils backdoor shows how maintainer trust, build-time conditions and binary test fixtures can combine. The historical conditions below describe affected releases, not every Linux system or SSH server.

## xz-utils: the maintainer (2024)

xz-utils is a compression library used by many Linux distributions. Its maintainer, Lasse Collin, ran it as an unpaid hobby project.

From late 2021 a contributor calling themselves **"Jia Tan"** sent helpful, ordinary patches. In 2022 several accounts, described in the linked historical reconstruction as suspected sock puppets, pressured Collin on the mailing list, complaining the project was slow and that he should hand over maintenance. Jia Tan gained commit access in late 2022 and was making releases by 2023.

In February and March 2024 Jia Tan released versions **5.6.0 and 5.6.1** containing a backdoor (**CVE-2024-3094**, CVSS 10.0, the maximum on CVSS's 0.0–10.0 severity scale). It was hidden with real care:

- The payload sat in two binary "test" files (`bad-3-corrupt_lzma2.xz`, `good-large_compressed.lzma`), whose encoded contents require additional inspection.
- The trigger was a modified `build-to-host.m4` that appeared **only in the release tarballs**, never in git.
- It activated only when building Debian or RPM packages on x86-64 Linux.
- Several distributions apply distribution-specific code patches to OpenSSH's `sshd` that links it to `libsystemd`, which links `liblzma`. The backdoor used that path to hook the server's RSA key verification, so the holder of the attacker's private key could run commands on any affected machine via SSH.

It was disclosed after a developer investigated unexpected behavior. Andres Freund, a PostgreSQL developer at Microsoft, noticed SSH logins on Debian unstable using unusual CPU (a failed login went from about 0.3 s to 0.8 s) and Valgrind errors, investigated, and disclosed it on 29 March 2024. The backdoored versions had reached Fedora Rawhide, Fedora 40 beta and Debian unstable and testing, primarily in prerelease distributions at disclosure; exact affected distributions and build conditions must be checked against their advisories.

Lessons:

- **The release artefact must match the source.** For the disclosed release-only trigger, building from the corresponding git source bypassed that trigger; this is not a general guarantee that git contents are safe.
- **Maintainer burnout is a security problem.** Critical infrastructure maintained by one tired volunteer is a soft target for social engineering.
- **Binary blobs need different review techniques.** Their purpose, generation process and decoded contents can be examined; they are not inherently unreviewable.

## Key takeaways
- The disclosed trigger was shipped in release tarballs rather than the git source.
- The SSH compromise depended on specific distribution linking and build conditions.
- Investigating unexpected latency and tool errors exposed the backdoor.
- Review release inputs and maintainer handovers, including how binary fixtures are generated.

## Further reading
- [Andres Freund disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4)
- [XZ project backdoor information](https://tukaani.org/xz-backdoor/)
- [Historical mailing-list timeline](https://research.swtch.com/xz-timeline)
