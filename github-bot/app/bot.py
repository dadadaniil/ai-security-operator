import base64
import json
import logging
import os
import struct
from typing import Dict, Any, Optional, Tuple

import requests
import uvicorn
from octokit import Octokit
from fastapi import FastAPI, Request


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


GITHUB_APP_ID = os.getenv('GITHUB_APP_ID', 'github_app_id')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY', 'github_private_key')
GITHUB_PRIVATE_KEY = str.replace(GITHUB_PRIVATE_KEY, '\\n', '\n')
ANALYZER_BASEURL = os.getenv('ANALYZER_BASEURL', 'http://localhost:8000')


app = FastAPI()

octokit = Octokit(auth='installation', app_id=GITHUB_APP_ID, private_key=GITHUB_PRIVATE_KEY)


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

    # for x in payload:
    #     logger.info(x)
    # logger.info(f'handling {event} - {payload}')

    if event == 'issue_comment' and action == 'created':
        await handle_issue_comment(payload)
    # not reacting to push events because uploading too sloow

    return {"status": "processed"}


def handle_requirements_command(owner: str, repo: str, issue: Dict, comment: Dict[str, Any]):
    if not str.startswith(issue['title'], 'TR'):
        return

    try:
        file_obj = ('TR.txt', comment['body'])

        files = {'file': file_obj}
        data = {}

        response = requests.post(
            f'{ANALYZER_BASEURL}/project/requirements',
            files=files,
            data=data,
            timeout=120
        )
        response.raise_for_status()

        response_message = f"@{comment['user']['login']}, issue text was uploaded as technical requirements for the project."
    except Exception as e:
        response_message = f"@{comment['user']['login']}, failed uploading issue text as technical requirements for the project: {str(e)}."

    octokit.issues.create_comment(
        owner=owner,
        repo=repo,
        issue_number=issue['number'],
        body=response_message
    )

    logger.info(f"Created comment: {owner} {repo} {issue['number']} {response_message}")


async def handle_unit_command(owner: str, repo: str, issue_number: int, comment: Dict[str, Any], feature_request: str) -> str:
    octokit.issues.create_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        body=f"@{comment['user']['login']}, I will generate unit-tests and respond with new PR url."
    )

    try:
        branch_name = f"unit-tests-{issue_number}"
        base_branch = "main"  # or "master" depending on your repo

        # Get the latest commit from base branch
        # todo get ref from PR, not main
        base_ref = octokit.git.get_ref(
            owner=owner,
            repo=repo,
            ref=f"heads/{base_branch}"
        )
        base_ref = json.loads(base_ref._response.text)

        base_commit_sha = base_ref['object']['sha']

        # Create new branch
        octokit.git.create_ref(
            owner=owner,
            repo=repo,
            ref=f"refs/heads/{branch_name}",
            sha=base_commit_sha
        )

        response = requests.get(f'{ANALYZER_BASEURL}/generation/unit-tests', timeout=120)
        response.raise_for_status()  # Raises exception for 4XX/5XX status codes

        file_path = f"tests/unit_tests_issue_{issue_number}.py"
        file_content = response.text

        file_bytes = file_content.encode("utf-8")
        base64_bytes = base64.b64encode(file_bytes)
        base64_string = base64_bytes.decode("ascii")

        octokit.repos.create_or_update_file_contents(
            owner=owner,
            repo=repo,
            path=file_path,
            message=f"Add unit tests for issue #{issue_number}",
            content=base64_string,
            branch=branch_name
        )

        pr = octokit.pulls.create(
            owner=owner,
            repo=repo,
            title=f"Unit tests for issue #{issue_number}",
            body=f"Generated unit tests for: {feature_request}",
            head=branch_name,
            base=base_branch
        )
        pr = json.loads(pr._response.text)

        pr_url = pr['html_url']
        response_message = f"@{comment['user']['login']}, generated unit-tests can be found at {pr_url}. Review carefully."
    except Exception as e:
        response_message = f"@{comment['user']['login']}, PR was not created, failed generating unit-tests: {str(e)}."
        raise

    octokit.issues.create_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        body=response_message
    )
    return response_message

def handle_attack_command(owner: str, repo: str, issue_number: int, comment: Dict[str, Any]) -> str:
    response_message = f"@{comment['user']['login']}, I will perform security testing for project and provide a report here."

    octokit.issues.create_comment(
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
        'requirements': lambda: handle_requirements_command(owner, repo_name, issue, comment),
        'attack': lambda: handle_attack_command(owner, repo_name, issue_number, comment)
    }

    if command == 'unit':
        await handle_unit_command(owner, repo_name, issue_number, comment, args)
    else:
        handler = handlers.get(command)
        if handler:
            handler()


# if __name__ == '__main__':
    # uvicorn.run(app, host="0.0.0.0", port=8000)