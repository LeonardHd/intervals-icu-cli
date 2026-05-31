from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Build the intervals-icu argument parser."""
    return argparse.ArgumentParser(
        prog="intervals-icu",
        description="Command-line interface for Intervals.icu.",
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point for the intervals-icu CLI. Currently a no-op."""
    build_parser().parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
