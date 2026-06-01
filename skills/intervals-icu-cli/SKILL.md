---
name: intervals-icu-cli
description: "Interact with Intervals.icu from the command line via the `intervals-icu` CLI. Use when the user wants to list activities, or list/create/delete calendar events and structured workouts on Intervals.icu from a terminal."
license: MIT
metadata:
  author: LeonardHd
  version: "0.1.0"
---

# Intervals.icu CLI (intervals-icu)

A command-line interface for Intervals.icu, exposed as the `intervals-icu` command.

## Installation

```bash
pip install intervals-icu-cli
# or, from source with uv:
uv build && uv pip install dist/*.whl
```

## Authentication

Credentials resolve from two sources, **environment variables taking precedence
over the stored config file**:

1. Environment (a local `.env` file is loaded automatically):
   - `INTERVALS_ICU_API_KEY` (required) — your Intervals.icu API key.
   - `INTERVALS_ICU_ATHLETE_ID` (required) — your athlete ID (e.g. `i12345`).
   - `INTERVALS_ICU_BASE_URL` (optional) — defaults to `https://intervals.icu`.
2. Config file at `~/.config/intervals-icu/config.toml` (honors
   `$XDG_CONFIG_HOME`), written with `0600` permissions:
   ```toml
   athlete_id = "i12345"
   api_key = "xxxx"
   base_url = "https://intervals.icu"  # optional
   ```

Requests authenticate via HTTP basic auth with username `API_KEY`.

### Managing credentials (`auth`)

```bash
# Interactive: prompts for athlete id + api key (key input hidden)
intervals-icu auth login

# Show how creds currently resolve (no network call); masks the key
intervals-icu auth status

# Remove the stored config file
intervals-icu auth logout
```

### Headless / CI usage

No command needs a TTY to *read* credentials — that's always non-interactive.
For automation, either set the env vars directly, or write the config file
non-interactively:

```bash
# Preferred for CI: just export the env vars (highest precedence)
export INTERVALS_ICU_API_KEY=xxxx
export INTERVALS_ICU_ATHLETE_ID=i12345

# Or persist a config file without prompts
intervals-icu auth login --athlete-id i12345 --api-key xxxx

# Read the secret from stdin (keeps it out of shell history / process list)
echo "$KEY" | intervals-icu auth login --athlete-id i12345 --api-key -
```

`auth login` only prompts when a terminal is attached. Run it headless with a
missing value and it exits non-zero with a clear message instead of hanging.

## Core Patterns

- Run `intervals-icu --help` (or `--help` on any subcommand) to discover options.
- Every list command supports `--json` for machine-readable output; without it,
  results print as tab-separated lines.
- Commands lazily build the API client, so `--help` works without credentials.

## Commands

### Activities

```bash
# List activities (defaults: last 30 days, limit 50)
intervals-icu activities list
intervals-icu activities list --start 2025-01-01 --end 2025-01-31 --limit 100
intervals-icu activities list --json
```

### Events

```bash
# List planned events (defaults: 30 days back to 30 days ahead, category WORKOUT)
intervals-icu events list
intervals-icu events list --oldest-days-ago 7 --newest-days-ahead 14 --json

# Delete an event by ID
intervals-icu events delete 123456
```

### Creating a structured workout event

`events create` reads a workout JSON object (with a `steps` array) from a file
(`--file/-f`) or stdin:

```bash
intervals-icu events create \
  --name "5x1km Intervals" \
  --date 2025-12-05T07:00:00 \
  --type Run \
  --file workout.json
```

Workout JSON schema:

- Each step is either a **leaf** (`label`, `duration` seconds, `distance` meters,
  `intensity`, `target`) or a **repeat block** (`label`, `reps`, nested `steps`).
- Pace `target` is either `{"value": 360, "units": "secs"}` (single pace) or
  `{"start": 290, "end": 310, "units": "secs"}` (pace range), in seconds per km.

Example `workout.json`:

```json
{
  "steps": [
    {"label": "Warmup", "duration": 600, "target": {"value": 360, "units": "secs"}},
    {
      "label": "Intervals",
      "reps": 5,
      "steps": [
        {"label": "Fast", "distance": 1000, "target": {"start": 240, "end": 250, "units": "secs"}},
        {"label": "Recovery", "duration": 90, "intensity": "recovery"}
      ]
    },
    {"label": "Cooldown", "duration": 600, "intensity": "easy"}
  ]
}
```

The structured workout is rendered into the event description as an indented
text block.
