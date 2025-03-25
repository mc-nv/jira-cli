import click
import os
from ..server import get_jira_client

@click.command()
@click.option("--project", required=True, help="Jira project key", default=lambda: os.getenv("JIRA_PROJECT"))
@click.option("--summary", required=True, help="Issue summary")
@click.option("--description", help="Issue description")
@click.option("--priority", help="Issue priority")
@click.option("--assignee", help="Issue assignee")
@click.option("--issuetype", help="Issue type", default="Task")
@click.option("--links-to", help="Issue key to link to (e.g., PROJ-123)")
@click.option("--link-type", help="Type of link (e.g., 'relates to', 'blocks', 'is blocked by')", default="relates to")
def create_issue(project, summary, description, priority, assignee, issuetype, links_to, link_type):
    """Create a new issue in the specified project."""
    jira = get_jira_client()
    try:
        # Prompt for mandatory fields if not provided
        if not project:
            project = click.prompt("Enter project key", type=str)
        if not summary:
            summary = click.prompt("Enter issue summary", type=str)
        if not description:
            description = click.prompt("Enter issue description", type=str)
        if not priority:
            priority = click.prompt("Enter issue priority", type=str)
        if not assignee:
            assignee = click.prompt("Enter issue assignee", type=str)

        issue_dict = {
            "project": {"key": project},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},
            "priority": {"name": priority},
            "assignee": {"name": assignee}
        }
        
        # Create the issue
        new_issue = jira.issue_create(fields=issue_dict)
        new_issue_key = new_issue.get('key')
        click.echo(f"Created issue: {new_issue_key}")
        
        # Create link if specified
        if links_to:
            try:
                jira.create_issue_link(link_type, new_issue_key, links_to)
                click.echo(f"Linked {new_issue_key} {link_type} {links_to}")
            except Exception as e:
                click.echo(f"Warning: Could not create link: {str(e)}")
                
    except Exception as e:
        raise click.ClickException(f"Error creating issue: {str(e)}") 