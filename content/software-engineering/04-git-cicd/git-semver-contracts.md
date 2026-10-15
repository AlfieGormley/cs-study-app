---
id: git-semver-contracts
title: Version numbers and compatibility contracts
level: advanced
minutes: 3
sourceLesson: git-cd-release
summary: SemVer signals compatibility with a declared public API.
---

Safe release engineering also communicates change to consumers. This unit covers compatibility promises, version ordering, dependency ranges and date-based alternatives.

## Semantic versioning

For anything others depend on (libraries, APIs, CLIs), the version number is a promise. **Semantic Versioning 2.0.0** defines `MAJOR.MINOR.PATCH`:

- **PATCH** (1.4.2 → 1.4.3): backward-compatible bug fixes.
- **MINOR** (1.4.3 → 1.5.0): backward-compatible new functionality, or deprecating something. Patch resets to 0.
- **MAJOR** (1.5.0 → 2.0.0): any backward-incompatible change to the public API. Minor and patch reset to 0.

Further rules worth knowing:

- **0.y.z is for initial development**: anything may change at any time. 1.0.0 defines the public API.
- **Pre-releases** use a hyphen: `2.0.0-rc.1`. A pre-release **ranks lower** than the release (it sorts earlier), and identifiers are compared piece by piece, numerically when they are digits. In this list `<` means "ranks lower than":

```
1.0.0-alpha < 1.0.0-alpha.1
 < 1.0.0-alpha.beta < 1.0.0-beta
 < 1.0.0-beta.2 < 1.0.0-beta.11
 < 1.0.0-rc.1 < 1.0.0
```

- **Build metadata** after a plus sign (`1.0.0+20260101`) is **ignored** for precedence.

### Version ranges

Package managers let consumers accept compatible updates automatically. In npm's notation:

| Range | Allows |
|---|---|
| `^1.2.3` | `>=1.2.3 <2.0.0` |
| `^0.2.3` | `>=0.2.3 <0.3.0` |
| `~1.2.3` | `>=1.2.3 <1.3.0` |
| `1.2.3` | Exactly 1.2.3 |

In this notation `>=` means "this version or newer" and `<` means "older than", so `>=1.2.3 <2.0.0` is every version from 1.2.3 up to, but not including, 2.0.0.

Note the caret is stricter below 1.0: `^0.2.3` does not accept 0.3.0, because in 0.x a minor bump may break things. Ranges also exclude pre-releases by default: `^1.2.3` does not match `1.3.0-beta.1`.

Ranges say what you are *willing* to accept; the **lockfile** records what you actually got, which helps reproduce dependency resolution. Bit-for-bit builds also require controlled toolchains, environment and other inputs.

### What counts as breaking?

More than you might think. Removing a function is obviously breaking. So can be: tightening input validation, changing an error type, changing default behaviour, or dropping support for a supported interpreter version. **Hyrum's Law** warns that with enough users, every observable behaviour of your system will be depended on by somebody. SemVer is a promise about your *documented* API; be conservative and document what is public.

## Calendar versioning

Not everything has an API contract. **CalVer** uses dates: Ubuntu's `24.04` is the April 2024 release. It suits applications and distributions where "how old is this?" matters more than compatibility signalling.

## Key takeaways

- SemVer signals compatibility with a declared public API.
- Pre-release identifiers affect precedence; build metadata does not.
- npm ranges define permitted versions, while a lockfile records a concrete resolution.
- Calendar versioning communicates release dates rather than API compatibility.

## Further reading

- [Semantic Versioning 2.0.0](https://semver.org/)
- [node-semver (range syntax)](https://github.com/npm/node-semver)
