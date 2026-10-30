---
id: nsec-tls-certificate-path
title: Building and checking a certificate path
level: intermediate
minutes: 3
summary: A certificate path connects the leaf certificate identity to an independently trusted anchor.
sourceLesson: nsec-tls
---

A server proving possession of a private key is useful only if the client can associate that key with the intended service. Certificate path validation and name checks supply that link.

## Certificate chains

A certificate ties a public key to names, and is signed by a **certificate authority** (CA). Clients use configured **trust anchors**, often from a browser, operating system or application root store. Store membership varies. Root private keys can be kept offline while intermediate CAs perform routine issuance; this is an operational design, not a property of every CA.

The following chain-shaped example illustrates a leaf certificate, intermediate and cross-signed root. It is not a live assertion of what `www.rfc-editor.org` currently serves:

```
0 leaf:  CN=rfc-editor.org
         issued by WE1
1 inter: WE1 (Google Trust Services)
         issued by GTS Root R4
2 cross: GTS Root R4
         issued by GlobalSign Root CA
```

The server sends its leaf certificate and needed intermediates. A client must independently trust a suitable anchor. Item 2 illustrates a **cross-signed certificate** for the same subject/key, with a different issuer and potentially different constraints, enabling an alternate path where supported.

Certificate validation includes the following checks (this is not an exhaustive validation algorithm; path-length/name constraints and unsupported critical extensions also matter):

1. Each signature verifies with the issuer's public key, up to a root it trusts.
2. The leaf certificate and intermediate certificates in the validation path are within their validity dates; trust-anchor handling is a separate client-policy input.
3. The leaf certificate's **Subject Alternative Name** matches the hostname. (Browsers ignore the old Common Name field.)
4. Intermediates are marked as CAs (`basicConstraints CA:TRUE`) and allowed to issue.
5. The leaf certificate is allowed for server authentication (extended key usage).
6. Applicable browser policies require **Certificate Transparency** evidence for publicly trusted certificates. A signed certificate timestamp is a log's promise to include the certificate, not itself an inclusion proof; SCTs need not be embedded in the certificate. Monitoring helps detect misissuance.

> [!analogy] Real-world analogy: a passport checked at a border
> A border officer accepts a passport only if it was issued by an authority the officer's government recognises, it has not expired, the photo and name match the traveller, and it is the right kind of document for entry. A passport printed by an unrecognised office is refused, however genuine it looks.
>
> **How it maps:** The passport is the leaf certificate, the issuing office is an intermediate CA, and the government's list of recognised authorities is the client's trust store of root anchors. Checking the photo and name is matching the Subject Alternative Name to the hostname; checking expiry and document type is checking validity dates, CA constraints and extended key usage.
>
> **Where it stops:** The officer compares physical features, while a client verifies digital signatures link by link and must also see proof that the server holds the matching private key (CertificateVerify): a copied certificate alone proves nothing. Trust stores also differ between browsers, operating systems and applications, so the "recognised authorities" are not the same everywhere.

> [!example] "It works in Chrome but not in curl"
> The server sends only its leaf certificate, not the intermediate. Desktop browsers often cope, because they cache intermediates or fetch them from a URL in the certificate. Other clients may fail with "unable to get local issuer certificate"; fetching and caching depend on the TLS backend, trust store and configuration, not just the application name. The fix is on the server: serve the full chain (leaf certificate plus intermediates).

## Key takeaways
- A certificate path connects the leaf certificate identity to an independently trusted anchor.
- Names, validity, permitted uses and CA constraints all matter.
- Serving required intermediates avoids depending on a particular client’s cache or fetching behaviour.

## Further reading
- [RFC 5280: Internet X.509 PKI Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280)
- [Certificate Transparency — MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Certificate_Transparency)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
