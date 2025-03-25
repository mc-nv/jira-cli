import click
from ..server import get_jira_client
from tabulate import tabulate

def get_priority_color(priority_name):
    """Get color based on priority level."""
    priority_colors = {
        '*Showstopper*': 'red',
        'P0 - Must have': 'magenta',
        'P1 - Should have': 'yellow',
        'P2 - Nice to have': 'blue',
        'Unprioritized': 'white'
    }
    return priority_colors.get(priority_name, 'white')

def get_predefined_query(flag):
    """Get predefined JQL query based on flag."""
    predefined_queries = {
        'my_issues': 'assignee = currentUser() ORDER BY priority DESC',
        'high_priority': 'priority in (Highest, High) ORDER BY priority DESC',
        'blocked': 'status = Blocked ORDER BY priority DESC',
        'in_progress': 'status = "In Progress" ORDER BY priority DESC',
        'overdue': 'due < now() ORDER BY priority DESC',
        'no_assignee': 'assignee is EMPTY ORDER BY priority DESC',
        'reported_by_me': 'reporter = currentUser() ORDER BY priority DESC',
        'blocked_by_me': 'issue in linkedIssues("is blocked by") AND assignee = currentUser() ORDER BY priority DESC',
        'blocking_me': 'issue in linkedIssues("blocks") AND assignee = currentUser() ORDER BY priority DESC',
        'my_sprint': 'assignee in (currentUser()) and sprint in openSprints()',
        'my_sprint_status': 'assignee in (currentUser()) and sprint in openSprints() ORDER BY status DESC'
    }
    return predefined_queries.get(flag)

@click.command()
@click.argument("jql", required=False)
@click.option('--my-issues', is_flag=True, help='Show issues assigned to me')
@click.option('--high-priority', is_flag=True, help='Show high priority issues')
@click.option('--blocked', is_flag=True, help='Show blocked issues')
@click.option('--in-progress', is_flag=True, help='Show in progress issues')
@click.option('--overdue', is_flag=True, help='Show overdue issues')
@click.option('--no-assignee', is_flag=True, help='Show unassigned issues')
@click.option('--reported-by-me', is_flag=True, help='Show issues reported by me')
@click.option('--blocked-by-me', is_flag=True, help='Show issues blocked by my issues')
@click.option('--blocking-me', is_flag=True, help='Show issues blocking my issues')
@click.option('--my-sprint', is_flag=True, help='Show issues in current sprint')
@click.option('--my-sprint-status', is_flag=True, help='Show issues in current sprint by status')
@click.option('--color', is_flag=True, help='Colorize the output based on priority', default=False)
def jql(jql, **flags):
    """Execute a JQL query and display results in a table format."""
    jira = get_jira_client()
    try:
        # Check for predefined queries
        for flag, value in flags.items():
            if value:
                jql = get_predefined_query(flag)
                break
            else:
                jql = get_predefined_query("my_sprint")
                break
        
        if not jql:
            click.echo("Please provide a JQL query or use one of the predefined flags.")
            return

        # Add ORDER BY priority to the query if it doesn't already have an ORDER BY clause
        if "ORDER BY" not in jql.upper():
            jql = f"{jql} ORDER BY priority DESC"
        
        issues = jira.jql(jql)
        
        if not issues:
            click.echo("No issues found matching the query.")
            return

        # Prepare table data
        table_data = []
        use_colors = flags.get('color', False)
        
        for issue in issues['issues']:
            priority = issue['fields']['priority']['name']
            color = get_priority_color(priority) if use_colors else None
            
            def style_text(text):
                if use_colors and color:
                    return click.style(text, fg=color)
                return text
            
            row = [
                style_text(issue['key']),
                style_text(issue['fields']['summary']),
                style_text(issue['fields']['status']['name']),
                style_text(issue['fields']['issuetype']['name']),
                style_text(priority),
                style_text(issue['fields']['assignee']['displayName']),
                style_text(issue['fields']['reporter']['displayName'])
            ]
            table_data.append(row)

        # Print table with headers
        headers = ["Key", "Summary", "Status", "Type", "Priority", "Assignee", "Reporter"]
        click.echo(tabulate(table_data, headers=headers))

    except Exception as e:
        raise click.ClickException(f"Error executing JQL query: {str(e)}")