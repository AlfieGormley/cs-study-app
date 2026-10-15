---
id: pki-certificates-trust-and-fields
title: Certificate trust chains and fields
level: intermediate
minutes: 3
sourceLesson: pki-certificates
summary: Certificates bind names to public keys under a trusted issuer and policy.
---

Public verification leaves an identity-binding gap. A signature proves that a message was made by the holder of some private key. It does not tell you *whose* key it is. If an attacker can hand you their public key and say "this is bank.com", every signature check passes and you are talking to the attacker.

A **certificate** closes that gap. It is a small signed document that says "this public key belongs to this name", signed by someone you already trust. A **public key infrastructure** (PKI) is everything around that: who is allowed to sign certificates, how they check identities, how trust is distributed, and how mistakes are undone.

## The idea: a chain of signatures

You cannot check every server's key in person. Instead you trust a small set of **root certificate authorities** (CAs), whose public keys ship with your operating system or browser. Each root vouches for a few **intermediate CAs**, which vouch for millions of websites.

```
Root CA        (in your trust store,
   |            key kept offline)
   | signs
   v
Intermediate   (online, issues certs)
   |
   | signs
   v
Leaf: shop.example.com + public key
```

Trust follows a **valid certification path**, not signatures alone: validity, constraints, permitted uses and relying-party policy must also pass. A correctly configured server sends the leaf and required intermediates; the client already has the trust anchor.

Why not let roots sign leaves directly? Replacing a widely distributed trust anchor can be operationally difficult because many relying parties need updated trust stores. So roots live in hardware security modules, often in offline vaults, and come out only to sign a new intermediate or a revocation list. If an intermediate is compromised, the root revokes it and signs a new one.

## Inside an X.509 certificate

Web certificates use the **X.509 v3** format (profiled in RFC 5280), encoded in ASN.1 DER and usually shown as base64 "PEM". The signed part is called the **TBSCertificate** ("to be signed"):

| Field | Example |
|---|---|
| Serial number | `04:3f:a1:...` (unique per CA) |
| Issuer | `CN=Toy Issuing CA` |
| Validity | not before / not after |
| Subject | `CN=shop.example.com` |
| Public key | EC P-256, 65 bytes |
| Extensions | see below |

After the TBS bytes come the signature algorithm and the CA's signature over them. Changing the signed subject or key bytes without a new valid signature causes verification to fail, under the scheme’s security assumptions.

The **extensions** carry most of the security meaning:

- **Subject Alternative Name (SAN)**: the DNS names (or IPs) the certificate is valid for, such as `shop.example.com` and `*.cdn.example.com`. Browsers match only against SAN; the old Common Name is ignored.
- **Basic Constraints**: `CA:TRUE` or `CA:FALSE`, plus an optional `pathLenConstraint` limiting the number of non-self-issued intermediate CA certificates below it in a valid path (not leaf certificates).
- **Key Usage / Extended Key Usage**: what the key may do, such as `keyCertSign` for a CA, or `serverAuth` and `clientAuth` for leaves.
- **Name Constraints**: limits a CA to certain namespaces, for example only names under `.corp.example.com`.
- **Authority Information Access**: where to download the issuer's certificate and where its OCSP responder lives.
- **CRL Distribution Points**: where to fetch the revocation list.
- **SCT list**: signed promises of timely inclusion in Certificate Transparency logs; an SCT is not itself a Merkle inclusion proof.

> [!warning] Basic Constraints is not optional
> In 2002, Moxie Marlinspike showed that Internet Explorer did not check Basic Constraints. Anyone with an ordinary leaf certificate could use it as a CA and sign a valid-looking certificate for any site. Microsoft documented the missing Basic Constraints checks in MS02-050; path authorization is separate from signature validity.

## Key takeaways
- Certificates bind names to public keys under a trusted issuer and policy.
- Roots anchor trust; intermediates permit routine issuance while restricting root-key use.
- SAN, Basic Constraints, key usage and name constraints add security meaning beyond a valid signature.

## Further reading
- [X.509 certificate profile — RFC 5280](https://www.rfc-editor.org/rfc/rfc5280)
- [ACME — RFC 8555](https://www.rfc-editor.org/rfc/rfc8555)
