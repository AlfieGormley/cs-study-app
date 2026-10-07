---
id: secp-secrets
title: Secrets management
level: intermediate
minutes: 13
summary: Where API keys, passwords and tokens should live, why git and environment variables leak them, and how secret stores, short-lived credentials, rotation and OIDC federation shrink the damage when one escapes.
---

A **secret** is sensitive material whose confidentiality helps protect access or cryptographic operations: a database password, an AWS access key, a Stripe API key, a TLS private key, an OAuth token, a signing key. A usable leaked bearer credential may grant access without exploiting another software flaw. An access-key ID alone, expired token or key requiring additional factors is not necessarily sufficient.

Secrets are hard because software needs them to *work*. Your service must present the database password to connect, so it has to be somewhere the service can read. The goal of secrets management is to make that "somewhere" as small, as short-lived and as well-watched as possible.

## How secrets leak

### Hard-coding and git

The classic mistake:

```python
import boto3

s3 = boto3.client(
    "s3",
    aws_access_key_id="AKIA...",
    aws_secret_access_key="wJalr...",
)
```

Once committed, the secret remains in reachable repository **history** until that history is rewritten; copies may persist in clones, forks, caches and backups. Deleting the line in the next commit changes nothing: `git log -p` still shows it. Rewriting history (`git filter-repo`) helps hygiene, but you cannot recall the copies already made.

> [!warning] Leaked means rotate
> The only reliable response to a secret that reached a repository, a log or a chat channel is to **revoke it and issue a new one**, then check for misuse. Public GitHub is scanned by bots continuously; exposed credentials can be copied before you notice.
> A universal time-to-abuse estimate is omitted because this review did not obtain a representative measurement dataset.

Private repositories are not safe either. In 2016 attackers got into a private GitHub repository used by Uber engineers, found an AWS access key, and used it to download files from S3 containing names, emails and phone numbers of tens of millions of riders and drivers. Uber then paid the attackers $100,000 through its bug-bounty programme and did not disclose the breach for a year, which became a scandal and an FTC case of its own.

### Environment variables

The **Twelve-Factor App** advice to keep config in environment variables is a big improvement over hard-coding: secrets stay out of code. But environment variables leak in ways people forget:

- **Child processes normally inherit them unless explicitly passed a filtered environment**, including any shell command or third-party binary you spawn.
- **Crash reporters and debug pages** often dump the environment (framework debug pages, error-tracking SDKs).
- **CI logs**: a stray `env` or `set -x` prints them. CI masking is best effort and platform-dependent; transformed or unregistered values may escape masking.
- **Process inspection**: on Linux, access to `/proc/<pid>/environ` is governed by ptrace-style credential/capability checks and additional system policy; matching a UID is not an unconditional permission guarantee.
- **Container metadata**: `docker inspect` shows environment variables passed at run time.

Environment variables are acceptable for injecting a secret at start-up, but they are not a *store*, and they do nothing about rotation or auditing.

### CI/CD systems

CI holds the keys to production: deploy credentials, registry tokens, signing keys. That makes it a prime target.

- **Codecov (2021)**: attackers modified Codecov's Bash Uploader script, which thousands of CI pipelines downloaded and ran on every build, to send the pipeline's environment variables to an attacker's server. It ran for about two months before a customer noticed the script's checksum didn't match.
- **CircleCI (January 2023)**: malware on an engineer's laptop stole a 2FA-backed SSO session cookie. With that engineer's access, the attacker exfiltrated customers' stored environment variables, tokens and keys. They were encrypted at rest, but the attacker also extracted the encryption keys from a running process. CircleCI told every customer to rotate every secret stored on the platform.

Both show the same pattern: **long-lived secrets stored in one place become a single, very valuable target.**

## Secret stores

A **secret store** (HashiCorp Vault, AWS Secrets Manager, Google Secret Manager, Azure Key Vault) centralises secrets and gives you:

