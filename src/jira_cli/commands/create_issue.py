import click
import os
from ..server import get_jira_client
from datetime import datetime
from tabulate import tabulate
import json
current_date = datetime.now()
date_formatted = current_date.strftime("%y.%m")

@click.command()
@click.option("--project", "-P", help="Jira project key", default=lambda: os.getenv("JIRA_PROJECT"))
@click.option("--summary", "-S", help="Issue summary" )
@click.option("--description", "-D", help="Issue description")
@click.option("--assignee", "-A", help="Issue assignee")
@click.option("--issuetype", "-T", help="Issue type", default="Task")
@click.option("--epic-name", "-EN", help="Epic name")
@click.option("--epic-link", "-EL", help="Epic link")
@click.option("--acceptance-criteria", "-AC", help="Acceptance criteria (one per line)")
@click.option("--links-jira", "-L", help="Issue key to link to (e.g., PROJ-123)")
@click.option("--debug", "-d", is_flag=True, help="Debug mode")
@click.option("--priority", help="Priority (default: P2)", default="P2", type=click.Choice(["S","P0", "P1", "P2"]))
@click.option("--estimate", "-E", help="Remaining estimate in hours (default: 2h)", default="2h")
@click.option("--fix-version", "-FV", help="Fix version(s) (comma-separated)")
@click.option("--story-points", "-SP", help="Story points (default: 1)", default=1.0)
@click.option("--add-to-current-sprint", "-ATS", help="Add to current sprint (default: current sprint)",is_flag=True, 
              default=False)
