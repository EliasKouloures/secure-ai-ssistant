# FAQ

## Is this a cloud service?

No.
The default path is a local web app talking to a local LM Studio server on the same machine.

## Does it work offline?

Yes, after Python dependencies and the model are installed.

## Does it auto-send anything?

No.
Users copy the output into their next program manually.

## What does the History panel store?

It stores local run history in SQLite:

- typed context
- prompt title
- prompt body
- output text
- file names

It does not need to persist uploaded file bodies.

## How are new prompt titles created?

If the user chooses `Add new Prompt`, the first non-empty line becomes the saved title.

## Why not force a separate prompt title field?

Because the app is aimed at non-technical users.
One editor is easier than two.

## Why is the GitHub repo called secure-secr-ai-tery?

GitHub repo slugs work best in lowercase with hyphens.
That keeps the clone path, package name, and command name simple.
The visible product name is `Secure-Secr-AI-tery`.

## Is this automatically GDPR compliant?

No software can promise that on its own.

What this repo does offer is a more defensible starting posture:

- local processing
- local storage
- no automatic outbound action
- no mandatory cloud inference

## Is this suitable for the EU AI Act?

It is designed to support a lower-friction governance posture, but legal evaluation still depends on the actual use case, data, and school context.

## Which model is recommended?

`meta-llama-3.1-8b-instruct`

## Why that model?

It is steadier for school-office drafting than the uncensored model variant that was tested earlier.
