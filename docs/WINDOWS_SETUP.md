# Windows Setup

## Requirements

- Windows 11
- Python 3.12, 3.13, or 3.14
- LM Studio or another OpenAI-compatible local backend

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

If `py -3` does not work, try:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Install the project:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

5. Copy the example config:

```powershell
Copy-Item config.example.toml config.toml
```

6. Start LM Studio and launch its local server.
7. Run the app:

```powershell
sekretariat-copilot
```

If that command is not found, run:

```powershell
.venv\Scripts\sekretariat-copilot.exe
```

## First-run check

- the top bar should show the local backend status
- the KPI should be visible
- you should be able to paste text and click `Process locally`
