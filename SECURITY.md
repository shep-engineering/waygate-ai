# Security Policy

Waygate AI is a small LLM access library, but it still sits on a sensitive boundary:
application prompts, user-controlled text, provider credentials, and model
responses.

## Supported Versions

Waygate AI is pre-1.0. Security fixes target the latest active branch until a public
release policy is established.

## Reporting a Vulnerability

Do not open a public issue for a suspected vulnerability that includes exploit
details, credentials, private prompts, or customer data.

Until a dedicated security contact is published for the public repository,
report vulnerabilities privately to the project maintainer.

Include:

- affected version or commit
- reproduction steps
- impact
- whether credentials, prompts, or generated content were exposed
- suggested remediation, if known

## Security Scope

In scope:

- credential leakage in logs, errors, examples, tests, or docs
- prompt-injection guard bypasses
- unsafe provider error handling
- dependency or packaging issues that affect consumers
- documentation that encourages unsafe usage

Out of scope for this library:

- authentication and authorization in consuming applications
- database security in consuming applications
- model hallucination or factual correctness
- provider-side outages or policy changes

## Maintainer Commitments

- Never intentionally log API keys or credential-bearing values.
- Keep prompt-injection guard behavior covered by tests.
- Document known limitations clearly.
- Treat security behavior changes as release-visible changes.
- Avoid claims that imply complete protection from prompt injection.
