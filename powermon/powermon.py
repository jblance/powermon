#!/usr/bin/env python3
"""
powermon runtime entrypoint (worker application)

This is the operational CLI used to execute device actions continuously
or once-off. All inspection, validation, and tooling lives in powermon-cli.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from platform import python_version

import typer
from rich import print

from powermon import __version__, tl
from powermon.runtime.config_loader import load_config
from powermon.runtime.runner import run_worker
from powermon.runtime.lifecycle import setup_logging

# ---------------------------------------------------------------------
# Typer app
# ---------------------------------------------------------------------

app = typer.Typer(
    name="powermon",
    no_args_is_help=True,
    help="Power Device Monitoring Utility (runtime worker)",
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _run(
    *,
    config_path: Path,
    once: bool,
    force_tasks: bool,
    log_level: str,
) -> None:
    """
    Shared execution wrapper.
    """
    setup_logging(log_level)
    config = load_config(config_path)
    asyncio.run(
        run_worker(
            config,
            once=once,
            force_tasks=force_tasks,
        )
    )


# ---------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------

@app.command()
def run(
    config: Path = typer.Option(
        "./powermon.yaml",
        "-C",
        "--config",
        exists=True,
        readable=True,
        help="Path to configuration file",
    ),
    force_tasks: bool = typer.Option(
        False,
        "--force-tasks",
        help="Force all tasks to run immediately (ignores triggers once)",
    ),
    log_level: str = typer.Option(
        "WARNING",
        "--log-level",
        help="Logging level (DEBUG, INFO, WARNING, ERROR)",
    ),
) -> None:
    """
    Run powermon continuously.

    Scheduling is entirely action-based (interval / schedule / disabled).
    """
    _run(
        config_path=config,
        once=False,
        force_tasks=force_tasks,
        log_level=log_level,
    )


@app.command()
def once(
    config: Path = typer.Option(
        "./powermon.yaml",
        "-C",
        "--config",
        exists=True,
        readable=True,
        help="Path to configuration file",
    ),
    force_tasks: bool = typer.Option(
        True,
        "--force-tasks",
        help="Force all tasks to run once regardless of trigger state",
    ),
    log_level: str = typer.Option(
        "WARNING",
        "--log-level",
        help="Logging level (DEBUG, INFO, WARNING, ERROR)",
    ),
) -> None:
    """
    Run all enabled tasks once and exit.

    Intended for operator-initiated tasks such as applying settings.
    """
    _run(
        config_path=config,
        once=True,
        force_tasks=force_tasks,
        log_level=log_level,
    )


@app.command()
def version() -> None:
    """Display version information."""
    name = tl("Power Device Monitoring Utility")
    print(
        f"{name}, version: {__version__}, "
        f"python version: {python_version()}"
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    app()


if __name__ == "__main__":
    main()