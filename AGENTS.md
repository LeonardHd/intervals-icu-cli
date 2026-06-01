# AGENTS.md

Command-line interface for Intervals.icu, packaged as `intervals-icu-cli` and exposed as the `intervals-icu` command.

## Layout

- `src/intervals_icu_cli/` — package source (`cli.py` holds the `intervals-icu` entry point).
- `skills/intervals-icu-cli/SKILL.md` — agent skill that documents the CLI.
- `.github/workflows/release.yml` — release pipeline.

## Build & run

Uses [uv](https://docs.astral.sh/uv/) with the `uv_build` backend (src layout).

```bash
uv build              # build wheel + sdist
intervals-icu --help  # run the CLI
```

## Releases

Automated via semantic-release on every push to `main`. Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` -> minor bump, `fix:` -> patch, `feat!:`/`BREAKING CHANGE` -> major.
- `docs:`, `chore:`, `ci:`, etc. do not trigger a release.

The pipeline bumps the version in `pyproject.toml`, updates `CHANGELOG.md`, tags, creates a GitHub release, and publishes to PyPI via trusted publishing.
