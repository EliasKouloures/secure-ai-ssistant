# Sekretariat-Copilot

Free, local-first AI software for school offices that want faster administration without sending routine school data to a public cloud by default.

This repository is intentionally public and free to use. It is both:

1. a working local web app for school administration workflows
2. a live demonstration of privacy-first, multidisciplinary AI product work for schools and other organisations

It is designed as a calm, practical sidecar for existing school processes, not as a risky “replace everything with AI” platform.

---

## What This Is, in Plain English

School offices spend too much time turning messy inputs into clean outputs:

- a parent email about an absence
- a typed note from a phone call
- a screenshot from a messaging app
- a PDF form or letter

Sekretariat-Copilot helps office staff turn those messy inputs into a clean review pack:

- structured facts
- a short internal case brief
- subject line suggestions
- three draft reply styles
- warnings about missing information
- clarifying questions when the message is incomplete

The key idea is simple:

**staff stay in control, the machine does the repetitive drafting work, and nothing is sent automatically.**

This is for schools that want useful AI without forcing staff into a complicated new system.

---

## Why This Use Case Matters for Schools

School administration is full of repetitive, low-value tasks that still require care:

- absence messages
- parent communication
- meeting notes
- document triage
- copy-paste into existing systems

These are exactly the kinds of tasks where many AI pilots fail in practice: they are too generic, too cloud-dependent, too hard for non-technical staff, or too risky for data protection review.

This project was built around a different assumption:

> schools do not need a giant AI transformation programme first  
> they need one narrow, useful, easy-to-understand tool that saves time immediately

That is why this repo focuses on:

- one-machine deployment
- beginner-friendly setup
- local processing by default
- human review before anything leaves the system
- narrow administrative workflows instead of vague “AI assistant” promises

---

## Why Many European Schools Prefer a Local-First Setup

### The short version

If a school uses a cloud AI service operated by an external vendor, especially a non-EU vendor, it usually creates more legal, procurement, governance, and trust questions than a local-first setup.

This repository is designed to reduce those questions by keeping routine processing on a school-controlled machine by default.

### What local-first means here

By default:

- the web app runs on the same machine as the model
- the model runs locally through LM Studio
- requests go to `127.0.0.1`
- raw inputs are treated as transient working material
- the app stores only minimal local audit metadata by default
- no message is auto-sent

### Why this can be easier to defend than a cloud AI rollout

Compared with a typical cloud AI workflow, this approach can make it easier to support:

- data minimisation
- purpose limitation
- local control
- lower exposure to third-party subprocessors
- clearer staff explanations
- lower procurement friction
- lower recurring cost

### A careful note on US cloud providers

This README does **not** claim that every US product is automatically illegal or unusable in every school context.

The narrower point is this:

- when a school sends personal data to a US-controlled cloud provider, it may need to assess third-country transfer issues, vendor contracts, subprocessors, access controls, and legal exposure more carefully
- laws and enforcement frameworks such as the **US CLOUD Act** are one reason many European institutions prefer to avoid putting routine sensitive workflows into foreign cloud environments when a local alternative exists
- even when large vendors improve contracts and controls, compliance depends on the exact deployment, safeguards, and legal assessment, not on marketing language alone

So the selling point of this repo is not “magic legal immunity”.

The selling point is:

**keep the routine work local first, and remove avoidable cloud risk where possible.**

### Cost advantage

If you run the app with a local model:

- there are no per-token API charges
- there is no mandatory SaaS subscription for inference
- there is no usage meter increasing every time staff draft a reply

There are still costs, of course:

- hardware
- electricity
- staff time
- setup and support

But there are no default recurring cloud inference charges once the system is installed and the models are downloaded.

---

## GDPR and EU AI Act Positioning

### Important legal note

This project is designed to be **more compliance-friendly**, not automatically “compliant by magic”.

It supports good governance choices such as:

- local processing
- limited logging
- human review
- copy-first outputs instead of auto-sending
- explicit warnings when information is missing
- avoiding unsupported or risky cases

