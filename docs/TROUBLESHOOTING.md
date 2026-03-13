# Troubleshooting

## Backend offline

- Confirm LM Studio is running.
- Confirm the local server is started.
- Confirm `base_url` and `model_id` in `config.toml`.
- Use the Diagnostics panel in the app to inspect reachability and recent errors.

## Vision OCR unavailable

- Enable `supports_vision = true` only when the selected local model actually supports image input.
- If vision is unavailable, paste text manually and continue with the text workflow.

## PDF parsing failed

- Check the file size and page count limits in `config.toml`.
- If the PDF is scanned and no vision model is active, paste the text manually or load a vision-capable model.

## Windows virtual environment issues

- Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` if PowerShell blocks activation.
- Re-open the shell after Python installation if `py -3.12` is not found immediately.

