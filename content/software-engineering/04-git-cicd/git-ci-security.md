---
id: git-ci-security
title: Pipeline credentials, actions and caches
level: intermediate
minutes: 3
sourceLesson: git-ci-pipelines
summary: Treat fork-controlled code as untrusted even when a trusted workflow invokes it.
---

CI executes code and may hold credentials. This unit treats that combination as a trust boundary: who controls the input, what access the job has, and what gets reused.

## Securing the pipeline

CI runners hold secrets (package download credentials, cloud credentials) and can push code. That makes them a prime target.

- **Least privilege.** Set `permissions` explicitly; give deploy credentials only to jobs that deploy, ideally via short-lived OIDC tokens rather than long-lived secrets.
- **Untrusted pull requests.** Fork pull_request workflows normally receive restricted tokens and no repository secrets, but runner isolation and repository settings still matter. pull_request_target can access privileged base-repository credentials, subject to explicit permissions and event policy. Executing untrusted PR code or injecting untrusted input into its commands can expose those credentials; merely using the trusted workflow file does not make it safe.
- **Pin third-party actions to a full commit SHA.** Tags can be moved. In March 2025 attackers modified the version tags of the popular `tj-actions/changed-files` action to point at a malicious commit that dumped CI secrets into workflow logs; pins to reviewed unaffected commits resisted that tag-repointing attack. A pin to malicious code, or an action that dynamically downloads unpinned code, is still unsafe.
- **Caches can be readable by PR workflows.** Never put secrets in cached paths. Key dependency caches on the lockfile hash, operating system and interpreter version; a `restore-keys` prefix can recover a near-match, but always run the installer to reconcile it with current requirements. A constant key can restore stale inputs.
- **Provenance.** Frameworks such as **SLSA** describe levels of build integrity, including signed provenance stating which source and build produced an artefact.

For deployments, cancelling a matching active run can interrupt a migration or leave remote work running after the CI job ends. Coordinate deployments within the relevant repository and external deployment system; a concurrency group is not a distributed lock. Grant only the token permissions the job needs rather than `write-all`.

## Pitfalls

- **Normalising red.** If `main` is broken for hours and people keep merging, you have lost CI. Stop and fix, or revert.
- **"Retry until green".** It hides flaky tests and real races.
- **Pipelines only one person understands.** Keep pipeline config in the repository, reviewed like code.
- **CI that differs from local.** Use the same commands (a `Makefile`, `tox`, `nox` or task runner) locally and in CI.

## Key takeaways

- Treat fork-controlled code as untrusted even when a trusted workflow invokes it.
- Use least privilege, short-lived credentials and reviewed full action commit pins.
- Cache dependencies by their relevant inputs and never cache secrets.
- Keep pipeline logic reviewed and fix broken feedback rather than retrying it into apparent success.

## Further reading

- [Secure use reference — GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use)
- [Securely using pull_request_target — GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
- [tj-actions/changed-files compromise — GitHub Advisory](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3)
- [SLSA: Supply-chain Levels for Software Artifacts](https://slsa.dev/)
- [GitHub Actions concurrency](https://docs.github.com/en/actions/using-jobs/using-concurrency)