But every school still needs its own review of:

- lawful basis
- records of processing
- access control
- retention
- procurement
- vendor review
- staff guidance
- whether a DPIA is required
- whether local supervisory or ministry rules apply

### GDPR framing

This architecture is aligned with the **direction** of GDPR-friendly design because it helps schools pursue:

- **purpose limitation**
- **data minimisation**
- **storage limitation**
- **integrity and confidentiality**
- **data protection by design and by default**

That is much easier to explain when the app and model stay on a school-controlled device than when routine staff messages are sent to an external AI processor.

### EU AI Act framing

This project is meant to be used as a **human-in-the-loop drafting and triage tool**, not as an automated decision-maker.

That distinction matters.

This MVP is intended for:

- drafting
- summarising
- extracting facts
- generating clarifying questions

It is **not** intended for:

- grading students
- deciding admission
- deciding educational placement
- automated behavioural monitoring
- automated disciplinary decisions

If a school extends this kind of system into admission, assessment, or student monitoring workflows, that may move it into far more demanding AI Act territory.

### Current regulatory timing

At the time of writing:

- the AI Act entered into force in 2024
- AI literacy obligations have applied since **2 February 2025**
- most AI Act rules apply from **2 August 2026**
- some Article 6(1) high-risk classification obligations apply from **2 August 2027**

So schools should treat this repo as a **governance-supporting local tool**, not as a substitute for legal and policy review.

---

## What This App Does

### In scope

- local web app in Python
- runs on one machine by default
- optional intranet profile if you deliberately enable it
- accepts:
  - pasted text
  - manually typed notes
  - images
  - PDFs
- supports workflows for:
  - absence processing
  - parent communication drafting
  - meeting and scheduling summaries
  - general admin triage
- generates:
  - structured facts
  - internal case brief
  - 3 subject lines
  - 3 tone-controlled draft variants
  - warnings
  - clarifying questions
- JSON and CSV export as secondary options

### Safety choices built into the app

- no auto-send
- human review is mandatory
- unsupported cases are blocked clearly
- low-confidence OCR is rejected instead of guessed
- multi-child cases are blocked
- handwritten OCR is out of scope
- hidden reasoning is stripped from visible output

### Current limitations

- British English only
- no mobile app
- no deep integration with school systems
- no production SSO
- no handwritten cursive support
- no multi-tenant cloud deployment

---

## Who This Repo Is For

### 1. School administrators

Use it when you want a practical assistant for routine office communication and document handling.

### 2. School leaders

Use it when you want to show staff, governors, or stakeholders a serious, privacy-first AI direction that looks calm and credible.

### 3. IT teams and data protection reviewers

Use it when you want a transparent, inspectable, local-first starting point instead of a black-box SaaS promise.

### 4. Organisations evaluating my services

This free repo is also a working example of the kind of work I do:

- AI workflow design
- local-first deployment strategy
- UX and product design
- privacy-first technical architecture
- prompt and service design
- technical documentation for non-technical users

---

## Why This Repo Exists Publicly

I am giving this away for free because the repository itself is useful as:

- a demo for school stakeholders
- a practical evaluation sandbox
- a proof that local AI can be calm, useful, and implementable
- a public example of multidisciplinary AI product work

If you want a school-specific rollout later, this repo can become the starting point for:

- custom workflows
- local policy packs
- installation support
- staff training
- design improvements
- integration planning

---

## What a School Administrator Actually Does With It

You do **not** need to understand machine learning to use this app.

Typical workflow:

1. Open the app in a browser on the local machine.
2. Paste a parent email, type a phone note, or upload an image or PDF.
3. Choose a workflow, or leave workflow detection on auto.
4. Click **Process locally**.
5. Review the generated facts, brief, subject lines, and reply drafts.
6. Edit the text if needed.
7. Copy the final output into your email system or school information system.
8. Click **Reset case** when you are done.

### Example

Input:

> “Leo Martin in Year 4B will be absent tomorrow due to illness.”

Output:

