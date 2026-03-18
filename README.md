# Secure Secr-AI-tery

![Secure Secr-AI-tery banner](docs/assets/sekretariat-copilot-banner.png)

**Your Free, Private & Offline AI Assistant.**

Secure Secr-AI-tery is a calm local workspace for school offices, school leaders, educators, and support teams.

It gives staff one clean screen for three things:

1. add context, information, and 2do's
2. choose or edit a saved prompt
3. run the local model and copy the result into email, a school system, or another tool

Nothing is auto-sent.
Nothing requires a cloud account.
Nothing needs a prompt engineer.

## Start Here

| If you are... | Read this first |
| --- | --- |
| a principal, headteacher, governor, or school decision-maker | [School Leader Brief](docs/SCHOOL_LEADER_BRIEF.md) |
| a school office operator or educator | this README |
| IT, a DPO, or a technical reviewer | [IT Deployment Guide](docs/IT_DEPLOYMENT.md) |
| testing on Windows | [Windows Setup](docs/WINDOWS_SETUP.md) |
| preparing a first trial | [Pilot Checklist](docs/PILOT_CHECKLIST.md) |

## What The App Does

The app follows one simple desktop flow:

1. open a past conversation from `History`, or start a new one
2. type or paste the task into `Context, Info & 2do's`
3. add one file if it helps
4. pick a saved prompt from `Prompts`, or write a new one
5. click `Run Prompt`
6. read the result in `AI Output`
7. delete it or copy it into the next program

The layout is intentionally rigid and simple for non-technical staff:

- left: recent chat history, newest first
- middle top: the current task context
- middle bottom: the current AI output
- right top: the prompt selector
- right bottom: the full editable prompt

## Why This Is Useful For Schools

School work is full of messages, notes, context fragments, and requests that need a reply, a summary, or a next step.

Most of that work is not complex.
It is repetitive.
It still needs judgement.

Secure Secr-AI-tery helps staff:

- draft calm replies
- summarise meetings
- turn rough notes into action lists
- prepare internal briefings
- reuse strong prompts without rewriting them each time

## Why Local-First Matters In Europe

This repo is built around a practical principle:

**if a school can keep routine AI drafting on a school-controlled machine, it removes a large amount of avoidable cloud complexity from day one.**

That matters because many schools worry about:

- data leaving the institution too quickly
- third-country transfer questions
- unclear processor chains
- foreign access risk under laws such as the US CLOUD Act
- recurring usage fees for everyday drafting

This project does not claim instant legal compliance by magic.
It makes a narrower and more useful promise:

- local by default
- offline-capable once the model is installed
- no mandatory cloud inference
- no automatic outbound action
- human review before anything is used elsewhere

That gives schools a stronger starting posture for GDPR review and for EU AI Act governance conversations.
It also removes default per-token costs when used with local models.

## Why Decision-Makers Like It

- It is easy to understand on one screen.
- It is easy to trial on one machine.
- It is easier to explain to staff than a general-purpose AI platform.
- It creates a visible privacy story, not just a marketing story.
- It can be inspected by IT because the repo, prompts, and logic are open.

## Why Operators Like It

- One place for context
- One place for prompts
- One clear run button
- One clear output box
- One clear copy button
- Prompt reuse without technical setup

## Why IT Teams Like It

- Python app
- SQLite
- local LM Studio server
- no container requirement
- cross-platform repo
- easy rollback
- no default internet dependency after setup

## Prompt Library

The right-hand side is a local prompt library.

- `Prompts` opens the saved prompt list.
- `Add new Prompt` starts a blank prompt.
- selecting a saved prompt loads its full text into the lower editor
- the lower editor is always editable
- `Save Prompt` writes the prompt into the local library

Important:
When you save a brand-new prompt, the app uses the **first non-empty line** as the prompt title.
That keeps the workflow simple for non-technical users and avoids forcing a separate title form.

## History

The left history panel stores past local runs from newest to oldest.

Each item shows a short purpose label so users can quickly reopen:

- what they were trying to do
- which prompt they used
- what kind of task the run was about

The app stores the local conversation context, prompt text, output text, and file names in SQLite so the user can reopen a previous run.
It does **not** need to store uploaded file bodies to make history work.

## Recommended First Use

Start with three saved prompts only:

1. `Draft a calm reply`
2. `Summarise key points`
3. `Turn notes into action list`

That is enough for a clean first pilot.

## Quick Start For IT

The full setup is in the [IT Deployment Guide](docs/IT_DEPLOYMENT.md).
The shortest local path is:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp config.example.toml config.toml
secure-secr-ai-tery
```

If the new launcher name is not found yet, the legacy fallback still works:

```bash
sekretariat-copilot
```

## Recommended LM Studio Model

Default app profile:

- backend: LM Studio local server
- model: `meta-llama-3.1-8b-instruct`
- temperature: `0.2`
- timeout: `120`

Recommended LM Studio inference settings are documented in the [IT Deployment Guide](docs/IT_DEPLOYMENT.md).

## Repository Structure

- `app/` UI and launcher
- `core/` typed models, config, storage, and shared helpers
- `services/` prompt runs, backend integration, file handling, and exports
- `prompts/` saved starter prompts and runtime prompt templates
- `fixtures/` synthetic examples for testing and demos
- `tests/` unit and integration tests
- `docs/` leadership, IT, privacy, pilot, and troubleshooting guides

## Limitations

- This is a desktop-first tool, not a mobile app.
- It is designed for human-reviewed drafting, not autonomous action.
- Uploaded files are single-file in the current UI by design, to keep the workflow simple.
- Prompt titles for new prompts are derived automatically from the first non-empty line.
- The GitHub repo name still says `Sekretariat-Copilot` for continuity, even though the app is now branded `Secure Secr-AI-tery`.

## Related Documents

- [IT Deployment Guide](docs/IT_DEPLOYMENT.md)
- [Windows Setup](docs/WINDOWS_SETUP.md)
- [School Leader Brief](docs/SCHOOL_LEADER_BRIEF.md)
- [Privacy Notes](docs/PRIVACY.md)
- [FAQ](docs/FAQ.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Pilot Checklist](docs/PILOT_CHECKLIST.md)
- [Demo Runbook](docs/DEMO_RUNBOOK.md)
- [Screen Recording Script](docs/SCREEN_RECORDING_SCRIPT.md)
- [Product Brief / PRD](docs/PRD.md)

## Creator

**Elias Kouloures = US-Speed + EU-Safeguards + Award-Winning Creativity**

- Homezone: Berlin, Germany
- Videocall: [calendar.app.google/ANb76KDuvg4J7LS28](https://calendar.app.google/ANb76KDuvg4J7LS28)
- E-Mail: [Elias.Kouloures@gmail.com](mailto:Elias.Kouloures@gmail.com)
- Website: [EliasKouloures.com](https://EliasKouloures.com)
- Videos: [YouTube.com/@EliasKouloures](https://YouTube.com/@EliasKouloures)
- Business: [LinkedIn.com/in/eliaskouloures](https://LinkedIn.com/in/eliaskouloures/)
