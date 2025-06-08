import logging
import os
from typing import Dict, Any, Optional, Tuple

from fastapi import FastAPI, Request
from octokit import Octokit


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(levelname)s %(asctime)s %(name)s - %(message)s", "%H:%M:%S")

    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = get_logger(__name__)

app = FastAPI()

# Configuration
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID', 'github_app_id')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY', 'github_private_key')


@app.post('/webhook')
async def handle_webhook(request: Request):
    # todo verify signature
    # signature = request.headers.get('x-hub-signature-256')
    # body = await request.body()

    # if not signature:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid signature"
    #     )

    event = request.headers.get('x-github-event')
    payload = await request.json()

    action = payload.get('action')

    for x in payload:
        logger.info(x)
    # logger.info(f'handling {event} - {payload}')

    if event == 'issue_comment' and action == 'created':
        handle_issue_comment(payload)
    # not reacting to push events because uploading too sloow

    return {"status": "processed"}


async def create_pull_request(owner: str, repo: str, title: str, body: str, head: str, base: str = "main") -> str:
    try:
        response = octokit.pulls.create(
            owner=owner,
            repo=repo,
            title=title,
            body=body,
            head=head,
            base=base
        )
        return response["html_url"]
    except Exception as e:
        logger.error(f"Failed to create PR: {str(e)}")
        raise

async def handle_requirements_command(owner: str, repo: str, issue_number: int, comment: Dict[str, Any]) -> str:
    try:
        response_message = f"@{comment['user']['login']}, uploading issue text as technical requirements for the project."
    except Exception as e:
        response_message = f"@{comment['user']['login']}, failed uploading issue text as technical requirements for the project: {str(e)}."

    await octokit.issues.create_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        body=response_message
    )

    logger.info(f"Created comment: {owner} {repo} {issue_number} {response_message}")
    return response_message

async def handle_unit_command(owner: str, repo: str, issue_number: int, comment: Dict[str, Any], feature_request: str) -> str:
    await octokit.issues.create_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        body=f"@{comment['user']['login']}, I will generate unit-tests and respond with new PR url."
    )

    try:
        branch_name = f"unit-tests-{issue_number}"
        
        pr_url = await create_pull_request(
            owner=owner,
            repo=repo,
            title=f"Unit tests for issue #{issue_number}",
            body=f"Generated unit tests for: {feature_request}",
            head=branch_name
        )

        response_message = f"@{comment['user']['login']}, generated unit-tests can be found at {pr_url}. Review carefully."
    except Exception as e:
        response_message = f"@{comment['user']['login']}, PR was not created, failed generating unit-tests: {str(e)}."

    await octokit.issues.create_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        body=response_message
    )
    return response_message

async def handle_attack_command(owner: str, repo: str, issue_number: int, comment: Dict[str, Any]) -> str:
    response_message = f"@{comment['user']['login']}, I will perform security testing for project and provide a report here."

    await octokit.issues.create_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        body=response_message
    )
    return response_message

def parse_command(body: str) -> Tuple[str, str]:
    if not body or not body.startswith('/'):
        return None, None
    
    parts = body.split(' ', 1)
    command = parts[0][1:]  # Remove leading '/'
    args = parts[1] if len(parts) > 1 else ''
    return command, args

async def handle_issue_comment(payload: Dict[str, Any]):
    comment = payload['comment']
    issue = payload['issue']
    repo = payload['repository']

    owner = repo['owner']['login']
    repo_name = repo['name']
    issue_number = issue['number']
    body = comment['body']

    command, args = parse_command(body)
    if not command:
        return

    handlers = {
        'requirements': lambda: handle_requirements_command(owner, repo_name, issue_number, comment),
        'unit': lambda: handle_unit_command(owner, repo_name, issue_number, comment, args),
        'attack': lambda: handle_attack_command(owner, repo_name, issue_number, comment)
    }

    handler = handlers.get(command)
    if handler:
        await handler()
