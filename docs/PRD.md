# Secure-Secr-AI-tery Product Brief

## Product

Secure-Secr-AI-tery is a private, offline-friendly AI workspace for European schools and school support teams.

## Core UX

Desktop-first three-column layout:

- `History`
- `Context, Info & 2do's`
- `AI Output`
- `Prompts`
- full editable prompt body

## Core Actions

- upload one file
- run prompt
- delete output
- copy output
- save prompt

## Core Principles

- local-first by default
- easy for non-technical users
- no auto-send
- human review always
- prompt library is editable and local
- history is readable and newest first

## Technical Shape

- Python
- Streamlit
- SQLite
- LM Studio local server
- `meta-llama-3.1-8b-instruct`

## Current Product Decision

The repo still keeps older analysis and export modules, but the main app experience is now focused on a prompt-driven local workspace rather than the earlier fixed workflow pack.
