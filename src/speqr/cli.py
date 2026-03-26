"""Speqr CLI — validate and submit OPC contracts."""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import click

from speqr.loader import load_speq_file
from speqr.validator import validate
from speqr.submit import submit as submit_speq, SpeqrSubmitError


@click.group()
@click.version_option()
def main():
    """Speqr — Define, validate, and certify OPC contracts."""


@main.command("validate")
@click.argument("paths", nargs=-1, required=True)
def validate_cmd(paths: tuple[str, ...]):
    """Validate one or more speq files."""
    files: list[Path] = []
    for p in paths:
        expanded = glob.glob(p)
        if expanded:
            files.extend(Path(f) for f in expanded)
        else:
            files.append(Path(p))

    all_passed = True
    for f in files:
        try:
            speq = load_speq_file(f)
        except (FileNotFoundError, ValueError) as e:
            click.echo(f"ERROR: {f}: {e}", err=True)
            all_passed = False
            continue

        result = validate(speq)
        if result.warnings:
            for w in result.warnings:
                click.echo(f"WARNING: {f}: {w}")
        if result.errors:
            for e in result.errors:
                click.echo(f"ERROR: {f}: {e}")
            all_passed = False
        else:
            click.echo(f"PASSED: {f} — ready for certification")

    sys.exit(0 if all_passed else 1)


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--endpoint", envvar="SPEQR_ENDPOINT", default="", help="Certification endpoint URL")
@click.option("--timeout", default=30.0, help="Request timeout in seconds")
def submit(path: str, endpoint: str, timeout: float):
    """Submit a speq file for certification."""
    if not endpoint:
        click.echo("ERROR: --endpoint is required (or set SPEQR_ENDPOINT env var)", err=True)
        sys.exit(1)

    try:
        speq = load_speq_file(Path(path))
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)

    try:
        result = submit_speq(speq, endpoint=endpoint, timeout=timeout)
    except (ValueError, SpeqrSubmitError) as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)

    if result.passed:
        click.echo(f"CERTIFIED: {path}")
    else:
        click.echo(f"REJECTED: {path}")
        for finding in result.findings:
            rule = finding.get("rule", "?")
            msg = finding.get("message", "no details")
            click.echo(f"  [{rule}] {msg}")
        sys.exit(1)
