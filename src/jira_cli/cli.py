import click
from .commands import get_issue, create_issue, update_issue, jql

@click.group()
def main():
    """Jira CLI tool for interacting with Jira instance."""
    pass

# Register commands
main.add_command(get_issue, name='get')
main.add_command(create_issue, name='create')
main.add_command(update_issue, name='update')
main.add_command(jql, name='jql')

if __name__ == "__main__":
    main() 