# Windows Setup

If you want the full technical context, start with the [IT Deployment Guide](IT_DEPLOYMENT.md).

## Requirements

- Windows 11
- Python 3.12, 3.13, or 3.14
- LM Studio
- `meta-llama-3.1-8b-instruct` loaded in LM Studio

## Steps

1. Open PowerShell in the repo root.
2. Check Python:

```powershell
py --version
python --version
```

3. Create a virtual environment:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

If `py -3` does not work:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Install the app:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item config.example.toml config.toml
```

5. Start LM Studio and enable the local server.
6. Load `meta-llama-3.1-8b-instruct`.
7. Run the app:

```powershell
secure-secr-ai-tery
```

Legacy fallback:

```powershell
sekretariat-copilot
```

Direct launcher fallback:

```powershell
.venv\Scripts\secure-secr-ai-tery.exe
```

Legacy direct launcher:

```powershell
.venv\Scripts\sekretariat-copilot.exe
```

## First-Run Check

You should be able to:

- type context into `Context, Info & 2do's`
- open the prompt menu
- save a prompt
- run the prompt
- copy text from `AI Output`
- reopen the run from `History`
