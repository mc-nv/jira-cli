import os
import click
from dotenv import load_dotenv
from atlassian import Jira

load_dotenv()

def get_jira_client():
    """Initialize Jira client from environment variables."""
    jira_url = os.getenv("JIRA_URL")
    jira_user = os.getenv("JIRA_USER")
    jira_token = os.getenv("JIRA_API_TOKEN")
    
    if not all([jira_url, jira_user, jira_token]):
        raise click.ClickException(
            "Please set JIRA_URL, JIRA_USER, and JIRA_API_TOKEN environment variables"
        )
    
    return Jira(
        url=jira_url,
        username=jira_user,
        password=jira_token
    ) 