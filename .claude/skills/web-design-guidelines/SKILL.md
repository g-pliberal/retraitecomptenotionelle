---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Read the pinned guidelines committed next to this file (see below)
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

This project pins the guidelines. Read them, with the Read tool, from the
committed snapshot before each review:

```
.claude/skills/web-design-guidelines/guidelines.md
```

Do not fetch anything for a normal review. `guidelines.md` is a verbatim copy
of `command.md` from https://github.com/vercel-labs/web-interface-guidelines
at the commit recorded in `guidelines.provenance.yaml` next to it. It contains
all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Read `guidelines.md` from this skill's directory
2. Read the specified files
3. Apply all rules from the guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

## Updating the pinned guidelines

Only on an explicit request to refresh the rules, never as a side effect of a
review. Upstream `main` is
`https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`.
The procedure (pick a commit, copy `command.md` verbatim over `guidelines.md`,
record commit, date and sha256 in `guidelines.provenance.yaml`, then run
`scripts/setup_ui_tools.sh --verifier`) is in `docs/outillage_interface.md`.
