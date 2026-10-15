---
id: secp-workload-secret-stores
title: Secret stores and workload identity
level: intermediate
minutes: 3
sourceLesson: secp-secrets
summary: Fetch a scoped secret with platform identity and understand its operational limits.
---

A secret store reduces scattered copies and provides controlled retrieval. The application must still authenticate to it, protect the returned plaintext and manage availability. Platform identity can avoid embedding a long-lived bootstrap key, provided the workload and credential-provider configuration are correct.

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

# In a configured workload, use its role.
sm = boto3.client("secretsmanager")

def db_creds(name="prod/billing/db"):
    # Fetch the permitted version now.
    resp = sm.get_secret_value(
        SecretId=name)
    # Expect a JSON-encoded credential pair.
    return json.loads(resp["SecretString"])
```

Notice there is no key in this code. boto3 uses its credential provider chain; in a correctly configured role-based workload it obtains temporary role credentials, but explicit/environment/profile credentials can take precedence. The bootstrap problem ("what secret do I use to get my secrets?") is solved by **platform identity**: the cloud vouches for the workload.

> [!note] Kubernetes Secrets are not encrypted by default
> A Kubernetes `Secret` is base64-encoded, which is an encoding, not encryption. Enable encryption at rest for etcd (ideally with a KMS provider) and restrict RBAC. Encryption protects stored data; an authorised API caller with `get secrets` can still retrieve the plaintext.

## Pitfalls and trade-offs

- **Secret sprawl**: the same key copied into five CI systems, two wikis and a Slack message. Count where each secret lives; aim for one.
- **The "god" secret**: one credential with admin rights shared by every service. Scope each secret to one consumer and the least privilege it needs.
- **Logging secrets**: request logs that include `Authorization` headers or full URLs with tokens. Redact at the logging layer.
- **Availability**: if an uncached startup fetch needs an unavailable store, the service may fail to start. Cache secrets briefly and run the store highly available.
- **Encrypted secrets in git** (SOPS, Sealed Secrets) are a reasonable GitOps pattern, but the decryption key becomes the new crown jewel.

## Key takeaways
- Secret stores provide access, version and audit facilities whose coverage depends on configuration.
- Check the SDK provider chain so a stored key does not silently override the intended workload role.
- Kubernetes Secret data is encoding rather than encryption; API permissions remain essential.
- Limit credential scope, cached lifetime and copies, while planning store availability.

## Further reading
- [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Boto3 credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
- [Kubernetes Secrets good practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
