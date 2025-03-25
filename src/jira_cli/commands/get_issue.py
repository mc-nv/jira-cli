import click
from ..server import get_jira_client
from tabulate import tabulate

@click.command()
@click.argument("issue_key")
def get_issue(issue_key):
    """Get issue details by issue key."""
    jira = get_jira_client()
    try:
        issue = jira.issue(issue_key)
        fields = issue.get('fields', {})

        # Prepare table data
        table_data = [
            [
                "Key",
                "Summary",
                "Status",
                "Type",
                "Priority",
                "Assignee",
                "Reporter",
                "Created",
                "Updated"
            ],
            [
                issue_key,
                fields.get('summary', ''),
                fields.get('status', {}).get('name', ''),
                fields.get('issuetype', {}).get('name', ''),
                fields.get('priority', {}).get('name', ''),
                fields.get('assignee', {}).get('displayName', ''),
                fields.get('reporter', {}).get('displayName', ''),
                fields.get('created', ''),
                fields.get('updated', '')
            ]
        ]

        # Print table
        click.echo(tabulate(table_data, headers="firstrow"))

    except Exception as e:
        raise click.ClickException(f"Error fetching issue: {str(e)}")