- **Encryption at rest**, typically with envelope encryption under a KMS or HSM key.
- **Access control per secret**: the billing service can read `billing/db` and nothing else.
- **Audit facilities** for secret accesses, subject to configuration, retention and service capabilities; cached application reads are not new store accesses.
- **Versioning and rotation** support.

The application authenticates to the store *as itself* (using its cloud role or Kubernetes service account), then fetches what it needs at runtime:

```python
import json
import boto3

sm = boto3.client("secretsmanager")

def db_creds(name="prod/billing/db"):
    resp = sm.get_secret_value(
        SecretId=name)
    return json.loads(resp["SecretString"])
```

Notice there is no key in this code. boto3 uses its credential provider chain; in a correctly configured role-based workload it obtains temporary role credentials, but explicit/environment/profile credentials can take precedence. The bootstrap problem ("what secret do I use to get my secrets?") is solved by **platform identity**: the cloud vouches for the workload.

> [!note] Kubernetes Secrets are not encrypted by default
> A Kubernetes `Secret` is base64-encoded, which is an encoding, not encryption. Enable encryption at rest for etcd (ideally with a KMS provider) and restrict RBAC. Encryption protects stored data; an authorised API caller with `get secrets` can still retrieve the plaintext.

## Short-lived and dynamic credentials

The best secret is one that is worthless by the time it leaks.

**Dynamic secrets** are generated on demand. Vault's database secrets engine, for example, can create a unique database credential per request with a **lease** (say one hour). Expiry/revocation triggers the configured database revocation operation; successful removal depends on connectivity, permissions and database semantics. Leases may also be renewable.

```
 service ── auth (k8s SA) ──> Vault
    ^                          │
    │  user v-billing-8f2a     │ CREATE
    │  + password, TTL 1h      │ USER
    └──────────────────────────┤
              lease expiry ──> │ revoke*
```

*Revocation attempts the configured database operation; monitor failures.

Benefits:

- A properly enforced lease bounds use; failed revocation must be detected and repaired.
- If each instance obtains a distinct credential and database auditing is enabled, logs identify that credential; theft means they cannot prove which actor used it.
- Revoking a credential used only by one instance limits the operational scope; shared credentials or dependent sessions can complicate this.

The same idea applies everywhere: AWS AssumeRole sessions can request 15 minutes up to the role's configured maximum of 1–12 hours; role chaining has a one-hour limit. Other STS APIs have different duration rules; GCP and Azure have equivalents.

## OIDC federation: no stored keys in CI

CI pipelines used to store a long-lived cloud access key as a CI secret, exactly the kind CircleCI lost. With **OIDC federation**, the CI platform instead issues a signed, short-lived JSON Web Token describing the job ("repo `acme/api`, branch `main`, workflow `deploy`"), and the cloud exchanges it for temporary credentials.

On AWS, the IAM role's trust policy pins what token it accepts:

```
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent
      .com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent
      .com:sub":
      "repo:acme/api:ref:refs/heads/main"
  }
}
```

(This is a schematic legacy-subject-format fragment, not directly executable JSON: wrapped key names must be joined. GitHub repositories created after 15 July 2026 or opting into immutable subjects include owner/repository IDs in `sub`; inspect the actual subject format. Environment jobs use an environment subject instead of this branch form.)

Federation removes the need to store that long-lived cloud access key. A matching job still needs permission to request an OIDC token (`id-token: write`) and must satisfy the full trust policy. A branch subject identifies a repository/ref, not one particular workflow; protect workflow changes and branch/environment rules.

> [!warning] The `sub` condition is the security
> A trust policy that checks only the audience, or uses a wildcard such as `repo:acme/*`, broadens which matching jobs could assume the role if they can obtain the required token. A fork PR does not automatically receive token permission; event type, workflow permissions, approvals and environment protections matter.

## Rotation

Rotation limits how long a stolen secret stays useful and proves you *can* rotate before an emergency forces you to. The hard part is doing it without downtime. The standard pattern keeps two credentials valid during a changeover:

