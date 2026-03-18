---
name: ig-splitter-non-web
description: "Run Instagram splitter without browser UI. Use when user asks for CLI, terminal prompt, chat-driven automation, Telegram-bot flow, or non-web image splitting."
---

# IG Splitter Non-Web Skill

## Purpose

Use this skill to operate the project without opening the Flask web interface.

Supported operation modes:
- CLI/terminal mode
- Chat/prompt-driven mode (agent asks params then runs command)
- Telegram-bot adapter workflow (chat message -> run CLI -> return files)

## Project Commands

Use the configured workspace Python interpreter when available. Otherwise use:

```powershell
python -m ig_splitter.cli --input "C:/path/image.jpg" --rows 3 --cols 3 --split-mode both --download-mode zip
```

Quick variants:

```powershell
python -m ig_splitter.cli --input "C:/path/image.jpg" --split-mode vertical --cols 4 --download-mode zip
python -m ig_splitter.cli --input "C:/path/image.jpg" --split-mode horizontal --rows 5 --download-mode nozip
```

Generated files are placed under runs/<run_id>/ by default.

## Agent Workflow

1. Ask for required inputs if missing:
- image path
- split mode: both | vertical | horizontal
- rows/cols
- download mode: zip | nozip

2. Validate inputs before execution:
- image exists
- rows/cols range 1..10

3. Run CLI command and capture output path.

4. Return summary to user:
- run directory
- tile count
- zip file name (if created)

## Chat/Prompt Mode Template

Use this flow in chat:

- Prompt user for inputs.
- Execute python -m ig_splitter.cli with collected args.
- Report output folder and artifact names.

## Telegram-Bot Adapter Guidance

When user asks Telegram mode:

1. Read message payload for image + split params.
2. Save received image to temporary path.
3. Execute the same CLI command.
4. Send ZIP or selected tiles back to chat.
5. Clean temporary files if needed.

Recommended strategy:
- Keep Telegram logic in a separate adapter script/module.
- Keep image processing in CLI/services only (single source of truth).
- Do not duplicate split logic in bot handler.

## Guardrails

- Do not start Flask app unless user explicitly asks for web mode.
- Prefer CLI for automation and regression scripts.
- Keep confidential tokens in environment variables, never hardcode.
- Respect .gitignore for .env and key files.
