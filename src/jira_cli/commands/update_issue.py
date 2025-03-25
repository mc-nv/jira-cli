import click
from ..server import get_jira_client

@click.command()
@click.argument("issue_key")
@click.option("--summary", help="New issue summary")
@click.option("--description", help="New issue description")
@click.option("--status", help="New issue status")
def update_issue(issue_key, summary, description, status):
    """Update an existing issue."""
    jira = get_jira_client()
    try:
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = description
            
        if fields:
            jira.issue_update(issue_key, fields=fields)
            click.echo(f"Updated issue: {issue_key}")
            
        if status:
            jira.issue_transition(issue_key, status)
            click.echo(f"Transitioned issue to status: {status}")
            
    except Exception as e:
        raise click.ClickException(f"Error updating issue: {str(e)}") 