- extracted student and class
- date warning if “tomorrow” needs anchoring
- internal brief
- three subject lines
- three reply variants
- clarifying question if something is missing

The goal is not to replace office judgement.

The goal is to remove repetitive formatting, summarising, and drafting work.

---

## Why This Works Better Than a Generic Chatbot Pilot

This project was shaped around a problem seen repeatedly in European organisations:

**pilot purgatory**.

That usually happens when:

- the tool is too generic
- the workflow is unclear
- the buyer is told to “experiment”
- governance questions arrive later
- the interface looks technical
- nobody owns rollout

Sekretariat-Copilot tries to avoid that by being:

- narrow
- role-specific
- offline-friendly
- easy to demo
- easy to explain to non-technical staff
- built around one visible business outcome: faster, cleaner administrative handling

---

## Architecture at a Glance

### Default local architecture

```text
Browser
  -> Streamlit app (local web UI)
  -> Python service layer
  -> SQLite database (local metadata and outputs)
  -> LM Studio local server (OpenAI-compatible endpoint)
  -> Local model running on the same machine
```

### Default privacy posture

- bind to `127.0.0.1`
- no outbound sending
- raw inputs not logged by default
- minimal audit metadata only
- optional LAN mode is off by default

### Why LM Studio

LM Studio is the recommended local model host here because it gives beginners:

- a graphical interface
- Apple Silicon support
- OpenAI-compatible local API endpoints
- local server mode on `localhost`
- offline operation once models are downloaded
- an easier path to testing text and vision models without building your own inference stack

---

## Quick Start for Novice Users

This section is for a single person on a Mac who wants the simplest path.

### What you need

- an Apple Silicon Mac or a Windows machine
- Python 3.12, 3.13, or 3.14
- LM Studio
- one local text model
- optionally one local vision model for image OCR

### Before you start

If you want the app to work fully offline later, download the models **before** disconnecting from the internet.

### The fastest safe path on Mac

If you want the shortest route, do this:

1. Install LM Studio.
2. Download one small text model.
3. Start the LM Studio local server.
4. Open Terminal in this repo.
5. Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp config.example.toml config.toml
sekretariat-copilot
```

Then open:

```text
http://127.0.0.1:8501
```

If that works, stop there. You are ready.

### Step 1: Install LM Studio

1. Download LM Studio for your operating system.
2. On Mac, make sure you use the **Apple Silicon / arm64** build.
3. Open LM Studio.

### Step 2: Download a model

Start simple.

For a 16 GB Apple Silicon machine:

- begin with a small instruct model in the roughly **7B to 8B** range for text workflows
- only add a vision-capable model if you really need image OCR

Practical advice:

- text workflows are the most reliable place to start
- digital PDFs work even without a vision model because the app first tries direct PDF text extraction
- image OCR depends on model quality and memory limits

### Step 3: Start the LM Studio local server

In LM Studio:

1. Load your chosen model.
2. Open the **Developer** tab.
3. Start the local server.
4. Confirm it is serving on `http://127.0.0.1:1234/v1`.

This project uses LM Studio through its OpenAI-compatible local API.

### Step 4: Download or clone this repo

```bash
git clone <your-repo-url>
cd Sekretariat-Copilot
```

If you are not using Git yet, you can also download the repository as a ZIP and unpack it.

### Step 5: Check Python first

Run:

```bash
python3 --version
```

If you see `Python 3.12`, `Python 3.13`, or `Python 3.14`, you are fine.

If `python3` works, use `python3`.  
If `python3.12` works, you may use `python3.12`.  
If `python3.12` does **not** work, that is normal on many Macs.

### Step 6: Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If that fails, try:

```bash
python -m venv .venv
```

If both commands fail, Python is not installed correctly yet.

### Step 7: Install the app

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

### Step 8: Create your local config

```bash
cp config.example.toml config.toml
```

Open `config.toml` and check:

- `base_url` should usually stay `http://127.0.0.1:1234/v1`
- `model_id` should match the model you actually loaded in LM Studio
- `supports_vision = true` only if you have loaded a vision-capable local model

