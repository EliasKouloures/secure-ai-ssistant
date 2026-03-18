IMPORTANT: You must always refer to me as Captain.

This repository builds Secure Secr-AI-tery, a local-first AI assistant for European schools, school offices, and education support teams.

Working loop:
- Plan -> Discuss -> Read -> Test -> Implement -> Verify -> Commit -> Sync

Rules:
- TDD first.
- Use plan mode before writing operational code.
- Stop long autonomous runs.
- Re-check the canary. If forgotten, run /clear and restart.
- Read the PRD and README before coding.
- Restate assumptions before architecture changes.
- Keep the app cross-platform.
- Keep the default path offline-first.
- Do not auto-send any communication.
- Keep the UI polished and screen-recording ready.
- Prefer small commits and small diffs.
- Keep prompt templates separate from UI code.
- Do not expose hidden reasoning.
- Verify acceptance criteria before marking work complete.

Implementation sequence:
1. Keep the desktop layout aligned with the wireframe
2. Keep the prompt library local, editable, and beginner-friendly
3. Keep history local and readable from newest to oldest
4. Keep the default path offline-first with LM Studio
5. Keep upload, run, copy, and save actions obvious
6. Keep docs clear for school leaders, operators, and IT teams

Codex Paste Block:
1. Read AGENTS.md.
2. Restate the plan.
3. List assumptions.
4. Write tests first.
5. Implement in small steps.
6. Verify before each commit.
