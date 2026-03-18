# Security Policy

Secure-Secr-AI-tery is a local-first AI workspace for European schools and school support teams.

Security and trust matter.

---

## Reporting a Security Issue

Please do not open a public GitHub issue for sensitive security findings.

Instead, report security concerns directly to:

- E-Mail: [Elias.Kouloures@gmail.com](mailto:Elias.Kouloures@gmail.com)

Please include:

- a short summary of the issue
- affected files or features
- reproduction steps
- potential impact

---

## Safe Disclosure Expectations

Please avoid:

- posting real personal data
- posting confidential school material
- posting raw student or family data in issues or screenshots

Use synthetic examples whenever possible.

---

## Scope

This policy is especially relevant for issues involving:

- local storage of case data
- prompt handling
- file parsing
- export behaviour
- LAN exposure
- accidental outbound data flow
- logging of sensitive content

---

## Project Security Boundaries

This project is intentionally designed to:

- run locally by default
- bind to `127.0.0.1` by default
- avoid default cloud inference
- avoid auto-send behaviour
- avoid raw source logging by default

If you find behaviour that breaks those expectations, please report it.