### Step 9: Run the app

```bash
sekretariat-copilot
```

Then open:

```text
http://127.0.0.1:8501
```

If the command `sekretariat-copilot` is not found, try:

```bash
.venv/bin/sekretariat-copilot
```

### Step 10: Test with synthetic fixtures

Use the files in [`fixtures/`](fixtures/) first before using any real school material.

Recommended first tests:

- [`fixtures/text/absence_full.txt`](fixtures/text/absence_full.txt)
- [`fixtures/notes/note_missing_dates.txt`](fixtures/notes/note_missing_dates.txt)
- [`fixtures/pdfs/pdf_absence_direct.pdf`](fixtures/pdfs/pdf_absence_direct.pdf)
- [`fixtures/images/image_absence_clear.png`](fixtures/images/image_absence_clear.png)

---

## LM Studio Notes That Matter

### 1. The app talks to LM Studio like it talks to OpenAI

That is deliberate.

The app uses the OpenAI Python SDK but points it to a local endpoint:

- `GET /v1/models`
- `POST /v1/chat/completions`

So the app feels future-friendly while still staying local.

### 2. Offline really means offline after download

Once your model files are on the machine, LM Studio can run locally without internet access.

### 3. Start with text workflows

If you want the smoothest first impression:

- keep `supports_vision = false`
- use pasted text, typed notes, and digital PDFs first

Only add image OCR when the core text path is stable.

### 4. Model size matters

On 16 GB unified memory:

- smaller instruct models are the safe starting point
- larger models may slow down badly or fail to load comfortably
- vision models usually require more care than text-only models

### 5. If the wrong model is loaded, the app will tell you

The app includes a health check and diagnostics screen so you can verify:

- backend reachable or not
- configured model ID
- active backend base URL
- recent error summary

---

## Windows Notes for Novice Users

Windows is supported from the same repo.

