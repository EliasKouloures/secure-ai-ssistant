# Privacy Notes

Secure Secr-AI-tery is designed for a local-first privacy posture.

## Default Processing Model

- the app runs locally
- the model runs locally through LM Studio
- the browser connects to `127.0.0.1` by default
- no automatic outbound action happens

## Local Storage

The app stores local run history in SQLite so users can reopen earlier work.

That includes:

- the typed context
- the selected prompt title
- the prompt body
- the generated output
- uploaded file names
- audit metadata

Uploaded file bodies do not need to be stored for history and should remain transient.

## Why This Matters

This design reduces avoidable cloud exposure for routine drafting work.
It does not remove the need for local policy, retention, and legal review.

## What Schools Should Decide Locally

- who may use the pilot machine
- how long local history should be kept
- which workflow scope is approved
- whether a DPIA is needed
- whether staff may process real personal data in the pilot

## Plain-Language Summary

This tool is built to keep work close to the school.
That is better for trust.
It is also easier to explain to staff, IT, and leadership.