1. **Create** a new credential alongside the old one.
2. **Deploy/propagate** it so all consumers start using it.
3. **Verify** nothing still uses the old one (check audit logs).
4. **Revoke** the old one.

AWS Secrets Manager uses version labels (`AWSPENDING`, `AWSCURRENT`, `AWSPREVIOUS`) and supports rotation workflows. Labels alone do not make two database passwords valid: the target must support overlap, for example through alternating users or dual-password support; single-user rotation has different transition behavior. Applications that fetch the secret at runtime (with a short cache) pick up the new value without a redeploy. Applications that read a secret once at boot need a restart, which is a reason to prefer runtime fetching.

## Catching leaks: secret scanning

Prevention fails, so detect leaks early:

- **Pre-commit hooks** (gitleaks, detect-secrets) block secrets before they leave the laptop.
- **Push protection** (GitHub secret scanning) rejects pushes containing recognised secret formats.
- **Repository and history scanning** finds what slipped through earlier.

Scanners combine **patterns** for known formats (this illustrative regex detects an `AKIA` prefix followed by 16 uppercase letters/digits; temporary AWS access-key IDs use other prefixes such as `ASIA`, and an ID alone is not the secret key) with **entropy**: random keys look more random than code.

```python
import math
import re
from collections import Counter

AWS_ID = re.compile(r"AKIA[0-9A-Z]{16}")

def entropy(s):
    n = len(s)
    counts = Counter(s).values()
    return sum(c / n * math.log2(n / c)
               for c in counts)

print(entropy("aaaaaaaa"))   # 0.0
print(entropy("abcdabcd"))   # 2.0
```

This function computes empirical character-frequency Shannon entropy, in bits per character; it does not measure the unpredictability of the process that generated a particular string. A string using 2 symbols equally often scores 1.0; 4 symbols, 2.0. The theoretical maximum for base64 is 6 bits per character; a finite sample's empirical score need not equal its generating distribution's entropy. Here `password` scores 2.75 and `get_user_by_id` about 3.3. Entropy alone produces false positives (hashes, UUIDs), so tools combine it with context like variable names (`password =`, `api_key:`).

## Pitfalls and trade-offs

- **Secret sprawl**: the same key copied into five CI systems, two wikis and a Slack message. Count where each secret lives; aim for one.
- **The "god" secret**: one credential with admin rights shared by every service. Scope each secret to one consumer and the least privilege it needs.
- **Logging secrets**: request logs that include `Authorization` headers or full URLs with tokens. Redact at the logging layer.
- **Availability**: if the secret store is down, services can't start. Cache secrets briefly and run the store highly available.
- **Encrypted secrets in git** (SOPS, Sealed Secrets) are a reasonable GitOps pattern, but the decryption key becomes the new crown jewel.

## Key takeaways
- A usable leaked credential can grant access; revoke exposed credentials and investigate misuse.
- Git history, environment variables, CI logs and crash reports all leak secrets in ways that are easy to forget.
- Secret stores give encryption, per-secret access control and audit; workloads authenticate with platform identity instead of a bootstrap key.
- Dynamic and short-lived credentials reduce exposure when expiry/revocation is enforced; monitor failed revocation and avoid assuming stored sessions disappear immediately.
- OIDC federation removes long-lived cloud keys from CI, but only if the trust policy pins the `sub` claim tightly.
- Rotate with an overlap window, and scan for secrets at commit, push and in history.

## Further reading
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Vault database secrets engine — HashiCorp](https://developer.hashicorp.com/vault/docs/secrets/databases)
- [Rotating secrets — AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [About security hardening with OpenID Connect — GitHub Docs](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [About push protection — GitHub Docs](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection)
- [CircleCI January 2023 incident report](https://circleci.com/blog/jan-4-2023-incident-report/)
- [FTC: Uber's expanded settlement over the 2016 breach](https://www.ftc.gov/news-events/news/press-releases/2018/04/uber-agrees-expanded-settlement-ftc-related-privacy-security-claims)
- [Kubernetes Secrets good practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
