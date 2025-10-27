"""Typer-powered CLI for pyteam-skills."""

from __future__ import annotations
import json
import os

from rich import print
from rich.table import Table
import typer

from .config import Config
from .dashboard import generate_dashboard
from .matrix import export_csvs
from .repo_scan import scan_repo


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def init(
    out: str = typer.Option("config.yml", help="Where to write the default config.")
) -> None:
    """Write a default configuration file to *out*."""
    cfg = Config()
    cfg.save(out)
    print(f"[green]Wrote config to[/green] {out}")


@app.command()
def scan(
    repo: str = typer.Option(".", help="Path to Git repository"),
    config: str = typer.Option(..., "--config", "-c", help="Config YAML"),
    out: str = typer.Option("scan.json", help="Where to write scan JSON"),
) -> None:
    """Scan a Git repository and write a JSON artifact."""
    cfg = Config.from_file(config)
    data = scan_repo(repo, cfg)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[green]Wrote scan to[/green] {out}")


@app.command()
def matrix(
    scan: str = typer.Option(..., help="scan.json from the scan step"),
    out: str = typer.Option("artifacts", help="Output directory"),
) -> None:
    """Export CSV artifacts from a previous scan JSON."""
    with open(scan, "r", encoding="utf-8") as f:
        data = json.load(f)
    paths = export_csvs(data, out)
    tbl = Table("Artifact", "Path")
    for k, v in paths.items():
        tbl.add_row(k, v)
    print(tbl)


@app.command()
def dashboard(
    scan: str = typer.Option(..., help="scan.json from the scan step"),
    out: str = typer.Option(
        "artifacts/dashboard", help="Output directory for static dashboard"
    ),
) -> None:
    """Build the static dashboard HTML and data.json from a scan JSON."""

    with open(scan, "r", encoding="utf-8") as f:
        data = json.load(f)
    paths = generate_dashboard(data, out)
    tbl = Table("Artifact", "Path")
    for k, v in paths.items():
        tbl.add_row(k, v)
    print(tbl)


if __name__ == "__main__":
    app()
