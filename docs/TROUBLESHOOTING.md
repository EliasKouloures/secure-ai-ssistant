# Troubleshooting

## The app says LM Studio could not be reached

Check:

1. LM Studio is open
2. the local server is running
3. the server address is `http://127.0.0.1:1234/v1`
4. `meta-llama-3.1-8b-instruct` is loaded

## The app says the model took too long

Try:

- shorter context
- shorter prompt
- LM Studio temperature `0.2`
- closing other heavy apps

## The launcher command is not found

Use:

```bash
.venv/bin/secure-secr-ai-tery
```

Legacy fallback:

```bash
.venv/bin/sekretariat-copilot
```

## Save Prompt did not create the title I expected

New prompt titles come from the first non-empty line.
Edit that line and save again.

## Delete Output did not seem to work

Refresh once and try again.
The current build now clears the output field via safe Streamlit state sync.

## History is empty

History only appears after you run at least one prompt successfully.

## The wrong prompt text loaded

Check the top prompt selector.
If you chose `Add new Prompt`, the lower editor stays blank until you type or paste a prompt.
