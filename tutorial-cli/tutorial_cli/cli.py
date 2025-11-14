#!/usr/bin/env python3
"""
Tutorial CLI - A simple Git wrapper for Python tutorial students.

This tool simplifies common Git operations so students can focus on learning
Python packages without needing deep Git knowledge.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


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


def print_success(msg: str) -> None:
    """Print a success message in green."""
    print(f"{Colors.GREEN}{Colors.BOLD}✓{Colors.END} {msg}")


def print_error(msg: str) -> None:
    """Print an error message in red."""
    print(f"{Colors.RED}{Colors.BOLD}✗{Colors.END} {msg}", file=sys.stderr)


def print_info(msg: str) -> None:
    """Print an info message in blue."""
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")


def print_warning(msg: str) -> None:
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")


def check_git_installed() -> bool:
    """Check if git is installed."""
    code, _ = run_command(["git", "--version"], capture=True)
    return code == 0


def is_git_repo() -> bool:
    """Check if the current directory is a git repository."""
    code, _ = run_command(["git", "rev-parse", "--git-dir"], capture=True)
    return code == 0


def cmd_config(args) -> int:
    """Configure Git with user information."""
    print(f"\n{Colors.BOLD}Git Configuration{Colors.END}")
    print("=" * 50)

    if not check_git_installed():
        print_error("Git is not installed. Please install Git first.")
        return 1

    # Get current config if it exists
    _, current_name = run_command(["git", "config", "--global", "user.name"], capture=True)
    _, current_email = run_command(["git", "config", "--global", "user.email"], capture=True)

    current_name = current_name.strip()
    current_email = current_email.strip()

    if current_name and current_email:
        print_info(f"Current configuration:")
        print(f"  Name:  {current_name}")
        print(f"  Email: {current_email}")

        response = input("\nDo you want to change it? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            print_info("Keeping current configuration.")
            return 0

    # Get user input
    print("\nPlease enter your information:")
    name = input("Your name (e.g., 'John Doe'): ").strip()
    email = input("Your email (e.g., 'john@example.com'): ").strip()

    if not name or not email:
        print_error("Name and email are required!")
        return 1

    # Set config
    code1, _ = run_command(["git", "config", "--global", "user.name", name], capture=True)
    code2, _ = run_command(["git", "config", "--global", "user.email", email], capture=True)

    if code1 == 0 and code2 == 0:
        print_success("Git configured successfully!")
        print(f"  Name:  {name}")
        print(f"  Email: {email}")
        return 0
    else:
        print_error("Failed to configure Git.")
        return 1


def cmd_init(args) -> int:
    """Initialize a Git repository."""
    print(f"\n{Colors.BOLD}Initialize Git Repository{Colors.END}")
    print("=" * 50)

    if not check_git_installed():
        print_error("Git is not installed. Please install Git first.")
        return 1

    if is_git_repo():
        print_warning("This directory is already a Git repository.")
        return 0

    # Initialize repo
    code, output = run_command(["git", "init"], capture=True)
    if code != 0:
        print_error(f"Failed to initialize repository: {output}")
        return 1

    print_success("Git repository initialized!")

    # Create .gitignore if it doesn't exist
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print_info("Creating .gitignore file...")
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
        print_success(".gitignore file created!")

    print_info("\nNext steps:")
    print("  1. Use 'tutorial commit' to save your changes")
    print("  2. Create a repository on GitHub")
    print("  3. Use 'tutorial sync' to push your code")

    return 0


def cmd_status(args) -> int:
    """Show the status of the repository."""
    if not is_git_repo():
        print_error("Not a Git repository. Run 'tutorial init' first.")
        return 1

    print(f"\n{Colors.BOLD}Repository Status{Colors.END}")
    print("=" * 50)

    code, _ = run_command(["git", "status"])
    return code


def cmd_commit(args) -> int:
    """Add and commit changes."""
    print(f"\n{Colors.BOLD}Commit Changes{Colors.END}")
    print("=" * 50)

    if not is_git_repo():
        print_error("Not a Git repository. Run 'tutorial init' first.")
        return 1

    # Check if there are changes to commit
    code, status_output = run_command(["git", "status", "--porcelain"], capture=True)
    if not status_output.strip():
        print_info("No changes to commit.")
        return 0

    # Show what will be committed
    print_info("Changes to be committed:")
    run_command(["git", "status", "--short"])
    print()

    # Get commit message
    if args.message:
        message = args.message
    else:
        message = input("Enter commit message: ").strip()
        if not message:
            print_error("Commit message cannot be empty!")
            return 1

    # Add all changes
    print_info("Adding changes...")
    code, _ = run_command(["git", "add", "."], capture=True)
    if code != 0:
        print_error("Failed to add changes.")
        return 1

    # Commit
    print_info("Creating commit...")
    code, output = run_command(["git", "commit", "-m", message], capture=True)
    if code != 0:
        print_error(f"Failed to commit: {output}")
        return 1

    print_success(f"Changes committed: '{message}'")

    # Check if remote is configured
    code, _ = run_command(["git", "remote", "get-url", "origin"], capture=True)
    if code == 0:
        print_info("\nNext step: Use 'tutorial sync' to push your changes to GitHub")
    else:
        print_info("\nNext steps:")
        print("  1. Create a repository on GitHub")
        print("  2. Connect it: git remote add origin <repository-url>")
        print("  3. Use 'tutorial sync' to push your changes")

    return 0


def cmd_sync(args) -> int:
    """Push changes to GitHub."""
    print(f"\n{Colors.BOLD}Sync with GitHub{Colors.END}")
    print("=" * 50)

    if not is_git_repo():
        print_error("Not a Git repository. Run 'tutorial init' first.")
        return 1

    # Check if remote is configured
    code, remote_url = run_command(["git", "remote", "get-url", "origin"], capture=True)
    if code != 0:
        print_error("No remote repository configured.")
        print_info("\nTo add a remote repository:")
        print("  1. Create a repository on GitHub")
        print("  2. Run: git remote add origin <repository-url>")
        print("     (use the SSH URL, e.g., git@github.com:username/repo.git)")
        return 1

    remote_url = remote_url.strip()
    print_info(f"Remote repository: {remote_url}")

    # Get current branch
    code, branch = run_command(["git", "branch", "--show-current"], capture=True)
    if code != 0:
        print_error("Failed to determine current branch.")
        return 1

    branch = branch.strip()
    if not branch:
        print_error("No branch found. Make sure you have at least one commit.")
        return 1

    print_info(f"Current branch: {branch}")

    # Check if there are uncommitted changes
    code, status_output = run_command(["git", "status", "--porcelain"], capture=True)
    if status_output.strip():
        print_warning("You have uncommitted changes!")
        response = input("Do you want to commit them first? [Y/n]: ").strip().lower()
        if response not in ['n', 'no']:
            return cmd_commit(args)

    # Push to remote
    print_info(f"Pushing to {remote_url}...")

    # Check if upstream is set
    code, _ = run_command(["git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"], capture=True)

    if code != 0:
        # First push - set upstream
        print_info("Setting up upstream branch...")
        code = run_command(["git", "push", "-u", "origin", branch])[0]
    else:
        # Normal push
        code = run_command(["git", "push"])[0]

    if code == 0:
        print_success("Changes pushed successfully!")
        print_info(f"\nYour code is now on GitHub!")
    else:
        print_error("Failed to push changes.")
        print_info("\nCommon issues:")
        print("  - Make sure you have set up SSH keys with GitHub")
        print("  - Check that the remote URL is correct (should use SSH)")
        print("  - Ensure you have permission to push to this repository")
        return 1

    return 0


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Tutorial CLI - A simple Git wrapper for Python tutorial students",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tutorial config              Configure Git with your name and email
  tutorial init                Initialize a new Git repository
  tutorial status              Check the status of your repository
  tutorial commit              Add and commit all changes
  tutorial commit -m "message" Commit with a specific message
  tutorial sync                Push your changes to GitHub

For more information, visit the tutorial documentation.
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Config command
    subparsers.add_parser(
        'config',
        help='Configure Git with your name and email'
    )

    # Init command
    subparsers.add_parser(
        'init',
        help='Initialize a new Git repository'
    )

    # Status command
    subparsers.add_parser(
        'status',
        help='Show the status of your repository'
    )

    # Commit command
    commit_parser = subparsers.add_parser(
        'commit',
        help='Add and commit all changes'
    )
    commit_parser.add_argument(
        '-m', '--message',
        help='Commit message',
        type=str
    )

    # Sync/Upload command
    subparsers.add_parser(
        'sync',
        help='Push your changes to GitHub (alias: upload)'
    )
    subparsers.add_parser(
        'upload',
        help='Push your changes to GitHub (alias: sync)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Map commands to functions
    commands = {
        'config': cmd_config,
        'init': cmd_init,
        'status': cmd_status,
        'commit': cmd_commit,
        'sync': cmd_sync,
        'upload': cmd_sync,  # alias for sync
    }

    if args.command in commands:
        return commands[args.command](args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