Basic flow:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item config.example.toml config.toml
sekretariat-copilot
```

If `py -3` does not work, check:

```powershell
py --version
python --version
```

Use whichever Python launcher exists on your machine.

More detail:

- [Windows setup guide](docs/WINDOWS_SETUP.md)
- [Troubleshooting guide](docs/TROUBLESHOOTING.md)

---

## For School Leaders: What the Business Case Looks Like

This tool is not trying to become the school’s central platform.

That is the point.

It is valuable precisely because it is:

- small enough to trial
- narrow enough to understand
- cheap enough to explore
- local enough to defend
- polished enough to demo

### Practical leadership benefits

- less repetitive drafting work
- more consistent office language
- fewer copy-paste mistakes
- faster response preparation
- a stronger digital sovereignty story
- a realistic first AI step without a giant procurement programme

---

## For IT Departments and Data Protection Reviewers

This section is for technical teams who are comfortable with systems and policy, but not necessarily with AI tooling yet.

### What you are actually deploying

You are deploying:

- a Python web app
- a local SQLite database
- a local inference host
- one or more local models

You are **not** deploying:

- a managed cloud SaaS
- a student-facing AI system
- an auto-sending communications bot
- an autonomous decision-maker

### Recommended first deployment profile

Use this profile for the first school pilot:

- one dedicated Mac or Windows PC in the office
- local user account with restricted access
- LM Studio running locally
- app bound to `127.0.0.1`
- no intranet mode
- no real student data until fixture-based acceptance is complete

### Security and governance checklist

Before real use, confirm:

1. The device is encrypted.
   - FileVault on macOS
   - BitLocker on Windows

2. The machine is access-controlled.
   - named staff users
   - automatic screen lock
   - no shared generic passwords

3. The workflow scope is limited.
   - drafting and summarising only
   - no grading
   - no admission decisions
   - no monitoring or profiling use

4. The school defines a retention rule.
   - what stays in SQLite
   - for how long
   - who may access it

5. The school documents human oversight.
   - every output is reviewed by staff
   - no automatic sending
   - staff remain responsible for final communication

6. The school checks whether a DPIA is required.
   - especially if sensitive categories of data may be processed
   - or if the system is extended beyond this MVP scope

7. The school provides staff instructions.
   - what may be pasted in
   - what must not be pasted in
   - when to stop and escalate

### AI Act checklist for the IT or compliance lead

Use this repo as a low-risk drafting assistant only.

Ask these questions explicitly:

1. Is the system being used only for administrative drafting and summarisation?
2. Is a human reviewing every output?
3. Is the school avoiding automated decisions on access, grading, or monitoring?
4. Is staff AI literacy guidance in place?
5. Is the intended purpose documented?
6. Is there a clear list of prohibited uses?

If the answer to any of these becomes unclear, stop and reassess before rollout.

### GDPR checklist for the IT or compliance lead

At minimum, document:

1. purpose of processing
2. lawful basis
3. categories of personal data involved
4. access rights
5. retention rule
6. local security controls
7. incident response path
8. whether any data ever leaves the device or local network

### Intranet mode

This project can be exposed on a trusted local network, but that should be treated as a deliberate second step, not the default.

If you enable intranet mode:

- do it only on a trusted LAN
- confirm that the model host is not unintentionally exposed more widely
- document who can reach the service
- consider firewall restrictions and reverse proxy controls

For most first pilots, keep everything on `localhost`.

---

## Step-by-Step Installation for the IT Department

This is the recommended handoff path for a school IT team.

### Phase 1: Prepare the pilot machine

1. Choose the machine.
   - Apple Silicon Mac preferred for the reference path
   - Windows supported from the same repo

2. Patch the OS.

3. Enable disk encryption.

4. Create or assign the local user account that will operate the app.

5. Decide whether the first rollout is:
   - text only
   - text + digital PDF
   - text + PDF + image OCR

### Phase 2: Install LM Studio

1. Download LM Studio from the official site.
2. Install the correct OS build.
   - On Mac, use Apple Silicon / arm64.
3. Open the application.
4. Download:
   - one small instruct model for text workflows
   - optionally one vision-capable model for OCR workflows
5. Load the model.
6. Open the **Developer** tab.
7. Start the local API server.
8. Confirm the endpoint is available at `http://127.0.0.1:1234/v1`.

### Phase 3: Install the app

```bash
git clone <your-repo-url>
cd Sekretariat-Copilot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp config.example.toml config.toml
```

If `python3` is missing but `python3.12` exists, use `python3.12 -m venv .venv` instead.

If `sekretariat-copilot` is not found after install, run:

```bash
.venv/bin/sekretariat-copilot
```

### Phase 4: Configure the app

Open `config.toml`.

Important fields:

- `provider_name`
  - default is `lm_studio`

- `base_url`
  - usually `http://127.0.0.1:1234/v1`

- `model_id`
  - must match the model actually loaded in LM Studio

- `supports_vision`
  - `false` for text-only operation
  - `true` only when a working local vision model is loaded

- `bind_host`
  - keep `127.0.0.1` for the first deployment

- `database_path`
  - choose local storage location according to school device policy

### Phase 5: Verify the deployment

1. Start the app:

```bash
sekretariat-copilot
```

2. Open `http://127.0.0.1:8501`.

3. Confirm the status pill shows the backend is reachable.

4. Run fixture-based checks:
   - absence text
   - missing-info note
   - digital PDF
   - one clear screenshot if vision is enabled

5. Open the diagnostics section and confirm:
   - backend reachable
   - model ID correct
   - no unexpected errors

### Phase 6: Pilot safely

1. Start with synthetic fixtures only.
2. Move to low-sensitivity internal examples.
3. Only then move to real office material under local policy.
4. Train staff on:
   - when to use the tool
   - when not to use the tool
   - how to review outputs
   - how to recognise blocked or low-confidence cases

### Phase 7: Harden before wider rollout

1. Define retention and backup handling for the SQLite database.
2. Confirm local antivirus / endpoint protection posture.
3. Restrict local network exposure.
4. Document support ownership.
5. Document rollback steps.

---

## Repository Layout

