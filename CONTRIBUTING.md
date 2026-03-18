# Contributing

Thank you for your interest in Secure-Secr-AI-tery.

This project is public because it is both a useful local-first tool and a proof-of-work repository.

If you want to contribute, please keep the purpose of the project clear:

- help school offices
- keep the default path local-first
- keep humans in control
- keep the repo understandable for non-specialists

---

## Principles

Good contributions for this repo usually:

- improve clarity
- improve reliability
- improve privacy posture
- improve beginner setup
- improve Windows and macOS portability
- improve trust for schools and IT reviewers

Avoid changes that:

- add default cloud dependency
- weaken human review
- add auto-send behaviour
- expand the scope into grading, admissions, or student monitoring
- make the setup harder for first-time users

---

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Run the checks:

```bash
ruff check .
mypy app core services
pytest
```

---

## Contribution Style

- Prefer small diffs.
- Keep prompt templates separate from UI code.
- Preserve the local-first default path.
- Do not expose hidden reasoning in user-facing output.
- Add or update fixtures and tests when behaviour changes.
- Keep docs readable for school staff, leaders, and IT teams.

---

## Pull Requests

Please explain:

- what changed
- why it helps
- whether any user-facing behaviour changed
- whether tests or fixtures were added or updated

If your change affects privacy, deployment, or workflow scope, update the relevant docs too.
