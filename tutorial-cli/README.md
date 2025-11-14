# Tutorial CLI

A simple Git wrapper for Python tutorial students. This tool abstracts common Git operations so students can focus on learning Python packages without needing deep Git knowledge.

## Installation

Install the tutorial CLI tool using pip:

```bash
pip install tutorial-cli/
```

Or install directly from the tutorial directory:

```bash
cd tutorial-cli
pip install .
```

## Usage

The `tutorial` command provides several subcommands to help you manage your Git repository:

### Configure Git

Set up your name and email for Git commits:

```bash
tutorial config
```

This command will prompt you for your name and email, and configure Git globally.

### Initialize Repository

Initialize a new Git repository in the current directory:

```bash
tutorial init
```

This will:
- Initialize a Git repository
- Create a `.gitignore` file with common Python exclusions

### Check Status

View the current status of your repository:

```bash
tutorial status
```

### Commit Changes

Add and commit all changes in your repository:

```bash
tutorial commit
```

This will prompt you for a commit message. Alternatively, you can provide the message directly:

```bash
tutorial commit -m "Your commit message here"
```

### Sync with GitHub

Push your commits to GitHub:

```bash
tutorial sync
```

or

```bash
tutorial upload
```

Both commands do the same thing - they push your changes to the remote GitHub repository.

## Typical Workflow

Here's a typical workflow for sharing your package on GitHub:

1. **Configure Git** (only needed once):
   ```bash
   tutorial config
   ```

2. **Initialize your repository**:
   ```bash
   cd mypackage
   tutorial init
   ```

3. **Commit your changes**:
   ```bash
   tutorial commit -m "Initial commit"
   ```

4. **Create a repository on GitHub** and connect it:
   - Go to https://github.com/new
   - Create a new repository named `mypackage`
   - Copy the SSH URL (e.g., `git@github.com:username/mypackage.git`)
   - Connect your local repository:
     ```bash
     git remote add origin git@github.com:username/mypackage.git
     ```

5. **Push to GitHub**:
   ```bash
   tutorial sync
   ```

6. **Make changes and update**:
   ```bash
   # ... make changes to your code ...
   tutorial commit -m "Describe your changes"
   tutorial sync
   ```

## Requirements

- Python 3.8 or higher
- Git installed on your system

## Help

For more information about any command, run:

```bash
tutorial --help
```

Or for help with a specific command:

```bash
tutorial <command> --help
```

## Notes

- The `tutorial sync` and `tutorial upload` commands are aliases - they do the same thing
- All commands use Git under the hood, so you can always fall back to regular Git commands if needed
- The tool assumes you're using SSH authentication with GitHub
