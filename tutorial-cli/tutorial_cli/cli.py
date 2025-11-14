#!/usr/bin/env python3
"""
Tutorial CLI - A simple Git wrapper for Python tutorial students.

This tool simplifies common Git operations so students can focus on learning
Python packages without needing deep Git knowledge.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table

app = typer.Typer(
    name="tutorial",
    help="Tutorial CLI - A simple Git wrapper for Python tutorial students",
    add_completion=False,
)

console = Console()


def run_command(cmd: List[str], capture: bool = False) -> tuple[int, str]:
    """
    Run a shell command and return the exit code and output.

    Args:
        cmd: Command and arguments as a list
        capture: If True, capture and return output; otherwise print to console

    Returns:
        Tuple of (exit_code, output_string)
    """
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode, result.stdout + result.stderr
        else:
            result = subprocess.run(cmd)
            return result.returncode, ""
    except FileNotFoundError:
        return 1, f"Error: Command '{cmd[0]}' not found"


def check_git_installed() -> bool:
    """Check if git is installed."""
    code, _ = run_command(["git", "--version"], capture=True)
    return code == 0


def is_git_repo() -> bool:
    """Check if the current directory is a git repository."""
    code, _ = run_command(["git", "rev-parse", "--git-dir"], capture=True)
    return code == 0


@app.command()
def config():
    """Configure Git with your name and email."""
    console.print()
    console.print(Panel.fit("Git Configuration", style="bold blue"))
    console.print()

    if not check_git_installed():
        console.print("[red]✗[/red] Git is not installed. Please install Git first.")
        raise typer.Exit(code=1)

    # Get current config if it exists
    _, current_name = run_command(["git", "config", "--global", "user.name"], capture=True)
    _, current_email = run_command(["git", "config", "--global", "user.email"], capture=True)

    current_name = current_name.strip()
    current_email = current_email.strip()

    if current_name and current_email:
        console.print("[blue]ℹ[/blue] Current configuration:")
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("Name:", current_name)
        table.add_row("Email:", current_email)
        console.print(table)
        console.print()

        if not Confirm.ask("Do you want to change it?", default=False):
            console.print("[blue]ℹ[/blue] Keeping current configuration.")
            return

    # Get user input
    console.print("Please enter your information:")
    name = Prompt.ask("Your name (e.g., 'John Doe')")
    email = Prompt.ask("Your email (e.g., 'john@example.com')")

    if not name or not email:
        console.print("[red]✗[/red] Name and email are required!")
        raise typer.Exit(code=1)

    # Set config
    code1, _ = run_command(["git", "config", "--global", "user.name", name], capture=True)
    code2, _ = run_command(["git", "config", "--global", "user.email", email], capture=True)

    if code1 == 0 and code2 == 0:
        console.print()
        console.print("[green]✓[/green] Git configured successfully!")
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("Name:", name)
        table.add_row("Email:", email)
        console.print(table)
    else:
        console.print("[red]✗[/red] Failed to configure Git.")
        raise typer.Exit(code=1)


@app.command()
def init():
    """Initialize a new Git repository."""
    console.print()
    console.print(Panel.fit("Initialize Git Repository", style="bold blue"))
    console.print()

    if not check_git_installed():
        console.print("[red]✗[/red] Git is not installed. Please install Git first.")
        raise typer.Exit(code=1)

    if is_git_repo():
        console.print("[yellow]⚠[/yellow] This directory is already a Git repository.")
        return

    # Initialize repo
    code, output = run_command(["git", "init"], capture=True)
    if code != 0:
        console.print(f"[red]✗[/red] Failed to initialize repository: {output}")
        raise typer.Exit(code=1)

    console.print("[green]✓[/green] Git repository initialized!")

    # Create .gitignore if it doesn't exist
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        console.print("[blue]ℹ[/blue] Creating .gitignore file...")
        default_ignores = [
            ".ipynb_checkpoints",
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".Python",
            "*.so",
            ".DS_Store",
        ]
        gitignore_path.write_text("\n".join(default_ignores) + "\n")
        console.print("[green]✓[/green] .gitignore file created!")

    console.print()
    console.print("[blue]ℹ[/blue] Next steps:")
    console.print("  1. Use [cyan]tutorial commit[/cyan] to save your changes")
    console.print("  2. Create a repository on GitHub")
    console.print("  3. Use [cyan]tutorial sync[/cyan] to push your code")


@app.command()
def status():
    """Show the status of your repository."""
    if not is_git_repo():
        console.print("[red]✗[/red] Not a Git repository. Run [cyan]tutorial init[/cyan] first.")
        raise typer.Exit(code=1)

    console.print()
    console.print(Panel.fit("Repository Status", style="bold blue"))
    console.print()

    code, _ = run_command(["git", "status"])
    raise typer.Exit(code=code)


@app.command()
def commit(
    message: Optional[str] = typer.Option(
        None,
        "-m",
        "--message",
        help="Commit message"
    )
):
    """Add and commit all changes."""
    console.print()
    console.print(Panel.fit("Commit Changes", style="bold blue"))
    console.print()

    if not is_git_repo():
        console.print("[red]✗[/red] Not a Git repository. Run [cyan]tutorial init[/cyan] first.")
        raise typer.Exit(code=1)

    # Check if there are changes to commit
    code, status_output = run_command(["git", "status", "--porcelain"], capture=True)
    if not status_output.strip():
        console.print("[blue]ℹ[/blue] No changes to commit.")
        return

    # Show what will be committed
    console.print("[blue]ℹ[/blue] Changes to be committed:")
    run_command(["git", "status", "--short"])
    console.print()

    # Get commit message
    if not message:
        message = Prompt.ask("Enter commit message")
        if not message:
            console.print("[red]✗[/red] Commit message cannot be empty!")
            raise typer.Exit(code=1)

    # Add all changes
    console.print("[blue]ℹ[/blue] Adding changes...")
    code, _ = run_command(["git", "add", "."], capture=True)
    if code != 0:
        console.print("[red]✗[/red] Failed to add changes.")
        raise typer.Exit(code=1)

    # Commit
    console.print("[blue]ℹ[/blue] Creating commit...")
    code, output = run_command(["git", "commit", "-m", message], capture=True)
    if code != 0:
        console.print(f"[red]✗[/red] Failed to commit: {output}")
        raise typer.Exit(code=1)

    console.print(f"[green]✓[/green] Changes committed: '{message}'")

    # Check if remote is configured
    code, _ = run_command(["git", "remote", "get-url", "origin"], capture=True)
    console.print()
    if code == 0:
        console.print("[blue]ℹ[/blue] Next step: Use [cyan]tutorial sync[/cyan] to push your changes to GitHub")
    else:
        console.print("[blue]ℹ[/blue] Next steps:")
        console.print("  1. Create a repository on GitHub")
        console.print("  2. Connect it: [cyan]git remote add origin <repository-url>[/cyan]")
        console.print("  3. Use [cyan]tutorial sync[/cyan] to push your changes")


@app.command()
def sync():
    """Push your changes to GitHub."""
    console.print()
    console.print(Panel.fit("Sync with GitHub", style="bold blue"))
    console.print()

    if not is_git_repo():
        console.print("[red]✗[/red] Not a Git repository. Run [cyan]tutorial init[/cyan] first.")
        raise typer.Exit(code=1)

    # Check if remote is configured
    code, remote_url = run_command(["git", "remote", "get-url", "origin"], capture=True)
    if code != 0:
        console.print("[red]✗[/red] No remote repository configured.")
        console.print()
        console.print("[blue]ℹ[/blue] To add a remote repository:")
        console.print("  1. Create a repository on GitHub")
        console.print("  2. Run: [cyan]git remote add origin <repository-url>[/cyan]")
        console.print("     (use the SSH URL, e.g., git@github.com:username/repo.git)")
        raise typer.Exit(code=1)

    remote_url = remote_url.strip()
    console.print(f"[blue]ℹ[/blue] Remote repository: {remote_url}")

    # Get current branch
    code, branch = run_command(["git", "branch", "--show-current"], capture=True)
    if code != 0:
        console.print("[red]✗[/red] Failed to determine current branch.")
        raise typer.Exit(code=1)

    branch = branch.strip()
    if not branch:
        console.print("[red]✗[/red] No branch found. Make sure you have at least one commit.")
        raise typer.Exit(code=1)

    console.print(f"[blue]ℹ[/blue] Current branch: {branch}")

    # Check if there are uncommitted changes
    code, status_output = run_command(["git", "status", "--porcelain"], capture=True)
    if status_output.strip():
        console.print("[yellow]⚠[/yellow] You have uncommitted changes!")
        if Confirm.ask("Do you want to commit them first?", default=True):
            # Call commit command
            ctx = typer.Context(app)
            ctx.invoke(commit)
            console.print()
            console.print(Panel.fit("Sync with GitHub", style="bold blue"))
            console.print()

    # Push to remote
    console.print(f"[blue]ℹ[/blue] Pushing to {remote_url}...")

    # Check if upstream is set
    code, _ = run_command(["git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"], capture=True)

    if code != 0:
        # First push - set upstream
        console.print("[blue]ℹ[/blue] Setting up upstream branch...")
        code = run_command(["git", "push", "-u", "origin", branch])[0]
    else:
        # Normal push
        code = run_command(["git", "push"])[0]

    console.print()
    if code == 0:
        console.print("[green]✓[/green] Changes pushed successfully!")
        console.print(f"[blue]ℹ[/blue] Your code is now on GitHub!")
    else:
        console.print("[red]✗[/red] Failed to push changes.")
        console.print()
        console.print("[blue]ℹ[/blue] Common issues:")
        console.print("  - Make sure you have set up SSH keys with GitHub")
        console.print("  - Check that the remote URL is correct (should use SSH)")
        console.print("  - Ensure you have permission to push to this repository")
        raise typer.Exit(code=1)


@app.command()
def upload():
    """Push your changes to GitHub (alias for sync)."""
    ctx = typer.Context(app)
    ctx.invoke(sync)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == '__main__':
    main()