@click.option("--labels", help="Labels (comma-separated)")
def create_issue( **kwargs):
    """Create a new issue in the specified project."""
    jira = get_jira_client()
    issue_fields = {}
    if kwargs.get("debug"):
        # Prepare table data
        table_data = [[key, value] for key, value in kwargs.items()]
        click.echo(click.style(f"\n[DEBUG] JIRA_URL: {jira.url}", fg="yellow"))
        click.echo(click.style("\n[DEBUG] Debug mode enabled. Issue fields:", fg="yellow"))
        click.echo(tabulate(table_data, headers=["Key", "Value"], tablefmt="simple"))
        click.echo()  # Add a blank line for readability

    try:
        # Get required fields with prompts if not provided
        if not kwargs.get("project"):
            kwargs["project"] = click.prompt("--project, -P: Enter project key", type=str)

        if not kwargs.get("summary"):
            kwargs["summary"] = click.prompt("--summary, -S: Enter issue summary", type=str)
        if not kwargs.get("description"):
            kwargs["description"] = click.edit(
                text="{panel:borderColor=green}\nh3. Input/Observations\n----\n\nh3. Problem\n----\n\nh3. Hypothesis/Fix/Proposed Solution\n----\n\n{panel}",
                require_save=True
            ).strip()
        # if not kwargs.get("assignee"):
        #     kwargs["assignee"] = click.prompt("--assignee, -A: Enter issue assignee", type=str)
        if not kwargs.get("acceptance_criteria"):
            kwargs["acceptance_criteria"] = click.prompt("--acceptance-criteria, -AC: Enter acceptance criteria (one per line)", type=str)
        if not kwargs.get("estimate"):
            kwargs["estimate"] = click.prompt("--estimate, -E: Enter remaining estimate in hours", type=str)
        if not kwargs.get("story_points"):
            kwargs["story_points"] = click.prompt("--story-points, -SP: Enter story points", type=float)
        if kwargs.get("issuetype") == "Epic" and not kwargs.get("epic_name"):
            kwargs["epic_name"] = click.prompt("--epic-name, -EN: Enter epic name", type=str)
            issue_fields["customfield_10006"] = kwargs.get("epic_name")

        issue_fields["project"] = {"key": kwargs.get("project")}
        issue_fields["summary"] = kwargs.get("summary")
        issue_fields["description"] = kwargs.get("description").replace("\\n", "\n").replace("\\t", "\t")
        if kwargs.get("assignee"):
            issue_fields["assignee"] = {"name": kwargs.get("assignee")}
        issue_fields["customfield_12714"] = kwargs.get("acceptance_criteria")
        issue_fields["issuetype"] = {"name": kwargs.get("issuetype")}
        issue_fields["timetracking"] = {"originalEstimate": kwargs.get("estimate")}
        issue_fields["customfield_10002"] = kwargs.get("story_points")
        if kwargs.get("labels"):
            issue_fields["labels"] = kwargs.get("labels").split(",")
        if kwargs.get("epic_link"):
            issue_fields["customfield_10005"] = kwargs.get("epic_link")
        if kwargs.get("fix_version"):
            issue_fields["fixVersions"] = [{"name": kwargs.get("fix_version")}]
        if kwargs.get("add_to_current_sprint"):
            try:
                sprints = jira.get_all_sprints_from_board(os.getenv("JIRA_PROJECT_BOARD_ID"), state="active", start=0, limit=50)
                if not sprints or not sprints.get('values'):
                    click.echo(click.style("Warning: No active sprints found", fg="yellow"))
                else:
                    current_sprint = sprints['values'][0]
                    sprint_id = current_sprint.get('id')
                    issue_fields["customfield_10004"] = sprint_id
                    if kwargs.get("debug"):
                        click.echo(click.style(f"\n[DEBUG] Added to sprint: {current_sprint.get('name')} (ID: {sprint_id})", fg="yellow"))
            except Exception as e:
                click.echo(click.style(f"Warning: Could not add to sprint: {str(e)}", fg="yellow"))
        
        if kwargs.get("priority"):
            if kwargs.get("priority") == "S":
                issue_fields["priority"] = {"name": "Showstopper"}
            elif kwargs.get("priority") == "P0":
                issue_fields["priority"] = {"name": "P0 - Must have"}
            elif kwargs.get("priority") == "P1":
                issue_fields["priority"] = {"name": "P1 - Should have"}
            elif kwargs.get("priority") == "P2":
                issue_fields["priority"] = {"name": "P2 - Nice to have"}
            else:
                issue_fields["priority"] = {"name": "Unprioritized"}
        
        if kwargs.get("debug"):
            table_data = [[key, value] for key, value in kwargs.items()]
            click.echo(click.style("\n[DEBUG] Updated issue fields:", fg="yellow"))
            click.echo(tabulate(table_data, headers=["Key", "Value"], tablefmt="simple"))
            click.echo()  # Add a blank line for readability

        # Create the issue
        new_issue = jira.issue_create_or_update(issue_fields)
        issue_key = new_issue.get("key")

        if kwargs.get("debug"):
            click.echo(click.style(f"[DEBUG] New issue: {new_issue}", fg="yellow"))

    

        if kwargs.get("links_jira"):
            outward_issue = kwargs.get("links_jira")
            inward_issue = issue_key
            click.echo(f"Creating issue link: {outward_issue} to {inward_issue}")
            link_data = {
                "type": {"name": "Relates"},
                "inwardIssue": {"key": outward_issue},
                "outwardIssue": {"key": issue_key}
            }
            jira.create_issue_link(link_data)

        if kwargs.get("debug"):
            table_data = [[key, value] for key, value in issue_fields.items()]        
            click.echo(click.style("\n[DEBUG] Debug mode enabled. Issue fields:", fg="yellow"))
            click.echo(tabulate(table_data, headers=["Key", "Value"], tablefmt="simple"))
            click.echo()  # Add a blank line for readability
            click.echo(click.style("\n[DEBUG] Print JSON. Issue fields:", fg="yellow"))
            click.echo(json.dumps(issue_fields, indent=4))
            click.echo()  # Add a blank line for readability

        click.echo(f"Created issue: {issue_key}")
        click.echo(click.style(f"Created URL: {jira.url}/browse/{issue_key}", fg="blue"))

                
    except Exception as e:
        raise click.ClickException(f"Error creating issue: {str(e)}") 