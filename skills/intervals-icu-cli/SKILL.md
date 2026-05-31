---
name: intervals-icu-cli
description: "Interact with Intervals.icu from the command line via the `intervals-icu` CLI. Use when the user wants to work with Intervals.icu training data, activities, workouts, or athletes from a terminal. NOTE: the CLI is currently an early stub with no subcommands yet."
license: MIT
metadata:
  author: LeonardHd
  version: "0.1.0"
---

# Intervals.icu CLI (intervals-icu)

A command-line interface for Intervals.icu, exposed as the `intervals-icu` command.

> Status: early stub. `intervals-icu` currently accepts no subcommands and does
> nothing when invoked. This skill is a placeholder that grows as CLI commands
> are added.

## Installation

```bash
pip install intervals-icu-cli
# or, from source with uv:
uv build && uv pip install dist/*.whl
```

## Core Patterns

- Run `intervals-icu --help` to discover the current command surface.
- Invoking `intervals-icu` with no subcommand is a no-op and exits 0.

## Commands

```bash
intervals-icu --help      # show usage
intervals-icu             # no-op (no subcommands implemented yet)
```
