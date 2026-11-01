---
id: secp-ci-oidc-trust
title: OIDC federation for CI
level: intermediate
minutes: 3
sourceLesson: secp-secrets
summary: Replace stored cloud keys with job identity and constrain which jobs may assume a role.
---

Federation moves the trust decision from possession of a long-lived stored cloud key to validation of a short-lived identity token. The cloud must verify the issuer, audience and permitted subject as well as the rest of its policy. A compromised matching workflow can still receive credentials.

## OIDC federation: no stored keys in CI

CI pipelines used to store a long-lived cloud access key as a CI secret, exactly the kind CircleCI lost. With **OIDC federation**, the CI platform instead issues a signed, short-lived JSON Web Token describing the job ("repo `acme/api`, branch `main`, workflow `deploy`"), and the cloud exchanges it for temporary credentials.

> [!analogy] Real-world analogy: a staff badge exchanged for a day pass
> Instead of giving a contractor a permanent copy of the building key, reception asks to see a photo badge issued by the contractor's employer that morning. If the badge names the right company and team, reception issues a day pass that stops working at 6 pm.
>
> **How it maps:** The employer is the CI platform acting as token issuer, the badge is the signed short-lived OIDC token, the names on it are claims such as `aud` and `sub`, reception's rule is the IAM trust policy, and the day pass is the temporary cloud credential. The permanent key copy is the long-lived access key stored as a CI secret.
>
> **Where it stops:** Reception trusts the employer completely. Anyone the employer will badge, here any job that matches the policy and may request a token, gets a pass, so a rule like "anyone from Acme" (`repo:acme/*`) admits far more people than intended.

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

(This is a schematic legacy-subject-format fragment, not directly executable JSON: key names split across lines must be joined. GitHub repositories created after 15 July 2026, renamed or transferred after that date, or opting into immutable subjects include owner/repository IDs in `sub` on GitHub.com; GitHub Enterprise Server does not provide this immutable format. Inspect the actual subject format. Environment jobs use an environment subject instead of this branch form.)

Federation removes the need to store that long-lived cloud access key. A matching job still needs permission to request an OIDC token (`id-token: write`) and must satisfy the full trust policy. A branch subject identifies a repository/ref, not one particular workflow; protect workflow changes and branch/environment rules.

> [!warning] The `sub` condition is the security
> A trust policy that checks only the audience claim, or uses a wildcard such as `repo:acme/*`, broadens which matching jobs could assume the role if they can obtain the required token. A fork PR does not automatically receive token permission; event type, workflow permissions, approvals and environment protections matter.

## Key takeaways
- OIDC federation removes a stored cloud key while preserving a policy-controlled credential exchange.
- Match the actual subject format and intended audience; repository/ref subjects do not identify a single workflow.
- Protect workflow changes, token permissions and deployment environments.
- Short-lived credentials still need least privilege, monitoring and compromise response.

## Further reading
- [GitHub OIDC reference and immutable subjects](https://docs.github.com/en/actions/reference/security/oidc)
- [GitHub OIDC for AWS](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
