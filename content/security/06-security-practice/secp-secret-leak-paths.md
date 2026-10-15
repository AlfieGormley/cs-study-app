---
id: secp-secret-leak-paths
title: Where credentials leak
level: intermediate
minutes: 4
sourceLesson: secp-secrets
summary: Trace how repository history, process environments and CI compromise expose reusable credentials.
---

A **secret** is sensitive material whose confidentiality helps protect access or cryptographic operations: a database password, an AWS access key, a Stripe API key, a TLS private key, an OAuth token, a signing key. A usable leaked bearer credential may grant access without exploiting another software flaw. An access-key ID alone, expired token or key requiring additional factors is not necessarily sufficient.

Secrets are hard because software needs them to *work*. Your service must present the database password to connect, so it has to be somewhere the service can read. The goal of secrets management is to make that "somewhere" as small, as short-lived and as well-watched as possible.


## How secrets leak

### Hard-coding and git

The classic mistake:

```python
import boto3

# Anti-pattern with placeholder values only.
# This constructs a client, not a request.
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

## Key takeaways
- Deleting a secret from the latest commit does not remove history or existing copies.
- Environment injection avoids literals in source but remains exposed to authorised inspection, children and diagnostics.
- CI systems holding many long-lived credentials are valuable targets.
- Revoke exposed credentials, replace them safely and investigate misuse.

## Further reading
- [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [FTC Uber 2016 breach account](https://search.ftc.gov/business-guidance/blog/2018/04/ftc-addresses-ubers-undisclosed-data-breach-new-proposed-order)
- [CircleCI incident report](https://circleci.com/blog/jan-4-2023-incident-report/)
- [Codecov incident report](https://about.codecov.io/security-update/)