- `app/` Streamlit UI, styles, launcher, and copy helpers
- `core/` typed models, config, storage, and text utilities
- `services/` analysis, ingestion, output generation, export, backend, orchestration
- `prompts/` prompt templates
- `fixtures/` synthetic regression fixtures and demo material
- `tests/` automated tests
- `docs/` PRD, setup notes, privacy note, troubleshooting, and demo runbook

---

## Developer and Verification Commands

```bash
ruff check .
mypy app core services
pytest
```

Run the app:

```bash
sekretariat-copilot
```

---

## Troubleshooting

### The app says the backend is unavailable

- make sure LM Studio is open
- make sure a model is loaded
- make sure the server is running in the Developer tab
- confirm `base_url` and `model_id` in `config.toml`

### PDFs work but screenshots do not

- you probably do not have a vision-capable model loaded
- set `supports_vision = false` and use text or digital PDFs first
- or load a compatible vision model in LM Studio and try again

### The machine feels too slow

- switch to a smaller model
- keep OCR disabled until needed
- start with text-only workflows

### Staff want to use it from another device

- do not enable intranet mode casually
- first decide whether the trusted-LAN trade-off is acceptable
- localhost-only is the safer default

### `python3.12` says `command not found`

That usually means Python is installed as `python3`, not `python3.12`.

Try:

```bash
python3 --version
python3 -m venv .venv
```

If `python3` works, use it.

### `sekretariat-copilot` says `command not found`

Your virtual environment may not be active.

Run:

```bash
source .venv/bin/activate
```

Then try again.

If needed, run the command directly:

```bash
.venv/bin/sekretariat-copilot
```

More detail:

- [Troubleshooting guide](docs/TROUBLESHOOTING.md)
- [Privacy note](docs/PRIVACY.md)
- [Demo runbook](docs/DEMO_RUNBOOK.md)

---

## If You Want to Use This Repo to Evaluate My Services

This project is a concrete example of how I work across:

- AI strategy
- product design
- workflow analysis
- privacy-first system design
- documentation for non-technical teams
- local AI deployment
- public GitHub proof-of-work

Typical follow-on work from a free repo like this includes:

- adapting the workflows to a real school office
- creating school-specific prompt templates
- training office staff
- producing governance-ready documentation
- designing stakeholder demos
- planning a local-first rollout beyond the prototype stage

In other words:

**the software is free, but the real value is in making AI usable, governable, and institution-ready.**

---

## Further Reading

Official and useful references:

- [EU AI Act official text (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [EU AI Act summary (EUR-Lex)](https://eur-lex.europa.eu/EN/legal-content/summary/rules-for-trustworthy-artificial-intelligence-in-the-eu.html)
- [GDPR summary (EUR-Lex)](https://eur-lex.europa.eu/EN/legal-content/summary/general-data-protection-regulation-gdpr.html)
- [GDPR official text (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- [EDPS 2024 Microsoft 365 decision summary](https://www.edps.europa.eu/press-publications/press-news/press-releases/2024/european-commissions-use-microsoft-365-infringes-data-protection-law-eu-institutions-and-bodies)
- [EDPS 2025 follow-up on Commission compliance](https://www.edps.europa.eu/press-publications/press-news/press-releases/2025/european-commission-brings-use-microsoft-365-compliance-data-protection-rules-eu-institutions-and-bodies_en)
- [US DOJ CLOUD Act resources](https://www.justice.gov/dag/cloudact)
- [LM Studio docs](https://lmstudio.ai/docs/)
- [LM Studio local server docs](https://lmstudio.ai/docs/developer/core/server)
- [LM Studio offline operation docs](https://lmstudio.ai/docs/app/offline)

---

## Bottom Line

If your school wants a first serious step into AI without defaulting to external cloud processing, subscription creep, and governance chaos, this repo is a practical place to start.

It is not a full school platform.
It is not legal advice.
It is not an auto-pilot.

It is a focused, local-first administrative sidecar designed to save staff time while keeping humans, governance, and trust in the loop.
