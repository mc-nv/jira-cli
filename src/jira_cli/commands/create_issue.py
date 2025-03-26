import click
import os
from ..server import get_jira_client
from datetime import datetime

current_date = datetime.now()
date_formatted = current_date.strftime("%y.%m")

@click.command()
@click.option("--project", "-P", required=True, help="-P,--project: Jira project key", default=lambda: os.getenv("JIRA_PROJECT"))
@click.option("--summary", "-S", required=True, help="-S,--summary: Issue summary")
@click.option("--description", "-D", help="-D,--description: Issue description")
@click.option("--assignee", "-A", help="-A,--assignee: Issue assignee", default=lambda: os.getenv("JIRA_USER"))
@click.option("--issuetype", "-T", help="-T,--issuetype: Issue type", default="Task")
@click.option("--acceptance-criteria", "-AC", help="-AC,--acceptance-criteria: Acceptance criteria (one per line)")
@click.option("--links-jira", "-L", help="-L,--links-jira: Issue key to link to (e.g., PROJ-123)")
@click.option("--debug", "-d", is_flag=True, help="-d,--debug: Debug mode")
@click.option("--priority", help="-p,--priority: Priority (default: P2)", default="P2", type=click.Choice(["S","P0", "P1", "P2"]))
@click.option("--estimate", "-E", help="-E,--estimate: Remaining estimate in hours (default: 2h)", default="2h")
@click.option("--fix-version", "-FV", help="-FV,--fix-version: Fix version(s) (comma-separated)", default=date_formatted)
@click.option("--story-points", "-SP", help="-SP,--story-points: Story points (default: 1)", default=1.0)
@click.option("--update", "-U", help="-U,--update: Update existing issue")

def create_issue( **kwargs):
    """Create a new issue in the specified project."""
    jira = get_jira_client()
    issue_fields = {}
    print("kwargs: ", kwargs)
    try:
        # Get required fields with prompts if not provided
        lambda: kwargs.keys()
        if "project" not in kwargs or kwargs.get("project") is None:
            kwargs["project"] = click.prompt("Enter project key", type=str)
        if "summary" not in kwargs or kwargs.get("summary") is None:
            kwargs["summary"] = click.prompt("Enter issue summary", type=str)
        if "description" not in kwargs or kwargs.get("description") is None:
            kwargs["description"] = click.edit(
                text="h3. Input",
                require_save=True
            ).strip()
        if "assignee" not in kwargs or kwargs.get("assignee") is None:
            kwargs["assignee"] = click.prompt("Enter issue assignee", type=str)
        if "acceptance_criteria" not in kwargs or kwargs.get("acceptance_criteria") is None:
            kwargs["acceptance_criteria"] = click.prompt("Enter acceptance criteria (one per line)", type=str)
        if "estimate" not in kwargs or kwargs.get("estimate") is None:
            kwargs["estimate"] = click.prompt("Enter remaining estimate in hours", type=str)
        if "story_points" not in kwargs or kwargs.get("story_points") is None:
            kwargs["story_points"] = click.prompt("Enter story points", type=float)
        if "update" in kwargs and kwargs.get("update") is None:
            kwargs["update"] = click.prompt("Enter issue key to update", type=str)

        issue_fields["project"] = {"key": kwargs.get("project")}
        issue_fields["summary"] = kwargs.get("summary")
        issue_fields["description"] = kwargs.get("description").replace("\\n", "\n").replace("\\t", "\t")
        issue_fields["assignee"] = {"name": kwargs.get("assignee")}
        issue_fields["customfield_12714"] = kwargs.get("acceptance_criteria")
        issue_fields["issuetype"] = {"name": kwargs.get("issuetype")}
        issue_fields["timetracking"] = {"originalEstimate": kwargs.get("estimate")}
        issue_fields["customfield_10002"] = kwargs.get("story_points")
        if "fix_version" in kwargs:
            issue_fields["fixVersions"] = [{"name": kwargs.get("fix_version")}]

        if "update" in kwargs and kwargs.get("update") is not None:
            issue_fields["issuekey"] =  kwargs.get("update")
        
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
            click.echo(f"Debug mode enabled. Issue fields: ")
            click.echo(click.style(f"{issue_fields}", fg="yellow"))
        

        # Create the issue
        new_issue = jira.issue_create_or_update(fields=issue_fields)

        if "update" in kwargs and kwargs.get("update") is not None:
            issue_key = kwargs.get("update")
        else:
            issue_key = new_issue.issue_key

        if "links_jira" in kwargs and kwargs.get("links_jira") is not None:
            outward_issue = kwargs.get("links_jira")
            inward_issue = issue_key
            click.echo(f"Creating issue link: {outward_issue} to {inward_issue}")
            link_data = {
                "type": {"name": "Relates"},
                "inwardIssue": {"key": outward_issue},
                "outwardIssue": {"key": issue_key}
            }
            jira.create_issue_link(link_data)

        click.echo(f"Created issue: {issue_key}")
        click.echo(click.style(f"Created URL: {jira.url}/browse/{issue_key}", fg="blue"))

                
    except Exception as e:
        raise click.ClickException(f"Error creating issue: {str(e)}") 