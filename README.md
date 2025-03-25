# Jira CLI

A command-line interface for Jira using the atlassian-python-api library.

## Setup and Installation

1. Create and activate a virtual environment using `uv`:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

2. Install the package in development mode:
   ```bash
   uv pip install -e .
   ```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Jira credentials:
   - `JIRA_URL`: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
   - `JIRA_USERNAME`: Your Jira email address
   - `JIRA_API_TOKEN`: Your Jira API token (create one at https://id.atlassian.com/manage-profile/security/api-tokens)

## Usage

Make sure your virtual environment is activated before running commands.

### Get Issue Details
```bash
jira get-issue PROJ-123
```

### Create New Issue
```bash
jira create-issue --project PROJ --summary "Issue summary" --description "Issue description"
```

### Update Issue
```bash
jira update-issue PROJ-123 --summary "New Summary" --description "New Description" --status "In Progress"
```

## Project Structure

- `src/jira_cli/`: Source code directory
  - `cli.py`: Main CLI implementation
  - `__init__.py`: Package initialization
  - `server/`: Server-related code
    - `client.py`: Jira client implementation
    - `__init__.py`: Server package initialization
  - `commands/`: CLI commands
    - `get_issue.py`: Get issue command
    - `create_issue.py`: Create issue command
    - `update_issue.py`: Update issue command
    - `__init__.py`: Commands package initialization
- `pyproject.toml`: Project configuration and dependencies
- `.env`: Configuration file for Jira credentials (not in version control)

## Development

The project uses:
- `uv` as the package manager
- Virtual environment for isolation
- Modern Python packaging with `pyproject.toml`
- `click` for CLI interface
- `atlassian-python-api` for Jira integration