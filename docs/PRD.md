# Sekretariat-Copilot PRD

## Title

Sekretariat-Copilot (School Administration Automator) — Agent-Ready MVP PRD for OpenAI Codex

## Context

Sekretariat-Copilot is a privacy-first, sovereign administrative sidecar for school offices. It reduces repetitive office work by turning messy inbound admin material into clean, copy-ready outputs.

The MVP is designed for one clear purpose:

1. Build a polished demo-ready product on a local iMac with Codex.
2. Publish the repo for free on GitHub.
3. Use the repo and demo film as proof of capability for premium AI services aimed at schools and other organisations.

## MVP requirements

- fully usable offline on one machine
- optionally usable on a trusted intranet
- easy for a beginner to build and run
- visually sleek, calm, and professional
- portable to Windows with the same repo
- upward-compatible with stronger local hardware and larger models later

## Product scope

### Inputs

- pasted text
- manually typed notes
- images
- PDFs

### Core workflows

- absence processing
- parent communication drafting
- meeting or scheduling summary
- general admin triage

### Outputs

- structured facts
- internal case brief
- three subject line options
- three communication variants:
  - Hemingway-style
  - Corporate
  - Educator-first
- warnings and missing information
- optional JSON and CSV export

## Key constraints

- British English only
- local web app by default
- human review mandatory
- no outbound auto-send
- no real school data; synthetic fixtures must ship with the repo
- handwritten OCR out of scope for MVP
- multi-child messages out of scope for MVP
- Windows compatibility required

## Functional requirements

### FR-1 Input analysis

- accept pasted text, typed note, image file, and PDF file
- auto-detect likely workflow
- allow manual workflow override
- normalise whitespace, dates, names, and obvious admin entities
- reject unsupported low-quality inputs gracefully

### FR-2 File analysis

- accept `.pdf`, `.png`, `.jpg`, `.jpeg`
- try direct text extraction for digital PDFs first
- use local vision OCR only when confidence is acceptable
- stop and ask for clearer input when OCR confidence is low
- report whether output came from direct text, OCR, or both

### FR-3 to FR-10

- infer whether the user needs extraction, drafting, scheduling summary, or triage
- detect conflicts, missing fields, duplicate collisions, unsupported multi-child cases, and unclear intent
- generate structured facts, action summary, internal brief, and communication outputs when relevant
- produce exactly 3 subject lines and exactly 3 tone variants in a fixed order
- generate a concise internal case brief for every successful run
- score confidence as High, Medium, or Low
- generate 1 to 3 clarifying questions when the minimum required information is missing
- require human review and allow reset

### FR-11 to FR-16

- keep copy-ready text primary and exports secondary
- run on `localhost` by default with optional intranet mode
- abstract the model backend behind config
- avoid containers and keep installation beginner-friendly
- include PRD, README, AGENTS.md, fixtures, and prompt templates
- support test-first milestone delivery

## Non-functional requirements

- target text-only p50 under 5 seconds and p95 under 12 seconds on recommended hardware
- fail safely
- never invent missing mandatory facts
- store minimal operational metadata only
- minimise OS-specific code
- keep prompt templates separate from UI code
- include synthetic fixtures for regression testing

## UX notes

### Visual direction

- Institutional Cyber-Trust meets Modern Bureaucracy
- calm, audited, secure, symmetrical, and structured
- avoid glitch aesthetics, cyberpunk, moody shadows, and generic AI visuals

### Layout

- one large headline
- two font sizes only
- 8px grid
- strong whitespace
- symmetrical grid
- one primary CTA: `Process locally`
- one reset control: `Reset case`

### Required structure

- top bar with headline, status pill, and KPI
- split main layout with inputs on the left and outputs on the right
- lower area with one chart and one recent-case list

## Data model

The MVP persists these entities:

- `Case`
- `InputAsset`
- `ExtractedRecord`
- `ReplySet`
- `CaseBrief`
- `ClarifyingQuestion`
- `AuditEvent`

See the original planning brief for the complete field-level contract. This implementation keeps those names and stable snake_case export keys.

## API contracts

The service layer exposes:

- `health_check()`
- `analyse_case(payload)`
- `generate_outputs(case_id)`
- `export_case(case_id, format)`
- `reset_case(case_id)`

## Acceptance focus

The MVP is accepted when it can:

- process full-detail absence text correctly
- surface placeholders and clarifying questions when information is missing
- always return exactly 3 subject lines and 3 tone variants for communication tasks
- extract digital PDF text before OCR
- reject blurry or handwritten image input without hallucinating
- block multi-child messages
- show clear recovery states when the backend is offline
- reset case state
- run from the same repo on Windows without code changes
- ship with 20 synthetic regression fixtures

