---
id: pki-certificates
title: Certificates and PKI
level: intermediate
minutes: 14
summary: How an X.509 certificate binds a name to a public key, how CAs validate domains and build chains of trust, why revocation is hard and certificates are getting shorter, and how Certificate Transparency keeps CAs honest.
---

The last lesson ended on a gap. A signature proves that a message was made by the holder of some private key. It does not tell you *whose* key it is. If an attacker can hand you their public key and say "this is bank.com", every signature check passes and you are talking to the attacker.

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

Trust follows a **valid certification path**, not signatures alone: validity, constraints, permitted uses and relying-party policy must also pass. The server sends the leaf and intermediates; the client already holds the root.

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

After the TBS bytes come the signature algorithm and the CA's signature over them. Change one bit of the subject or key and the signature fails.

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

## Getting a certificate

1. You generate a key pair. Protect the private key; where it is generated, backed up or used depends on the deployment and key-management service.
2. You create a **certificate signing request** (CSR, PKCS#10): your public key and requested names, *signed with your private key*. That signature proves you hold the key.
3. The CA validates that you control the names.
4. The CA signs a certificate and you install it with the intermediate chain.

For the web, step 3 is **domain validation** (DV), and **ACME** (RFC 8555) is one widely used automation protocol. It was developed through the IETF, with Let's Encrypt as an early deployment. The CA gives you a random token and checks you can publish it:

| Challenge | Proof of control |
|---|---|
| HTTP-01 | Serve key authorization under `/.well-known/acme-challenge/<token>` |
| DNS-01 | Publish a digest of key authorization under `_acme-challenge.<name>` |
| TLS-ALPN-01 | Present a special cert on port 443 |

For Let's Encrypt wildcard requests, use DNS-01. Control of the delegated challenge record can satisfy this validation; it need not give control of every record in the entire zone. Organisation Validation (OV) and Extended Validation (EV) add legal-entity validation requirements. They do not inherently provide stronger encryption than DV; actual cryptographic strength depends on the chosen keys, algorithms and protocol. Historical UI-effectiveness claims are omitted here because their research evidence was not reviewed.

Domain validation has a weak spot: it trusts DNS and routing *from the CA's point of view*. An attacker who hijacks a BGP route to your server for a few minutes could pass HTTP-01. CAs now validate from several network vantage points (**multi-perspective validation**), and you can publish a **CAA** DNS record listing which CAs may issue for your domain at all.

## How a client validates a chain

A client given a leaf and some intermediates must **build a path** to a trusted root, then check every link:

1. Each certificate's signature verifies with the next one's public key.
2. The certificates in the path are within their validity windows. A trust anchor is an input to validation, not necessarily processed as another path certificate; root-certificate expiry handling varies.
3. Intermediate issuers are authorized CAs; Basic Constraints, applicable Key Usage, path length, name constraints and unrecognized critical extensions are checked.
4. The leaf's SAN matches the hostname, and its EKU allows `serverAuth`.
5. Apply the client's revocation and browser CT policies. Coverage, freshness and failure handling vary; certificate-path validation alone does not establish either.

Path building is harder than it looks, because a CA can have several certificates with the same key: a self-signed root plus **cross-signed** versions issued by older roots, so new CAs work on old devices. On 30 September 2021 the old root that cross-signed Let's Encrypt, DST Root CA X3, expired. Clients that built paths properly switched to Let's Encrypt's own ISRG Root X1. Older OpenSSL 1.0.2 builds insisted on the expired path and failed, breaking many API integrations that day.

Here is step 1 alone, using the `cryptography` library:

```python
from cryptography import x509

def check_links(chain):
    # chain[0] = leaf, chain[-1] = root
    for c, iss in zip(chain, chain[1:]):
        # raises if the signature is bad
        c.verify_directly_issued_by(iss)
        print(c.subject.rfc4514_string(),
              "<-",
              iss.subject.rfc4514_string())
```

For a root, intermediate and leaf, this prints `CN=shop.test <- CN=Toy Issuing CA` then `CN=Toy Issuing CA <- CN=Toy Root`. `verify_directly_issued_by` checks issuer/subject name agreement and signature validity; this loop does not check dates, hostname, CA constraints, trust, revocation or CT. Use a maintained validator and configure the required policy. `cryptography.x509.verification.PolicyBuilder` can build a server verifier with hostname/path checks, but does **not** automatically perform live revocation or browser CT enforcement.

## Revocation: the unsolved part

If a server's private key leaks, its certificate stays cryptographically valid until it expires. **Revocation** tries to cut that short:

- **CRLs**: the CA publishes a signed list of revoked serial numbers. Simple, but lists can grow to megabytes.
- **OCSP**: the client asks the CA's responder about one certificate. Small, but slow, and it tells the CA which sites you visit.
- **OCSP stapling**: the server fetches a signed OCSP response itself and attaches it to the handshake, fixing privacy and latency.

All three hit the same problem: what should a client do if the answer does not arrive? Hard-failing breaks sites whenever a responder has an outage. A **soft-fail** policy accepts when status cannot be obtained, which an attacker may exploit by blocking retrieval. Other clients use hard-fail, cached or pushed status. No single behavior applies to every browser, platform and private PKI.

Browser approaches differ. Chrome distributes **CRLSets** with selected revocations rather than complete coverage. Mozilla began production **CRLite** use in Firefox 142, using compressed revocation data for covered WebPKI certificates; coverage and fallback policy matter. Let's Encrypt ended its OCSP service in 2025 and publishes CRLs instead.

Shorter validity reduces the exposure window for a particular certificate, but does not eliminate the need for revocation, key replacement or preventing fraudulent renewal. The CA/Browser Forum has voted to cut maximum public certificate lifetimes from 398 days to 200 days from March 2026, then 100 days in 2027 and 47 days in 2029. The issuance-date cutoffs are 15 March 2026, 2027 and 2029 respectively. Automation becomes operationally valuable; the policy does not mandate ACME specifically.

## Keeping CAs honest

An unconstrained trusted CA can authorize names outside the domains it usually serves. The accepted root set and constraints vary by platform and policy, so one compromised CA can affect many relying parties.

> [!example] DigiNotar, 2011
> Attackers broke into the Dutch CA DigiNotar and issued hundreds of fraudulent certificates, including one for `*.google.com`, which was used to intercept Gmail users in Iran. Chrome caught it because it pinned Google's keys. Mozilla removed trust following the incident. This example concerns the documented certificate compromise, not a verified account of the company's later legal or financial proceedings.

Since then, the main defence has been **Certificate Transparency** (CT, RFC 6962). For certificates subject to public-browser CT policies, issuance involves submitting certificates or precertificates to append-only Merkle-tree logs. This does not apply to every private or non-TLS certificate. The log returns a **signed certificate timestamp** (SCT), a promise to include the certificate, which can be delivered in a certificate extension or by other supported TLS/OCSP mechanisms. Chrome and Safari reject public certificates without enough SCTs from independent logs.

CT does not prevent mis-issuance; it makes it **visible**. You can watch the logs for your domains (crt.sh, or your CA's monitoring), and researchers routinely spot CAs breaking the rules. Chrome's 2018 Symantec changes eventually distrusted certificates chaining to its old infrastructure, not only newly issued ones. Its Entrust/AffirmTrust change used a November 2024 issuance cutoff. Exact browser policies and managed-environment exceptions differ.

Browsers also run their own root programmes. Mozilla, Apple, Microsoft and Google each decide which roots to ship, and audit them against the CA/Browser Forum's Baseline Requirements.

## Private PKI

Not every certificate comes from a public CA. Organisations run **private CAs** for internal services, VPNs, devices and **mutual TLS**, where clients present certificates too. Service meshes such as Istio issue each workload a certificate with a SPIFFE identity (`spiffe://cluster/ns/shop/sa/api`), valid for about a day by default, and rotate it automatically.

Private PKI gives you control and short lifetimes, but you inherit the CA's problems: protecting the root key, distributing trust to every client, and handling revocation. Appropriate name constraints can limit what enforcing clients accept, but must cover the identity forms actually used. DNS constraints alone do not constrain arbitrary SPIFFE URI identities. A stolen issuing key can keep signing until its trust is removed or otherwise rejected.

## Pitfalls

- **Disabling verification.** `verify=False`, `CERT_NONE` or `InsecureSkipVerify: true` turn TLS into encryption with a stranger.
- **Missing intermediates.** Some clients recover missing intermediates through caches or AIA retrieval; others do not. Serve the needed intermediate chain rather than depending on client-specific recovery.
- **Expiry outages.** Certificates expire on a schedule you know years ahead, and still take down major services. Automate renewal and alert on days-to-expiry.
- **Pinning without a plan.** HTTP Public Key Pinning (HPKP) was removed from browsers because a wrong pin could lock users out for months. Apps that pin should pin a CA or a backup key, not a single leaf.

## Key takeaways
- A certificate is a CA's signature binding names (in SAN) to a public key; PKI is the system of who may sign and how trust is distributed.
- Trust flows from a small root store through intermediates to leaves; root-key protection and infrequent use are common operational designs, not requirements of every PKI.
- Clients must check signatures, dates, CA constraints, the hostname, key usage and revocation; skipping one has broken real systems.
- ACME automates domain validation; CAA and multi-perspective validation narrow attacks on it.
- Revocation is unreliable because clients soft-fail; browsers push revocation data and the industry is moving to 47-day certificates.
- CT policies promote public logging and monitoring can reveal mis-issuance; SCT promises, log operation and client enforcement do not guarantee every mis-issued certificate is immediately detected.

## Further reading
- [RFC 5280: Internet X.509 PKI Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280)
- [RFC 8555: Automatic Certificate Management Environment (ACME)](https://www.rfc-editor.org/rfc/rfc8555)
- [How Certificate Transparency works](https://certificate.transparency.dev/howctworks/)
- [DST Root CA X3 expiration (September 2021) — Let's Encrypt](https://letsencrypt.org/docs/dst-root-ca-x3-expiration-september-2021/)
- [X.509 verification — pyca/cryptography docs](https://cryptography.io/en/latest/x509/verification/)
- [DigiNotar — Wikipedia](https://en.wikipedia.org/wiki/DigiNotar)
